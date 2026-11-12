"""User-local project index; project-local installation records remain authoritative."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

from .config import CONFIG_DIR
from .installations import load_installations


def registry_path():
    return Path(os.environ.get('VIBE_PROJECTS_FILE') or CONFIG_DIR / 'projects.json').expanduser().absolute()


def _name(value):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or value in ('.', '..') or any(c in value for c in '/\\\x00\n\r'):
        raise ValueError('Invalid project name: ' + repr(value))
    return value


def _path_key(path):
    return os.path.normcase(str(Path(path).expanduser().resolve()))


def load_registry():
    path = registry_path()
    if path.is_symlink():
        raise ValueError('Project registry must not be a symlink')
    if not path.exists():
        return {'schema_version': 1, 'projects': {}}
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1 or not isinstance(data.get('projects'), dict):
        raise ValueError('Invalid project registry: ' + str(path))
    seen_names, seen_paths = set(), set()
    for name, entry in data['projects'].items():
        _name(name)
        if not isinstance(entry, dict) or set(entry) != {'path', 'source'} or any(not isinstance(v, str) or not Path(v).is_absolute() for v in entry.values()):
            raise ValueError('Invalid project entry: ' + name)
        if name.casefold() in seen_names or _path_key(entry['path']) in seen_paths:
            raise ValueError('Duplicate project name or path in registry')
        seen_names.add(name.casefold()); seen_paths.add(_path_key(entry['path']))
    return data


@contextmanager
def _lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + '.lock')
    if lock.is_symlink():
        raise ValueError('Project registry lock must not be a symlink')
    with lock.open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'0'); stream.flush()
        deadline = time.monotonic() + 5
        while True:
            try:
                if os.name == 'nt':
                    import msvcrt
                    stream.seek(0); msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise ValueError('Project registry is busy; retry after the other writer finishes')
                time.sleep(0.05)
        try:
            yield
        finally:
            if os.name == 'nt':
                import msvcrt
                stream.seek(0); msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _save(data):
    path = registry_path()
    if path.is_symlink():
        raise ValueError('Project registry must not be a symlink')
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    if path.is_file() and path.read_text(encoding='utf-8') == text:
        return
    fd, name = tempfile.mkstemp(prefix='.projects-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(text); stream.flush(); os.fsync(stream.fileno())
        os.chmod(name, 0o600)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _select(data, query):
    names = [n for n, e in data['projects'].items()
             if n.casefold() == query.casefold() or _path_key(e['path']) == _path_key(query)]
    if len(names) != 1:
        raise ValueError('Unknown or ambiguous project: ' + query)
    return names[0]


def register(target, source, name=None):
    target, source = Path(target).expanduser().resolve(), Path(source).expanduser().resolve()
    if not target.is_dir():
        raise ValueError('Project directory is missing: ' + str(target))
    if not (source / 'manifests').is_dir() or not (source / 'skills').is_dir():
        raise ValueError('Source repository needs manifests/ and skills/: ' + str(source))
    # Validate existing records, but registration does not infer or install any.
    load_installations(target)
    if name is not None:
        _name(name)
    with _lock(registry_path()):
        data = load_registry()
        old = next((n for n, e in data['projects'].items() if _path_key(e['path']) == _path_key(target)), None)
        candidate = name or old or target.name or 'project'
        _name(candidate)
        collision = next((n for n in data['projects'] if n.casefold() == candidate.casefold() and n != old), None)
        if collision:
            if name:
                raise ValueError('Project name already belongs to another path: ' + name)
            candidate += '-' + hashlib.sha256(str(target).encode()).hexdigest()[:8]
            if candidate in data['projects']:
                raise ValueError('Automatic project name collision: ' + candidate)
        if old and old != candidate:
            del data['projects'][old]
        data['projects'][candidate] = {'path': str(target), 'source': str(source)}
        _save(data)
    return candidate


def auto_register(target, source):
    """Only real completed installs call this, never staging or dry runs."""
    try:
        name = register(target, source)
        print('Project registered: ' + name)
        return name
    except (OSError, ValueError) as exc:
        print('Warning: project files are installed; index registration needs attention: ' + str(exc), file=sys.stderr)
        return None


def resolve(query):
    data = load_registry(); name = _select(data, str(query))
    return name, data['projects'][name]


def remove(query):
    with _lock(registry_path()):
        data = load_registry(); name = _select(data, query)
        del data['projects'][name]; _save(data)
    return name


def rename(query, name):
    _name(name)
    with _lock(registry_path()):
        data = load_registry(); old = _select(data, query)
        if any(n.casefold() == name.casefold() and n != old for n in data['projects']):
            raise ValueError('Project name already exists: ' + name)
        entry = data['projects'].pop(old); data['projects'][name] = entry; _save(data)
    return name


def relocate(query, target):
    target = Path(target).expanduser().resolve()
    if not target.is_dir():
        raise ValueError('New project path is missing: ' + str(target))
    load_installations(target)
    with _lock(registry_path()):
        data = load_registry(); name = _select(data, query)
        if any(_path_key(e['path']) == _path_key(target) and n != name for n, e in data['projects'].items()):
            raise ValueError('New path is already registered')
        data['projects'][name]['path'] = str(target); _save(data)
    return name


def describe(name, entry):
    result = dict(name=name, **entry, status='ready', manifests=[], skills=[], mode='legacy', errors=[])
    target = Path(entry['path'])
    if not target.is_dir():
        result['status'] = 'missing'
        return result
    try:
        records = load_installations(target)
        result['manifests'] = list(records['manifests'])
        result['skills'] = list(records['skills'])
        result['installations'] = records
        if (target / '.vibe-setup.json').exists():
            from .setup import read_state
            state = read_state(target)
            result['mode'] = 'setup'
            result['setup'] = state['manifests']
        if not result['manifests'] and not result['skills']:
            result['status'] = 'unmanaged'
    except (OSError, ValueError) as exc:
        result['status'] = 'invalid'; result['errors'].append(str(exc))
    if not Path(entry['source']).is_dir():
        result['errors'].append('Source repository is missing')
        if result['status'] == 'ready':
            result['status'] = 'source_missing'
    return result


def list_projects():
    return [describe(n, e) for n, e in sorted(load_registry()['projects'].items())]


def configure(subparsers):
    parser = subparsers.add_parser('project', aliases=['projects'], help='Track projects and update their installed resources')
    children = parser.add_subparsers(dest='project_action')
    parser.set_defaults(func=lambda args: parser.print_help() or 0)
    for action in ('list', 'show'):
        child = children.add_parser(action, help='Read the project index and local installation records')
        if action == 'show':
            child.add_argument('project', help='Project name or registered path')
        child.add_argument('--json', dest='json_out', action='store_true')
        child.set_defaults(func=dispatch)
    child = children.add_parser('add', help='Register an existing project without installing resources')
    child.add_argument('path', type=Path)
    child.add_argument('--name')
    child.add_argument('--source', type=Path, help='Source vibe repository; defaults to current/configured repository')
    child.set_defaults(func=dispatch)
    for action in ('remove', 'rename', 'relocate'):
        child = children.add_parser(action, help='Change the index only; project files are untouched')
        child.add_argument('project')
        if action == 'rename':
            child.add_argument('new_name')
        if action == 'relocate':
            child.add_argument('path', type=Path)
        child.set_defaults(func=dispatch)
    child = children.add_parser('update', help='Update selected/all installed resources with one backup per project')
    child.add_argument('project', nargs='?')
    child.add_argument('--all', dest='all_projects', action='store_true', help='Visit every registered project')
    child.add_argument('--manifest', action='append', default=None, help='Update this installed manifest and installed dependencies; repeatable')
    child.add_argument('--skill', action='append', default=None, help='Update this installed skill; repeatable')
    child.add_argument('-n', '--dry-run', action='store_true')
    child.set_defaults(func=dispatch)


def dispatch(args):
    action = args.project_action
    if action == 'list':
        rows = list_projects()
        if args.json_out:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        elif not rows:
            print('No registered projects. Install with setup/init/add, or use vibe project add PATH.')
        else:
            print(f"{'PROJECT':<24} {'STATUS':<16} {'MANIFESTS':<24} {'SKILLS':<7} PATH")
            for row in rows:
                print(f"{row['name']:<24} {row['status']:<16} {','.join(row['manifests']) or '-':<24} {len(row['skills']):<7} {row['path']}")
        return 0
    if action == 'show':
        name, entry = resolve(args.project); row = describe(name, entry)
        if args.json_out:
            print(json.dumps(row, ensure_ascii=False, indent=2))
        else:
            print(f"Project: {name}\nPath: {row['path']}\nSource: {row['source']}\nStatus: {row['status']}\nMode: {row['mode']}")
            print('Manifests: ' + (', '.join(row['manifests']) or '-'))
            print('Skills: ' + (', '.join(row['skills']) or '-'))
            for error in row['errors']:
                print('Attention: ' + error)
        return 0
    if action == 'add':
        source = args.source
        if source is None:
            try:
                _, entry = resolve(str(args.path.resolve())); source = Path(entry['source'])
            except ValueError:
                from .config import find_repo_root
                source = find_repo_root()
        name = register(args.path, source, args.name)
        print('Project registered: ' + name)
        return 0
    if action == 'remove':
        print('Removed registration only: ' + remove(args.project)); return 0
    if action == 'rename':
        print('Project renamed: ' + rename(args.project, args.new_name)); return 0
    if action == 'relocate':
        print('Project path rebound: ' + relocate(args.project, args.path)); return 0
    if action == 'update':
        if bool(args.project) == bool(args.all_projects):
            raise ValueError('Select one project name/path OR --all')
        entries = list(load_registry()['projects'].items()) if args.all_projects else [resolve(args.project)]
        if not entries:
            print('No registered projects to update.'); return 0
        from .project_sync import update_project
        failed = []
        for name, entry in entries:
            print(f"\nProject: {name} ({entry['path']})")
            try:
                rc = update_project(Path(entry['source']), Path(entry['path']), manifests=args.manifest, skills=args.skill, dry_run=args.dry_run)
            except (OSError, ValueError, RuntimeError) as exc:
                print('Project update failed: ' + str(exc), file=sys.stderr); rc = 1
            print(f"Result: {name} = {'failed' if rc else 'previewed' if args.dry_run else 'updated/no-op'}")
            if rc:
                failed.append(name)
        print(f"\n{len(entries)} project(s), {len(failed)} failed" + (': ' + ', '.join(failed) if failed else ''))
        return int(bool(failed))
    raise ValueError('Unknown project action: ' + action)
