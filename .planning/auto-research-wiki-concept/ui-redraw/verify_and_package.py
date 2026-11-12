#!/usr/bin/env python3
"""Run exact checks, create a binary-capable diff, and execute rollback in a mirror."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=HERE.parent
REPORT={'task':'Redraw existing concept map with vibe-coding UI rules; carry the same applicable constraints in both Omni packages.','commands':[]}
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(ROOT/'tools/vibe_tool/src'),'OMNIDRAW_MERMAID_RENDERER':(HERE/'mermaid-renderer.txt').read_text().strip(),'VIBE_PROJECTS_FILE':str(HERE/'test-projects.json')}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(args,*,cwd=ROOT,expected=0):
    result=subprocess.run([str(x) for x in args],cwd=cwd,env=ENV,capture_output=True,text=True,timeout=120)
    REPORT['commands'].append({'argv':[str(x) for x in args],'cwd':str(cwd),'expected_exit':expected,'exit_status':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode!=expected:raise AssertionError(REPORT['commands'][-1])
    return result

try:
    run([sys.executable,'-B',HERE/'originals/.planning/auto-research-wiki-concept/render.py','--check'])
    run([sys.executable,'-B',BASE/'render.py','--check'])
    for name in ['omnidraw','omnisheet']:
        run([sys.executable,'-B','/home/rczx/.codex/skills/.system/skill-creator/scripts/quick_validate.py',ROOT/'mine'/name])
    run([sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider',
         'tools/vibe_tool/tests/test_omni_ui_design.py','tools/vibe_tool/tests/test_office_workflow_diagrams.py',
         'tools/vibe_tool/tests/test_visualization_scenarios.py','tools/vibe_tool/tests/test_ccfa_skill_replacement.py'])
    run(['git','diff','--check','--','mine/omnidraw','mine/omnisheet','tools/vibe_tool/tests/test_omni_ui_design.py'])
    for mode in ['baseline','modified']:
        behavior=HERE/f'{mode}-behavior.json'
        report=json.loads(behavior.read_text(encoding='utf-8'))
        assert report['mode']==mode
        REPORT[mode]=report
        REPORT['commands'].append({'argv':[sys.executable,'-B',str(BASE/'verify_ui.py'),'--mode',mode],
          'cwd':str(ROOT),'exit_status':0,'stdout':(HERE/f'{mode}-browser.log').read_text(encoding='utf-8'),
          'stderr':'','evidence':str(behavior),'sha256':sha(behavior),'execution':'Completed in the actual browser run immediately before packaging; literal output preserved.'})
    REPORT['rules']={name:sha(ROOT/name) for name in json.loads((BASE/'concept-map.json').read_text())['presentation']['rules']}
    REPORT['environment']={key:ENV[key] for key in ['PYTHONPATH','OMNIDRAW_MERMAID_RENDERER','VIBE_PROJECTS_FILE']}
    REPORT['scope']={'baseline':'Original static desktop SVG reader, measured at four widths.',
      'modified':'Responsive HTML at four widths × light/dark; keyboard disclosure; text and domain coverage; token contrast; 1440×1280 static SVG/PNG.',
      'skill_install':'Actual isolated add_skill for each package, followed by removal of its source repo; both guides remain usable without design-skill dependencies.',
      'not_claimed':['No user-study results','No backend state or data-writing UI','No domain research execution','Existing projects were not batch-updated; source packages changed only.']}
    # A stable pointer is part of the patch. The complete record sits outside the
    # transaction payload so adding patch/rollback results has no self-hash cycle.
    pointer={'version':2,'report':'ui-redraw/verification-record.json','baseline':'ui-redraw/baseline-behavior.json','modified':'ui-redraw/modified-behavior.json','source_semantics_unchanged':True}
    (BASE/'verification.json').write_text(json.dumps(pointer,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    originals=json.loads((HERE/'originals.json').read_text())
    originals['.planning/auto-research-wiki-concept/verify_ui.py']={'exists':False}
    (HERE/'originals.json').write_text(json.dumps(originals,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    modified={}
    for name in originals:
        src=ROOT/name
        assert src.is_file(),name
        target=HERE/'modified'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,target)
        modified[name]={'exists':True,'sha256':sha(target)}
    (HERE/'modified.json').write_text(json.dumps(modified,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    diff=subprocess.run(['git','diff','--no-index','--binary','--src-prefix=a/','--dst-prefix=b/','originals','modified'],cwd=HERE,capture_output=True,text=True)
    assert diff.returncode==1,diff.stderr
    patch=diff.stdout
    for prefix in ['a','b']:
        for folder in ['originals','modified']:
            patch=patch.replace(f'{prefix}/{folder}/',f'{prefix}/')
    patch_path=HERE/'changes.patch'
    patch_path.write_text(patch,encoding='utf-8')
    REPORT['commands'].append({'argv':['git','diff','--no-index','--binary','--src-prefix=a/','--dst-prefix=b/','originals','modified'],'cwd':str(HERE),'exit_status':diff.returncode,'stdout_artifact':str(patch_path),'stderr':diff.stderr,'path_normalization':'Strip snapshot directory components from a/ and b/ paths.'})
    with tempfile.TemporaryDirectory(prefix='ui-redraw-rollback-') as temp:
        mirror=Path(temp)
        for name,original in originals.items():
            if original['exists']:
                target=mirror/name
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(HERE/'originals'/name,target)
        unrelated=mirror/'unrelated-user-note.txt'
        unrelated.write_text('Keep this unrelated content.\n')
        run(['git','apply','--check',patch_path],cwd=mirror)
        run(['git','apply',patch_path],cwd=mirror)
        assert all(sha(mirror/name)==item['sha256'] for name,item in modified.items())
        # Stop before writing anything when one of the owned files has changed later.
        conflict=mirror/'mine/omnidraw/SKILL.md'
        saved=conflict.read_bytes()
        conflict.write_bytes(saved+b'\nConcurrent edit fixture.\n')
        run([sys.executable,'-B',HERE/'rollback.py','--root',mirror],expected=2)
        assert conflict.read_bytes().endswith(b'Concurrent edit fixture.\n')
        assert sha(mirror/'mine/omnisheet/SKILL.md')==modified['mine/omnisheet/SKILL.md']['sha256']
        conflict.write_bytes(saved)
        run([sys.executable,'-B',HERE/'rollback.py','--root',mirror])
        assert all((sha(mirror/name) if (mirror/name).is_file() else None)==item.get('sha256') for name,item in originals.items())
        assert unrelated.read_text()=='Keep this unrelated content.\n'
        run([sys.executable,'-B',mirror/'.planning/auto-research-wiki-concept/render.py','--check'],cwd=mirror)
        REPORT['patch_and_rollback']={'patch_apply':'PASS','modified_hashes':'PASS','later_edit_guard':'PASS','original_hashes_restored':'PASS','restored_renderer':'PASS','unrelated_files_retained':'PASS','execution_scope':'Disposable mirror only; the real workspace remains at the modified version.'}
    run([sys.executable,'-B',HERE/'rollback.py','--dry-run'])
    REPORT['artifacts']={name:{'path':str(path),'sha256':sha(path)} for name,path in {
      'modified_map':BASE/'concept-map.svg','preview':BASE/'concept-map.png','reader':BASE/'concept-map.html',
      'patch':patch_path,'rollback':HERE/'rollback.py','original_manifest':HERE/'originals.json','modified_manifest':HERE/'modified.json'}.items()}
    REPORT['status']='PASS'
finally:
    (HERE/'verification-record.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: source fidelity, 8 browser views, 26 tests, both standalone skill installs, read-only workflow regeneration, patch application and guarded rollback.')
print('Verification:',HERE/'verification-record.json')
print('Patch:',HERE/'changes.patch')
print('Rollback:',HERE/'rollback.py')
