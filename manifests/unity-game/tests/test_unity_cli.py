"""Fake Editor integration and pure-unit checks; no Unity license/installation needed.

Run: python3 -m unittest discover -s manifests/unity-game/tests -p test_unity_cli.py -v
"""
import contextlib
import importlib.util
import io
import hashlib
import json
import os
from pathlib import Path
import plistlib
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("unity_game_cli", ROOT / "scripts/unity_cli.py")
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)

VERSION = "6000.0.23f1"
FAKE_EDITOR = r'''
import json
import os
from pathlib import Path
import sys
import time
args = sys.argv[1:]
if "-version" in args:
    print(os.environ.get("FAKE_VERSION", "6000.0.23f1"))
    sys.exit(int(os.environ.get("FAKE_VERSION_EXIT", "0")))
def value(flag):
    return args[args.index(flag) + 1]
behavior = os.environ.get("FAKE_BEHAVIOR", "success")
if behavior == "changed_input":
    (Path(value("-projectPath")) / "Assets/Gameplay.cs").write_text("// changed during run")
if behavior == "missing_log":
    Path(value("-logFile")).unlink()
elif behavior != "no_log":
    Path(value("-logFile")).write_text("Fake Editor log\n", encoding="utf-8")
print(json.dumps(args))
print("Fake stderr", file=sys.stderr)
if behavior == "timeout":
    time.sleep(10)
if "-runTests" in args and behavior != "missing":
    xml = '<test-run total="1" passed="1" failed="0" skipped="0" result="Passed"><test-case result="Passed" /></test-run>'
    if behavior == "failed_tests":
        xml = '<test-run total="1" passed="0" failed="1" result="Failed"><test-case result="Failed" /></test-run>'
    elif behavior == "failed_xml_exit":
        xml = '<test-run total="1" passed="0" failed="1" result="Failed"><test-case result="Failed" /></test-run>'
    elif behavior == "zero":
        xml = '<test-run total="0" passed="0" failed="0" result="Passed" />'
    elif behavior == "malformed":
        xml = '<test-run'
    elif behavior == "skipped":
        xml = '<test-run total="1" passed="0" failed="0" skipped="1" result="Skipped"><test-case result="Skipped" /></test-run>'
    Path(value("-testResults")).write_text(xml, encoding="utf-8")
if "-buildOutput" in args and behavior != "missing":
    output = Path(value("-buildOutput"))
    if value("-buildTarget") == "WebGL":
        output.mkdir()
        (output / "index.html").write_text("<html>fake build</html>", encoding="utf-8")
        (output / "Build").mkdir()
        for name in ("game.loader.js", "game.wasm", "game.data"):
            (output / "Build" / name).write_bytes(b"fixture")
        files = list(output.rglob("*"))
    else:
        output.write_bytes(b"" if behavior == "empty" else b"random text" if behavior == "random_file" else b"\x7fELFfake game fixture")
        files = [output]
        if behavior not in ("empty", "random_file", "no_data"):
            data = output.with_name(output.stem + "_Data")
            data.mkdir()
            (data / "globalgamemanagers").write_bytes(b"fixture data")
            files += list(data.rglob("*"))
    if behavior.startswith("report_"):
        import hashlib
        report = {"schema_version": 1, "result": "Succeeded", "target": "StandaloneLinux64",
                  "output": str(output), "errors": 0, "scenes": ["Assets/Main.unity"],
                  "files": [{"path": str(p), "bytes": p.stat().st_size,
                             "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file()]}
        if behavior == "report_wrong_target": report["target"] = "Android"
        if behavior == "report_wrong_output": report["output"] = str(output.parent / "other")
        if behavior == "report_failed": report["result"] = "Failed"
        if behavior == "report_errors": report["errors"] = 1
        if behavior == "report_missing_scenes": report["scenes"] = []
        if behavior == "report_bad_hash": report["files"][0]["sha256"] = "0" * 64
        if behavior == "report_bad_bytes_type": report["files"][0]["bytes"] = float(report["files"][0]["bytes"])
        if behavior == "report_missing_file": report["files"].pop()
        if behavior == "report_bad_schema": report["schema_version"] = 2
        Path(value("-buildReport")).write_text(json.dumps(report))
sys.exit(3 if behavior in ("exit_failure", "failed_xml_exit") else 0)
'''


