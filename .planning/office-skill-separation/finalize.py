from pathlib import Path
import difflib, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
R=Path.cwd(); A=R/'.planning/office-skill-separation/artifacts'; BASE=json.loads((A/'baseline.json').read_text())
def put(path,data):
 path.parent.mkdir(parents=True,exist_ok=True); temp=path.with_name(path.name+'.tmp');temp.write_text(data,encoding='utf-8');os.replace(temp,path)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
previous=json.loads((A/'verification.json').read_text()) if (A/'verification.json').is_file() else {}
records=previous.get('commands',[])
reuse=any(x.get('label')=='actual project install' and x.get('exit_status')==0 for x in records)
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(R/'tools/vibe_tool/src'),'VIBE_HOME':str(R),'VIBE_PROJECTS_FILE':str(A/'project-registry.json')}
def run(command, *, cwd=R, expect=0, label=None):
 result=subprocess.run(list(map(str,command)),cwd=cwd,env=ENV,capture_output=True,text=True)
 record={'label':label,'command':list(map(str,command)),'cwd':str(cwd),'inputs':{},'stdout':result.stdout,'stderr':result.stderr,'exit_status':result.returncode}
 records.append(record); print(label or command, 'exit',result.returncode,flush=True)
 if result.returncode!=expect:
  put(A/'verification.json',json.dumps({'status':'incomplete','commands':records},ensure_ascii=False,indent=2)+'\n');raise RuntimeError(result.stdout+result.stderr)
 return result
if not reuse:
 # Preserve the exact completed baseline result, not a rerun on changed sources.
 records.append({'label':'baseline regression','command':['python','-m','pytest','tools/vibe_tool/tests/test_office_install.py','tools/vibe_tool/tests/test_office_runtime.py','tools/vibe_tool/tests/test_office_workflow_diagrams.py','-q','-p','no:cacheprovider'],'cwd':str(R),'environment':{'PYTHONDONTWRITEBYTECODE':'1'},'inputs':{'source_snapshot':'baseline.json'},'stdout':(A/'baseline-tests.log').read_text(),'stderr':'','exit_status':0})
 run([sys.executable,'/home/rczx/.codex/skills/.system/skill-creator/scripts/quick_validate.py','mine/office'],label='skill validation')
 for root in ['mine/office','manifests/office']:
  run([sys.executable,root+'/scripts/render_workflow.py','--source',root+'/assets/workflow.json','--output',root+'/assets/workflow.svg','--check'],label=root+' workflow check')
 # Actual sources, no synthetic format skills and no global registry mutation.
 run([sys.executable,'-m','vibe_tool','add','skill','office',A/'standalone-project'],label='standalone skill install')
 run([sys.executable,'-m','vibe_tool','init','office',A/'office-project','--dry-run'],label='actual project dry-run')
 assert not (A/'office-project').exists()
 run([sys.executable,'-m','vibe_tool','init','office',A/'office-project'],label='actual project install')
 assert not (A/'standalone-project/office').exists()
 assert not (A/'standalone-project/AGENTS.md').exists()
 assert not (A/'office-project/office/docx/CLAUDE.md').exists()
 assert (A/'office-project/.agents/skills/office/docx/macros/OfficeLayout.bas').is_file()
 for root in [A/'standalone-project/.agents/skills/office',A/'office-project/office']:
  run([sys.executable,root/'scripts/render_workflow.py','--source',root/'assets/workflow.json','--output',root/'assets/workflow.svg','--check'],label='installed workflow check')
else:
 print('Reusing verified standalone/project installations and prior command records.',flush=True)
# Both VBA sources are moved byte-for-byte, not rewritten during repackaging.
macro_proof=[]
for name in ['docx/macros/OfficeLayout.bas','xlsx/macros/OfficeWorkbook.bas']:
 old='manifests/office/'+name; new='mine/office/'+name
 assert BASE['files'][old]['sha256']==sha(R/new)
 macro_proof.append({'baseline':old,'modified':new,'sha256':sha(R/new),'byte_identical':True,'native_execution':'not part of this packaging change'})
# Include all new/moved implementation files in the reviewable patch.
current={}
for rel in BASE['scopes']:
 p=R/rel
 for f in ([p] if p.is_file() else p.rglob('*') if p.is_dir() else []):
  if f.is_file() and not {'__pycache__','.pytest_cache'}.intersection(f.parts):current[f.relative_to(R).as_posix()]=f
changes=[]; patch=[]
for name in sorted(set(BASE['files'])|set(current)):
 old=A/'baseline'/name; new=current.get(name); before=BASE['files'].get(name,{}).get('sha256');after=sha(new) if new else None
 if before==after:continue
 mode=new.stat().st_mode&0o777 if new else None
 changes.append({'path':name,'before':before,'after':after,'before_mode':BASE['files'].get(name,{}).get('mode'),'after_mode':mode})
 patch.append(f'diff --git a/{name} b/{name}\n')
 if before is None:patch.append(f'new file mode {0o100755 if mode & 0o111 else 0o100644:o}\n')
 elif after is None:patch.append(f'deleted file mode {0o100755 if BASE["files"][name]["mode"] & 0o111 else 0o100644:o}\n')
 oldtext=old.read_bytes().decode('utf-8') if before else ''; newtext=new.read_bytes().decode('utf-8') if after else ''
 for line in difflib.unified_diff(oldtext.splitlines(keepends=True),newtext.splitlines(keepends=True),fromfile='a/'+name if before else '/dev/null',tofile='b/'+name if after else '/dev/null'):
  patch.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
