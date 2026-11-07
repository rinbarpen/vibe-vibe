#!/usr/bin/env python3
"""Package changed source + canonical runtime dependencies; verify actual detached install and rollback."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tarfile,tempfile
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3];records=[]
sha=lambda data:hashlib.sha256(data).hexdigest()
def command(argv,cwd,expected=0):
 result=subprocess.run(list(map(str,argv)),cwd=cwd,text=True,capture_output=True,
                       env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0'})
 records.append({'command':list(map(str,argv)),'cwd':str(cwd),'stdin':'','env':{'PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0'},'stdout':result.stdout,'stderr':result.stderr,'exit_status':result.returncode})
 assert result.returncode==expected,result.stdout+result.stderr
 return result

def unpack(archive,target):
 with tarfile.open(archive) as tar:
  for member in tar.getmembers():
   rel=Path(member.name);assert member.isfile() and not rel.is_absolute() and '..' not in rel.parts
   path=target/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(tar.extractfile(member).read());path.chmod(member.mode)

def main():
 assert sha((BASE/'baseline.tar.gz').read_bytes())==(BASE/'baseline.sha256').read_text().strip()
 with tempfile.TemporaryDirectory(prefix='game-production-package-') as temp:
  work=Path(temp);previous=work/'previous';previous.mkdir();unpack(BASE/'baseline.tar.gz',previous)
  source_paths=[Path('README.md')]+sorted(p.relative_to(ROOT) for p in (ROOT/'manifests/game-design').rglob('*') if p.is_file() and p.suffix!='.pyc' and '__pycache__' not in p.parts)
  dependencies=[Path('manifests/unity-game/scripts/dcc_cli.py'),Path('manifests/unity-game/templates/Blender/export_model.py')]
  old_paths=[p.relative_to(previous) for p in previous.rglob('*') if p.is_file()]
  changes=[]
  for rel in sorted(set(source_paths)|set(old_paths)):
   old=previous/rel;new=ROOT/rel;before=sha(old.read_bytes()) if old.is_file() else None;after=sha(new.read_bytes()) if new.is_file() else None
   if before!=after:
    changes.append({'path':str(rel),'before':before,'after':after,'before_mode':old.stat().st_mode&0o777 if old.is_file() else 0o644})
    if old.is_file():
     target=BASE/'originals'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,target)
  payload=[{'path':str(rel),'sha256':sha((ROOT/rel).read_bytes()),'role':'canonical_dependency' if rel in dependencies else 'source'} for rel in source_paths+dependencies]
  (BASE/'changes.json').write_text(json.dumps({'target':str(ROOT),'baseline':'previous game-design revision','changes':changes,'payload':payload},ensure_ascii=False,indent=2)+'\n')
  with tarfile.open(BASE/'modified.tar.gz','w:gz') as tar:
   for rel in source_paths+dependencies:tar.add(ROOT/rel,arcname=str(rel),recursive=False)
  # A temporary local index gives reproducible project-relative paths without touching the user's index.
  patchrepo=work/'patchrepo';shutil.copytree(previous,patchrepo)
  command(['git','init','-q','.'],patchrepo);command(['git','add','--all'],patchrepo)
  for rel in source_paths:
   destination=patchrepo/rel;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,destination)
  new_paths=[rel for rel in source_paths if not (previous/rel).is_file()]
  if new_paths:command(['git','add','--intent-to-add','--',*new_paths],patchrepo)
  patch=command(['git','diff','--binary','--no-ext-diff'],patchrepo).stdout
  (BASE/'changes.patch').write_text(patch)
  detached=work/'detached';detached.mkdir();unpack(BASE/'modified.tar.gz',detached)
  for item in payload:assert sha((detached/item['path']).read_bytes())==item['sha256']
  installed=work/'new game'
  command([sys.executable,detached/'manifests/game-design/scripts/install_manifest.py',installed],detached)
  runtime=installed/'.game-design'
  for rel in dependencies:
   dst=runtime/('scripts/dcc_cli.py' if rel.name=='dcc_cli.py' else 'templates/Blender/export_model.py')
   assert dst.read_bytes()==(ROOT/rel).read_bytes()
  for args in [('check-production',),('render-production','--check'),('genre','--id','roguelike'),('work','--area','modeling')]:
   result=command([sys.executable,runtime/'scripts/production_tools.py',*args],installed)
   if args[0]=='check-production':
    value=json.loads(result.stdout);assert (value['genres'],value['areas'],value['tasks'])==(32,19,94)
  command([sys.executable,runtime/'scripts/render_workflow.py','--source',runtime/'references/workflow.json','--output',runtime/'references/workflow.svg','--check'],installed)
  command([sys.executable,runtime/'scripts/dcc_cli.py','doctor','--blender',work/'missing-blender','--output-dir',work/'dcc-evidence'],installed,2)
  assert json.loads((work/'dcc-evidence/result.json').read_text())['status']=='not_run'
  command([sys.executable,runtime/'scripts/version_check.py','--project',installed],installed,1)
  # Paired behavior: previous revision lacks the detailed production query; new detached install exposes it.
  result=command([sys.executable,previous/'manifests/game-design/scripts/production_tools.py','check-production'],previous,2)
  patched=work/'patched';shutil.copytree(previous,patched)
  command(['git','apply','--check',BASE/'changes.patch'],patched);command(['git','apply',BASE/'changes.patch'],patched)
  for rel in source_paths:assert (patched/rel).read_bytes()==(detached/rel).read_bytes()
  command([sys.executable,BASE/'rollback.py','--target',patched,'--check'],patched)
  command([sys.executable,BASE/'rollback.py','--target',patched],patched)
  for rel in old_paths:assert (patched/rel).read_bytes()==(previous/rel).read_bytes()
  assert all(not (patched/rel).exists() for rel in new_paths)
  command([sys.executable,BASE/'rollback.py','--target',patched],patched)
 # Test logs are literal prior command output; known failures are compared with the confirmed HEAD baseline.
 for source,name,argv,rc in [
  ('/tmp/game-production-focused.log','focused.log','PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src python3 -m pytest manifests/game-design/tests manifests/unity-game/tests/test_dcc_cli.py tests/test_manifest_workflow.py -q',0),
  ('/tmp/game-production-regression-final.log','regression.log','PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src python3 -m pytest tools/vibe_tool/tests tests/test_manifest_workflow.py manifests/game-design/tests manifests/unity-game/tests/test_dcc_cli.py -q',1)]:
  shutil.copyfile(source,BASE/name)
  records.append({'command':argv,'cwd':str(ROOT),'stdin':'','combined_output':(BASE/name).read_text(),'exit_status':rc})
 baseline=(BASE.parent/'baseline-regression.log').read_text()
 failed=lambda value:{line for line in value.splitlines() if line.startswith('FAILED ')}
 assert len(failed(baseline))==9 and failed(baseline)==failed((BASE/'regression.log').read_text())
 assert '104 passed' in (BASE/'focused.log').read_text()
 result={'status':'verified','scope':'extension relative to previous delivered manifest; canonical dependencies unchanged',
         'coverage':{'engines':23,'genres':32,'areas':19,'tasks':94},'changed_source_files':len(changes),
         'payload_files':len(payload),'runtime_modeling_and_gameplay':'not_run',
         'artifact_hashes':{name:sha((BASE/name).read_bytes()) for name in ('modified.tar.gz','changes.patch','rollback.py')},
         'verified_behaviors':['Previous revision lacks detailed production query; new install exposes complete 32/19/94 catalogs',
                              'Detached archive actually installs and canonical DCC bytes match upstream',
                              'Missing Blender is not_run; local non-Git project is reported without initialization',
                              'Patch matches archive source bytes; rollback restores previous source bytes and is idempotent'],
         'known_baseline_failures':sorted(failed(baseline)),'records':records}
 (BASE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 reopened=json.loads((BASE/'verification.json').read_text());assert reopened['status']=='verified'
 print('VERIFIED:',len(changes),'changed source paths;',len(payload),'payload files;',len(records),'command records')

if __name__=='__main__':main()
