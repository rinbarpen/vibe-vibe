#!/usr/bin/env python3
"""Restore this task's source changes, retaining all planning/verification evidence."""
import argparse,hashlib,json,os
from pathlib import Path
import sys,tempfile

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--target',type=Path)
 parser.add_argument('--check',action='store_true')
 args=parser.parse_args()
 base=Path(__file__).resolve().parent
 record=json.loads((base/'changes.json').read_text())
 root=(args.target or Path(record['target'])).resolve()
 actions=[]
 for change in record['files']:
  rel=Path(change['path'])
  if rel.is_absolute() or '..' in rel.parts or not (str(rel)=='README.md' or str(rel).startswith('manifests/game-design/')):
   raise ValueError('invalid source path')
  dest=root/rel
  if dest.is_symlink() or any(p.is_symlink() for p in dest.parents if p!=root.parent):
   raise ValueError('symlink path')
  if dest.exists() and not dest.is_file():raise ValueError('destination type conflict: '+str(rel))
  actual=sha(dest.read_bytes()) if dest.is_file() else None
  if actual==change['before']:continue
  if actual!=change['after']:raise ValueError('post-task edit conflict: '+str(rel))
  original=base/'baseline'/rel
  old=original.read_bytes() if change['before'] is not None else None
  if old is not None and sha(old)!=change['before']:raise ValueError('baseline hash mismatch')
  actions.append((dest,old))
 if not args.check:
  for dest,old in reversed(actions):
   if old is None:dest.unlink()
   else:
    fd,temp=tempfile.mkstemp(dir=dest.parent)
    with os.fdopen(fd,'wb') as out:out.write(old)
    os.chmod(temp,0o644);os.replace(temp,dest)
 print(('Checked' if args.check else 'Restored')+f': {len(actions)} source paths; planning/evidence retained')
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except (OSError,ValueError,KeyError) as exc:
  print(str(exc),file=sys.stderr);sys.exit(1)
