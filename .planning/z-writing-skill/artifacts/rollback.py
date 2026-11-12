#!/usr/bin/env python3
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
