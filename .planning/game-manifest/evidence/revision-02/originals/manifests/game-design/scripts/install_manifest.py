#!/usr/bin/env python3
"""Install game-design resources; preserve user state, ledger-limit force, record rollback."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import uuid
from restore_install import atomic, checked, restore, sha

SOURCE = Path(__file__).resolve().parents[1]
LEDGER = '.game-design/install.json'


def source_files():
    result = []
    for name in ('CLAUDE.md', 'AGENTS.md'):
        result.append((SOURCE / name, name, False))
    result.append((SOURCE / 'README.md', '.game-design/README.md', False))
    for directory in ('references', 'templates', 'scripts'):
        for path in sorted((SOURCE / directory).rglob('*')):
            if path.is_symlink():
                raise ValueError(f'symlink source: {path}')
            if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            if path.name in ('init-game-design.sh', 'install_manifest.py', 'restore_install.py'):
                continue
            result.append((path, '.game-design/' + path.relative_to(SOURCE).as_posix(), False))
    for source in sorted((SOURCE / 'templates/state').iterdir()):
        result.append((source, '.game-design/state/' + source.name, True))
    for path, _, _ in result:
        if not path.is_file():
            raise ValueError(f'missing source: {path}')
    return result


def install(target, force=False, dry_run=False):
    target = target.expanduser().resolve()
    if target.exists() and not target.is_dir():
        raise ValueError('target must be a directory')
    if target == SOURCE or SOURCE.is_relative_to(target) or target.is_relative_to(SOURCE):
        raise ValueError('target must be separate from source')
    ledger_path = checked(target, LEDGER)
    owned = {}
    if ledger_path.exists():
        previous = json.loads(ledger_path.read_text(encoding='utf-8'))
        if (not isinstance(previous, dict) or previous.get('manifest') != 'game-design'
                or type(previous.get('schema_version')) is not int or previous['schema_version'] != 1
                or not isinstance(previous.get('files'), dict)):
            raise ValueError('invalid installation ledger')
        for key, value in previous['files'].items():
            checked(target, key)
            if not isinstance(value, str) or not re.fullmatch('[a-f0-9]{64}', value):
                raise ValueError('invalid ledger hash')
        owned = dict(previous['files'])
    actions = []
    for source, relative, protected in source_files():
        dest = checked(target, relative)
        # Preflight file and all parent types before any write.
        if dest.exists() and not dest.is_file():
            raise ValueError(f'expected file: {relative}')
        for parent in dest.parents:
            if parent == target.parent:
                break
            if parent.exists() and not parent.is_dir():
                raise ValueError(f'expected directory: {parent}')
        data = source.read_bytes()
        if dest.exists() and (protected or relative not in owned or not force):
            print(f'KEEP {relative}')
            continue
        if dest.is_file() and dest.read_bytes() == data:
            continue
        actions.append((dest, relative, data, source.stat().st_mode & 0o777))
        if not protected:
            owned[relative] = sha(data)
        print(f'COPY {relative}')
    new_ledger = (json.dumps({'manifest': 'game-design', 'schema_version': 1, 'files': owned},
                             indent=2, sort_keys=True) + '\n').encode()
    if not ledger_path.is_file() or ledger_path.read_bytes() != new_ledger:
        actions.append((ledger_path, LEDGER, new_ledger, 0o644))
    for name in ('.game-design/deliverables', '.game-design/backups'):
        path = checked(target, name)
        if path.exists() and not path.is_dir():
            raise ValueError(f'expected directory: {name}')
    print(f'{"[dry-run]" if dry_run else "[game-design]"} {len(actions)} writes: {target}')
    if dry_run:
        return 0
    # The complete plan and original hashes are durable before the first payload write.
    if actions:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
        base = checked(target, '.game-design/backups/' + stamp)
        transaction = {'manifest': 'game-design', 'schema_version': 1, 'target': str(target), 'files': []}
        for dest, relative, data, mode in actions:
            old = dest.read_bytes() if dest.is_file() else None
            old_mode = dest.stat().st_mode & 0o777 if old is not None else 0o644
            if old is not None:
                atomic(checked(base / 'originals', relative), old, old_mode)
            transaction['files'].append({'path': relative, 'old_sha256': sha(old) if old is not None else None,
                                         'new_sha256': sha(data), 'old_mode': old_mode})
        atomic(base / 'transaction.json', (json.dumps(transaction, indent=2) + '\n').encode())
        atomic(base / 'restore.py', (SOURCE / 'scripts/restore_install.py').read_bytes(), 0o755)
        try:
            for dest, _, data, mode in actions:
                atomic(dest, data, mode)
        except OSError:
            restore(base, target)
            raise
        print(f'Rollback: python3 {str(base / "restore.py")!r}')
    (target / '.game-design/deliverables').mkdir(parents=True, exist_ok=True)
    if any((target / name).read_bytes() != (SOURCE / name).read_bytes() for name in ('CLAUDE.md', 'AGENTS.md')):
        print('Existing root instructions preserved: merge the .game-design/README.md entry manually.')
    print('Next: read .game-design/README.md; detect the project, then confirm design direction.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', nargs='?', default='.')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('-n', '--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        return install(Path(args.target), args.force, args.dry_run)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'Installation failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
