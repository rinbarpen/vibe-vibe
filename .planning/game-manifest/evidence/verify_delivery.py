#!/usr/bin/env python3
"""Reopen package/patch/rollback and execute all in disposable verification copies."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,tarfile,tempfile

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
records=[]
def run(argv,cwd,expected=0,env=None):
 result=subprocess.run(list(map(str,argv)),cwd=cwd,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1',**(env or {})},text=True,capture_output=True)
 records.append({'command':list(map(str,argv)),'cwd':str(cwd),'stdin':'','env':env or {},'stdout':result.stdout,'stderr':result.stderr,'exit_status':result.returncode})
 assert result.returncode==expected,result.stdout+result.stderr
 return result

def main():
 changes=json.loads((BASE/'changes.json').read_text())
 sha=lambda data:hashlib.sha256(data).hexdigest()
 with tempfile.TemporaryDirectory(prefix='game-design-artifact-verify-') as temp:
  workspace=Path(temp);archive=workspace/'archive';stage=workspace/'patch';archive.mkdir();stage.mkdir()
  with tarfile.open(BASE/'modified.tar.gz') as tar:
   assert sorted(tar.getnames())==sorted(c['path'] for c in changes['files'])
   for item in tar.getmembers():
    path=Path(item.name);assert not path.is_absolute() and '..' not in path.parts and item.isfile()
   tar.extractall(archive,filter='data')
  shutil.copyfile(BASE/'baseline/README.md',stage/'README.md')
  run(['git','apply','--check',BASE/'changes.patch'],stage)
  run(['git','apply',BASE/'changes.patch'],stage)
  for change in changes['files']:
   assert sha((archive/change['path']).read_bytes())==change['after']
   assert (stage/change['path']).read_bytes()==(archive/change['path']).read_bytes()
  run([sys.executable,archive/'manifests/game-design/scripts/game_design.py','check-catalog'],archive)
  run([sys.executable,archive/'manifests/game-design/scripts/game_design.py','render-adapters','--check'],archive)
  run([sys.executable,archive/'manifests/game-design/scripts/render_workflow.py','--source',archive/'manifests/game-design/references/workflow.json','--output',archive/'manifests/game-design/references/workflow.svg','--check'],archive)
  fixture=workspace/'fixture';fixture.mkdir();(fixture/'project.godot').write_text('config_version=5\n')
  run([sys.executable,stage/'manifests/game-design/scripts/game_design.py','detect','--project',fixture],stage)
  run([sys.executable,BASE/'rollback.py','--target',stage,'--check'],stage)
  run([sys.executable,BASE/'rollback.py','--target',stage],stage)
  assert (stage/'README.md').read_bytes()==(BASE/'baseline/README.md').read_bytes()
  assert all(not (stage/c['path']).exists() for c in changes['files'] if c['before'] is None)
  run([sys.executable,BASE/'rollback.py','--target',stage],stage)
 # Baseline versus modified discovery: exact paired commands, current external checkout unchanged.
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--baseline-root", type=Path)
 args=parser.parse_args()
 context=json.loads((BASE/"baseline-context.json").read_text())
 baseline=str(args.baseline_root or context["baseline_root"])
 code='from pathlib import Path; from vibe_tool.discovery import discover_manifests; print("game-design" in {m.name for m in discover_manifests(Path("manifests"))})'
 run([sys.executable,'-c',code],baseline,env={'PYTHONPATH':str(Path(baseline)/'tools/vibe_tool/src')})
 assert records[-1]['stdout']=='False\n'
 run([sys.executable,'-c',code],ROOT,env={'PYTHONPATH':str(ROOT/'tools/vibe_tool/src')})
 assert records[-1]['stdout']=='True\n'
 # Reopen literal test outputs, including known nonzero baseline results.
 for name,cmd,exit_code in [
  ('focused.log','PYTHONPATH=tools/vibe_tool/src PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s manifests/game-design/tests -v',0),
  ('regression.log','PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src python3 -m pytest tools/vibe_tool/tests tests/test_manifest_workflow.py manifests/game-design/tests -q',1),
  ('baseline-regression.log','PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src python3 -m pytest tools/vibe_tool/tests/test_ccfa_skill_replacement.py tools/vibe_tool/tests/test_mattpocock_manifest.py -q',1)]:
  records.append({'command':cmd,'cwd':baseline if name.startswith('baseline') else str(ROOT),'stdin':'','combined_output':(BASE/name).read_text(),'exit_status':exit_code})
 text=(BASE/'regression.log').read_text();before=(BASE/'baseline-regression.log').read_text()
 failures=lambda s:{line for line in s.splitlines() if line.startswith('FAILED ')}
 assert failures(text)==failures(before) and len(failures(text))==9
 result={'status':'verified','source_files':len(changes['files']),'artifact_hashes':{name:sha((BASE/name).read_bytes()) for name in ('modified.tar.gz','changes.patch','rollback.py')},'behaviors':['HEAD baseline: game-design not discoverable; modified: discoverable','Godot format hint detected with runtime_validation=not_run','patch payload matches archive; rollback restores baseline bytes and removes new source files'],'runtime_engine_execution':'not_run','known_baseline_failures':sorted(failures(text)),'records':records}
 (BASE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 # Reopen record after writing; checksums bind the four deliverable roles.
 saved=json.loads((BASE/'verification.json').read_text());assert saved['status']=='verified'
 print('Verified package, patch, record, rollback:',len(changes['files']),'source paths;',len(records),'command records')

if __name__=='__main__':main()
