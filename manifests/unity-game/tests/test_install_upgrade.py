"""Generic opt-in skill bundle compatibility checks never erase custom content."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/vibe_tool/src'))
from vibe_tool.manifest import _install_required_skills
from vibe_tool.types import ManifestInfo


class SkillUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifests = self.root / 'manifests'
        self.manifest_path = self.manifests / 'fixture'
        self.source = self.root / 'mine/fixture-bundle'
        self.target = self.root / 'game'
        self.installed = self.target / '.agents/skills/fixture-bundle'
        self.manifest_path.mkdir(parents=True)
        (self.root / 'skills').mkdir()
        for rel, text in {
            'SKILL.md': '---\nname: fixture-bundle\ndescription: Root fixture\n---\n# Fixture\n',
            'fixture-leaf/SKILL.md': '---\nname: fixture-leaf\ndescription: Leaf fixture\n---\n# Leaf\n',
            'references/skill-map.json': json.dumps({'schema_version': 4}),
            'references/working-contract.md': '# Shared execution contract\n',
            'scripts/__init__.py': '',
            'assets/sample.bin': '\x00\x01',
        }.items():
            path = self.source / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.manifest = ManifestInfo('fixture', self.manifest_path, 'Fixture', False, None,
                                     required_skills=['fixture-bundle'])
        self.policy = {'preserve_existing': True, 'validate_required_files': True,
                       'required_catalog_schemas': {'fixture-bundle/references/skill-map.json': 4}}
        self.write_policy()

    def write_policy(self):
        (self.manifest_path / 'skills-policy.json').write_text(json.dumps(self.policy))

    def install(self, force=True, dry_run=False):
        self.output, self.errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.errors):
            return _install_required_skills(self.manifests, self.manifest, self.target, force, dry_run)

    def copy_bundle(self):
        shutil.copytree(self.source, self.installed)
        (self.installed / 'custom.txt').write_text('custom user data')
        (self.installed / 'SKILL.md').write_text('custom root skill instructions')

    def snapshot(self):
        return {str(path.relative_to(self.target)): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.target.rglob('*') if path.is_file()}

    def test_fresh_install_validates_current_bundle_and_dry_run_is_read_only(self):
        self.assertEqual(self.install(dry_run=True), 0, self.errors.getvalue())
        self.assertFalse(self.target.exists())
        self.assertEqual(self.install(), 0, self.errors.getvalue())
        self.assertTrue((self.installed / 'fixture-leaf/SKILL.md').is_file())

    def test_canonical_bundle_paths_support_required_name_case_and_aliases(self):
        for required in ('FIXTURE-BUNDLE', 'fixture-bund'):
            for catalog_root in ('fixture-bundle', required):
                with self.subTest(required=required, catalog_root=catalog_root):
                    self.manifest.required_skills = [required]
                    self.policy['required_catalog_schemas'] = {
                        f'{catalog_root}/references/skill-map.json': 4}
                    self.write_policy()
                    self.assertEqual(self.install(), 0, self.errors.getvalue())
                    self.assertEqual(self.install(dry_run=True), 0, self.errors.getvalue())
                    self.assertTrue((self.installed / 'fixture-leaf/SKILL.md').is_file())
                    self.assertFalse((self.target / '.agents/skills' / required).exists()
                                     and required != 'fixture-bundle')

    def test_custom_complete_current_bundle_preserved_on_force(self):
        self.copy_bundle()
        before = self.snapshot()
        self.assertEqual(self.install(), 0, self.errors.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_missing_new_leaf_reports_migration_preserves_all_custom_files(self):
        self.copy_bundle()
        (self.installed / 'fixture-leaf/SKILL.md').unlink()
        before = self.snapshot()
        self.assertEqual(self.install(), 1)
        self.assertIn('needs_migration', self.errors.getvalue())
        self.assertIn('fixture-leaf/SKILL.md', self.errors.getvalue())
        self.assertIn('Back up', self.errors.getvalue())
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.install(dry_run=True), 1)
        self.assertEqual(self.snapshot(), before)

    def test_missing_support_reference_detected_with_current_catalog_and_all_skills(self):
        self.copy_bundle()
        (self.installed / 'references/working-contract.md').unlink()
        before = self.snapshot()
        self.assertEqual(self.install(), 1)
        self.assertIn('references/working-contract.md', self.errors.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_copy_exclusions_and_legitimate_empty_binary_support_files(self):
        for excluded in ('.git/SKILL.md', '__pycache__/fake.py', '.venv/fixture.txt'):
            path = self.source / excluded
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('excluded')
        self.assertEqual(self.install(), 0, self.errors.getvalue())
        self.assertEqual((self.installed / 'scripts/__init__.py').read_bytes(), b'')
        self.assertEqual((self.installed / 'assets/sample.bin').read_bytes(), b'\x00\x01')
        for excluded in ('.git/SKILL.md', '__pycache__/fake.py', '.venv/fixture.txt'):
            self.assertFalse((self.installed / excluded).exists())

    def test_old_catalog_with_complete_skill_tree_still_reports_migration(self):
        self.copy_bundle()
        catalog = self.installed / 'references/skill-map.json'
        for value in (3, None, True):
            with self.subTest(value=value):
                catalog.write_text(json.dumps({'schema_version': value}))
                before = self.snapshot()
                self.assertEqual(self.install(), 1)
                self.assertIn('incompatible catalog', self.errors.getvalue())
                self.assertEqual(self.snapshot(), before)

    def test_absent_malformed_or_symlink_catalog_reports_migration(self):
        self.copy_bundle()
        catalog = self.installed / 'references/skill-map.json'
        for value in ('{bad', '[]'):
            with self.subTest(value=value):
                catalog.write_text(value)
                self.assertEqual(self.install(), 1)
                self.assertIn('catalog', self.errors.getvalue())
        catalog.unlink()
        self.assertEqual(self.install(), 1)
        outside = self.root / 'outside.json'
        outside.write_text('{"schema_version": 4}')
        catalog.symlink_to(outside)
        self.assertEqual(self.install(), 1)
        self.assertIn('symlink', self.errors.getvalue())
        self.assertEqual(outside.read_text(), '{"schema_version": 4}')

    def test_empty_unreadable_and_symlink_leaf_never_count_as_present(self):
        self.copy_bundle()
        leaf = self.installed / 'fixture-leaf/SKILL.md'
        leaf.write_text('')
        self.assertEqual(self.install(), 1)
        leaf.write_text(' \n')
        self.assertEqual(self.install(), 1)
        leaf.write_bytes(b'\xff\xfe')
        self.assertEqual(self.install(), 1)
        leaf.unlink()
        outside = self.root / 'outside-leaf'
        outside.write_text('outside skill')
        leaf.symlink_to(outside)
        self.assertEqual(self.install(), 1)
        self.assertIn('symlink', self.errors.getvalue())
        self.assertEqual(outside.read_text(), 'outside skill')

    def test_policy_paths_and_schema_types_rejected_before_copy(self):
        cases = [
            {'validate_required_files': 'yes'},
            {'required_catalog_schemas': {'../outside.json': 4}},
            {'required_catalog_schemas': {'/outside.json': 4}},
            {'required_catalog_schemas': {'fixture-bundle/../outside': 4}},
            {'required_catalog_schemas': {'.': 4}},
            {'required_catalog_schemas': {'other-bundle/catalog.json': 4}},
            {'required_catalog_schemas': {'fixture-bundle/catalog.json': True}},
            {'required_catalog_schemas': {'fixture-bundle/catalog.json': 0}},
            {'required_catalog_schemas': []},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                self.policy = {'preserve_existing': True, **changes}
                self.write_policy()
                self.assertEqual(self.install(), 1)
                self.assertIn('invalid skill policy', self.errors.getvalue())
                self.assertFalse(self.target.exists())

    def test_legacy_manifest_without_opt_in_retains_previous_behavior(self):
        self.copy_bundle()
        (self.installed / 'fixture-leaf/SKILL.md').unlink()
        (self.manifest_path / 'skills-policy.json').unlink()
        self.assertEqual(self.install(force=False), 0, self.errors.getvalue())
        self.assertEqual((self.installed / 'custom.txt').read_text(), 'custom user data')
        self.assertEqual(self.install(force=True), 0, self.errors.getvalue())
        self.assertFalse((self.installed / 'custom.txt').exists())
        self.assertEqual((self.installed / 'SKILL.md').read_text(), (self.source / 'SKILL.md').read_text())

    def test_preserve_only_policy_is_backwards_compatible(self):
        self.copy_bundle()
        (self.installed / 'fixture-leaf/SKILL.md').unlink()
        self.policy = {'preserve_existing': True}
        self.write_policy()
        before = self.snapshot()
        self.assertEqual(self.install(), 0, self.errors.getvalue())
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