@unittest.skipIf(os.name == "nt", "POSIX executable fake Editor fixture; parser/unit tests remain portable")
class EditorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="unity helper test ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "Game with spaces"
        for folder in ("Assets", "ProjectSettings", "Packages"):
            (self.project / folder).mkdir(parents=True)
        (self.project / "ProjectSettings/ProjectVersion.txt").write_text(f"m_EditorVersion: {VERSION}\n", encoding="utf-8")
        self.manifest = self.project / "Packages/manifest.json"
        self.manifest.write_text(json.dumps({"dependencies": {"com.unity.test-framework": "1.4.6"}}), encoding="utf-8")
        (self.project / "Assets/Gameplay.cs").write_text("// original gameplay")
        (self.project / "Packages/packages-lock.json").write_text('{"dependencies": {}}')
        self.editor = self.root / "Hub" / VERSION / "Editor/Unity"
        self.editor.parent.mkdir(parents=True)
        self.editor.write_text("#!" + sys.executable + "\n" + FAKE_EDITOR, encoding="utf-8")
        self.editor.chmod(self.editor.stat().st_mode | stat.S_IXUSR)
        (self.editor.parent / "Data/PlaybackEngines/LinuxStandaloneSupport").mkdir(parents=True)
        self.env = mock.patch.dict(os.environ, {"FAKE_BEHAVIOR": "success", "FAKE_VERSION": VERSION,
                                               "FAKE_VERSION_EXIT": "0", "UNITY_EDITOR": str(self.editor)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def run_helper(self, operation="test", *extra, behavior="success", explicit=True):
        argv = [operation, "--project", str(self.project), "--timeout", "5"]
        if explicit:
            argv += ["--editor", str(self.editor)]
        if operation == "test":
            argv += ["--mode", "editmode"]
        elif operation == "build":
            argv += ["--target", "StandaloneLinux64", "--execute-method", "UnityGameBuild.Build", "--output", "Builds/game"]
        argv += list(extra)
        with mock.patch.dict(os.environ, {"FAKE_BEHAVIOR": behavior}):
            result = cli.execute(cli.parser().parse_args(argv))
        if "run_dir" in result:
            run = Path(result["run_dir"])
            self.assertEqual(result, json.loads((run / "result.json").read_text(encoding="utf-8")))
            for name in ("stdout.txt", "stderr.txt"):
                self.assertTrue((run / name).exists())
            if behavior != "missing_log":
                self.assertTrue((run / "editor.log").exists())
        self.assertFalse((self.project / ".unity-game/editor-helper.lock").exists())
        return result

    def test_doctor_validates_editor_version_and_dependencies(self):
        result = self.run_helper("doctor")
        self.assertEqual("passed", result["status"])
        self.assertEqual(VERSION, result["project_version"])
        self.assertEqual("1.4.6", result["test_framework"])
        self.assertEqual(0, result["version_probe"]["exit_code"])
        self.assertTrue(result["modules"]["StandaloneLinux64"])
        self.assertEqual([], result["command"])

    def test_editmode_pass_records_literal_command_and_output(self):
        result = self.run_helper()
        self.assertEqual("passed", result["status"])
        self.assertEqual(0, result["exit_code"])
        command = result["command"]
        self.assertEqual(str(self.editor), command[0])
        self.assertEqual(str(self.project), command[command.index("-projectPath") + 1])
        self.assertEqual("EditMode", command[command.index("-testPlatform") + 1])
        self.assertNotIn("-quit", command)
        run = Path(result["run_dir"])
        self.assertEqual("Fake Editor log\n", (run / "editor.log").read_text())
        self.assertEqual("Fake stderr\n", (run / "stderr.txt").read_text())
        self.assertEqual(command[1:], json.loads((run / "stdout.txt").read_text()))
        self.assertEqual(1, result["tests"]["passed"])

    def test_playmode_uses_test_runner_platform(self):
        result = self.run_helper("test", "--mode", "playmode")
        command = result["command"]
        self.assertEqual("PlayMode", command[command.index("-testPlatform") + 1])

    def test_failure_results_are_not_success(self):
        for behavior, reason in (("failed_tests", "tests_not_passed"), ("zero", "zero_tests"),
                                 ("skipped", "tests_not_passed"), ("missing", "missing_test_results"),
                                 ("malformed", "malformed_test_results"), ("exit_failure", "editor_failed")):
            with self.subTest(behavior=behavior):
                result = self.run_helper(behavior=behavior)
                self.assertEqual("failed", result["status"])
                self.assertEqual(reason, result["reason"])

    def test_nonzero_exit_keeps_xml_evidence_and_exit_status(self):
        result = self.run_helper(behavior="failed_xml_exit")
        self.assertEqual("failed", result["status"])
        self.assertEqual("editor_failed", result["reason"])
        self.assertEqual(3, result["exit_code"])
        self.assertEqual(1, result["tests"]["failed"])

    def test_symlinked_run_root_does_not_write_outside_project(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.project / ".unity-game").symlink_to(outside, target_is_directory=True)
        result = self.run_helper("doctor")
        self.assertEqual("symlinked_run_root", result["reason"])
        self.assertEqual([], list(outside.iterdir()))

    def test_invalid_project_version_is_not_run(self):
        (self.project / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: unknown")
        result = self.run_helper("doctor")
        self.assertEqual("not_run", result["status"])
        self.assertEqual("invalid_project_version", result["reason"])

    def test_timeout_stops_editor_and_records_failure(self):
        result = self.run_helper("test", "--timeout", "0.2", behavior="timeout")
        self.assertEqual("failed", result["status"])
        self.assertEqual("timeout", result["reason"])
        self.assertTrue(result["timed_out"])
        self.assertIsInstance(result["exit_code"], int)

    def test_missing_framework_stops_before_editor_project_open(self):
        self.manifest.write_text('{"dependencies": {}}')
        result = self.run_helper()
        self.assertEqual("not_run", result["status"])
        self.assertEqual("missing_test_framework", result["reason"])
        self.assertEqual([], result["command"])

    def test_bad_package_manifest_is_reported(self):
        self.manifest.write_text('{"dependencies": []}')
        result = self.run_helper()
        self.assertEqual("invalid_package_manifest", result["reason"])
        self.assertEqual("not_run", result["status"])

    def test_missing_editor_preserves_not_run(self):
        result = self.run_helper("doctor", "--editor", str(self.root / "missing"))
        self.assertEqual("missing_editor", result["reason"])
        self.assertEqual("not_run", result["status"])

    def test_environment_editor_is_used(self):
        result = self.run_helper("doctor", explicit=False)
        self.assertEqual(str(self.editor), result["editor"])
        self.assertEqual("passed", result["status"])

    def test_explicit_editor_overrides_environment(self):
        with mock.patch.dict(os.environ, {"UNITY_EDITOR": str(self.root / "missing")}):
            result = self.run_helper("doctor")
        self.assertEqual("passed", result["status"])

    def test_version_mismatch_never_opens_project(self):
        with mock.patch.dict(os.environ, {"FAKE_VERSION": "6000.0.24f1"}):
            result = self.run_helper()
        self.assertEqual("not_run", result["status"])
        self.assertEqual("editor_version_mismatch", result["reason"])
        self.assertEqual([], result["command"])
        self.assertTrue((Path(result["run_dir"]) / "version-probe.json").exists())

    def test_failed_version_probe_never_opens_project(self):
        with mock.patch.dict(os.environ, {"FAKE_VERSION_EXIT": "9"}):
            result = self.run_helper("doctor")
        self.assertEqual("editor_version_unverified", result["reason"])
        self.assertEqual("not_run", result["status"])

    def test_ambiguous_discovery_requests_explicit_path(self):
        with mock.patch.dict(os.environ, {"UNITY_EDITOR": ""}), mock.patch.object(cli, "discover_editors", return_value=[self.editor, self.root / "other"]):
            result = self.run_helper("doctor", explicit=False)
        self.assertEqual("ambiguous_editor", result["reason"])

    def test_matching_discovery_is_used(self):
        with mock.patch.dict(os.environ, {"UNITY_EDITOR": ""}), mock.patch.object(cli, "discover_editors", return_value=[self.editor]):
            result = self.run_helper("doctor", explicit=False)
        self.assertEqual("passed", result["status"])

    def test_open_project_lock_is_respected(self):
        (self.project / "Temp").mkdir()
        (self.project / "Temp/UnityLockfile").touch()
        result = self.run_helper()
        self.assertEqual("project_open", result["reason"])
        self.assertTrue((self.project / "Temp/UnityLockfile").exists())
        self.assertEqual([], result["command"])

    def test_helper_lock_is_never_deleted_by_other_call(self):
        lock = self.project / ".unity-game/editor-helper.lock"
        lock.parent.mkdir()
        lock.write_text('{"pid": 12345}')
        args = cli.parser().parse_args(["test", "--project", str(self.project), "--mode", "editmode"])
        result = cli.execute(args)
        self.assertEqual("helper_busy", result["reason"])
        self.assertEqual('{"pid": 12345}', lock.read_text())

    def test_each_call_gets_distinct_audit_directory(self):
        first, second = self.run_helper(), self.run_helper()
        self.assertNotEqual(first["run_dir"], second["run_dir"])
        self.assertTrue((Path(first["run_dir"]) / "result.json").is_file())

    def test_build_records_target_method_and_verifies_output(self):
        result = self.run_helper("build")
        self.assertEqual("passed", result["status"])
        command = result["command"]
        self.assertEqual("Linux64", command[command.index("-buildTarget") + 1])
        self.assertEqual("UnityGameBuild.Build", command[command.index("-executeMethod") + 1])
        self.assertEqual(str(self.project / "Builds/game"), command[command.index("-buildOutput") + 1])
        self.assertEqual(2, result["artifacts"]["files"])
        self.assertGreater(result["artifacts"]["bytes"], 0)
        self.assertEqual("structure_verified", result["artifacts"]["format_status"])
        self.assertEqual("not_run", result["artifacts"]["runtime_status"])
        self.assertEqual("not_provided", result["artifacts"]["build_report_status"])

    def test_build_accepts_directory_artifact(self):
        (self.editor.parent / "Data/PlaybackEngines/WebGLSupport").mkdir()
        result = self.run_helper("build", "--target", "WebGL", behavior="directory")
        self.assertEqual("passed", result["status"])
        self.assertEqual(4, result["artifacts"]["files"])

    def test_run_binds_inputs_and_hashes_logs_xml_and_bundle(self):
        for operation in ("test", "build"):
            with self.subTest(operation=operation):
                result = self.run_helper(operation)
                provenance = result["input_provenance"]
                self.assertTrue(provenance["unchanged"])
                self.assertEqual([], provenance["changed_paths"])
                self.assertEqual(provenance["before"]["sha256"], provenance["after"]["sha256"])
                before = json.loads(Path(provenance["before"]["manifest"]).read_text())
                for path in ("Assets/Gameplay.cs", "Packages/manifest.json", "Packages/packages-lock.json", "ProjectSettings/ProjectVersion.txt"):
                    self.assertEqual(cli.digest(self.project / path), before["files"][path])
                self.assertFalse(any(path.startswith(".unity-game/") or path.startswith("Builds/") for path in before["files"]))
                evidence = {Path(entry["path"]).name: entry for entry in result["evidence_files"]}
                for name in ("stdout.txt", "stderr.txt", "editor.log", "inputs-before.json", "inputs-after.json"):
                    self.assertEqual(cli.digest(Path(result["run_dir"]) / name), evidence[name]["sha256"])
                if operation == "test":
                    self.assertIn("results.xml", evidence)
                else:
                    self.assertTrue(all(entry["sha256"] == cli.digest(Path(entry["path"])) for entry in result["artifacts"]["manifest"]))

    def test_changes_during_run_invalidate_success(self):
        for operation in ("test", "build"):
            with self.subTest(operation=operation):
                (self.project / "Assets/Gameplay.cs").write_text("// original gameplay")
                result = self.run_helper(operation, behavior="changed_input")
                self.assertEqual("failed", result["status"])
                self.assertEqual("project_inputs_changed", result["reason"])
                self.assertFalse(result["input_provenance"]["unchanged"])
                self.assertIn("Assets/Gameplay.cs", result["input_provenance"]["changed_paths"])

    def test_random_text_or_missing_player_data_is_not_a_build(self):
        for behavior in ("random_file", "no_data"):
            with self.subTest(behavior=behavior):
                result = self.run_helper("build", "--output", "Builds/" + behavior, behavior=behavior)
                self.assertEqual("failed", result["status"])
                self.assertEqual("build_structure_mismatch", result["reason"])

    def test_build_report_is_bound_to_platform_output_and_hashes(self):
        good = self.run_helper("build", "--output", "Builds/report-ok", behavior="report_success")
        self.assertEqual("passed", good["status"])
        self.assertEqual("verified", good["artifacts"]["build_report_status"])
        self.assertIn("build-result.json", {Path(r["path"]).name for r in good["evidence_files"]})
        for behavior in ("report_wrong_target", "report_wrong_output", "report_failed", "report_errors", "report_missing_scenes", "report_bad_hash", "report_bad_bytes_type", "report_missing_file", "report_bad_schema"):
            with self.subTest(behavior=behavior):
                result = self.run_helper("build", "--output", "Builds/" + behavior, behavior=behavior)
                self.assertEqual("failed", result["status"])
                self.assertIn(result["reason"], ("build_report_mismatch", "build_report_manifest_mismatch", "build_report_missing_scenes", "invalid_build_report_schema"))

    def test_nonempty_editor_log_is_required_without_discarding_evidence(self):
        for operation in ("test", "build"):
            for behavior in ("no_log", "missing_log"):
                with self.subTest(operation=operation, behavior=behavior):
                    extras = ("--output", f"Builds/{behavior}") if operation == "build" else ()
                    result = self.run_helper(operation, *extras, behavior=behavior)
                    self.assertEqual("failed", result["status"])
                    self.assertEqual("missing_or_empty_editor_log", result["reason"])
                    self.assertEqual(0, result["exit_code"])
                    if operation == "test":
                        self.assertEqual("passed", result["tests"]["status"])
                        self.assertTrue((Path(result["run_dir"]) / "results.xml").is_file())
                    else:
                        self.assertTrue(result["artifacts"]["nonempty"])
                        self.assertTrue(Path(result["output"]).is_file())

    def test_symlinked_resource_roots_are_protected_build_destinations(self):
        for name in ("Assets", "Packages"):
            outside = self.root / f"shared-{name.lower()}"
            original = self.project / name
            original.rename(outside)
            original.symlink_to(outside, target_is_directory=True)
            for output in (f"{name}/release", str(outside / "release")):
                with self.subTest(resource=name, output=output):
                    result = self.run_helper("build", "--output", output)
                    self.assertEqual("not_run", result["status"])
                    self.assertEqual("invalid_build_output", result["reason"])
                    self.assertEqual([], result["command"])
                    self.assertFalse((outside / "release").exists())

    def test_build_needs_actual_nonempty_output(self):
        for behavior in ("missing", "empty"):
            with self.subTest(behavior=behavior):
                result = self.run_helper("build", "--output", f"Builds/{behavior}", behavior=behavior)
                self.assertEqual("failed", result["status"])
                self.assertEqual("missing_or_empty_build_artifact", result["reason"])

    def test_build_preserves_existing_artifact(self):
        existing = self.project / "Builds/game"
        existing.parent.mkdir()
        existing.write_bytes(b"previous release")
        result = self.run_helper("build")
        self.assertEqual("build_output_exists", result["reason"])
        self.assertEqual("not_run", result["status"])
        self.assertEqual(b"previous release", existing.read_bytes())

    def test_build_preserves_existing_player_companions(self):
        data = self.project / "Builds/game_Data"
        data.mkdir(parents=True)
        (data / "boot.config").write_text("previous build")
        result = self.run_helper("build")
        self.assertEqual("not_run", result["status"])
        self.assertEqual("build_output_exists", result["reason"])
        self.assertEqual("previous build", (data / "boot.config").read_text())

    def test_build_preserves_shared_player_libraries_and_mono_directory(self):
        for companion in ("UnityPlayer.dll", "UnityPlayer.so", "GameAssembly.dll", "GameAssembly.so", "UnityCrashHandler64.exe", "baselib.dll", "WinPixEventRuntime.dll", "MonoBleedingEdge", "D3D12"):
            with self.subTest(companion=companion):
                output = self.project / "Builds" / companion / "game"
                output.parent.mkdir(parents=True)
                existing = output.parent / companion
                if companion in ("MonoBleedingEdge", "D3D12"):
                    existing.mkdir()
                    sentinel = existing / "original.bin"
                else:
                    sentinel = existing
                sentinel.write_bytes(b"previous build must survive")
                result = self.run_helper("build", "--output", str(output))
                self.assertEqual("not_run", result["status"])
                self.assertEqual("build_output_exists", result["reason"])
                self.assertEqual([], result["command"])
                self.assertEqual(b"previous build must survive", sentinel.read_bytes())

    def test_mono_and_shared_libraries_are_bound_in_bundle_hashes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            player = root / "game"
            player.write_bytes(b"\x7fELFfixture")
            for name in ("game_Data", "MonoBleedingEdge"):
                (root / name).mkdir()
                (root / name / "fixture.bin").write_bytes(b"fixture")
            (root / "UnityPlayer.so").write_bytes(b"fixture")
            artifacts = cli.build_artifacts(player, "StandaloneLinux64")
            self.assertEqual(4, artifacts["files"])
            paths = {entry["path"] for entry in artifacts["manifest"]}
            self.assertIn(str(root / "MonoBleedingEdge/fixture.bin"), paths)
            self.assertIn(str(root / "UnityPlayer.so"), paths)

    def test_build_does_not_target_game_resources_or_parent(self):
        for output in ("Assets/build", "Packages/build", "ProjectSettings/build", ".unity-game/build", str(self.root)):
            with self.subTest(output=output):
                result = self.run_helper("build", "--output", output)
                self.assertEqual("not_run", result["status"])
                self.assertIn(result["reason"], ("invalid_build_output", "build_output_exists"))

    def test_missing_module_is_not_run(self):
        result = self.run_helper("build", "--target", "WebGL")
        self.assertEqual("missing_platform_module", result["reason"])
        self.assertEqual("not_run", result["status"])
        self.assertEqual([], result["command"])

    def test_build_invalid_target_and_method(self):
        result = self.run_helper("build", "--target", "ImaginaryPlatform")
        self.assertEqual("unsupported_target", result["reason"])
        result = self.run_helper("build", "--execute-method", "NotQualified")
        self.assertEqual("invalid_build_method", result["reason"])

    def test_main_prints_json_and_meaningful_exit_codes(self):
        command = [sys.executable, str(ROOT / "scripts/unity_cli.py"), "test", "--project", str(self.project), "--mode", "editmode", "--editor", str(self.editor)]
        for behavior, expected in (("success", 0), ("failed_tests", 1)):
            with mock.patch.dict(os.environ, {"FAKE_BEHAVIOR": behavior}):
                completed = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(expected, completed.returncode, completed.stderr)
            self.assertEqual(expected, {"passed": 0, "failed": 1}[json.loads(completed.stdout)["status"]])
        completed = subprocess.run(command + ["--editor", str(self.root / "missing")], capture_output=True, text=True, check=False)
        self.assertEqual(2, completed.returncode)
        self.assertEqual("not_run", json.loads(completed.stdout)["status"])


class PortableUnitTests(unittest.TestCase):
    def test_source_snapshot_tracks_relevant_inputs_not_generated_folders(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ("Assets", "Packages", "ProjectSettings", "Library", "Temp", "Builds", ".unity-game/runs"):
                (root / name).mkdir(parents=True)
                (root / name / "fixture.txt").write_text("original")
            before = cli.input_snapshot(root)
            for name in ("Library", "Temp", "Builds", ".unity-game/runs"):
                (root / name / "fixture.txt").write_text("generated")
            self.assertEqual([], cli.source_changes(before, cli.input_snapshot(root)))
            (root / "Packages/fixture.txt").write_text("changed lock/package")
            (root / "Assets/fixture.txt").unlink()
            self.assertEqual(["Assets/fixture.txt", "Packages/fixture.txt"], cli.source_changes(before, cli.input_snapshot(root)))

    def test_optional_git_revision_and_dirty_diff_are_bound_to_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ("Assets", "Packages", "ProjectSettings"):
                (root / name).mkdir()
            first_head = subprocess.CompletedProcess([], 0, b"a" * 40 + b"\n", b"")
            next_head = subprocess.CompletedProcess([], 0, b"b" * 40 + b"\n", b"")
            diff = subprocess.CompletedProcess([], 0, b"dirty fixture diff", b"")
            with mock.patch.object(cli.subprocess, "run", side_effect=[first_head, diff, next_head, diff]):
                before, after = cli.input_snapshot(root), cli.input_snapshot(root)
            self.assertEqual("a" * 40, before["git"]["head"])
            self.assertEqual(hashlib.sha256(diff.stdout).hexdigest(), before["git"]["dirty_diff_sha256"])
            self.assertNotEqual(before["sha256"], after["sha256"])
            self.assertEqual(["<git-revision-or-diff>"], cli.source_changes(before, after))

    def test_target_specific_artifact_profiles(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixtures = []
            for target, filename, header in (("StandaloneWindows", "game32.exe", b"MZ"), ("StandaloneWindows64", "game.exe", b"MZ"), ("StandaloneLinux64", "game", b"\x7fELF")):
                path = root / filename
                path.write_bytes(header + b"fixture")
                data = path.with_name(path.stem + "_Data")
                data.mkdir(exist_ok=True)
                (data / "boot.config").write_text("fixture")
                fixtures.append((target, path))
            mac = root / "Game.app"
            (mac / "Contents/MacOS").mkdir(parents=True)
            (mac / "Contents/Resources/Data").mkdir(parents=True)
            (mac / "Contents/Info.plist").write_bytes(plistlib.dumps({"CFBundleExecutable": "Game"}))
            (mac / "Contents/MacOS/Game").write_bytes(b"\xcf\xfa\xed\xfe" + b"fixture")
            (mac / "Contents/Resources/Data/boot.config").write_text("fixture")
            fixtures.append(("StandaloneOSX", mac))
            for extension, required in (("apk", ("AndroidManifest.xml", "classes.dex")), ("aab", ("base/manifest/AndroidManifest.xml", "BundleConfig.pb"))):
                package = root / ("game." + extension)
                with zipfile.ZipFile(package, "w") as archive:
                    for name in required:
                        archive.writestr(name, b"fixture")
                fixtures.append(("Android", package))
            web = root / "web"
            (web / "Build").mkdir(parents=True)
            for name in ("index.html", "Build/g.loader.js", "Build/g.wasm.br", "Build/g.data.gz"):
                (web / name).write_text("fixture")
            fixtures.append(("WebGL", web))
            ios = root / "ios"
            for name in ("Unity-iPhone.xcodeproj", "Classes", "Data"):
                (ios / name).mkdir(parents=True)
            for name in ("Unity-iPhone.xcodeproj/project.pbxproj", "Classes/main.mm", "Data/globalgamemanagers"):
                (ios / name).write_text("fixture")
            fixtures.append(("iOS", ios))
            for target, path in fixtures:
                with self.subTest(target=target, path=path):
                    artifacts = cli.build_artifacts(path, target)
                    cli.validate_build(path, target, artifacts, root / "no-report.json")
                    self.assertEqual("structure_verified", artifacts["format_status"])
                    self.assertEqual("not_run", artifacts["runtime_status"])
                    self.assertEqual(artifacts["files"], len(artifacts["manifest"]))
            junk = root / "random.txt"
            junk.write_text("not a game")
            for target in cli.TARGETS:
                with self.subTest(reject=target), self.assertRaisesRegex(ValueError, "build_structure_mismatch"):
                    cli.validate_build(junk, target, cli.build_artifacts(junk, target), root / "no-report.json")

    def test_symlinked_bundle_files_are_not_counted_as_local_artifacts(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "link"
            target = Path(folder) / "outside"
            target.write_bytes(b"fixture")
            try:
                path.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("Host does not support symlinks")
            with self.assertRaisesRegex(ValueError, "symlinked_build_artifact"):
                cli.build_artifacts(path)

    def test_nunit2_result_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "result.xml"
            path.write_text('<test-results total="2" failures="0" errors="0" not-run="0"><test-suite success="True"><test-case success="True"/><test-case result="Success"/></test-suite></test-results>')
            result = cli.test_summary(path)
        self.assertEqual("passed", result["status"])
        self.assertEqual(2, result["passed"])

    def test_failure_in_cases_overrules_root_success(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "result.xml"
            path.write_text('<test-run total="1" passed="1" result="Passed"><test-case result="Failed"/></test-run>')
            self.assertEqual("failed", cli.test_summary(path)["status"])

    def test_invalid_xml_and_counts_are_rejected(self):
        for xml in ('<random total="1"/>', '<test-run total="bad"/>', '<test-run total="-1"/>', '<test-run total="1" passed="2"/>', '<test-run/>', '<test-run total="1" passed="1"/>', '<test-run total="2" passed="2"><test-case result="Passed"/></test-run>', '<test-run total="2" passed="1"><test-case result="Passed"/><test-case result="Passed"/></test-run>'):
            with self.subTest(xml=xml), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "result.xml"
                path.write_text(xml)
                with self.assertRaisesRegex(ValueError, "malformed_test_results"):
                    cli.test_summary(path)

    def test_missing_xml_has_distinct_reason(self):
        with self.assertRaisesRegex(ValueError, "missing_test_results"):
            cli.test_summary(Path("/path/does/not/exist/results.xml"))

    def test_targets_accept_native_and_cli_names(self):
        self.assertEqual("StandaloneLinux64", cli.canonical_target("Linux64"))
        self.assertEqual("StandaloneWindows64", cli.canonical_target("win64"))
        self.assertEqual("StandaloneOSX", cli.canonical_target("StandaloneOSX"))

    def test_missing_project_does_not_create_project(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "missing"
            result = cli.execute(cli.parser().parse_args(["doctor", "--project", str(project)]))
            self.assertEqual("not_run", result["status"])
            self.assertEqual("missing_project", result["reason"])
            self.assertFalse(project.exists())

    def test_regular_file_run_roots_return_structured_errors(self):
        for component in (".unity-game", ".unity-game/runs"):
            with self.subTest(component=component), tempfile.TemporaryDirectory() as folder:
                project = Path(folder)
                path = project / component
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("preserve me", encoding="utf-8")
                result = cli.execute(cli.parser().parse_args(["doctor", "--project", str(project)]))
                self.assertEqual("failed", result["status"])
                self.assertEqual("helper_error", result["reason"])
                self.assertNotIn("run_dir", result)
                self.assertEqual("preserve me", path.read_text(encoding="utf-8"))

    def test_run_root_permission_error_returns_structured_error(self):
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(Path, "mkdir", side_effect=PermissionError("permission denied")):
            result = cli.execute(cli.parser().parse_args(["doctor", "--project", folder]))
        self.assertEqual("failed", result["status"])
        self.assertEqual("helper_error", result["reason"])
        self.assertNotIn("run_dir", result)

    def test_invalid_timeout_is_rejected(self):
        for timeout in ("0", "-1", "nan", "inf"):
            with self.subTest(timeout=timeout), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    cli.main(["doctor", "--project", ".", "--timeout", timeout])
                self.assertEqual(2, raised.exception.code)

    def test_discovery_uses_matching_hub_version_only(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            matching = home / f"Unity/Hub/Editor/{VERSION}/Editor/Unity"
            matching.parent.mkdir(parents=True)
            matching.touch()
            newer = home / "Unity/Hub/Editor/6000.0.99f1/Editor/Unity"
            newer.parent.mkdir(parents=True)
            newer.touch()
            with mock.patch.object(Path, "home", return_value=home):
                self.assertIn(matching, cli.discover_editors(VERSION))
                self.assertNotIn(newer, cli.discover_editors(VERSION))


if __name__ == "__main__":
    unittest.main()
