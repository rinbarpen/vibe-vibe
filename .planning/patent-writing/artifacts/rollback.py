#!/usr/bin/env python3
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
