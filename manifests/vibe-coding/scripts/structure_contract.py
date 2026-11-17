"""Validate project-owned structure contracts and collect scoped source files."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from pathlib import Path

EXTENSIONS = {'.py', '.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx', '.go', '.rs',
              '.java', '.cs', '.dart', '.c', '.h', '.cpp', '.cc', '.hpp', '.swift', '.kt'}
PRUNED = {'.git', '.vibe-tool', '__pycache__', 'node_modules', '.venv', 'venv',
          '.next', '.nuxt', '.gradle', '.dart_tool'}


class ContractError(ValueError):
    """An invalid or incomplete input must not be reported as a passing check."""


def digest(value):
    return hashlib.sha256(value).hexdigest()


def load_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as exc:
        raise ContractError(f'{path.name}: {exc}') from exc


def relative(value):
    if value == '.':
        return value
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or value.startswith('/') or any(p in {'.', '..', ''} for p in value.split('/'))):
        raise ContractError(f'Expected a project-relative POSIX path: {value!r}')
    return value


def within(root, name):
    relative(name)
    path = root / name
    if any(part.is_symlink() for part in (path, *path.parents) if part != root and root in part.parents):
        raise ContractError(f'Symlink input is not followed: {name}')
    if not path.resolve().is_relative_to(root):
        raise ContractError(f'Path leaves project root: {name}')
    return path


def strings(value, label, allow_empty=True):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
        raise ContractError(f'{label} must be a list of nonempty strings')
    if len(set(value)) != len(value) or (not value and not allow_empty):
        raise ContractError(f'{label} must be unique and nonempty when required')
    return value


def integer(value, label):
    if type(value) is not int or value < 1:
        raise ContractError(f'{label} must be a positive integer')
    return value


def fields(value, allowed, required, label):
    if not isinstance(value, dict) or set(value) - allowed or required - set(value):
        raise ContractError(f'{label}: missing or unknown fields; expected {sorted(allowed)}')


def load_contract(root, name):
    path = within(root, name)
    data = load_json(path)
    fields(data, {'schema_version', 'source_roots', 'exclude', 'extensions', 'modules',
                  'max_lines', 'snapshot', 'dependency_evidence', 'external_prefixes'},
           {'schema_version', 'source_roots', 'modules', 'snapshot'}, 'contract')
    if type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ContractError('Unsupported contract schema_version (expected 1)')
    for name in strings(data['source_roots'], 'source_roots', False):
        if not within(root, name).is_dir():
            raise ContractError(f'Source root does not exist: {name}')
    for name in ('snapshot', 'dependency_evidence'):
        if name in data:
            within(root, data[name])
    strings(data.get('exclude', []), 'exclude')
    strings(data.get('external_prefixes', []), 'external_prefixes')
    extensions = strings(data.get('extensions', sorted(EXTENSIONS)), 'extensions', False)
    if any(not x.startswith('.') or '/' in x for x in extensions):
        raise ContractError('extensions must be filename suffixes starting with a dot')
    if 'max_lines' in data:
        integer(data['max_lines'], 'max_lines')
    if not isinstance(data['modules'], list) or not data['modules']:
        raise ContractError('modules must be a nonempty list')
    names, prefixes, paths = set(), set(), []
    for module in data['modules']:
        fields(module, {'name', 'paths', 'responsibility', 'allowed_dependencies', 'public_paths',
                        'import_prefixes', 'entrypoints', 'docs', 'max_lines'},
               {'name', 'paths', 'responsibility', 'allowed_dependencies', 'public_paths',
                'import_prefixes', 'entrypoints', 'docs'}, 'module')
        name = module['name']
        if not isinstance(name, str) or not name or name in names:
            raise ContractError('Module names must be unique nonempty strings')
        names.add(name)
        if not isinstance(module['responsibility'], str) or not module['responsibility'].strip():
            raise ContractError(f'{name}: responsibility is required')
        for field in ('paths', 'public_paths', 'entrypoints', 'docs', 'import_prefixes', 'allowed_dependencies'):
            strings(module[field], name + '.' + field, field not in {'paths', 'docs'})
        for field in ('paths', 'public_paths', 'entrypoints', 'docs'):
            for item in module[field]:
                within(root, item)
        if len(module['paths']) != 1 and module['import_prefixes']:
            raise ContractError(f'{name}: import prefix resolution requires one path; use file evidence for multi-root modules')
        for prefix in module['import_prefixes']:
            if prefix in prefixes or prefix.startswith('.'):
                raise ContractError(f'Duplicate or relative import prefix: {prefix}')
            prefixes.add(prefix)
        for directory in module['paths']:
            if not any(under(directory, source) for source in data['source_roots']):
                raise ContractError(f'{directory}: module path must be inside a source root')
            for previous in paths:
                if under(directory, previous) or under(previous, directory):
                    raise ContractError(f'Overlapping module paths: {directory}, {previous}')
            paths.append(directory)
        for entry in module['entrypoints'] + module['public_paths']:
            if not any(under(entry, directory) for directory in module['paths']):
                raise ContractError(f'{entry}: entrypoint/public path must belong to {name}')
        if 'max_lines' in module:
            integer(module['max_lines'], name + '.max_lines')
    for module in data['modules']:
        if set(module['allowed_dependencies']) - names or module['name'] in module['allowed_dependencies']:
            raise ContractError(f"{module['name']}: unknown or self dependency")
    return data, digest(json.dumps(data, sort_keys=True, separators=(',', ':')).encode())


def under(path, directory):
    return directory == '.' or path == directory or path.startswith(directory + '/')


def owner(path, contract):
    return next((m for m in contract['modules'] if any(under(path, d) for d in m['paths'])), None)


def collect(root, contract):
    files = {}
    skipped = set()
    extensions = set(contract.get('extensions', EXTENSIONS))
    for source in contract['source_roots']:
        for directory, dirs, names in os.walk(within(root, source), followlinks=False):
            for name in list(dirs):
                path = Path(directory) / name
                rel = path.relative_to(root).as_posix()
                if name in PRUNED or any(fnmatch.fnmatchcase(rel + '/', g) for g in contract.get('exclude', [])):
                    dirs.remove(name); skipped.add(rel)
                elif path.is_symlink():
                    raise ContractError(f'Symlink input is not followed: {rel}')
            for name in sorted(names):
                path = Path(directory) / name
                rel = path.relative_to(root).as_posix()
                if any(fnmatch.fnmatchcase(rel, g) for g in contract.get('exclude', [])):
                    skipped.add(rel); continue
                if path.suffix not in extensions:
                    continue
                path = within(root, rel)
                try:
                    raw = path.read_bytes()
                    text = raw.decode('utf-8-sig')
                except (OSError, UnicodeError) as exc:
                    raise ContractError(f'{rel}: unreadable UTF-8 source: {exc}') from exc
                files[rel] = {'text': text, 'sha256': digest(raw), 'lines': len(text.splitlines())}
    return dict(sorted(files.items())), sorted(skipped)
