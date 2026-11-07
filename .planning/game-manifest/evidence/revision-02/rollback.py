#!/usr/bin/env python3
"""Restore this extension to its previous manifest revision; retain planning/evidence."""
import argparse,hashlib,json,os
from pathlib import Path
import sys,tempfile

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args()
 base=Path(__file__).resolve().parent;data=json.loads((base/'changes.json').read_text());root=(args.target or Path(data['target'])).resolve();actions=[]
 for item in data['changes']:
  rel=Path(item['path'])
  if rel.is_absolute() or '..' in rel.parts or not (str(rel)=='README.md' or str(rel).startswith('manifests/game-design/')):raise ValueError('invalid rollback path')
  dest=root/rel
  if dest.is_symlink() or any(p.is_symlink() for p in dest.parents if p.is_relative_to(root)):raise ValueError('symlink rollback path')
  if dest.exists() and not dest.is_file():raise ValueError('destination type conflict')
  actual=sha(dest.read_bytes()) if dest.is_file() else None
  if actual==item['before']:continue
  if actual!=item['after']:raise ValueError('post-extension edit conflict: '+str(rel))
  old=(base/'originals'/rel).read_bytes() if item['before'] is not None else None
  if old is not None and sha(old)!=item['before']:raise ValueError('original digest mismatch')
  actions.append((dest,old,item['before_mode']))
 if not args.check:
  for dest,old,mode in reversed(actions):
   if old is None:dest.unlink()
   else:
    dest.parent.mkdir(parents=True,exist_ok=True);fd,temp=tempfile.mkstemp(dir=dest.parent)
    with os.fdopen(fd,'wb') as out:out.write(old)
    os.chmod(temp,mode);os.replace(temp,dest)
 print(('Checked' if args.check else 'Restored')+f': {len(actions)} extension source paths; earlier revision/planning/evidence retained')
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except (OSError,ValueError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(1)
