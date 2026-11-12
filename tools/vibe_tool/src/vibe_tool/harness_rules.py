"""Compile manifest rules into ordinary Markdown, independent of an editor client.

Legacy MDC is a source format, not a runtime dependency. Scope expressions are
preserved as data; no generic host is claimed to evaluate Cursor frontmatter.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
from urllib.parse import urlsplit

PROJECT_INDEX = Path('PROJECT_RULES.md')
FRONTMATTER = re.compile(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', re.S)


def bundle_root(name):
    return Path('rules') / name


def hosts(agent):
    if agent == 'generic':
        return ('codex',)  # AGENTS.md is the ordinary Markdown import surface.
    return ('codex', 'claude') if agent == 'both' else (agent,)


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.vibe-tmp')
    temp.write_text(text, encoding='utf-8'); os.replace(temp, path)


def _scope(text):
    match = FRONTMATTER.match(text)
    raw = match[1] if match else ''
    fields = {}
    key = None
    for line in raw.splitlines():
        field = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if field:
            key = field[1]; fields[key] = field[2]
        elif key:
            fields[key] += '\n' + line
    value = fields.get('always', fields.get('alwaysApply', '')).strip().lower()
    always = True if value == 'true' else False if value == 'false' else None
    return {'always': always, 'paths_expression': fields.get('paths', fields.get('globs', '')),
            'when': fields.get('when', fields.get('description', '')),
            'frontmatter_raw': raw}, text[match.end():] if match else text


def _merge(existing, name, content):
    begin, end = f'<!-- vibe:rules:{name}:begin -->', f'<!-- vibe:rules:{name}:end -->'
    if existing.count(begin) != existing.count(end) or existing.count(begin) > 1:
        raise ValueError('Malformed portable rule import: ' + name)
    block = begin + '\n' + content.rstrip() + '\n' + end
    if begin in existing:
        a, b = existing.index(begin), existing.index(end)
        if b < a:
            raise ValueError('Reversed portable rule import: ' + name)
        return existing[:a] + block + existing[b + len(end):]
    return existing + ('\n' if existing.endswith('\n') else '\n\n') + block + '\n'


def project_index(existing, name):
    if not existing:
        existing = ('# Project rules — harness independent\n\n'
                    'Read the linked manifest contracts and applicable rules before related work. '
                    'Keep existing project goals/constraints. These are ordinary Markdown files, '
                    'not editor plugins or proof that host tools are available.\n')
    return _merge(existing, name, f'## {name}\n\n'
                  f'- Contract: [{name}](rules/{name}/CONTRACT.md)\n'
                  f'- Rules and applicability: [INDEX](rules/{name}/INDEX.md)\n'
                  'Read always-applicable rules first; select conditional rules by the preserved '
                  'project-root-relative paths/task conditions. Never silently promote a conditional rule to global. '
                  'Resolve unknown scope before relying on it. Use real host capabilities; '
                  'do not invent slash commands, agents, tools, approvals, or weaken required gates.')


def _rebase(text, destination, origin, existing, mappings, prefix):
    def mapped(path):
        path = posixpath.normpath(path)
        if path in mappings:
            if not destination.startswith(prefix + '/') and not path.startswith('.cursor/') and path in existing:
                return path
            return mappings[path]
        if path.startswith('.cursor/'):
            return prefix + '/' + path[len('.cursor/'):]
        return path
    def link(match):
        value = match[1]
        # Leave external URLs, anchors, and Markdown links with titles alone.
        if not value or value.startswith('#') or re.search(r'\s+[\"\']', value):
            return match[0]
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or parts.path.startswith('/'):
            return match[0]
        rooted = posixpath.normpath(posixpath.join(posixpath.dirname(origin), parts.path))
        if rooted not in mappings and rooted not in existing and parts.path in existing:
            rooted = parts.path
        if rooted.startswith('.cursor/') and mapped(rooted) not in existing and rooted[len('.cursor/'):] in existing:
            rooted = rooted[len('.cursor/'):]
        if rooted not in mappings and rooted not in existing:
            legacy = posixpath.normpath(posixpath.join('.cursor/rules', parts.path))
            if legacy in mappings or legacy in existing:
                rooted = legacy
            elif 'office/' + rooted in existing:
                rooted = 'office/' + rooted
        if rooted not in mappings and rooted not in existing and not rooted.startswith('.cursor/'):
            return match[0]
        target = mapped(rooted)
        target = posixpath.relpath(target, posixpath.dirname(destination) or '.')
        suffix = ('?' + parts.query if parts.query else '') + ('#' + parts.fragment if parts.fragment else '')
        return '](' + target + suffix + ')'
    # Rewrite each original span once. Replacing source substrings again after
    # rebasing a link would nest rules/<name>/ inside its own destination.
    aliases = {old: new for old, new in mappings.items() if old.startswith('.cursor/')}
    pattern = '|'.join(re.escape(old) for old in sorted(aliases, key=len, reverse=True))
    pattern = '(?:' + pattern + '|\\.cursor/)' if pattern else r'\.cursor/'
    def raw(value):
        return re.sub(pattern, lambda m: aliases.get(m[0], prefix + '/'), value)
    return ''.join(re.sub(r'\]\(([^)]+)\)', link, part) if i % 2 else raw(part)
                   for i, part in enumerate(re.split(r'(\]\([^)]+\))', text)))


def compile_bundle(manifest, stage, options, *, strip_cursor=True):
    """Compile staged/source rules once, preserve scope, and publish a plain entry."""
    stage = Path(stage)
    base = bundle_root(manifest.name)
    prefix = base.as_posix()
    sources = [(manifest.path / 'rules', 'rules')]
    for scenario in filter(None, options.get('scenario', '').split(',')):
        sources.append((manifest.path / 'scenarios' / scenario / 'rules', 'scenarios/' + scenario + '/rules'))
    chosen = {}
    for directory, source_prefix in sources:
        for source in sorted(directory.rglob('*'), key=lambda p: (p.suffix == '.md', p.as_posix())):
            if source.is_file() and source.suffix in ('.md', '.mdc'):
                relative = source.relative_to(directory)
                chosen[relative.with_suffix('.md').as_posix()] = (source, source_prefix + '/' + relative.as_posix(), relative)
    mappings, origins = {}, {}
    for destination, (_, source_name, relative) in chosen.items():
        output = (base / 'rules' / destination).as_posix()
        mappings['.cursor/rules/' + relative.as_posix()] = output
        mappings[source_name] = output
    # Migrate only the temporary render tree. Never delete a user's old folder.
    cursor = stage / '.cursor'
    for source in sorted(cursor.rglob('*')):
        if not source.is_file():
            continue
        relative = source.relative_to(cursor)
        if relative.parts[0] == 'rules':
            continue
        destination = base / relative
        out = stage / destination
        out.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, out)
        origins[destination.as_posix()] = '.cursor/' + relative.as_posix()
        mappings['.cursor/' + relative.as_posix()] = destination.as_posix()
    # Publish the supporting source layout as ordinary files, not registered
    # editor commands/plugins. This keeps relative contract/diagram links real.
    for kind in ('references', 'commands', 'templates', 'scripts'):
        for source in sorted((manifest.path / kind).rglob('*')):
            if not source.is_file() or any(p in {'.git', '__pycache__', 'node_modules', '.venv'} for p in source.relative_to(manifest.path).parts):
                continue
            relative = source.relative_to(manifest.path)
            destination = base / relative
            if not (stage / destination).exists():
                effective = stage / relative if (stage / relative).is_file() else source
                out = stage / destination; out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(effective, out)
                origins[destination.as_posix()] = relative.as_posix()
            mappings[relative.as_posix()] = destination.as_posix()
    records = []
    for destination, (source, source_name, relative) in chosen.items():
        staged_candidates = [stage / '.cursor/rules' / relative, stage / 'office/rules' / relative,
                             stage / base / 'rules' / relative]
        effective = next((p for p in staged_candidates if p.is_file()), source)
        raw = effective.read_text(encoding='utf-8')
        scope, body = _scope(raw)
        path = base / 'rules' / destination
        origins[path.as_posix()] = effective.relative_to(stage).as_posix() if effective.is_relative_to(stage / 'office/rules') else source_name
        applicability = 'always' if scope['always'] is True else 'conditional' if scope['always'] is False else 'manual scope review'
        index_link = posixpath.relpath((base / 'INDEX.md').as_posix(), path.parent.as_posix())
        preamble = ('> Applicability: ' + applicability + '. See [rule index](' + index_link + ') for exact paths/task conditions.\n\n')
        _write(stage / path, preamble + body)
        records.append(dict(file='rules/' + destination, source=source_name,
                            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                            effective_sha256=hashlib.sha256(raw.encode()).hexdigest(), **scope))
    # Preserve generated-only rules, rather than silently dropping native output.
    for source in sorted((cursor / 'rules').rglob('*')):
        if not source.is_file() or source.suffix not in ('.md', '.mdc'):
            continue
        destination = source.relative_to(cursor / 'rules').with_suffix('.md').as_posix()
        if destination in chosen:
            continue
        raw = source.read_text(encoding='utf-8'); scope, body = _scope(raw)
        path = base / 'rules' / destination
        index_link = posixpath.relpath((base / 'INDEX.md').as_posix(), path.parent.as_posix())
        _write(stage / path, '> Applicability: see [rule index](' + index_link + ').\n\n' + body)
        origins[path.as_posix()] = source.relative_to(stage).as_posix()
        mappings[source.relative_to(stage).as_posix()] = path.as_posix()
        records.append(dict(file='rules/' + destination, source='generated/' + source.name,
                            effective_sha256=hashlib.sha256(raw.encode()).hexdigest(), **scope))
    # A raw Cursor root file is migration input only, not a new output adapter.
    if (stage / '.cursorrules').is_file():
        raw = (stage / '.cursorrules').read_text(encoding='utf-8')
        _write(stage / base / 'legacy-root.md', raw)
        origins[(base / 'legacy-root.md').as_posix()] = '.cursorrules'
        records.append(dict(file='legacy-root.md', source='.cursorrules', always=True,
                            paths_expression='', when='Legacy root project contract', frontmatter_raw=''))
    contract = stage / 'AGENTS.md'
    if manifest.name == 'vibe-coding' and (stage / 'MANIFEST.md').is_file():
        contract = stage / 'MANIFEST.md'
    elif not contract.is_file():
        contract = stage / 'CLAUDE.md'
    if not contract.is_file():
        contract = next((manifest.path / name for name in ('AGENTS.md', 'CLAUDE.md', 'PROJECT_RULES.md')
                         if (manifest.path / name).is_file()), None)
    if contract is None:
        raise ValueError('Manifest has no plain Markdown contract')
    _write(stage / base / 'CONTRACT.md', contract.read_text(encoding='utf-8'))
    origins[(base / 'CONTRACT.md').as_posix()] = contract.name
    if strip_cursor:
        shutil.rmtree(cursor, ignore_errors=True)
        (stage / '.cursorrules').unlink(missing_ok=True)
    existing = {p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_file()}
    for source in sorted(stage.rglob('*')):
        if source.is_file() and not source.is_symlink() and source.suffix == '.md' and source.relative_to(stage) not in (base / 'INDEX.md', PROJECT_INDEX):
            destination = source.relative_to(stage).as_posix()
            origin = origins.get(destination, destination)
            text = source.read_text(encoding='utf-8')
            _write(source, _rebase(text, destination, origin, existing, mappings, prefix))
    lines = ['# ' + manifest.name + ': portable rules', '',
             'These are ordinary Markdown instructions. No Cursor rule loader is required. ',
             'Read CONTRACT.md for the business workflow. Supporting commands/scripts are files, not auto-registered host plugins. Always rules apply at entry; ',
             'conditional/manual rules retain their paths and task conditions below. ',
             'Unknown scope requires review, not silent global application.', '',
             '[Business contract](CONTRACT.md) · [Machine-readable scope/provenance](rules.json)', '']
    if not records:
        lines += ['No additional rule files; follow the business contract and its referenced runtime requirements.', '']
    for rule in records:
        lines += ['## [' + rule['file'] + '](' + rule['file'] + ')', '',
                  '- always: `' + str(rule['always']).lower() + '`',
                  '- paths expression (preserved): `' + rule['paths_expression'].replace('\n', ' ') + '`',
                  '- task condition: ' + rule['when'].replace('\n', ' '),
                  '- source: `' + rule['source'] + '`', '']
    _write(stage / base / 'INDEX.md', '\n'.join(lines))
    _write(stage / base / 'rules.json', json.dumps({'schema_version': 1, 'manifest': manifest.name, 'rules': records}, ensure_ascii=False, indent=2) + '\n')
    _write(stage / PROJECT_INDEX, project_index('', manifest.name))
    return base


def merge_project_index(target, stage, name):
    destination = Path(target) / PROJECT_INDEX
    if destination.is_symlink():
        raise ValueError('PROJECT_RULES.md is a symlink; review before replacing it')
    existing = destination.read_text(encoding='utf-8') if destination.is_file() else ''
    _write(Path(stage) / PROJECT_INDEX, project_index(existing, name))
