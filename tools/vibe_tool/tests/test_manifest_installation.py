"""Offline regression tests for manifest delegation and learning installation.

Run with:
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src \
        python -m unittest discover -s tools/vibe_tool/tests \
        -p test_manifest_installation.py -v
"""

import contextlib
import io
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from vibe_tool.manifest import _run_init_script
from vibe_tool.types import ManifestInfo


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "manifests" / "tutor"
SCRIPT = MANIFEST / "scripts" / "vibe-init-tutor.sh"
SCENARIOS = ("self-study", "exam-prep", "course-learning", "research-reading")


def _environment():
    env = dict(os.environ)
    env["VIBE_HOME"] = str(REPO_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(REPO_ROOT / "tools" / "vibe_tool" / "src")
    return env


def _snapshot(directory):
    """Capture contents and metadata, including unexpected new empty folders."""
    return {
        path.relative_to(directory).as_posix(): (
            "file" if path.is_file() else "directory",
            path.read_bytes() if path.is_file() else None,
            path.stat().st_mtime_ns,
            path.stat().st_mode,
        )
        for path in sorted(directory.rglob("*"))
    }


def _managed_files():
    """Use live resources so newly added commands/templates are covered too."""
    for filename in ("CLAUDE.md", "AGENTS.md", "README.md", ".cursorrules"):
        yield MANIFEST / filename, Path(filename)
    yield MANIFEST / "scripts/export-notes.py", Path("scripts/export-notes.py")
    for source_dir, destination_dir in (
        ("rules", ".cursor/rules"),
        ("commands", ".cursor/commands"),
        ("skills", "skills"),
        ("references", "references"),
        ("agents", "agents"),
        ("templates", ".cursor/templates"),
    ):
        root = MANIFEST / source_dir
        for source in sorted(root.rglob("*")):
            if source.is_file():
                yield source, Path(destination_dir) / source.relative_to(root)


class ScriptDelegationTests(unittest.TestCase):
    def _manifest(self, name):
        return ManifestInfo(
            name=name,
            path=Path("/fixtures/manifest with spaces"),
            description="Test fixture",
            has_init_script=True,
            init_script_path=Path("/fixtures/manifest with spaces/init.sh"),
        )

    def test_all_mapped_flags_keep_values_as_independent_arguments(self):
        values = {
            "scenario": "chapter one,chapter two",
            "owner": "Owner Name",
            "org": "Example Organization",
            "repo": "Repository Name",
            "email": "First Last@example.test",
            "cloud": "Cloud Provider",
            "unrecognized": "ignored value",
        }
        identity = [
            "-o", values["owner"], "--org", values["org"],
            "--repo", values["repo"], "--email", values["email"],
        ]
        expected = {
            "vibe-coding": [f"--scenario={values['scenario']}", *identity,
                            f"--cloud={values['cloud']}", "-f"],
            "github-enterprise": [*identity, "-f"],
            "auto-research": identity[:-2] + ["-f"],
            "auto-research-ars": ["-f"],
            "tutor": ["--scenario", values["scenario"], "--force"],
            # The UI installer overwrites templates already and has no force flag.
            "ui-testing": [f"--scenario={values['scenario']}"],
            "fund-proposal": ["-f"],
            "unmapped-fixture": ["-f"],
        }
        target = Path("/fixtures/project with spaces")
        for name, flags in expected.items():
            with self.subTest(manifest=name):
                manifest = self._manifest(name)
                with patch("vibe_tool.manifest.subprocess.run") as run:
                    run.return_value.returncode = 0
                    with contextlib.redirect_stdout(io.StringIO()):
                        rc = _run_init_script(manifest, target, True, False, **values)
                self.assertEqual(rc, 0)
                run.assert_called_once()
                args, kwargs = run.call_args
                self.assertEqual(args, ([str(manifest.init_script_path), str(target), *flags],))
                self.assertEqual(kwargs["cwd"], str(target if target.is_dir() else Path.cwd()))
                self.assertEqual(kwargs["env"]["VIBE_MANIFEST"], str(manifest.path))
                self.assertFalse(kwargs.get("shell", False))

    def test_empty_values_and_disabled_force_are_omitted(self):
        manifest = self._manifest("tutor")
        target = Path("/fixtures/project")
        with patch("vibe_tool.manifest.subprocess.run") as run:
            run.return_value.returncode = 0
            with contextlib.redirect_stdout(io.StringIO()):
                rc = _run_init_script(manifest, target, False, False, scenario="", owner="")
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_args.args[0], [str(manifest.init_script_path), str(target)])

    def test_script_exit_status_is_propagated(self):
        with patch("vibe_tool.manifest.subprocess.run") as run:
            run.return_value.returncode = 17
            with contextlib.redirect_stdout(io.StringIO()):
                rc = _run_init_script(self._manifest("tutor"), Path("/tmp"), False, False)
        self.assertEqual(rc, 17)

    def test_dry_run_never_executes_scripts_without_a_native_preview(self):
        for name in ("github-enterprise", "auto-research-ars", "tutor", "ui-testing",
                     "fund-proposal", "unmapped-fixture"):
            with self.subTest(manifest=name):
                output = io.StringIO()
                with patch("vibe_tool.manifest.subprocess.run") as run:
                    with contextlib.redirect_stdout(output):
                        rc = _run_init_script(self._manifest(name), Path("/tmp/new project"),
                                              True, True, scenario="self-study")
                self.assertEqual(rc, 0)
                run.assert_not_called()
                self.assertIn("[dry-run]", output.getvalue())
                command = output.getvalue().splitlines()[0].split("Would run: ", 1)[1]
                scenario = (["--scenario", "self-study"] if name == "tutor" else
                            ["--scenario=self-study"] if name in ("vibe-coding", "ui-testing") else [])
                force = ([] if name == "ui-testing" else
                         ["--force"] if name == "tutor" else ["-f"])
                self.assertEqual(shlex.split(command),
                                 [str(self._manifest(name).init_script_path), "/tmp/new project",
                                  *scenario, *force, "-n"])

    def test_known_native_previews_receive_dry_run_flag(self):
        for name in ("vibe-coding", "auto-research", "office", "unity-game"):
            with self.subTest(manifest=name):
                target = Path("/fixtures/native preview project with spaces")
                with patch("vibe_tool.manifest.subprocess.run") as run:
                    run.return_value.returncode = 0
                    with contextlib.redirect_stdout(io.StringIO()):
                        rc = _run_init_script(self._manifest(name), target, False, True)
                self.assertEqual(rc, 0)
                run.assert_called_once()
                self.assertEqual(run.call_args.args[0],
                                 [str(self._manifest(name).init_script_path), str(target), "-n"])


class TutorInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="learning manifest tests ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def _cli(self, *args, expected=0):
        result = subprocess.run(
            [sys.executable, "-m", "vibe_tool", *map(str, args)],
            cwd=REPO_ROOT, env=_environment(), capture_output=True, text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def _script(self, *args):
        return subprocess.run(
            ["bash", str(SCRIPT), *map(str, args)], cwd=self.root,
            env=_environment(), capture_output=True, text=True, timeout=30,
        )

    def _assert_installed(self, target, scenario=None):
        for source, relative in _managed_files():
            with self.subTest(resource=str(relative)):
                destination = target / relative
                self.assertTrue(destination.is_file(), str(destination))
                self.assertEqual(destination.read_bytes(), source.read_bytes(), str(relative))
        for relative in ("materials/pdf", "materials/slides", "materials/video", "materials/web",
                         "materials/audio", "materials/images", "materials/exercises", "materials/epub",
                         "notes/atoms", "notes/summaries", "flashcards/decks", "flashcards/reviews", "projects"):
            self.assertTrue((target / relative).is_dir(), relative)
        self.assertTrue((target / "notes/_index.md").is_file())
        self.assertTrue((target / ".cursor/commands/learn/COMMAND.md").is_file())
        self.assertTrue((target / "skills/material-processor/SKILL.md").is_file())
        self.assertTrue((target / ".cursor/templates/LEARNING_PATH.md.example").is_file())
        self.assertTrue((target / "scripts/export-notes.py").is_file())
        if scenario:
            self.assertEqual((target / ".cursor/scenario.md").read_bytes(),
                             (MANIFEST / "scenarios" / scenario / "CLAUDE.md").read_bytes())
        else:
            self.assertFalse((target / ".cursor/scenario.md").exists())

    def test_cli_init_and_add_install_all_resources_in_paths_with_spaces(self):
        for operation in ("init", "add"):
            with self.subTest(operation=operation):
                target = self.root / f"{operation} project with spaces"
                if operation == "init":
                    self._cli("init", "tutor", target)
                else:
                    target.mkdir()
                    self._cli("add", "manifest", "tutor", target)
                self._assert_installed(target)

    def test_cli_init_installs_each_supported_scenario(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                target = self.root / f"{scenario} project"
                self._cli("init", "tutor", target, "--scenario", scenario)
                self._assert_installed(target, scenario)

    def test_shared_delegation_ui_force_keeps_the_requested_target(self):
        # Its shell parser treats unknown flags as a new target directory.
        target = self.root / "UI project with spaces"
        self._cli("init", "ui-testing", target, "--scenario", "web-e2e", "--force")
        self.assertTrue((target / ".cursor/rules/ui-testing-core.mdc").is_file())
        self.assertEqual((target / "CLAUDE.ui-testing.md").read_bytes(),
                         (REPO_ROOT / "manifests/ui-testing/scenarios/web-e2e/CLAUDE.md").read_bytes())
        self.assertFalse((target / "-f").exists())
        self.assertFalse((target / "--force").exists())

    def test_reinstall_preserves_edits_and_force_only_replaces_managed_files(self):
        target = self.root / "existing project"
        self._cli("init", "tutor", target, "--scenario", "self-study")
        managed = [relative for _, relative in _managed_files()] + [Path(".cursor/scenario.md")]
        for relative in managed:
            (target / relative).write_text(f"local edit: {relative}\n", encoding="utf-8")
        personal = [Path("MANIFEST.md"), Path("materials/pdf/my textbook.pdf"), Path("references/my notes.md"),
                    Path("skills/custom/SKILL.md"), Path(".cursor/commands/custom/COMMAND.md"),
                    Path(".cursor/templates/custom.md"), Path("projects/custom/LEARNING_PATH.md"),
                    Path("projects/custom/LEARNING_RECORD.md"),
                    Path("projects/custom/notes/chapter 1.md"),
                    Path("projects/custom/notes/chapter 1.pdf"),
                    Path("projects/custom/notes/assets/concept.svg"),
                    Path("notes/summaries/custom/U01-chapter.md"),
                    Path("notes/summaries/custom/U01-chapter.pdf"),
                    Path("notes/assets/custom/concept.svg"),
                    Path("scripts/my-helper.py"), Path("notes/_index.md")]
        for relative in personal:
            (target / relative).parent.mkdir(parents=True, exist_ok=True)
            (target / relative).write_text(f"keep personal data: {relative}\n", encoding="utf-8")
        expected = {relative: (target / relative).read_bytes() for relative in [*managed, *personal]}

        self._cli("add", "manifest", "tutor", target)
        for relative, content in expected.items():
            self.assertEqual((target / relative).read_bytes(), content, str(relative))

        self._cli("init", "tutor", target, "--scenario", "self-study", "--force")
        self._assert_installed(target, "self-study")
        for relative in personal:
            self.assertEqual((target / relative).read_bytes(), expected[relative], str(relative))

    def test_cli_add_force_replaces_managed_files_without_deleting_user_files(self):
        target = self.root / "add force project"
        target.mkdir()
        self._cli("add", "manifest", "tutor", target)
        (target / ".cursor/commands/learn/COMMAND.md").write_text("custom command\n", encoding="utf-8")
        personal = target / "materials/pdf/user.pdf"
        personal.write_bytes(b"user data")
        self._cli("add", "manifest", "tutor", target, "--force")
        self._assert_installed(target)
        self.assertEqual(personal.read_bytes(), b"user data")

    def test_force_replaces_file_links_without_modifying_the_original(self):
        for link_type in ("symbolic", "hard"):
            with self.subTest(link_type=link_type):
                target = self.root / f"{link_type} link project"
                target.mkdir()
                original = self.root / f"{link_type} original.txt"
                original.write_bytes(b"personal file outside the installation target\n")
                original_stat = original.stat()
                destination = target / "README.md"
                if link_type == "symbolic":
                    destination.symlink_to(original)
                else:
                    os.link(original, destination)

                self._cli("add", "manifest", "tutor", target, "--force")

                self._assert_installed(target)
                self.assertFalse(destination.is_symlink())
                self.assertNotEqual(destination.stat().st_ino, original.stat().st_ino)
                self.assertEqual(original.read_bytes(), b"personal file outside the installation target\n")
                self.assertEqual(original.stat().st_ino, original_stat.st_ino)
                self.assertEqual(original.stat().st_mtime_ns, original_stat.st_mtime_ns)
                self.assertEqual(original.stat().st_mode, original_stat.st_mode)

    def test_force_rejects_file_destination_directory_without_changing_its_contents(self):
        target = self.root / "directory conflict project"
        conflict = target / "README.md"
        conflict.mkdir(parents=True)
        (conflict / "README.md").write_bytes(b"personal nested README that cp must not overwrite\n")
        (conflict / "other.txt").write_bytes(b"keep this too\n")
        before = _snapshot(conflict)

        result = self._script(target, "--force")

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(conflict.is_dir())
        self.assertEqual(_snapshot(conflict), before)

    def test_install_rejects_linked_parent_directories_before_external_writes(self):
        # Include both copied resources and folders created by initial scaffolding.
        for relative in ("references", ".cursor/commands", "skills/material-processor",
                         "materials/pdf", "notes", "scripts"):
            for force in (False, True):
                with self.subTest(relative=relative, force=force):
                    case = self.root / f"parent link {relative.replace('/', '-')} {force}"
                    target = case / "project"
                    external = case / "external personal directory"
                    target.mkdir(parents=True)
                    external.mkdir()
                    (external / "personal.txt").write_bytes(b"keep external data\n")
                    destination = target / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.symlink_to(external, target_is_directory=True)
                    before = _snapshot(external)
                    arguments = [target, "--force"] if force else [target]

                    result = self._script(*arguments)

                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertTrue(destination.is_symlink())
                    self.assertEqual(_snapshot(external), before)

    def test_cli_dry_run_does_not_create_target_or_mutate_existing_project(self):
        missing = self.root / "new dry run project"
        self._cli("init", "tutor", missing, "--scenario", "exam-prep", "--dry-run")
        self.assertFalse(missing.exists())
        target = self.root / "existing dry run project"
        self._cli("init", "tutor", target)
        before = _snapshot(target)
        self._cli("init", "tutor", target, "--force", "--dry-run")
        self.assertEqual(_snapshot(target), before)
        self._cli("add", "manifest", "tutor", target, "--force", "--dry-run")
        self.assertEqual(_snapshot(target), before)

    def test_script_accepts_options_before_and_after_target_and_equals_scenario(self):
        arrangements = (
            lambda target: [target, "--scenario", "self-study", "--force"],
            lambda target: ["--scenario", "exam-prep", target, "--force"],
            lambda target: [target, "--force", "--scenario=course-learning"],
            lambda target: ["--force", "--scenario=research-reading", target],
        )
        for index, (arguments, scenario) in enumerate(zip(arrangements, SCENARIOS)):
            with self.subTest(scenario=scenario):
                target = self.root / f"argument order {index}"
                result = self._script(*arguments(target))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self._assert_installed(target, scenario)

    def test_script_rejects_invalid_options_and_scenarios_before_any_write(self):
        bad_arguments = (
            ["--scenario"], ["--scenario", "--force"], ["--scenario="],
            ["--scenario", "not-a-scenario"], ["--scenario=../self-study"],
            ["--unknown-option"], ["--strict"], ["--notebooklm"], ["extra target"],
        )
        for index, flags in enumerate(bad_arguments):
            with self.subTest(flags=flags):
                target = self.root / f"invalid target {index}"
                result = self._script(target, *flags)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(target.exists(), result.stdout + result.stderr)
        existing = self.root / "existing invalid target"
        existing.mkdir()
        (existing / "personal.txt").write_text("keep this", encoding="utf-8")
        before = _snapshot(existing)
        result = self._script(existing, "--force", "--scenario", "invalid")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(_snapshot(existing), before)

    def test_script_help_is_read_only_and_omits_removed_mode_switches(self):
        result = self._script("--help")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("--scenario", result.stdout)
        self.assertNotIn("--strict", result.stdout)
        self.assertNotIn("--notebooklm", result.stdout)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_cli_invalid_scenario_does_not_install_files(self):
        target = self.root / "invalid CLI scenario"
        result = subprocess.run(
            [sys.executable, "-m", "vibe_tool", "init", "tutor", str(target),
             "--scenario", "not-a-scenario"],
            cwd=REPO_ROOT, env=_environment(), capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(list(target.rglob("*")), [])

    def test_plan_is_an_assistant_command_not_a_vibe_cli_flag(self):
        target = self.root / "not a CLI plan"
        self._cli("init", "tutor", target, "--plan", expected=2)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
