#!/usr/bin/env python3
"""Restore only this redraw's files; stop before touching later edits.

python3 .planning/auto-research-wiki-concept/ui-redraw/rollback.py --dry-run
python3 .planning/auto-research-wiki-concept/ui-redraw/rollback.py
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=HERE.parents[2])
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    root=args.root.resolve()
    before=json.loads((HERE/'originals.json').read_text(encoding='utf-8'))
    after=json.loads((HERE/'modified.json').read_text(encoding='utf-8'))
    conflicts=[]
    for name,original in before.items():
        path=root/name
        if root not in path.resolve().parents:
            raise SystemExit('Invalid destination: '+name)
        known={original.get('sha256'),after[name].get('sha256')}
        if sha(path) not in known:
            conflicts.append(name)
        if original['exists']:
            assert sha(HERE/'originals'/name)==original['sha256'],name
    if conflicts:
        print('CONFLICT: later edits detected; no files changed: '+', '.join(conflicts))
        return 2
    restored=removed=0
    for name,original in before.items():
        path=root/name
        if original['exists']:
            restored+=1
            if not args.dry_run:
                path.parent.mkdir(parents=True,exist_ok=True)
                temp=path.with_name(path.name+'.rollback-tmp')
                shutil.copy2(HERE/'originals'/name,temp)
                os.replace(temp,path)
        elif path.exists():
            removed+=1
            if not args.dry_run:path.unlink()
    print(f'{"DRY RUN" if args.dry_run else "RESTORED"}: {restored} originals; {removed} additions removed')
    if not args.dry_run:
        assert all(sha(root/name)==original.get('sha256') for name,original in before.items())
        print('Original SHA256 set verified; unrelated files retained.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
