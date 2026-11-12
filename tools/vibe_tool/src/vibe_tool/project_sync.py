"""Plan every selected project resource, then apply one backed-up transaction."""
from __future__ import annotations

import copy
from pathlib import Path
import shutil
import tempfile

from .discovery import resolve_manifest, resolve_skill
from .installations import load_installations, source_ref
from .manifest_update import _is_resource, render_manifest
from .portable import LEGACY, NATIVE, render as render_portable
from .project_update import _options, _recorded_skill, _stage_records, _stage_skill
from .rollback import checked_path
from .setup import STATE, digest, read_state, _merge_import, _import_block
from .harness_rules import PROJECT_INDEX, hosts, merge_project_index, project_index
from .skill import _is_excluded
from .transaction import Change, apply_update, ensure_separate


def _installed_skill(root, name, records):
    info = _recorded_skill(root, name, records)
    if info is None:
        candidate = resolve_skill((root / 'skills', root / 'mine'), name)
        info = _recorded_skill(root, candidate.name, records)
    if info is None:
        raise ValueError('Skill has no installation record: ' + name)
    return info


def _setup_resource(name, relative, state):
    if (Path('rules') / name) in relative.parents:
        return True  # Generated static support, not live project state.
    text = relative.as_posix()
    if any(p in {'.git', '.vibe-tool', '.auto-research', '__pycache__', 'backups', 'state'} for p in relative.parts):
        return False
    if relative.name in {'README.md', 'CONTRIBUTING.md', 'VERSION', 'CHANGELOG.md', 'install.json', '.gitkeep'}:
        return False
    if text.startswith('outline/') or text == 'notes/_index.md':
        return False
    if text == 'MANIFEST.md' and name != 'vibe-coding':
        return False
    return True


def _stage_setup_manifest(manifest, target, stage, state, options):
    entry = state['manifests'][manifest.name]
    render_portable(manifest, stage, target, options)
    entry_texts = {filename: (stage / filename).read_text(encoding='utf-8')
                   for filename in ('AGENTS.md', 'CLAUDE.md') if (stage / filename).is_file()}
    for host, filename in (('codex', 'AGENTS.md'), ('claude', 'CLAUDE.md')):
        if host in hosts(entry['agent']) and filename not in entry_texts:
            text = next(iter(entry_texts.values()),
                f'Read [business contract](rules/{manifest.name}/CONTRACT.md) and [rule scope](rules/{manifest.name}/INDEX.md).\n')
            (stage / filename).write_text(text, encoding='utf-8')
    merge_project_index(target, stage, manifest.name)
    changes = []
    for old_path in [p for p, record in state['files'].items()
                     if (p.startswith('.cursor/') or p == '.cursorrules') and record['owner'] == manifest.name]:
        del state['files'][old_path]
    for file in sorted(stage.rglob('*')):
        if not file.is_file():
            continue
        relative = file.relative_to(stage)
        if not _setup_resource(manifest.name, relative, state):
            continue
        if relative.as_posix() in ('AGENTS.md', 'CLAUDE.md'):
            host = 'codex' if relative.name == 'AGENTS.md' else 'claude'
            if host not in hosts(entry['agent']):
                continue
            # Root files are user-owned import surfaces. Refresh only the
            # sidecar contract and managed import, leaving user content intact.
            root_file = checked_path(target, relative)
            marker = '<!-- vibe:setup:' + manifest.name + ':begin -->'
            if root_file.is_symlink() or not root_file.is_file() or marker not in root_file.read_text(encoding='utf-8'):
                raise ValueError('Setup import is missing: ' + relative.as_posix())
            root_stage = stage / 'root-imports' / relative
            root_stage.parent.mkdir(parents=True, exist_ok=True)
            sidecar = f'{relative.stem}.vibe-{manifest.name}.md'
            root_stage.write_text(_merge_import(root_file.read_text(encoding='utf-8'), manifest.name,
                                               _import_block(manifest.name, sidecar, host)), encoding='utf-8')
            changes.append(Change(relative, root_stage))
            relative = Path(sidecar)
            # An existing project ledger may have a separate Vibe contract.
            alternate = f'MANIFEST.vibe-{manifest.name}.md'
            if alternate in state['files']:
                file.write_text(file.read_text(encoding='utf-8').replace('MANIFEST.md', alternate), encoding='utf-8')
        elif relative.as_posix() == 'MANIFEST.md':
            alternate = f'MANIFEST.vibe-{manifest.name}.md'
            if alternate in state['files']:
                relative = Path(alternate)
        changes.append(Change(relative, file))
    return changes