put(A/'changes.json',json.dumps({'source_root':str(R),'changes':changes},ensure_ascii=False,indent=2)+'\n')
put(A/'office-separation.patch',''.join(patch))
rollback='''#!/usr/bin/env python3
"""Restore only this change, without touching Git's index or later user files."""
from pathlib import Path
import argparse,hashlib,json,os,tempfile
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path);p.add_argument('--dry-run',action='store_true');args=p.parse_args()
record=json.loads((HERE/'changes.json').read_text());root=(args.root or Path(record['source_root'])).resolve()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
pending=[]
for item in record['changes']:
 path=root/item['path'];actual=sha(path)
 if actual==item['before']:continue
 if actual!=item['after']:raise SystemExit('Later change detected; review before restoring: '+str(path))
 if item['before'] is not None and sha(HERE/'baseline'/item['path'])!=item['before']:raise SystemExit('Baseline hash mismatch: '+item['path'])
 pending.append(item)
if args.dry_run:print('Would restore '+str(len(pending))+' files; no writes.');raise SystemExit(0)
for item in pending:
 path=root/item['path']
 if item['before'] is None:path.unlink()
 else:
  path.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as temp:
   temp.write((HERE/'baseline'/item['path']).read_bytes());name=temp.name
  os.chmod(name,item['before_mode']);os.replace(name,path)
 if sha(path)!=item['before']:raise SystemExit('Restore verification failed: '+str(path))
# Remove only empty directories introduced by this change, preserving user data.
for item in pending:
 path=(root/item['path']).parent
 while path!=root:
  try:path.rmdir()
  except OSError:break
  path=path.parent
print('Restored and verified '+str(len(pending))+' files. Git index untouched.')
'''
put(A/'rollback.py',rollback);(A/'rollback.py').chmod(0o755)
# Reopen/apply the patch to the actual baseline, then execute rollback on that
# independent copy; never revert and reapply over the user's working tree.
with tempfile.TemporaryDirectory(prefix='office patch rollback ') as directory:
 copy=Path(directory)/'repo';shutil.copytree(A/'baseline',copy)
 run(['git','apply','--check',A/'office-separation.patch'],cwd=copy,label='patch applicability on baseline')
 run(['git','apply',A/'office-separation.patch'],cwd=copy,label='patch application on baseline')
 for item in changes:assert sha(copy/item['path'])==item['after'],item['path']
 sentinel=copy/'mine/office/user-later-note.txt';sentinel.parent.mkdir(parents=True,exist_ok=True);sentinel.write_text('Preserve unrelated later data.\n')
 run([sys.executable,A/'rollback.py','--root',copy,'--dry-run'],label='rollback preview on modified copy')
 run([sys.executable,A/'rollback.py','--root',copy],label='rollback execution on modified copy')
 for name,info in BASE['files'].items():assert sha(copy/name)==info['sha256'],name
 assert sentinel.read_text()=='Preserve unrelated later data.\n'
 for item in changes:
  if item['before'] is None:assert not (copy/item['path']).exists()
run([sys.executable,A/'rollback.py','--dry-run'],label='live rollback preview only')
# Reusable distributable, validated by reopening every member.
with zipfile.ZipFile(A/'office.skill','w',compression=zipfile.ZIP_DEFLATED) as archive:
 for path in sorted((R/'mine/office').rglob('*')):
  if path.is_file() and '__pycache__' not in path.parts:archive.write(path,'office/'+path.relative_to(R/'mine/office').as_posix())
with zipfile.ZipFile(A/'office.skill') as archive:
 assert archive.testzip() is None
 assert 'office/SKILL.md' in archive.namelist()
# Final regression after renderer portability fixes.
tests=['tools/vibe_tool/tests/'+p.name for p in sorted((R/'tools/vibe_tool/tests').glob('test_office*.py'))]
tests += ['tools/vibe_tool/tests/'+name for name in ['test_omnippt.py','test_omni_ui_design.py','test_setup.py','test_project_update.py','test_manifest_installation.py']]
result=run(['uv','run','--no-project','--offline','--with','python-docx','--with','openpyxl','--with','python-pptx','--with','pypdf','--with','pillow','--with','pytest','python','-m','pytest',*tests,'-q','-p','no:cacheprovider'],label='final scoped regression')
put(A/'final-regression.log',result.stdout+result.stderr)
report={'status':'verified','changed_file_count':len(changes),'baseline_manifest':'baseline.json','changes':'changes.json','patch':'office-separation.patch','rollback':'rollback.py','skill_archive':{'path':'office.skill','sha256':sha(A/'office.skill')},'macro_preservation':macro_proof,'visual_review':{'method':'CairoSVG PNGs viewed in chat after CJK font and SVG 1.1 text fixes','files':['office-skill-workflow.png','office-project-workflow.png'],'result':'Chinese labels, branch labels, nodes and lane boundaries readable; no clipping observed'},'commands':records,'limits':['Native Microsoft Office VBA compile/run was not performed by this packaging change.','Final regression skip reasons are retained in the pytest output; fixture results are not production document acceptance.']}
put(A/'verification.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Verify the record and the advertised deliverables can be reopened.
assert json.loads((A/'verification.json').read_text())['status']=='verified'
assert all(sha(R/i['path'])==i['after'] for i in changes)
print('VERIFIED',len(changes),'changed paths; patch replay and rollback passed.',flush=True)
print(result.stdout[-500:],flush=True)
