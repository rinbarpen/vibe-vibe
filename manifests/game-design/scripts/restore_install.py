#!/usr/bin/env python3
"""Standalone file-level rollback; leaves transaction evidence and user files intact."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked(root, relative):
    rel = Path(relative)
    native = (len(rel.parts) == 3 and rel.parts[1] == 'agents'
              and rel.stem.startswith('game-design-')
              and ((rel.parts[0] == '.claude' and rel.suffix == '.md')
                   or (rel.parts[0] == '.codex' and rel.suffix == '.toml')))
    if (not relative or rel.is_absolute() or '..' in rel.parts or '\\' in relative
            or rel.as_posix() != relative
            or not (relative in ('CLAUDE.md', 'AGENTS.md') or relative.startswith('.game-design/') or native)):
        raise ValueError(f'invalid managed path: {relative}')
    path = root
    for part in rel.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f'symlink destination: {relative}')
    return path


def atomic(path, data, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name + '.')
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data)
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def restore(base, target=None, check=False):
    transaction = json.loads((base / 'transaction.json').read_text(encoding='utf-8'))
    if transaction.get('manifest') != 'game-design' or transaction.get('schema_version') != 1:
        raise ValueError('invalid transaction')
    root = Path(target or transaction['target']).resolve()
    actions = []
    for item in transaction['files']:
        dest = checked(root, item['path'])
        if dest.exists() and not dest.is_file():
            raise ValueError(f'expected file: {item["path"]}')
        current = sha(dest.read_bytes()) if dest.is_file() else None
        old = item['old_sha256']
        if current not in (item['new_sha256'], old):
            raise ValueError(f'post-install edit conflict: {item["path"]}')
        if current == old:
            continue
        data = None
        if old is not None:
            source = checked(base / 'originals', item['path'])
            data = source.read_bytes()
            if sha(data) != old:
                raise ValueError(f'backup hash mismatch: {item["path"]}')
        actions.append((dest, data, item['old_mode']))
    if not check:
        for dest, data, mode in reversed(actions):
            if data is None:
                dest.unlink()
            else:
                atomic(dest, data, mode)
    return len(actions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        count = restore(Path(__file__).resolve().parent, args.target, args.check)
        print(f'{"Checked" if args.check else "Restored"}: {count} paths')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Rollback failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