def _validate_setup_change(target, change, state, *, merged_roots=False):
    """Do not discard user edits or extra files in a full skill replacement."""
    relative = change.path.as_posix()
    dest = checked_path(target, change.path)
    if relative in ('.vibe-tool/installations.json', 'PROJECT_RULES.md') or (merged_roots and relative in ('AGENTS.md', 'CLAUDE.md')):
        return
    if change.source.is_dir():
        expected = {p: r for p, r in state['files'].items() if p.startswith(relative + '/')}
        actual = set()
        for file in dest.rglob('*'):
            if file.is_symlink():
                raise ValueError('Local skill symlink needs review: ' + str(file))
            if file.is_file():
                name = file.relative_to(target).as_posix(); actual.add(name)
                if name not in expected or digest(file) != expected[name]['sha256']:
                    raise ValueError('Local skill edit needs review: ' + name)
        if actual != set(expected):
            raise ValueError('Local skill files are missing; review before refresh: ' + relative)
    elif dest.exists() or dest.is_symlink():
        if dest.is_symlink() or not dest.is_file():
            raise ValueError('Local path type needs review: ' + relative)
        previous = state['files'].get(relative)
        if (not previous or digest(dest) != previous['sha256']) and dest.read_bytes() != change.source.read_bytes():
            raise ValueError('Local edit needs review: ' + relative)


def _record_setup_change(change, state, owner):
    relative = change.path.as_posix()
    previous = state['files'].get(relative)
    if change.source.is_dir():
        previous_owner = next((r['owner'] for p, r in state['files'].items() if p.startswith(relative + '/')), owner)
        for p in [p for p in state['files'] if p.startswith(relative + '/')]:
            del state['files'][p]
        for file in sorted(change.source.rglob('*')):
            if file.is_file():
                name = (change.path / file.relative_to(change.source)).as_posix()
                state['files'][name] = {'owner': previous_owner, 'sha256': digest(file)}
    else:
        state['files'][relative] = {'owner': previous['owner'] if previous else owner, 'sha256': digest(change.source)}


def update_project(root, target, *, manifests=None, skills=None, dry_run=False):
    """Update local installed resources; no implicit source fetch or new skills."""
    root, target = Path(root).resolve(), Path(target).resolve()
    if not target.is_dir():
        raise ValueError('Project directory is missing: ' + str(target))
    if not (root / 'manifests').is_dir() or not (root / 'skills').is_dir():
        raise ValueError('Project source repository is missing: ' + str(root))
    ensure_separate(root, target)
    records = load_installations(target)
    if not records['manifests'] and not records['skills']:
        raise ValueError('Project has no installation records; run setup/init/add first')
    updated = copy.deepcopy(records)
    state = read_state(target) if (target / STATE).exists() else None
    original_state = copy.deepcopy(state)
    all_resources = manifests is None and skills is None
    selected_manifests = list(records['manifests']) if all_resources else list(manifests or ())
    selected_skills = list(records['skills']) if all_resources else list(skills or ())
    for name in selected_manifests:
        if name not in records['manifests']:
            raise ValueError('Manifest is not installed: ' + name)
    with tempfile.TemporaryDirectory(prefix='vibe-project-update-') as directory:
        stage = Path(directory).resolve()
        changes, owners = {}, {}
        def add(change, owner):
            key = change.path.as_posix()
            if state and owner in state['manifests'] and key in ('AGENTS.md', 'CLAUDE.md'):
                old = changes[key].source.read_text(encoding='utf-8') if key in changes else (target / key).read_text(encoding='utf-8')
                host = 'codex' if key == 'AGENTS.md' else 'claude'
                sidecar = f'{Path(key).stem}.vibe-{owner}.md'
                change.source.write_text(_merge_import(old, owner, _import_block(owner, sidecar, host)), encoding='utf-8')
                changes[key] = change; owners[key] = 'shared'; return
            if key == PROJECT_INDEX.as_posix():
                old = changes[key].source.read_text(encoding='utf-8') if key in changes else (
                    (target / PROJECT_INDEX).read_text(encoding='utf-8') if (target / PROJECT_INDEX).is_file() else '')
                change.source.write_text(project_index(old, owner), encoding='utf-8')
                changes[key] = change; owners[key] = 'shared'; return
            if key in changes:
                a, b = changes[key].source, change.source
                if a.is_file() and b.is_file() and a.read_bytes() == b.read_bytes():
                    return
                raise ValueError('Selected manifests produce conflicting resources: ' + key)
            changes[key] = change; owners[key] = owner
        skill_infos = {}
        for index, name in enumerate(selected_manifests):
            manifest = resolve_manifest(root / 'manifests', name)
            stored = records['manifests'][name]
            if stored['source'] != source_ref(root, manifest.path):
                raise ValueError('Recorded manifest source changed: ' + name)
            configured = state and name in state['manifests']
            effective = (dict(state['manifests'][name]['options']) if configured else _options(manifest, stored, {}))
            rendered = stage / f'manifest-{index}'
            if configured:
                proposed = _stage_setup_manifest(manifest, target, rendered, state, effective)
            else:
                native = NATIVE.get(manifest.name)
                portable = not manifest.has_init_script or manifest.name in LEGACY or (native and (manifest.path / native).is_file())
                if portable:
                    render_portable(manifest, rendered, target, effective)
                    merge_project_index(target, rendered, manifest.name)
                    paths = [p.relative_to(rendered) for p in sorted(rendered.rglob('*'))
                             if p.is_file() and _is_resource(manifest.name, p.relative_to(rendered), effective)]
                else:
                    render_manifest(manifest, rendered, target, effective)
                    from .harness_rules import compile_bundle
                    compile_bundle(manifest, rendered, effective)
                    merge_project_index(target, rendered, manifest.name)
                    paths = [p.relative_to(rendered) for p in sorted(rendered.rglob('*'))
                             if p.is_file() and _is_resource(manifest.name, p.relative_to(rendered), effective)]
                proposed = [Change(p, rendered / p) for p in paths]
            for change in proposed:
                add(change, name)
            # Only dependencies already installed in the project may refresh.
            roots = (root / 'skills', root / 'mine', manifest.path / 'skills')
            for dependency in manifest.required_skills:
                info = _recorded_skill(root, dependency, records)
                if info is None:
                    try:
                        candidate = resolve_skill(roots, dependency)
                        info = _recorded_skill(root, candidate.name, records)
                    except ValueError:
                        info = None
                if info and (target / '.agents/skills' / info.name / 'SKILL.md').is_file():
                    skill_infos[info.name] = info
                else:
                    print('  SKIP  ' + dependency + ' (required skill not installed; use setup/add to install)')
        for name in selected_skills:
            info = _installed_skill(root, name, records)
            if not (target / '.agents/skills' / info.name / 'SKILL.md').is_file():
                if not all_resources:
                    raise ValueError('Skill files are missing: ' + info.name)
                print('  SKIP  ' + info.name + ' (installed files are missing)')
                continue
            skill_infos[info.name] = info
        for index, info in enumerate(skill_infos.values()):
            change = _stage_skill(root, info, target, stage / f'skill-{index}', updated)
            if state:
                # Materialize support links just like the portable setup path.
                shutil.rmtree(change.source)
                shutil.copytree(info.source_path, change.source, symlinks=False,
                                ignore=lambda d, ns: [n for n in ns if _is_excluded(Path(d) / n)])
            add(change, 'skills')
            mirrored = target / '.claude/skills' / info.name
            mirror_prefix = '.claude/skills/' + info.name + '/'
            if state and any(p.startswith(mirror_prefix) for p in state['files']):
                add(Change(Path('.claude/skills') / info.name, change.source), 'skills')
        for change in _stage_records(target, stage / 'records', records, updated):
            add(change, 'shared')
        if state:
            # Validate every change before applying even the first resource.
            for key, change in changes.items():
                _validate_setup_change(target, change, original_state, merged_roots=owners[key] == 'shared')
                _record_setup_change(change, state, owners[key])
            if state != original_state:
                payload = stage / STATE
                import json
                payload.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
                add(Change(Path(STATE), payload), 'shared')
        return apply_update(target, list(changes.values()), label='project resources', dry_run=dry_run)


