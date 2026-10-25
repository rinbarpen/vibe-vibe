"""Regression coverage for main/Unity required-skill installation semantics."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from vibe_tool.manifest import _install_required_skills
from vibe_tool.types import ManifestInfo


class ManifestMergeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifests = self.root / "manifests"
        self.manifest_path = self.manifests / "fixture"
        self.source = self.manifest_path / "skills/local-bundle"
        self.source.mkdir(parents=True)
        (self.root / "skills").mkdir()
        (self.source / "SKILL.md").write_text("# Local bundle\n")
        (self.source / "catalog.json").write_text('{"schema_version": 4}')
        self.target = self.root / "project"
        self.installed = self.target / ".agents/skills/local-bundle"
        self.manifest = ManifestInfo(
            name="fixture", path=self.manifest_path, description="Fixture",
            has_init_script=False, init_script_path=None,
            required_skills=["local-bundle"],
        )
        self.output = io.StringIO()
        self.errors = io.StringIO()

    def install(self, *, force=False, dry_run=False):
        with contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.errors):
            return _install_required_skills(
                self.manifests, self.manifest, self.target, force, dry_run,
            )

    def enable_policy(self):
        (self.manifest_path / "skills-policy.json").write_text(json.dumps({
            "preserve_existing": True,
            "validate_required_files": True,
            "required_catalog_schemas": {"local-bundle/catalog.json": 4},
        }))

    def snapshot(self):
        return {
            str(path.relative_to(self.target)): path.read_bytes()
            for path in self.target.rglob("*") if path.is_file()
        }

    def test_manifest_local_skill_installs_with_provenance(self):
        self.assertEqual(self.install(), 0)
        self.assertEqual((self.installed / "SKILL.md").read_text(), "# Local bundle\n")
        records = json.loads((self.target / ".vibe-tool/installations.json").read_text())
        self.assertIn("manifests/fixture/skills/local-bundle", json.dumps(records))

    def test_missing_skill_dry_run_succeeds_without_writes(self):
        self.manifest.required_skills = ["missing-bundle"]
        self.assertEqual(self.install(dry_run=True), 0)
        self.assertIn("not found", self.output.getvalue())
        self.assertFalse(self.target.exists())
        self.assertEqual(self.install(), 1)

    def test_local_policy_accepts_alias_and_preserves_customization_on_force(self):
        self.enable_policy()
        self.manifest.required_skills = ["LOCAL-BUNDLE"]
        self.assertEqual(self.install(), 0, self.errors.getvalue())
        (self.installed / "SKILL.md").write_text("# Customized bundle\n")
        (self.installed / "custom.txt").write_text("User data\n")
        before = self.snapshot()
        self.assertEqual(self.install(force=True), 0, self.errors.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_local_policy_dry_run_is_read_only(self):
        self.enable_policy()
        self.assertEqual(self.install(force=True, dry_run=True), 0, self.errors.getvalue())
        self.assertFalse(self.target.exists())

    def test_incompatible_local_bundle_requires_migration_even_in_dry_run(self):
        self.enable_policy()
        self.assertEqual(self.install(), 0, self.errors.getvalue())
        (self.installed / "catalog.json").write_text('{"schema_version": 3}')
        (self.installed / "custom.txt").write_text("User data\n")
        before = self.snapshot()
        for dry_run in (False, True):
            with self.subTest(dry_run=dry_run):
                self.assertEqual(self.install(force=True, dry_run=dry_run), 1)
                self.assertIn("needs_migration", self.errors.getvalue())
                self.assertEqual(self.snapshot(), before)
