#!/usr/bin/env python3
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
