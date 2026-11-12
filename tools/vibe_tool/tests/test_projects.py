"""Offline registry and one-transaction project updates, runnable on all three OSes."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from vibe_tool import projects
from vibe_tool.setup import check, setup

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'tools/vibe_tool/src'


def snapshot(path, include_backups=True):
    result = {}
    for p in path.rglob('*'):
        if p.is_file() and (include_backups or '.vibe-tool/backups' not in p.as_posix()):
            result[p.relative_to(path).as_posix()] = (p.read_bytes(), p.stat().st_mtime_ns)
    return result


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='vibe 项目 registry ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = self.root / 'config/projects.json'
        self.env_patch = patch.dict(os.environ, VIBE_PROJECTS_FILE=str(self.registry), PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
        self.env_patch.start(); self.addCleanup(self.env_patch.stop)
        self.repo = self.root / 'source repo'
        self.manifest = self.repo / 'manifests/custom'
        self.write(self.manifest / 'CLAUDE.md', '# Contract v1\n')
        self.write(self.manifest / 'AGENTS.md', '# Contract v1\n')
        self.write(self.manifest / 'rules/custom.mdc', 'Rule v1\n')
        self.write(self.manifest / 'references/guide.md', 'Guide v1\n')
        self.write(self.manifest / 'skills.txt', 'demo\n')
        self.write(self.repo / 'skills/demo/SKILL.md', '---\nname: demo\ndescription: Demo\n---\nBody v1\n')
        self.write(self.repo / 'skills/demo/references/support.md', 'Support v1\n')
        self.write(self.repo / 'skills/demo/obsolete.py', 'old support\n')
        self.write(self.repo / 'skills/extra/SKILL.md', '# Extra v1\n')
        (self.repo / 'mine').mkdir()
        self.target = self.root / 'business 项目'

    def write(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding='utf-8'); return path

    def cli(self, *args, expected=0, no_source=False):
        env = dict(os.environ, PYTHONPATH=str(SRC), VIBE_HOME=str(self.repo))
        if no_source:
            env.pop('VIBE_HOME', None)
        result = subprocess.run([sys.executable, '-B', '-m', 'vibe_tool', *map(str, args)],
                                env=env, cwd=self.root, text=True, capture_output=True, encoding='utf-8')
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def install(self, target=None):
        target = target or self.target
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup(self.repo, 'custom', target, skills=['extra']), 0)
        return projects.resolve(str(target))[0]

    def test_automatic_setup_registration_has_no_staging_projects(self):
        self.install()
        data = projects.load_registry()['projects']
        self.assertEqual(len(data), 1)
        row = next(iter(data.values()))
        self.assertEqual(row['path'], str(self.target.resolve()))
        self.assertEqual(row['source'], str(self.repo.resolve()))

    def test_cli_init_and_skill_add_register_only_completed_projects(self):
        self.cli('init', 'custom', self.target)
        self.assertEqual(len(projects.list_projects()), 1)
        other = self.root / 'skill-only'
        self.cli('add', 'skill', 'demo', other)
        self.assertEqual(len(projects.list_projects()), 2)
        before = self.registry.read_bytes(), self.registry.stat().st_mtime_ns
        self.cli('init', 'custom', self.root / 'preview', '--dry-run')
        self.cli('add', 'skill', 'missing', self.root / 'failed', expected=1)
        self.assertEqual((self.registry.read_bytes(), self.registry.stat().st_mtime_ns), before)

    def test_read_only_list_show_and_dry_run_without_repo_discovery(self):
        name = self.install()
        before = snapshot(self.target), self.registry.read_bytes(), self.registry.stat().st_mtime_ns
        listed = self.cli('project', 'list', '--json', no_source=True)
        self.assertEqual(json.loads(listed.stdout)[0]['name'], name)
        self.assertEqual(json.loads(self.cli('projects', 'show', name, '--json', no_source=True).stdout)['mode'], 'setup')
        self.write(self.manifest / 'AGENTS.md', '# Contract v2\n')
        self.cli('project', 'update', name, '--dry-run', no_source=True)
        self.assertEqual((snapshot(self.target), self.registry.read_bytes(), self.registry.stat().st_mtime_ns), before)

    def test_alias_collision_dedup_rename_move_remove_only_index(self):
        name = self.install()
        self.assertEqual(projects.register(self.target, self.repo), name)
        other = self.root / 'another' / self.target.name
        other.mkdir(parents=True)
        other_name = projects.register(other, self.repo)
        self.assertNotEqual(name, other_name)
        with self.assertRaises(ValueError):
            projects.register(other, self.repo, name=name)
        projects.rename(name, 'research')
        moved = self.root / 'moved 项目'
        shutil.move(str(self.target), str(moved))
        self.assertEqual(projects.list_projects()[1 if projects.list_projects()[0]['name'] != 'research' else 0]['status'], 'missing')
        projects.relocate('research', moved)
        before = snapshot(moved)
        self.cli('project', 'remove', 'research')
        self.assertEqual(snapshot(moved), before)
        self.assertEqual(len(projects.list_projects()), 1)

    def test_unmanaged_registration_does_not_invent_installations(self):
        self.target.mkdir()
        self.cli('project', 'add', self.target, '--name', 'plain', '--source', self.repo)
        self.assertEqual(projects.list_projects()[0]['status'], 'unmanaged')
        self.cli('project', 'update', 'plain', expected=1)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_setup_refresh_manifest_and_full_dual_skills_in_one_backup(self):
        name = self.install()
        self.write(self.manifest / 'CLAUDE.md', '# Contract v2\n')
        self.write(self.manifest / 'AGENTS.md', '# Contract v2\n')
        self.write(self.manifest / 'references/guide.md', 'Guide v2\n')
        self.write(self.repo / 'skills/demo/references/support.md', 'Support v2\n')
        (self.repo / 'skills/demo/obsolete.py').unlink()
        (self.target / 'AGENTS.md').write_text((self.target / 'AGENTS.md').read_text(encoding='utf-8') + '\nUser added rule\n', encoding='utf-8')
        old_count = len(list((self.target / '.vibe-tool/backups').iterdir()))
        self.cli('project', 'update', name)
        self.assertEqual(len(list((self.target / '.vibe-tool/backups').iterdir())), old_count + 1)
        self.assertIn('User added rule', (self.target / 'AGENTS.md').read_text(encoding='utf-8'))
        for host in ('.agents', '.claude'):
            self.assertEqual((self.target / host / 'skills/demo/references/support.md').read_text(), 'Support v2\n')
            self.assertFalse((self.target / host / 'skills/demo/obsolete.py').exists())
        self.assertEqual((self.target / 'CLAUDE.vibe-custom.md').read_text(), '# Contract v2\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check(self.target), 0)
        before = snapshot(self.target)
        self.cli('project', 'update', name)
        self.assertEqual(snapshot(self.target), before)

    def test_later_skill_add_updates_both_hosts_records_and_hashes(self):
        name = self.install()
        self.write(self.repo / 'skills/later/SKILL.md', '# Later v1\n')
        before = snapshot(self.target)
        self.cli('add', 'skill', 'later', self.target, '--dry-run')
        self.assertEqual(snapshot(self.target), before)
        self.cli('add', 'skill', 'later', self.target)
        self.assertEqual((self.target / '.claude/skills/later/SKILL.md').read_text(), '# Later v1\n')
        with contextlib.redirect_stdout(io.StringIO()):
            check(self.target)
        self.write(self.repo / 'skills/later/SKILL.md', '# Later v2\n')
        self.cli('project', 'update', name, '--skill', 'later')
        self.assertEqual((self.target / '.claude/skills/later/SKILL.md').read_text(), '# Later v2\n')
        with contextlib.redirect_stdout(io.StringIO()):
            check(self.target)

    def test_single_entry_manifest_refreshes_both_host_fallbacks(self):
        (self.manifest / 'AGENTS.md').unlink()
        name = self.install()
        self.write(self.manifest / 'CLAUDE.md', '# One entry v2\n')
        self.cli('project', 'update', name, '--manifest', 'custom')
        self.assertEqual((self.target / 'AGENTS.vibe-custom.md').read_text(), '# One entry v2\n')
        self.assertEqual((self.target / 'CLAUDE.vibe-custom.md').read_text(), '# One entry v2\n')

    def test_skill_only_scope_does_not_refresh_manifest_or_other_skills(self):
        name = self.install()
        old = (self.target / 'AGENTS.vibe-custom.md').read_bytes()
        self.write(self.manifest / 'AGENTS.md', '# Contract v2\n')
        self.write(self.repo / 'skills/demo/SKILL.md', '# Demo v2\n')
        self.write(self.repo / 'skills/extra/SKILL.md', '# Extra v2\n')
        self.cli('project', 'update', name, '--skill', 'demo')
        self.assertEqual((self.target / 'AGENTS.vibe-custom.md').read_bytes(), old)
        self.assertEqual((self.target / '.claude/skills/demo/SKILL.md').read_text(), '# Demo v2\n')
        self.assertEqual((self.target / '.agents/skills/extra/SKILL.md').read_text(), '# Extra v1\n')
        with contextlib.redirect_stdout(io.StringIO()):
            check(self.target)

    def test_manifest_scope_skips_new_dependencies_and_extra_skill(self):
        name = self.install()
        self.write(self.manifest / 'skills.txt', 'demo\nnew-skill\n')
        self.write(self.repo / 'skills/new-skill/SKILL.md', '# Newly required\n')
        self.write(self.repo / 'skills/demo/SKILL.md', '# Demo v2\n')
        self.write(self.repo / 'skills/extra/SKILL.md', '# Extra v2\n')
        self.cli('project', 'update', name, '--manifest', 'custom')
        self.assertFalse((self.target / '.agents/skills/new-skill').exists())
        self.assertEqual((self.target / '.agents/skills/demo/SKILL.md').read_text(), '# Demo v2\n')
        self.assertEqual((self.target / '.agents/skills/extra/SKILL.md').read_text(), '# Extra v1\n')

    def test_local_customization_blocks_whole_project_before_writes(self):
        name = self.install()
        self.write(self.target / '.claude/skills/demo/local.md', 'User content\n')
        self.write(self.manifest / 'AGENTS.md', '# Contract v2\n')
        before = snapshot(self.target)
        self.cli('project', 'update', name, expected=1)
        self.assertEqual(snapshot(self.target), before)

    def test_single_transaction_failure_and_standalone_restore(self):
        name = self.install()
        self.write(self.manifest / 'AGENTS.md', '# Contract v2\n')
        self.write(self.repo / 'skills/demo/SKILL.md', '# Demo v2\n')
        before = {p: v[0] for p, v in snapshot(self.target, False).items()}
        from vibe_tool import transaction
        from vibe_tool.project_sync import update_project
        original = transaction._replace
        count = 0
        def fail(source, dest):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError('injected project application error')
            original(source, dest)
        with patch('vibe_tool.transaction._replace', side_effect=fail), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(update_project(self.repo, self.target), 1)
        self.assertEqual({p: v[0] for p, v in snapshot(self.target, False).items()}, before)
        self.cli('project', 'update', name)
        backup = sorted((self.target / '.vibe-tool/backups').glob('*/restore.py'))[-1]
        restored = subprocess.run([sys.executable, str(backup)], capture_output=True, text=True)
        self.assertEqual(restored.returncode, 0, restored.stderr)
        self.assertEqual({p: v[0] for p, v in snapshot(self.target, False).items()}, before)
        with contextlib.redirect_stdout(io.StringIO()):
            check(self.target)

    def test_legacy_project_keeps_existing_update_semantics(self):
        self.cli('init', 'custom', self.target)
        name = projects.resolve(str(self.target))[0]
        self.write(self.manifest / 'AGENTS.md', '# Contract v2\n')
        self.write(self.repo / 'skills/demo/SKILL.md', '# Demo v2\n')
        self.write(self.target / 'business.txt', 'Do not touch\n')
        self.cli('project', 'update', name)
        self.assertEqual((self.target / 'AGENTS.md').read_text(), '# Contract v2\n')
        self.assertEqual((self.target / '.agents/skills/demo/SKILL.md').read_text(), '# Demo v2\n')
        self.assertEqual((self.target / 'business.txt').read_text(), 'Do not touch\n')
        self.assertFalse((self.target / '.vibe-setup.json').exists())

    def test_builtin_legacy_project_uses_portable_render_with_existing_resource_policy(self):
        source = self.repo / 'manifests/auto-research'
        shutil.copytree(ROOT / 'manifests/auto-research', source, ignore=shutil.ignore_patterns('__pycache__'))
        self.write(source / 'skills.txt', '')
        self.target.mkdir()
        from vibe_tool.installations import record_manifest
        record_manifest(self.repo, self.target, 'auto-research', source, {})
        from vibe_tool.project_sync import update_project
        with patch('vibe_tool.project_sync.render_manifest', side_effect=AssertionError('No Bash renderer')):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(update_project(self.repo, self.target, manifests=['auto-research']), 0)
        self.assertTrue((self.target / 'references/idea-validation.md').is_file())
        self.assertFalse((self.target / 'README.md').exists())
        self.assertFalse((self.target / 'MANIFEST.md').exists())
        self.assertFalse((self.target / '.vibe-setup.json').exists())

    def test_batch_continues_after_missing_path_and_returns_failure(self):
        name = self.install()
        self.install(self.root / 'second')
        shutil.rmtree(self.target)
        self.write(self.manifest / 'AGENTS.md', '# Contract v2\n')
        result = self.cli('project', 'update', '--all', expected=1)
        self.assertIn('2 project(s), 1 failed', result.stdout)
        self.assertEqual((self.root / 'second/AGENTS.vibe-custom.md').read_text(), '# Contract v2\n')
        self.assertIn(name, projects.load_registry()['projects'])

    def test_concurrent_registrations_do_not_drop_projects(self):
        processes = []
        for i in range(4):
            target = self.root / f'concurrent-{i}'
            target.mkdir()
            env = dict(os.environ, PYTHONPATH=str(SRC))
            processes.append(subprocess.Popen([sys.executable, '-B', '-m', 'vibe_tool', 'project', 'add', str(target), '--source', str(self.repo)],
                                              env=env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        for process in processes:
            out, err = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, out + err)
        self.assertEqual(len(projects.list_projects()), 4)

    def test_corrupt_index_preserved_and_index_failure_does_not_undo_install(self):
        self.registry.parent.mkdir()
        self.registry.write_text('{broken')
        with self.assertRaises(ValueError):
            projects.load_registry()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(setup(self.repo, 'custom', self.target), 0)
        self.assertIn('index registration needs attention', errors.getvalue())
        self.assertEqual(self.registry.read_text(), '{broken')
        self.assertTrue((self.target / '.vibe-tool/installations.json').is_file())


if __name__ == '__main__':
    unittest.main()
