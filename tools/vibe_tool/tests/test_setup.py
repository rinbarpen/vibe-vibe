"""Offline, standard-library setup tests; intended for Linux/macOS/Windows CI."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from vibe_tool.discovery import discover_manifests, resolve_manifest
from vibe_tool.portable import render
from vibe_tool.setup import STATE, check, setup

ROOT = Path(__file__).resolve().parents[3]


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.vibe-tool/backups' not in p.as_posix()}


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='setup Unicode 测试 ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry_env = patch.dict(os.environ, {'VIBE_PROJECTS_FILE': str(self.root / 'registry/projects.json')})
        self.registry_env.start(); self.addCleanup(self.registry_env.stop)
        self.repo = self.root / 'source repo'
        self.manifest = self.repo / 'manifests/custom'
        self.manifest.mkdir(parents=True)
        (self.repo / 'skills/example/references').mkdir(parents=True)
        (self.repo / 'mine').mkdir()
        for name in ('AGENTS.md', 'CLAUDE.md'):
            (self.manifest / name).write_text('# Custom workflow\nRead references/workflow.md\n', encoding='utf-8')
        (self.manifest / 'references').mkdir()
        (self.manifest / 'references/workflow.md').write_text('Original workflow evidence', encoding='utf-8')
        (self.manifest / 'skills.txt').write_text('example\n', encoding='utf-8')
        (self.repo / 'skills/example/SKILL.md').write_text('---\nname: example\ndescription: Example\n---\nRead references/support.md\n', encoding='utf-8')
        (self.repo / 'skills/example/references/support.md').write_text('full support bundle', encoding='utf-8')
        self.target = self.root / 'project 项目 with spaces'

    def install(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return setup(self.repo, 'custom', self.target, **kwargs)

    def test_actual_cli_dispatch_accepts_repo_generation_option_and_target(self):
        from vibe_tool.setup import main
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['custom', str(self.target), '--repo', 'business-repo', '--dry-run'], repo=self.repo), 0)
            self.assertFalse(self.target.exists())
            self.assertEqual(main(['custom', str(self.target), '--repo', 'business-repo'], repo=self.repo), 0)
            self.assertEqual(main(['custom', str(self.target), '--check'], repo=self.repo), 0)

    def test_both_hosts_full_skill_bundles_and_source_provenance(self):
        self.assertEqual(self.install(), 0)
        for root in ('.agents', '.claude'):
            self.assertEqual((self.target / root / 'skills/example/references/support.md').read_text(), 'full support bundle')
            self.assertFalse((self.target / root / 'skills/example').is_symlink())
        for host in ('AGENTS', 'CLAUDE'):
            self.assertIn(f'{host}.vibe-custom.md', (self.target / f'{host}.md').read_text())
            self.assertEqual((self.target / f'{host}.vibe-custom.md').read_bytes(), (self.manifest / f'{host}.md').read_bytes())
        records = json.loads((self.target / '.vibe-tool/installations.json').read_text())
        self.assertEqual(records['manifests']['custom']['source'], 'manifests/custom')
        self.assertEqual(records['skills']['example']['source'], 'skills/example')
        before = snapshot(self.target)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check(self.target), 0)
        self.assertEqual(snapshot(self.target), before)

    def test_agent_specific_imports(self):
        for host, present, absent in (('codex', 'AGENTS.md', 'CLAUDE.md'), ('claude', 'CLAUDE.md', 'AGENTS.md')):
            with self.subTest(host=host):
                self.target = self.root / host
                self.assertEqual(self.install(agent=host), 0)
                self.assertTrue((self.target / present).is_file())
                self.assertFalse((self.target / absent).exists())
                self.assertEqual((self.target / '.claude/skills/example').exists(), host == 'claude')

    def test_dry_run_new_and_existing_projects_are_unchanged(self):
        self.assertEqual(self.install(dry_run=True), 0)
        self.assertFalse(self.target.exists())
        self.target.mkdir()
        (self.target / 'AGENTS.md').write_bytes(b'User rules\n\n')
        before = snapshot(self.target)
        self.assertEqual(self.install(dry_run=True), 0)
        self.assertEqual(snapshot(self.target), before)
        self.assertFalse((self.target / '.vibe-tool').exists())

    def test_preserve_root_rules_and_business_data_with_one_import(self):
        self.target.mkdir()
        (self.target / 'AGENTS.md').write_bytes(b'User rules\n\n')
        (self.target / 'README.md').write_text('User README')
        (self.target / 'data.csv').write_text('original data')
        self.assertEqual(self.install(), 0)
        rules = (self.target / 'AGENTS.md').read_text()
        self.assertTrue(rules.startswith('User rules\n\n'))
        self.assertEqual(rules.count('<!-- vibe:setup:custom:begin -->'), 1)
        before = snapshot(self.target)
        backups = list((self.target / '.vibe-tool/backups').iterdir())
        self.assertEqual(self.install(), 0)
        self.assertEqual(snapshot(self.target), before)
        self.assertEqual(list((self.target / '.vibe-tool/backups').iterdir()), backups)
        self.assertEqual((self.target / 'README.md').read_text(), 'User README')
        self.assertEqual((self.target / 'data.csv').read_text(), 'original data')

    def test_missing_dependency_and_invalid_scenario_write_nothing(self):
        (self.manifest / 'skills.txt').write_text('missing\n')
        with self.assertRaises(ValueError):
            self.install()
        self.assertFalse(self.target.exists())
        (self.manifest / 'skills.txt').write_text('example\n')
        with self.assertRaises(ValueError):
            self.install(scenario='../other')
        self.assertFalse(self.target.exists())

    def test_user_skill_conflict_preserved_before_any_project_writes(self):
        skill = self.target / '.claude/skills/example/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('User customized skill')
        before = snapshot(self.target)
        with self.assertRaisesRegex(ValueError, 'Preserved local conflicts'):
            self.install()
        self.assertEqual(snapshot(self.target), before)

    def test_changed_resource_check_fails_read_only_and_rerun_keeps_edits(self):
        self.assertEqual(self.install(), 0)
        resource = self.target / 'references/workflow.md'
        resource.write_text('User edit')
        before = snapshot(self.target)
        with self.assertRaisesRegex(ValueError, 'Changed or missing'):
            check(self.target)
        with self.assertRaisesRegex(ValueError, 'Preserved local conflicts'):
            self.install()
        self.assertEqual(snapshot(self.target), before)

    def test_source_refresh_only_updates_unmodified_managed_resources(self):
        self.assertEqual(self.install(), 0)
        (self.manifest / 'references/workflow.md').write_text('New source')
        self.assertEqual(self.install(), 0)
        self.assertEqual((self.target / 'references/workflow.md').read_text(), 'New source')
        with contextlib.redirect_stdout(io.StringIO()):
            check(self.target)

    def test_backup_standalone_restore_restores_original_project_and_registry(self):
        self.target.mkdir()
        (self.target / 'AGENTS.md').write_text('Original instructions')
        (self.target / 'data.csv').write_text('Original data')
        before = snapshot(self.target)
        self.assertEqual(self.install(), 0)
        backups = list((self.target / '.vibe-tool/backups').iterdir())
        self.assertEqual(len(backups), 1)
        result = subprocess.run([sys.executable, str(backups[0] / 'restore.py')], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.target), before)

    def test_application_failure_rolls_back_imports_skills_and_installation_records(self):
        self.target.mkdir()
        (self.target / 'AGENTS.md').write_text('Original')
        before = snapshot(self.target)
        from vibe_tool import transaction
        original = transaction._replace
        count = 0
        def fail(source, dest):
            nonlocal count
            count += 1
            if count == 4:
                raise OSError('injected write error')
            return original(source, dest)
        with patch('vibe_tool.transaction._replace', side_effect=fail):
            self.assertEqual(self.install(), 1)
        self.assertEqual(snapshot(self.target), before)

    def test_declines_source_overlap(self):
        with self.assertRaisesRegex(ValueError, 'overlap'):
            setup(self.repo, 'custom', self.repo / 'my-project')


class PortableRendererTests(unittest.TestCase):
    def test_every_current_manifest_has_a_shell_free_renderer(self):
        # All real manifest resources/native Python installers, without pulling
        # unrelated skill bundles into this offline portability test.
        for manifest in discover_manifests(ROOT / 'manifests'):
            with self.subTest(manifest=manifest.name), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                stage = base / 'rendered'
                result = []
                original_run = subprocess.run
                def no_shell(argv, **kwargs):
                    self.assertIsInstance(argv, list)
                    self.assertEqual(argv[0], sys.executable)
                    self.assertTrue(argv[1].endswith('.py'))
                    self.assertFalse(kwargs.get('shell', False))
                    result.append(argv)
                    return original_run(argv, **kwargs)
                with patch('vibe_tool.portable.subprocess.run', side_effect=no_shell):
                    render(manifest, stage, base / 'actual project', {'provider': 'git'})
                self.assertTrue((stage / 'CLAUDE.md').is_file())
                self.assertFalse(any(p.is_symlink() for p in stage.rglob('*')))

    def test_vibe_default_and_provider_output_match_legacy_resource_content(self):
        manifest = resolve_manifest(ROOT / 'manifests', 'vibe-coding')
        for provider in ('git', 'github', 'gitlab', 'gitee'):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                render(manifest, base / 'portable', base / 'target', {'provider': provider, 'scenario': 'fullstack-web'})
                if os.name == 'nt':
                    continue  # Native CI tests the portable path, not Git Bash.
                result = subprocess.run(['bash', str(manifest.init_script_path), str(base / 'legacy'),
                                         '--provider=' + provider, '--scenario=fullstack-web', '--no-git'],
                                        capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse((base / 'portable/.cursor').exists())
                self.assertTrue((base / 'portable/PROJECT_RULES.md').is_file())
                metadata = json.loads((base / 'portable/rules/vibe-coding/rules.json').read_text())
                def normalize(text):
                    for rule in metadata['rules']:
                        if rule['file'].startswith('rules/') and rule['source'].endswith('.mdc'):
                            old = '.cursor/rules/' + Path(rule['source']).name
                            text = text.replace('rules/vibe-coding/' + rule['file'], old)
                    return text.replace('rules/vibe-coding/', '.cursor/').replace(manifest.path.as_posix(), 'SOURCE').replace('manifests/vibe-coding', 'SOURCE')
                for p in (base / 'portable').rglob('*'):
                    if p.is_file():
                        relative = p.relative_to(base / 'portable')
                        if relative.as_posix().startswith('rules/') or relative.name == 'PROJECT_RULES.md':
                            continue  # The neutral bundle is covered by rule/scope preservation tests.
                        old = base / 'legacy' / relative
                        self.assertTrue(old.is_file(), str(relative))
                        if p.suffix in ('.md', '.mdc'):
                            self.assertEqual(normalize(p.read_text()), normalize(old.read_text()), str(relative))
                        else:
                            self.assertEqual(p.read_bytes(), old.read_bytes(), str(relative))

    def test_checked_in_setup_workflow_is_current_and_read_only(self):
        source, svg = ROOT / 'docs/project-setup-workflow.json', ROOT / 'docs/project-setup-workflow.svg'
        before = svg.read_bytes(), svg.stat().st_mtime_ns
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/render-manifest-workflow.py'),
                                 '--source', str(source), '--output', str(svg), '--check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((svg.read_bytes(), svg.stat().st_mtime_ns), before)
        graph = json.loads(source.read_text(encoding='utf-8'))
        routes = {(e['from'], e['to']) for e in graph['edges']}
        self.assertIn(('install', 'rollback'), routes)
        self.assertIn(('rollback', 'preview'), routes)
        self.assertIn(('decision', 'select'), routes)

    def test_cli_shim_runs_from_an_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/setup-project.py'), '--list'], cwd=directory,
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('auto-research', {m['name'] for m in json.loads(result.stdout)})


if __name__ == '__main__':
    unittest.main()