def add_setup_skills(root, target, names, *, force=False, dry_run=False, skip_is_success=False):
    """Add skills to a setup project without leaving its Claude/hash view stale."""
    from .installations import write_installations
    from .skill import add_skill
    import json
    root, target = Path(root).resolve(), Path(target).resolve()
    ensure_separate(root, target)
    original = load_installations(target)
    state = read_state(target)
    mirror = any(e['agent'] in ('claude', 'both') for e in state['manifests'].values())
    changes, skipped = [], 0
    with tempfile.TemporaryDirectory(prefix='vibe-project-add-') as directory:
        stage = Path(directory)
        write_installations(stage, original)
        seen = set()
        for name in names:
            info = resolve_skill((root / 'skills', root / 'mine'), name)
            if info.name in seen:
                continue
            seen.add(info.name)
            relative = Path('.agents/skills') / info.name
            if (target / relative).exists() and not force:
                print('  SKIP  ' + info.name + ' (exists, use --force to overwrite)')
                skipped += 1; continue
            if add_skill((root / 'skills', root / 'mine'), info.name, stage):
                raise ValueError('Skill staging failed: ' + info.name)
            source = stage / relative
            changes.append(Change(relative, source))
            if mirror:
                changes.append(Change(Path('.claude/skills') / info.name, source))
        if not changes:
            return 0 if skip_is_success else 2 if skipped else 0
        for change in changes:
            if not force:
                _validate_setup_change(target, change, state)
            _record_setup_change(change, state, 'skills')
        updated = load_installations(stage)
        changes.extend(_stage_records(target, stage / 'metadata', original, updated))
        for change in changes:
            if change.path.as_posix() == '.vibe-tool/installations.json':
                _record_setup_change(change, state, 'shared')
        payload = stage / 'setup-state.json'
        payload.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        changes.append(Change(Path(STATE), payload))
        return apply_update(target, changes, label='add setup skills', dry_run=dry_run)
