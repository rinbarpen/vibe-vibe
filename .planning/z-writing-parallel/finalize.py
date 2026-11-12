from pathlib import Path
import difflib, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
R=Path.cwd(); A=R/'.planning/z-writing-parallel/artifacts'; B=json.loads((A/'baseline.json').read_text()); records=[json.loads((A/'baseline-verification.json').read_text())]
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(R/'tools/vibe_tool/src'),'VIBE_HOME':str(R),'VIBE_PROJECTS_FILE':str(A/'projects.json')}
def put(p,s):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.tmp');t.write_text(s,encoding='utf-8');os.replace(t,p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
def run(args,*,cwd=R):
 p=subprocess.run(list(map(str,args)),cwd=cwd,env=ENV,text=True,capture_output=True)
 records.append({'command':list(map(str,args)),'cwd':str(cwd),'stdout':p.stdout,'stderr':p.stderr,'exit_status':p.returncode})
 print(args[0],p.returncode,p.stdout[-200:],flush=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p
changes=[];patch=[]
for name,old in B['files'].items():
 new={'sha256':sha(R/name),'mode':(R/name).stat().st_mode&0o777}
 if old==new:continue
 changes.append({'path':name,'before':old,'after':new})
 patch.append(f'diff --git a/{name} b/{name}\n')
 if old is None:patch.append('new file mode 100644\n')
 oldtext=(A/'baseline'/name).read_text() if old else ''
 patch.extend(difflib.unified_diff(oldtext.splitlines(True),(R/name).read_text().splitlines(True),fromfile='a/'+name if old else '/dev/null',tofile='b/'+name))
put(A/'changes.json',json.dumps({'source_root':str(R),'changes':changes},ensure_ascii=False,indent=2)+'\n');put(A/'z-writing-parallel.patch',''.join(patch))
rollback='''#!/usr/bin/env python3
"""Restore only this update, protecting later edits and the Git index."""
from pathlib import Path
import argparse,hashlib,json,os,tempfile
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path);p.add_argument('--dry-run',action='store_true');a=p.parse_args();r=json.loads((H/'changes.json').read_text());root=(a.root or Path(r['source_root'])).resolve()
def node(p):
 if p.is_symlink():raise SystemExit('Review changed symlink before restoring: '+str(p))
 return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':p.stat().st_mode&0o777} if p.is_file() else None
pending=[]
for c in r['changes']:
 actual=node(root/c['path'])
 if actual==c['before']:continue
 if actual!=c['after']:raise SystemExit('Later edit detected: '+c['path'])
 if c['before'] and node(H/'baseline'/c['path'])!=c['before']:raise SystemExit('Baseline mismatch: '+c['path'])
 pending.append(c)
if a.dry_run:print('Would restore '+str(len(pending))+' paths; no writes.');raise SystemExit(0)
for c in pending:
 q=root/c['path']
 if c['before']:
  with tempfile.NamedTemporaryFile(dir=q.parent,delete=False) as f:f.write((H/'baseline'/c['path']).read_bytes());name=f.name
  os.chmod(name,c['before']['mode']);os.replace(name,q)
 else:q.unlink()
 if node(q)!=c['before']:raise SystemExit('Restore mismatch: '+c['path'])
print('Restored and verified '+str(len(pending))+' paths; Git index untouched.')
'''
put(A/'rollback.py',rollback);(A/'rollback.py').chmod(0o755)
# Execute patch replay and real rollback only on an independent copy.
with tempfile.TemporaryDirectory(prefix='z-writing-parallel-patch-') as directory:
 clone=Path(directory)/'repo';shutil.copytree(A/'baseline',clone)
 for name,info in B['files'].items():
  if info:os.chmod(clone/name,info['mode'])
 run(['git','apply','--check',A/'z-writing-parallel.patch'],cwd=clone)
 run(['git','apply',A/'z-writing-parallel.patch'],cwd=clone)
 for c in changes:assert sha(clone/c['path'])==c['after']['sha256']
 sentinel=clone/'user-note.md';sentinel.write_text('preserve user edits\n')
 run([sys.executable,A/'rollback.py','--root',clone,'--dry-run'])
 run([sys.executable,A/'rollback.py','--root',clone])
 for name,info in B['files'].items():assert sha(clone/name)==(info['sha256'] if info else None)
 assert sentinel.read_text()=='preserve user edits\n'
run([sys.executable,A/'rollback.py','--dry-run'])
# A current, self-contained real installation, then validate the archive itself.
with tempfile.TemporaryDirectory(prefix='z-writing-parallel-install-') as directory:
 project=Path(directory)/'project'
 run([sys.executable,'-m','vibe_tool','add','skill','z-writing',project])
 installed=project/'.agents/skills/z-writing';assert not any(p.is_symlink() for p in installed.rglob('*'))
 assert (installed/'references/parallel-chapters.md').read_bytes()==(R/'mine/z-writing/references/parallel-chapters.md').read_bytes()
 assert not (project/'AGENTS.md').exists()
 with zipfile.ZipFile(A/'z-writing.skill','w',compression=zipfile.ZIP_DEFLATED) as z:
  for file in sorted(installed.rglob('*')):
   if file.is_file():z.write(file,'z-writing/'+file.relative_to(installed).as_posix())
 with zipfile.ZipFile(A/'z-writing.skill') as z:
  assert z.testzip() is None
  assert z.read('z-writing/references/parallel-chapters.md')==(R/'mine/z-writing/references/parallel-chapters.md').read_bytes()
  z.extractall(Path(directory)/'archive-check');member_count=len(z.namelist())
 run([sys.executable,'/home/rczx/.codex/skills/.system/skill-creator/scripts/quick_validate.py',Path(directory)/'archive-check/z-writing'])
# Reopen the exact test output and preserve its executed command and status.
regression=(A/'regression.log').read_text();assert '81 passed, 5 subtests passed' in regression
records.append({'command':'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src uv run --no-project --offline --with python-docx --with openpyxl --with python-pptx --with pypdf --with pillow --with pytest python -m pytest tools/vibe_tool/tests/test_z_writing.py tools/vibe_tool/tests/test_project_update.py tools/vibe_tool/tests/test_office_skill_separation.py tools/vibe_tool/tests/test_writing_design_sources.py -q -rs -p no:cacheprovider','cwd':str(R),'stdout':regression,'stderr':'','exit_status':0})
report={'status':'verified','change':'Host-driven chapter agents with single-writer main-agent merge; no new runtime scheduler.','changed_paths':changes,'package':{'path':'z-writing.skill','sha256':sha(A/'z-writing.skill'),'members':member_count},'commands':records,'limits':['No real manuscript or model-driven multi-agent writing evaluation was run.','Automated tests validate packaging, update/restore behavior and preservation of an existing user chapter; they do not score prose or semantic merge quality.']}
put(A/'verification.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert json.loads((A/'verification.json').read_text())['status']=='verified'
assert all(sha(R/c['path'])==c['after']['sha256'] for c in changes)
print('VERIFIED:',len(changes),'changed paths;',member_count,'archive members; patch replay, installation and rollback passed.')
