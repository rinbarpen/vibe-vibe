#!/usr/bin/env python3
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
