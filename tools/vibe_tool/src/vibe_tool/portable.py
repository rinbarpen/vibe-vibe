"""Portable setup rendering. Existing init/add and shell entrypoints stay unchanged.

Reuse native Python installers when available; otherwise mirror the explicit
resource layout of the small legacy shell installers. Never execute a shell.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

NATIVE = {
    'tutor': 'scripts/install-tutor.py',
    'office': 'scripts/install_office.py',
    'unity-game': 'scripts/install_manifest.py',
    'game-design': 'scripts/install_manifest.py',
}
LEGACY = {'vibe-coding', 'auto-research', 'auto-research-ars', 'ui-testing', 'fund-proposal'}


def _copy(src: Path, stage: Path, relative: str | Path, substitutions=None):
    if not src.is_file():
        raise ValueError(f'Missing source: {src}')
    dst = stage / relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    if substitutions:
        text = src.read_text(encoding='utf-8')
        for old, new in substitutions.items():
            text = text.replace(old, new)
        dst.write_text(text, encoding='utf-8')
    else:
        shutil.copy2(src, dst)


def _tree(src: Path, stage: Path, relative: str | Path, substitutions=None):
    for p in sorted(src.rglob('*')):
        if not p.is_file() or any(part in {'__pycache__', '.git', '.venv', 'node_modules'} for part in p.relative_to(src).parts):
            continue
        _copy(p, stage, Path(relative) / p.relative_to(src), substitutions)


def _commands(src, stage):
    # Legacy commands consist of immediate files inside named command folders.
    for directory in sorted(src.iterdir()) if src.is_dir() else ():
        if directory.is_dir():
            for file in sorted(directory.iterdir()):
                if file.is_file():
                    _copy(file, stage, Path('.cursor/commands') / directory.name / file.name)


def _render_raw(manifest, stage: Path, target: Path, options: dict[str, str]):
    """Render a fresh setup tree; all persistent writes are handled by setup."""
    src = manifest.path
    name = manifest.name
    stage.mkdir(parents=True, exist_ok=True)
    if name in NATIVE:
        command = [sys.executable, str(src / NATIVE[name]), str(stage)]
        if options.get('scenario'):
            command += ['--scenario', options['scenario']]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
        result = subprocess.run(command, env=env, capture_output=True, text=True, encoding='utf-8')
        if result.returncode:
            raise ValueError(f'Python initializer failed ({result.returncode}): {result.stdout}\n{result.stderr}')
        return
    if manifest.has_init_script and name not in LEGACY:
        raise ValueError(f'{name}: add a portable Python renderer before using setup; legacy init is unchanged')
    # Root files and native agent definitions retain the existing source layout.
    for file in ('CLAUDE.md', 'AGENTS.md', 'PROJECT_RULES.md', 'MANIFEST.md', 'README.md', 'CONTRIBUTING.md', '.cursorrules', '.editorconfig', '.gitignore'):
        if (src / file).is_file():
            _copy(src / file, stage, file)
    for directory in ('.claude/agents', '.codex/agents'):
        _tree(src / directory, stage, directory)
    if name == 'vibe-coding':
        _vibe(src, stage, target, options)
    elif name == 'auto-research':
        _research(src, stage, options)
    elif name == 'auto-research-ars':
        for directory in ('references', 'templates'):
            _tree(src / directory, stage, directory)
    elif name == 'ui-testing':
        subst = {'{{UI_TESTING_MANIFEST}}': src.as_posix()}
        _tree(src / 'rules', stage, '.cursor/rules', subst)
        for scenario in options.get('scenario', '').split(','):
            if not scenario:
                continue
            base = src / 'scenarios' / scenario
            _tree(base / 'rules', stage, '.cursor/rules', subst)
            if (base / 'CLAUDE.md').is_file():
                _copy(base / 'CLAUDE.md', stage, 'CLAUDE.ui-testing.md')
    elif name == 'fund-proposal':
        _tree(src / 'rules', stage, '.cursor/rules')
        for file in ('skeleton', 'innovations', 'key_problems'):
            p = stage / f'outline/{file}.md'; p.parent.mkdir(parents=True, exist_ok=True); p.touch()
    else:
        _tree(src / 'rules', stage, '.cursor/rules', {'{{VIBE_MANIFEST}}': src.as_posix()})
        _commands(src / 'commands', stage)
        # A newly authored generic manifest explicitly ships its workflow assets.
        # This does not change the legacy generic init/add asset policy.
        _tree(src / 'references', stage, 'references')
        _tree(src / 'scripts', stage, 'scripts')
        _tree(src / 'templates', stage, 'templates')


def _research(src, stage, options):
    substitutions = {'${DEFAULT_OWNER}': options.get('owner') or 'researcher',
                     '${ORG_NAME}': options.get('org') or 'org',
                     '${REPO_NAME}': options.get('repo') or 'repo'}
    _tree(src / '.github', stage, '.github', substitutions)
    for directory in ('templates', 'references', 'writing', 'lifecycle'):
        _tree(src / directory, stage, directory)
    for name in ('writing_plan.py', 'research_workflow.py', 'stage_contract.py', 'table_plan.py',
                 'table_ablation.py', 'experiment_stats.py', 'figure_smoke.py', 'latex_template_gate.py', 'render_idea_workflow.py'):
        _copy(src / 'scripts' / name, stage, 'scripts/' + name)


def _vibe(src, stage, target, options):
    provider = options.get('provider') or 'git'
    if provider not in {'git', 'github', 'gitlab', 'gitee'}:
        raise ValueError('Unknown code provider: ' + provider)
    # Copies instead of symlinks: no Windows Developer Mode/admin requirement.
    for name in ('AGENTS.md', 'CLAUDE.md'):
        _copy(src / 'MANIFEST.md', stage, name)
    subst = {'{{VIBE_MANIFEST}}': src.as_posix()}
    _tree(src / 'rules', stage, '.cursor/rules', subst)
    for scenario in filter(None, options.get('scenario', '').split(',')):
        _tree(src / 'scenarios' / scenario / 'rules', stage, '.cursor/rules', subst)
    assets = ('references/codegraph-workflow.json', 'references/codegraph-workflow.svg', 'scripts/render_codegraph_workflow.py',
              'references/ui-usability.md', 'references/ui-usability-workflow.json', 'references/ui-usability-workflow.svg',
              'references/readme-guide.md', 'references/setup-guide.md', 'references/docs-readability-workflow.json',
              'references/docs-readability-workflow.svg', 'scripts/version_guard.py')
    for relative in assets:
        _copy(src / relative, stage, relative)
    for directory in ('language-specs', 'decision-trees'):
        _tree(src / 'references' / directory, stage, '.cursor/references/' + directory)
    for name in ('branching-strategy', 'pages-guide', 'pr-conventions', 'readme-guide', 'release-process', 'tag-convention', 'lifecycle-guide'):
        if (src / f'references/{name}.md').is_file():
            _copy(src / f'references/{name}.md', stage, f'.cursor/references/{name}.md')
    for name in ('docs-readability-workflow.json', 'docs-readability-workflow.svg'):
        _copy(src / 'references' / name, stage, '.cursor/references/' + name)
    _commands(src / 'commands', stage)
    _tree(src / 'templates', stage, '.cursor/templates')
    if provider == 'github':
        replacements = {'${DEFAULT_OWNER}': options.get('owner') or 'default-owner',
                        '${ORG_NAME}': options.get('org') or 'org', '${REPO_NAME}': options.get('repo') or 'repo',
                        '${SECURITY_EMAIL}': options.get('email') or 'security@example.com'}
        _tree(src / '.github', stage, '.github', replacements)
    elif provider == 'gitlab':
        _copy(src / 'platforms/gitlab/.gitlab-ci.yml', stage, '.gitlab-ci.yml')
    elif provider == 'gitee':
        _tree(src / 'platforms/gitee/.workflow', stage, '.workflow')
    # Reuse version validation against existing project metadata, not a default
    # version invented by the setup renderer. Only a temporary tree is touched.
    for relative in ('VERSION', 'CHANGELOG.md', 'package.json', 'pyproject.toml'):
        if (target / relative).is_file():
            _copy(target / relative, stage, relative)
    result = subprocess.run([sys.executable, str(src / 'scripts/init_version.py'), str(stage)],
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1'),
                            capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    # Existing package metadata is an input, not a generated setup resource.
    for relative in ('package.json', 'pyproject.toml'):
        (stage / relative).unlink(missing_ok=True)


def render(manifest, stage: Path, target: Path, options: dict[str, str]):
    """Publish a harness-independent tree; legacy formats are migration input."""
    from .harness_rules import compile_bundle
    _render_raw(manifest, stage, target, options)
    compile_bundle(manifest, stage, options, strip_cursor=True)
