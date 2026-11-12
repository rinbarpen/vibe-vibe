from pathlib import Path
import difflib,hashlib,json,os,shutil,subprocess,sys,tempfile,zipfile
R=Path.cwd();A=R/'.planning/z-writing-skill/artifacts';B=json.loads((A/'baseline.json').read_text());records=[];O=Path(tempfile.mkdtemp(prefix='z-writing-office-'))/'project'
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(R/'tools/vibe_tool/src'),'VIBE_HOME':str(R),'VIBE_PROJECTS_FILE':str(A/'projects.json')}
def put(p,s):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.tmp');t.write_text(s,encoding='utf-8');os.replace(t,p)
def node(p):
 if p.is_symlink():return {'kind':'link','target':os.readlink(p)}
 if p.is_file():return {'kind':'file','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 return {'kind':'missing'}
def run(args,*,cwd=R,expected=0,label=''):
 p=subprocess.run(list(map(str,args)),cwd=cwd,env=ENV,capture_output=True,text=True)
 records.append({'label':label,'command':list(map(str,args)),'cwd':str(cwd),'stdout':p.stdout,'stderr':p.stderr,'exit_status':p.returncode,'expected_exit_status':expected})
 print(label,p.returncode,flush=True)
 put(A/'verification-in-progress.json',json.dumps({'status':'in_progress','commands':records},ensure_ascii=False,indent=2)+'\n')
 if p.returncode!=expected:raise RuntimeError(p.stdout+p.stderr)
 return p
baseline_code="""import json;from pathlib import Path;b=json.loads(Path('.planning/z-writing-skill/artifacts/baseline.json').read_text());a=Path('.planning/z-writing-skill/artifacts/baseline');assert 'mine/z-writing/SKILL.md' not in b['files'];assert 'ai-vibe-writing' in (a/'manifests/office/skills.txt').read_text();assert not any(x.startswith('mine/z-humanizer/skills/') for x in b['links']);print('BASELINE: no unified writer; Office uses AI Vibe directly; scholarly humanizer bundles absent.')"""
run([sys.executable,'-c',baseline_code],label='baseline architecture verification against saved bytes')
run([sys.executable,'/home/rczx/.codex/skills/.system/skill-creator/scripts/quick_validate.py','mine/z-writing'],label='skill metadata validation')
if not (A/'standalone/.agents/skills/z-writing/SKILL.md').is_file():
 run([sys.executable,'-m','vibe_tool','add','skill','z-writing',A/'standalone'],label='actual-source standalone installation')
else:
 print('Reusing already installed standalone writer.',flush=True)
S=A/'standalone/.agents/skills/z-writing'
assert not any(p.is_symlink() for p in S.rglob('*'))
assert not (A/'standalone/.ai_context').exists()
assert (S/'references/z-humanizer/skills/academic-humanizer/SKILL.md').is_file()
# A complete source-backed project setup, not a fixture-only dependency test.
run([sys.executable,'-m','vibe_tool','setup','office',O,'--harness','generic','--dry-run'],label='actual Office setup preview')
assert not (O).exists()
run([sys.executable,'-m','vibe_tool','setup','office',O,'--harness','generic'],label='actual Office setup')
run([sys.executable,'-m','vibe_tool','setup','office',O,'--check'],label='actual Office setup hash check')
assert (O/'.agents/skills/z-writing/references/ai-vibe-writing/.ai_context/prompts/1_style_extractor.md').is_file()
# Execute a real packaged engine after installation. Synthetic samples are
# explicitly not user style evidence or a semantic authorship evaluation.
D=A/'voice-demo';(D/'samples').mkdir(parents=True,exist_ok=True)
put(D/'samples/example.md','We inspect evidence before revising a claim. Each table has one source. A clear draft preserves conditions and technical names.\n'*4)
engine=S/'references/z-humanizer/references/unslop/scripts'
run([sys.executable,engine/'voice_profile.py',D/'samples','-o',D/'profile.json'],label='bundled voice profile execution')
run([sys.executable,engine/'voice_card.py','--profile',D/'profile.json','--samples',D/'samples','--out',D/'card','--name','synthetic-demo','--provenance'],label='bundled voice card execution')
assert json.loads((D/'profile.json').read_text())['metadata']['low_confidence'] is True
put(D/'original.txt','The dataset contains 64 entries.\n');put(D/'candidate.txt','There are 64 entries in the dataset.\n');put(D/'constraints.json',json.dumps({'constraints':[{'type':'number','value':'64'}]}))
run([sys.executable,engine/'validate_preservation.py',D/'original.txt',D/'candidate.txt',D/'constraints.json'],label='preserved-number positive fixture')
put(D/'candidate.txt','There are 65 entries in the dataset.\n')
run([sys.executable,engine/'validate_preservation.py',D/'original.txt',D/'candidate.txt',D/'constraints.json'],expected=1,label='changed-number negative fixture')
# A distributable contains real files, not source-repository symlinks.
with zipfile.ZipFile(A/'z-writing.skill','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in sorted(S.rglob('*')):
  if p.is_file():z.write(p,'z-writing/'+p.relative_to(S).as_posix())
with zipfile.ZipFile(A/'z-writing.skill') as z:assert z.testzip() is None and 'z-writing/SKILL.md' in z.namelist()
current={}
for rel in B['scopes']:
 p=R/rel
 for f in ([p] if p.is_file() or p.is_symlink() else p.rglob('*') if p.is_dir() else []):
  if not {'__pycache__','.pytest_cache'}.intersection(f.parts) and (f.is_file() or f.is_symlink()):current[f.relative_to(R).as_posix()]=f
before={k:{'kind':'file','sha256':v['sha256']} for k,v in B['files'].items()};before.update({k:{'kind':'link','target':v} for k,v in B['links'].items()})
changes=[];patch=[]
for name in sorted(set(before)|set(current)):
 old=before.get(name,{'kind':'missing'});new=node(current[name]) if name in current else {'kind':'missing'}
 if old==new:continue
 changes.append({'path':name,'before':old,'after':new,'before_mode':B['files'].get(name,{}).get('mode')})
 patch.append(f'diff --git a/{name} b/{name}\n')
 if old['kind']=='missing':patch.append('new file mode '+('120000' if new['kind']=='link' else '100755' if current[name].stat().st_mode&0o111 else '100644')+'\n')
 if new['kind']=='missing':patch.append('deleted file mode '+('120000' if old['kind']=='link' else '100755' if B['files'][name]['mode']&0o111 else '100644')+'\n')
 oldtext=old['target'] if old['kind']=='link' else (A/'baseline'/name).read_bytes().decode('utf-8') if old['kind']=='file' else ''
 newtext=new['target'] if new['kind']=='link' else current[name].read_bytes().decode('utf-8') if new['kind']=='file' else ''
 for line in difflib.unified_diff(oldtext.splitlines(keepends=True),newtext.splitlines(keepends=True),fromfile='a/'+name if old['kind']!='missing' else '/dev/null',tofile='b/'+name if new['kind']!='missing' else '/dev/null'):
  patch.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
put(A/'changes.json',json.dumps({'source_root':str(R),'changes':changes},ensure_ascii=False,indent=2)+'\n');put(A/'z-writing.patch',''.join(patch))
rollback='''#!/usr/bin/env python3
"""Restore this task's files/links only; preserve later edits and the Git index."""
from pathlib import Path
import argparse,hashlib,json,os,tempfile
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path);p.add_argument('--dry-run',action='store_true');a=p.parse_args();record=json.loads((HERE/'changes.json').read_text());root=(a.root or Path(record['source_root'])).resolve()
def node(p):
 if p.is_symlink():return {'kind':'link','target':os.readlink(p)}
 if p.is_file():return {'kind':'file','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 return {'kind':'missing'}
pending=[]
for item in record['changes']:
 actual=node(root/item['path'])
 if actual==item['before']:continue
 if actual!=item['after']:raise SystemExit('Later edit detected; review before restoring: '+item['path'])
 if item['before']['kind']=='file' and node(HERE/'baseline'/item['path'])!=item['before']:raise SystemExit('Baseline hash mismatch: '+item['path'])
 pending.append(item)
if a.dry_run:print('Would restore '+str(len(pending))+' paths; no writes.');raise SystemExit(0)
for item in pending:
 p=root/item['path'];before=item['before']
 if p.is_symlink() or p.is_file():p.unlink()
 if before['kind']=='link':p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to(before['target'],target_is_directory=True)
 elif before['kind']=='file':
  p.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.NamedTemporaryFile(dir=p.parent,delete=False) as temp:temp.write((HERE/'baseline'/item['path']).read_bytes());name=temp.name
  os.chmod(name,item['before_mode']);os.replace(name,p)
 if node(p)!=before:raise SystemExit('Restore verification failed: '+str(p))
for item in pending:
 p=(root/item['path']).parent
 while p!=root:
  try:p.rmdir()
  except OSError:break
  p=p.parent
print('Restored and verified '+str(len(pending))+' paths. Git index untouched.')
'''
put(A/'rollback.py',rollback);(A/'rollback.py').chmod(0o755)
with tempfile.TemporaryDirectory(prefix='z-writing patch rollback ') as directory:
 copy=Path(directory)/'repo';shutil.copytree(A/'baseline',copy)
 for name,target in B['links'].items():
  q=copy/name;q.parent.mkdir(parents=True,exist_ok=True);q.symlink_to(target,target_is_directory=True)
 run(['git','apply','--check',A/'z-writing.patch'],cwd=copy,label='patch applicability on baseline')
 run(['git','apply',A/'z-writing.patch'],cwd=copy,label='patch replay on baseline')
 for item in changes:assert node(copy/item['path'])==item['after'],item['path']
 sentinel=copy/'mine/z-writing/later-user-note.txt';sentinel.write_text('keep later user data\n')
 run([sys.executable,A/'rollback.py','--root',copy,'--dry-run'],label='rollback preview on modified copy')
 run([sys.executable,A/'rollback.py','--root',copy],label='actual rollback on modified copy')
 for name,n in before.items():assert node(copy/name)==n,name
 assert sentinel.read_text()=='keep later user data\n'
 for item in changes:
  if item['before']['kind']=='missing':assert node(copy/item['path'])=={'kind':'missing'}
run([sys.executable,A/'rollback.py','--dry-run'],label='live rollback preview only')
regression=A/'final-regression.log';text=regression.read_text();assert 'failed' not in text.lower() and 'passed' in text
records.append({'label':'final scoped regression','command':'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src uv run --no-project --offline --with python-docx --with openpyxl --with python-pptx --with pypdf --with pillow --with pytest python -m pytest tools/vibe_tool/tests/test_z_writing.py tools/vibe_tool/tests/test_writing_design_sources.py tools/vibe_tool/tests/test_office*.py tools/vibe_tool/tests/test_omnippt.py tools/vibe_tool/tests/test_omni_ui_design.py tools/vibe_tool/tests/test_setup.py tools/vibe_tool/tests/test_project_update.py tools/vibe_tool/tests/test_manifest_installation.py -q -rs -p no:cacheprovider','cwd':str(R),'stdout':text,'stderr':'','exit_status':0,'expected_exit_status':0})
report={'status':'verified','changed_paths':len(changes),'baseline':'baseline.json','commands':records,'package':{'path':'z-writing.skill','sha256':node(A/'z-writing.skill')['sha256']},'resolved_defect':'Nested registered engine symlinks are now materialized on update; retargeted engine sources are rejected without changing installed files.','limits':['Prompt-based writing and semantic voice matching were not measured by a model-driven authoring benchmark.','English synthetic voice samples validate real script execution only; Chinese style judgment uses contextual examples, not the English profile metrics.','Research lifecycle and public-article writing-agent workflows were not migrated.']}
put(A/'verification.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert json.loads((A/'verification.json').read_text())['status']=='verified'
assert all(node(R/i['path'])==i['after'] for i in changes)
print('VERIFIED',len(changes),'paths; package, patch replay and rollback passed.',flush=True)
