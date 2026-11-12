"""Transactional, shell-free project setup with harness-independent Markdown rules."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from .discovery import discover_manifests, resolve_manifest, resolve_skill
from .installations import load_installations, record_manifest, write_installations
from .harness_rules import PROJECT_INDEX, hosts, merge_project_index
from .manifest import _install_required_skills
from .portable import render
from .rollback import checked_path
from .skill import add_skill
from .transaction import Change, apply_update, ensure_separate

STATE = '.vibe-setup.json'
AGENTS = ('generic', 'codex', 'claude', 'both')
PROTECTED_NAMES = {'README.md', 'MANIFEST.md', 'VERSION', 'CHANGELOG.md', '.gitignore', '.editorconfig', 'CONTRIBUTING.md'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_state(target):
    path = checked_path(target, STATE)
    if not path.exists():
        return {'schema_version': 1, 'manifests': {}, 'files': {}}
    if path.is_symlink():
        raise ValueError('Setup record is a symlink')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('files'), dict) or not isinstance(data.get('manifests'), dict):
        raise ValueError('Invalid setup record')
    for name, entry in data['manifests'].items():
        if (not isinstance(name, str) or not name or not isinstance(entry, dict)
                or entry.get('agent') not in AGENTS or not isinstance(entry.get('options'), dict)
                or any(not isinstance(k, str) or not isinstance(v, str) for k, v in entry['options'].items())
                or not isinstance(entry.get('skills'), list) or any(not isinstance(v, str) for v in entry['skills'])
                or not isinstance(entry.get('source'), str)):
            raise ValueError('Invalid setup manifest record: ' + str(name))
    for name, record in data['files'].items():
        checked_path(target, name)
        if not isinstance(record, dict) or not isinstance(record.get('sha256'), str) or len(record['sha256']) != 64 or not isinstance(record.get('owner'), str):
            raise ValueError('Invalid setup file record: ' + name)
    return data


def check(target):
    """Read-only file/hash check; host skill activation is verified in the host."""
    if not (target / STATE).is_file():
        raise ValueError('No setup record: ' + str(target / STATE))
    state = read_state(target)
    errors = []
    for name, record in state['files'].items():
        path = checked_path(target, name)
        if path.is_symlink() or not path.is_file() or digest(path) != record['sha256']:
            errors.append(name)
    if errors:
        raise ValueError('Changed or missing setup resources: ' + ', '.join(errors))
    print(f"Verified {len(state['files'])} files for {', '.join(state['manifests'])}; host activation not simulated.")
    return 0


def _write(stage, relative, content):
    path = stage / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return path


def _import_block(name, relative, agent):
    return (f'<!-- vibe:setup:{name}:begin -->\n'
            f'## {name}: project workflow\n\n'
            f'Read [{relative}]({relative}) and [portable rule scope](rules/{name}/INDEX.md) before related work. Paths in that contract are project-root-relative.\n'
            f'Preserve existing project goals and constraints; resolve substantive conflicts before execution.\n'
            f'Skills: {".agents/skills" if agent == "codex" else ".claude/skills"}/.\n'
            f'<!-- vibe:setup:{name}:end -->\n')


def _merge_import(existing, name, block):
    start, end = f'<!-- vibe:setup:{name}:begin -->', f'<!-- vibe:setup:{name}:end -->'
    if existing.count(start) != existing.count(end) or existing.count(start) > 1:
        raise ValueError('Malformed setup import block for ' + name)
    if start in existing:
        a, b = existing.index(start), existing.index(end) + len(end)
        if b < a:
            raise ValueError('Reversed setup import block')
        return existing[:a] + block.rstrip('\n') + existing[b:]
    return existing + ('\n' if existing.endswith('\n') else '\n\n') + block


def setup(source_root, name, target, *, agent='both', dry_run=False, skills=(), **options):
    repo, target = source_root.resolve(), target.expanduser().resolve()
    ensure_separate(repo, target)
    if target.exists() and not target.is_dir():
        raise ValueError('Target is not a directory: ' + str(target))
    manifest = resolve_manifest(repo / 'manifests', name)
    name = manifest.name
    if agent not in AGENTS:
        raise ValueError('Unknown agent: ' + agent)
    selected = list(filter(None, options.get('scenario', '').split(',')))
    if len(selected) != len(set(selected)) or any(s not in manifest.scenarios for s in selected):
        raise ValueError('Unknown or repeated scenario; available: ' + ', '.join(manifest.scenarios))
    if name != 'vibe-coding' and len(selected) > 1:
        raise ValueError('This manifest accepts one scenario')
    # Resolve every dependency before rendering or creating the target. No
    # partial installation or implicit network fetch when a source is missing.
    roots = (repo / 'skills', repo / 'mine', manifest.path / 'skills')
    dependencies = {}
    for dependency in dict.fromkeys([*manifest.required_skills, *skills]):
        resolved = resolve_skill(roots, dependency)
        dependencies[resolved.name] = resolved
    state = read_state(target)
    existing_installations = load_installations(target)
    with tempfile.TemporaryDirectory(prefix='vibe-setup-') as directory:
        stage = Path(directory) / 'rendered'
        render(manifest, stage, target, options)
        # Native initializers may create their own temporary install backups.
        # The outer setup transaction provides the real project rollback.
        for p in sorted(stage.rglob('*')):
            if p.is_dir() and p.name in {'backups', '__pycache__'}:
                shutil.rmtree(p)
        write_installations(stage, existing_installations)
        if _install_required_skills(repo / 'manifests', manifest, stage, False, False):
            raise ValueError('Required skill installation failed in staging')
        for extra in skills:
            if add_skill(roots, extra, stage) not in (0, 2):
                raise ValueError('Additional skill installation failed: ' + extra)
        record_manifest(repo, stage, name, manifest.path, options, force=True)
        # Keep a full support-file bundle in each host's documented directory.
        # Copies avoid symlink privilege requirements on Windows.
        if agent in ('claude', 'both'):
            for canonical in dependencies:
                source = stage / '.agents/skills' / canonical
                dest = stage / '.claude/skills' / canonical
                if dest.exists():
                    raise ValueError('Rendered skill name collision: ' + canonical)
                shutil.copytree(source, dest)
        # .agents remains canonical for provenance/update even in Claude-only
        # setup; --agent selects the instruction imports and Claude mirror.
        entry_texts = {name: (stage / name).read_text(encoding='utf-8')
                       for name in ('AGENTS.md', 'CLAUDE.md') if (stage / name).is_file()}
        for host, root_name in (('codex', 'AGENTS.md'), ('claude', 'CLAUDE.md')):
            if host not in hosts(agent):
                (stage / root_name).unlink(missing_ok=True)
                continue
            text = entry_texts.get(root_name) or next(iter(entry_texts.values()),
                f'Read [business contract](rules/{name}/CONTRACT.md) and [rule scope](rules/{name}/INDEX.md).\n')
            alternate = f'{root_name[:-3]}.vibe-{name}.md'
            _write(stage, alternate, text)
            old = checked_path(target, root_name)
            if old.is_symlink():
                raise ValueError('Resolve existing instruction symlink before setup: ' + root_name)
            existing = old.read_text(encoding='utf-8') if old.is_file() else '# Project instructions\n'
            _write(stage, root_name, _merge_import(existing, name, _import_block(name, alternate, host)))
        merge_project_index(target, stage, name)
        # Retire old editor-specific tracking without deleting user files.
        for old_path in [p for p, record in state['files'].items()
                         if (p.startswith('.cursor/') or p == '.cursorrules') and record['owner'] == name]:
            del state['files'][old_path]
        # A Vibe Coding MANIFEST is executable guidance, not an output ledger.
        # Preserve a user's root ledger and point the imported contract at its
        # own version when those roles collide.
        root_manifest = stage / 'MANIFEST.md'
        old_manifest = target / 'MANIFEST.md'
        if name == 'vibe-coding' and old_manifest.is_file() and root_manifest.is_file() and old_manifest.read_bytes() != root_manifest.read_bytes() and state['files'].get('MANIFEST.md', {}).get('owner') != name:
            alternate = f'MANIFEST.vibe-{name}.md'
            shutil.copy2(root_manifest, stage / alternate)
            root_manifest.unlink()
            for host in ('AGENTS', 'CLAUDE'):
                p = stage / f'{host}.vibe-{name}.md'
                if p.is_file():
                    p.write_text(p.read_text(encoding='utf-8').replace('MANIFEST.md', alternate), encoding='utf-8')
        # Fresh native ledgers must not claim preserved or imported root files.
        for relative in ('.unity-game/install.json', '.game-design/install.json'):
            p = stage / relative
            if p.is_file():
                data = json.loads(p.read_text(encoding='utf-8'))
                for key in ('AGENTS.md', 'CLAUDE.md', 'MANIFEST.md', 'README.md'):
                    data.get('files', {}).pop(key, None)
                p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        entry = dict(agent=agent, options=options, skills=list(dependencies), source=f'manifests/{name}')
        state['manifests'][name] = entry
        changes, conflicts = [], []
        for source in sorted(stage.rglob('*')):
            if not source.is_file():
                continue
            relative = source.relative_to(stage).as_posix()
            if relative.startswith('.vibe-tool/') and relative != '.vibe-tool/installations.json':
                continue
            dest = checked_path(target, relative)
            previous = state['files'].get(relative)
            # Preserve business state, existing README/ledgers/release metadata.
            protected = (not relative.startswith('rules/' + name + '/')) and (relative in PROTECTED_NAMES or '/state/' in relative or relative == 'notes/_index.md')
            if dest.is_symlink():
                conflicts.append(relative); continue
            if dest.exists() and not dest.is_file():
                conflicts.append(relative); continue
            if dest.is_file() and dest.read_bytes() != source.read_bytes():
                if protected:
                    print('  KEEP  ' + relative)
                    continue
                if relative not in ('AGENTS.md', 'CLAUDE.md', 'PROJECT_RULES.md', '.vibe-tool/installations.json'):
                    if not previous or previous['owner'] != name or digest(dest) != previous['sha256']:
                        conflicts.append(relative); continue
            state['files'][relative] = {'sha256': digest(source), 'owner': 'shared' if relative in ('AGENTS.md', 'CLAUDE.md', 'PROJECT_RULES.md', '.vibe-tool/installations.json') else name}
            changes.append(Change(Path(relative), source))
        if conflicts:
            raise ValueError('Preserved local conflicts; no project writes: ' + ', '.join(conflicts))
        record = _write(stage, STATE, json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
        changes.append(Change(Path(STATE), record))
        if dry_run:
            if target.is_dir():
                return apply_update(target, changes, label='setup ' + name, dry_run=True)
            print(f'[dry-run] Setup {name} for {agent} in {target}: {len(changes)} planned files; no project writes.')
            return 0
        target.mkdir(parents=True, exist_ok=True)
        rc = apply_update(target, changes, label='setup ' + name)
        if rc == 0:
            check(target)
            print(f'Project context ready: {target}. Continue the actual task in your AI tool; application/runtime work has not been run.')
            from .projects import auto_register
            auto_register(target, repo)
        return rc


def configure(parser):
    parser.add_argument('manifest', nargs='?', help='Manifest selected by the AI (not a natural-language classifier)')
    parser.add_argument('target', nargs='?', default='.', type=Path)
    parser.add_argument('--harness', '--agent', dest='agent', choices=AGENTS, default='both', help='generic publishes ordinary Markdown; named modes add host entrypoints')
    parser.add_argument('--scenario', default='')
    parser.add_argument('--provider', choices=('git', 'github', 'gitlab', 'gitee'), default='git')
    for option in ('owner', 'org', 'repo', 'email'):
        parser.add_argument('--' + option, default='')
    parser.add_argument('--skill', action='append', default=[], help='Additional skill; repeat as needed')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('--check', action='store_true', help='Read-only installed-file/hash check')
    parser.add_argument('--list', action='store_true', help='Print manifest catalog JSON for AI selection')


def dispatch(args, repo):
    if args.list:
        print(json.dumps([asdict(m) for m in discover_manifests(repo / 'manifests')], default=str, ensure_ascii=False, indent=2))
        return 0
    if args.check:
        return check(args.target.expanduser().resolve())
    if not args.manifest:
        raise ValueError('Select a manifest from --list; follow BOOTSTRAP.md for AI-guided selection or creation')
    options = {key: getattr(args, key) for key in ('scenario', 'provider', 'owner', 'org', 'repo', 'email')}
    return setup(repo, args.manifest, args.target, agent=args.agent, dry_run=args.dry_run, skills=args.skill, **options)


def main(argv=None, repo=None):
    parser = argparse.ArgumentParser(description=__doc__)
    configure(parser)
    args = parser.parse_args(argv)
    if repo is None:
        from .config import find_repo_root
        repo = find_repo_root()
    try:
        return dispatch(args, repo)
    except (OSError, ValueError, RuntimeError) as exc:
        print('Setup failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
