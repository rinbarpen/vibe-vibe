"""Reproduce local verification, package the manifest, and test scoped rollback."""
from pathlib import Path
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[2]
A = R / '.planning/patent-writing/artifacts'
B = json.loads((A / 'baseline.json').read_text())
records = [json.loads((A / 'baseline-verification.json').read_text())]
work = Path(tempfile.mkdtemp(prefix='patent-writing-verified-'))
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
           PYTHONPATH=str(R / 'tools/vibe_tool/src'),
           VIBE_PROJECTS_FILE=str(work / 'registry/projects.json'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(argv, *, cwd=R, expected=0, label=''):
    argv = list(map(str, argv))
    p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    records.append(dict(label=label, command=argv, cwd=str(cwd),
                        environment={k:env[k] for k in ('PYTHONDONTWRITEBYTECODE','PYTHONPATH','VIBE_PROJECTS_FILE')},
                        stdout=p.stdout, stderr=p.stderr, exit_status=p.returncode,
                        expected_exit_status=expected))
    print(f'{label}: exit={p.returncode}', flush=True)
    if p.returncode != expected:
        print(p.stdout[-6000:], p.stderr[-6000:], flush=True)
        raise AssertionError(label)
    return p

def put(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.tmp')
    tmp.write_text(text, encoding='utf-8'); os.replace(tmp, p)

# Prove that the one repository-wide link failure predates this change. Read
# original catalog bytes in memory, without switching files in the workspace.
baseline_link = '''import importlib.util
from pathlib import Path
from unittest.mock import patch
root=Path.cwd(); spec=importlib.util.spec_from_file_location("language_tests",root/"tools/vibe_tool/tests/test_documentation_languages.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=Path.read_text
mapping={str((root/n).resolve()):root/".planning/patent-writing/artifacts/baseline"/n for n in ("docs/catalog.md","docs/catalog_EN.md")}
def read(p,*a,**kw):
 return old(mapping.get(str(p.resolve()),p),*a,**kw)
with patch.object(Path,"read_text",read):m.test_all_document_links_and_readme_anchors_resolve()
'''
p = run([sys.executable, '-c', baseline_link], expected=1, label='baseline unrelated missing-source link')
assert '../skills/visual-explainer/plugins/visual-explainer' in p.stderr
records.append(dict(label='initial broad regression before local graph refinement',
                    command=[sys.executable,'-m','pytest','tools/vibe_tool/tests/test_patent_writing_manifest.py',
                             'tools/vibe_tool/tests/test_setup.py','tools/vibe_tool/tests/test_harness_rules.py',
                             'tools/vibe_tool/tests/test_projects.py','tools/vibe_tool/tests/test_documentation_languages.py',
                             'tests/test_manifest_workflow.py','-q','-p','no:cacheprovider'],
                    cwd=str(R),stdout=(A/'regression-initial.txt').read_text(),stderr='',exit_status=1,
                    note='91 passed, 121 subtests passed; existing missing visual-explainer source link failed.'))
pytest = [sys.executable, '-m', 'pytest', 'tools/vibe_tool/tests/test_patent_writing_manifest.py',
          'tools/vibe_tool/tests/test_setup.py', 'tools/vibe_tool/tests/test_harness_rules.py',
          'tools/vibe_tool/tests/test_projects.py', 'tools/vibe_tool/tests/test_documentation_languages.py',
          'tests/test_manifest_workflow.py', '-q', '-p', 'no:cacheprovider',
          '-k', 'not test_all_document_links_and_readme_anchors_resolve']
p = run(pytest, label='final relevant regression excluding reproduced pre-existing source gap')
put(A / 'regression.txt', p.stdout + p.stderr)

p = run([sys.executable, '-m', 'vibe_tool', 'list', 'manifests', '--json'], label='modified manifest discovery')
manifest, = [m for m in json.loads(p.stdout) if m['name'] == 'writing']
assert manifest['scenarios'] == ['patent']
assert manifest['required_skills'] == ['chinese-patent', 'omnidraw']

project = work / 'project 专利'
command = [sys.executable, R/'scripts/setup-project.py', 'writing', project,
           '--harness', 'both', '--scenario', 'patent']
run(command + ['--dry-run'], label='actual-source setup preview')
assert not project.exists()
run(command, label='actual-source complete setup')
run([sys.executable, R/'scripts/setup-project.py','writing',project,'--check'], label='actual-source installed hashes')
for base in (R/'manifests/writing', project, project/'rules/writing'):
    args = [sys.executable, base/'scripts/render_patent_workflow.py', '--source',
            base/'references/patent-workflow.json', '--output', base/'references/patent-workflow.svg']
    before = sha(base/'references/patent-workflow.svg')
    run(args, label='workflow regeneration ' + str(base))
    run(args + ['--check'], label='workflow read-only check ' + str(base))
    assert sha(base/'references/patent-workflow.svg') == before
    ET.parse(base/'references/patent-workflow.svg')

# Export smoke fixture: deliberately not a patent draft or invented experiment.
smoke = project / 'drafts/export-smoke'
smoke.mkdir(parents=True)
put(smoke/'说明书.html', '''<!doctype html><html lang="zh-CN"><meta charset="UTF-8"><body>
<h1>导出格式烟雾测试</h1><p>本文件仅验证中文正文、公式和本地图片的转换，不作为专利样稿。</p>
<p>公式：\\(E=mc^2\\)</p><img src="pixel.png" alt="测试图"></body></html>''')
(smoke/'pixel.png').write_bytes(bytes.fromhex('89504e470d0a1a0a0000000d4948445200000001000000010804000000b51c0c020000000b4944415478da6364f80f00010501012718e3660000000049454e44ae426082'))
run(['pandoc', '--version'], label='export prerequisite version')
run([sys.executable, project/'.agents/skills/chinese-patent/scripts/html_to_docx.py',
     smoke/'说明书.html', '-o', smoke/'说明书.docx'], label='installed skill real DOCX export smoke')
with zipfile.ZipFile(smoke/'说明书.docx') as z:
    assert z.testzip() is None
    xml = z.read('word/document.xml').decode()
    assert '导出格式烟雾测试' in xml and 'oMath' in xml
    assert any(n.startswith('word/media/') for n in z.namelist())
    ET.fromstring(xml)
run([sys.executable, '-c', 'import zipfile,sys;from xml.etree import ElementTree as E;z=zipfile.ZipFile(sys.argv[1]);assert z.testzip() is None;d=z.read("word/document.xml");E.fromstring(d);assert "导出格式烟雾测试" in d.decode();assert b"oMath" in d;assert any(n.startswith("word/media/") for n in z.namelist());print("DOCX_REOPEN: Chinese text, math XML and local image present; page layout not assessed.")',
     smoke/'说明书.docx'], label='reopen DOCX and validate literal content')
shutil.copy2(smoke/'说明书.docx', A/'export-smoke.docx')

# Package source with every resource; verify extraction and regeneration.
package = A / 'writing-patent-manifest.zip'
with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted((R/'manifests/writing').rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            z.write(p, 'writing/' + p.relative_to(R/'manifests/writing').as_posix())
with zipfile.ZipFile(package) as z:
    assert z.testzip() is None
    z.extractall(work/'package-check')
    package_members = len(z.namelist())
base = work/'package-check/writing'
run([sys.executable,base/'scripts/render_patent_workflow.py','--source',base/'references/patent-workflow.json',
     '--output',base/'references/patent-workflow.svg','--check'], label='reopened packaged workflow')

# Minimal replayable patch; retain originals and hashes for every changed file.
names = sorted(set(B['files']) | {
    p.relative_to(R).as_posix() for p in (R/'manifests/writing').rglob('*')
    if p.is_file() and '__pycache__' not in p.parts
} | {'tools/vibe_tool/tests/test_patent_writing_manifest.py'})
changes, diffs = [], []
for name in names:
    p = R/name; old = A/'baseline'/name
    old_hash = B['files'].get(name)
    if old_hash:
        assert sha(old) == old_hash
    changes.append(dict(path=name, before=old_hash, after=sha(p)))
    before = old.read_text(encoding='utf-8') if old_hash else ''
    after = p.read_text(encoding='utf-8')
    if before == after:
        continue
    diffs.append(f'diff --git a/{name} b/{name}\n')
    if not old_hash:
        diffs.append('new file mode 100644\n')
    diffs.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                    fromfile='a/'+name if old_hash else '/dev/null', tofile='b/'+name))
put(A/'changes.json', json.dumps(dict(source_root=str(R), changes=changes), ensure_ascii=False, indent=2)+'\n')
put(A/'writing-patent.patch', ''.join(diffs))
rollback = '''#!/usr/bin/env python3
"""Restore only the verified writing/patent changes; preserve later user data."""
import argparse, hashlib, json, os
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--target',type=Path);p.add_argument('--check',action='store_true');a=p.parse_args()
base=Path(__file__).resolve().parent;data=json.loads((base/'changes.json').read_text());root=(a.target or Path(data['source_root'])).resolve()
for c in data['changes']:
 f=root/c['path'];current=sha(f) if f.is_file() else None
 if f.is_symlink() or (f.exists() and not f.is_file()) or current not in (c['before'],c['after']):raise SystemExit('Local edit needs review: '+c['path'])
 if c['before'] and sha(base/'baseline'/c['path'])!=c['before']:raise SystemExit('Original hash mismatch: '+c['path'])
if a.check:print('ROLLBACK_CHECK: all changed paths and preserved originals verified.');raise SystemExit(0)
for c in reversed(data['changes']):
 f=root/c['path']
 if c['before']:
  f.parent.mkdir(parents=True,exist_ok=True);tmp=f.with_name(f.name+'.restore-tmp');tmp.write_bytes((base/'baseline'/c['path']).read_bytes());os.replace(tmp,f)
 else:
  f.unlink(missing_ok=True);parent=f.parent
  while parent!=root:
   try:parent.rmdir()
   except OSError:break
   parent=parent.parent
for c in data['changes']:
 f=root/c['path'];assert (sha(f) if f.is_file() else None)==c['before'],c['path']
print('ROLLBACK_OK: original hashes restored; later unrelated files retained.')
'''
put(A/'rollback.py', rollback)
run([sys.executable,A/'rollback.py','--check'], label='workspace rollback preflight only')
copy = work/'patch replay';copy.mkdir()
for name in B['files']:
    p=copy/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(A/'baseline'/name,p)
run(['git','apply','--check',A/'writing-patent.patch'], cwd=copy, label='reopened patch applicability')
run(['git','apply',A/'writing-patent.patch'], cwd=copy, label='execute patch on baseline copy')
assert all(sha(copy/c['path']) == c['after'] for c in changes)
sentinel=copy/'manifests/writing/later-user-note.txt';put(sentinel,'Retain later user data.\n')
p=copy/'manifests/writing/AGENTS.md';original=p.read_bytes();p.write_bytes(original+b'User edit\n')
run([sys.executable,A/'rollback.py','--target',copy], expected=1, label='rollback stops before changing locally edited paths')
assert p.read_bytes() == original+b'User edit\n'
p.write_bytes(original)
run([sys.executable,A/'rollback.py','--target',copy,'--check'], label='copy rollback preflight')
run([sys.executable,A/'rollback.py','--target',copy], label='execute rollback on patched copy')
assert sentinel.read_text()=='Retain later user data.\n'
assert all((sha(copy/c['path']) if (copy/c['path']).is_file() else None)==c['before'] for c in changes)

report = dict(status='verified_with_preexisting_environment_gap', changed_files=len(changes),
              object='manifests/writing; scenario=patent',
              source_root=str(R), actual_install=str(project),
              baseline='writing/patent absent; reusable chinese-patent skill present',
              modified='writing/patent discoverable; complete setup, installed workflow, real DOCX export, patch replay and rollback verified',
              artifacts={n:dict(path=str(A/n),sha256=sha(A/n)) for n in
                         ('writing-patent-manifest.zip','writing-patent.patch','rollback.py','changes.json','export-smoke.docx','workflow-preview.png')},
              package_members=package_members, commands=records,
              visual_review='Browser canvas raster inspected: Chinese text, three lanes, arrows and workflow branches; local renderer uses facing-edge arrows for same-row stages.',
              known_environment_gap='Full repository documentation-link test also fails against original catalog contents because skills/visual-explainer/plugins/visual-explainer is absent. No unrelated sources initialized.',
              limits=['No actual invention, live prior-art search or patent application authored or submitted.',
                      'DOCX smoke reopens ZIP/XML and checks text/math/image; rendered page layout and legal sufficiency not assessed.',
                      'Host skill auto-activation not observed; explicit file discovery/copies and hashes verified.',
                      'Legacy init/add manifest support is not promised; use setup for this scenario.'])
put(A/'verification.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
loaded=json.loads((A/'verification.json').read_text());assert len(loaded['commands'])==len(records)
assert all(isinstance(c['stdout'],str) and isinstance(c['stderr'],str) for c in loaded['commands'])
print(json.dumps(dict(status=loaded['status'],files=len(changes),package_members=package_members,verification=str(A/'verification.json')),ensure_ascii=False))
