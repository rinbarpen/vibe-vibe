#!/usr/bin/env python3
"""Auditable, stdlib-only Unity Editor runner. No Editor installation or project creation.

Usage (options follow the subcommand):
  python .unity-game/scripts/unity_cli.py doctor --project . --editor /path/to/Unity
  python .unity-game/scripts/unity_cli.py test --project . --mode editmode
  python .unity-game/scripts/unity_cli.py build --project . --target WebGL \
      --execute-method UnityGameBuild.Build --output Builds/webgl-001

Relative build outputs are resolved against --project. Existing outputs are preserved:
choose a fresh per-build directory for player bundles (shared companions are protected).
Test/build evidence binds source/config snapshots before and after execution. Build
profiles establish structure only; device launch/signing remain separate acceptance.
Exit codes: 0 passed, 1 failed, 2 not_run.
See the project's version-matched Unity CLI and Test Framework documentation before
extending flags; test execution deliberately omits -quit (the test runner exits).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET
import zipfile

VERSION_RE = re.compile(r"\b\d+\.\d+\.\d+[abfp]\d+(?:c\d+)?\b")
# Public target identifiers are BuildTarget names; Unity's CLI uses shorter aliases.
TARGETS = {
    "StandaloneWindows": ("Win", "WindowsStandaloneSupport"),
    "StandaloneWindows64": ("Win64", "WindowsStandaloneSupport"),
    "StandaloneOSX": ("OSXUniversal", "MacStandaloneSupport"),
    "StandaloneLinux64": ("Linux64", "LinuxStandaloneSupport"),
    "Android": ("Android", "AndroidPlayer"),
    "iOS": ("iOS", "iOSSupport"),
    "WebGL": ("WebGL", "WebGLSupport"),
}


class PreflightError(Exception):
    def __init__(self, reason: str, detail: str):
        self.reason, self.detail = reason, detail
        super().__init__(detail)


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def project_info(project: Path) -> dict:
    if not project.is_dir():
        raise PreflightError("missing_project", f"Project directory does not exist: {project}")
    missing = [p for p in ("Assets", "ProjectSettings", "Packages") if not (project / p).is_dir()]
    if missing:
        raise PreflightError("invalid_project", "Missing Unity directories: " + ", ".join(missing))
    try:
        version_text = (project / "ProjectSettings/ProjectVersion.txt").read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise PreflightError("missing_project_version", str(exc)) from exc
    match = re.search(r"^m_EditorVersion:\s*(\S+)", version_text, re.MULTILINE)
    if not match or not VERSION_RE.fullmatch(match[1]):
        raise PreflightError("invalid_project_version", "ProjectVersion.txt needs a valid m_EditorVersion")
    try:
        manifest = json.loads((project / "Packages/manifest.json").read_text(encoding="utf-8-sig"))
        deps = manifest.get("dependencies", {})
        if not isinstance(deps, dict):
            raise ValueError("dependencies must be an object")
    except (OSError, ValueError, AttributeError) as exc:
        raise PreflightError("invalid_package_manifest", str(exc)) from exc
    return {"project_version": match[1], "test_framework": deps.get("com.unity.test-framework")}


def discover_editors(version: str) -> list[Path]:
    home = Path.home()
    roots = [home / "Unity/Hub/Editor", home / "UnityHub/Editor", Path("/opt/Unity/Hub/Editor"),
             Path("/Applications/Unity/Hub/Editor")]
    for key in ("ProgramFiles", "ProgramFiles(x86)"):
        if os.environ.get(key):
            roots.append(Path(os.environ[key]) / "Unity/Hub/Editor")
    found = set()
    for root in roots:
        for relative in ("Editor/Unity", "Editor/Unity.exe", "Unity.app/Contents/MacOS/Unity"):
            path = root / version / relative
            if path.is_file():
                found.add(path.resolve())
    return sorted(found, key=str)


def resolve_editor(explicit: str | None, version: str) -> Path:
    specified = explicit if explicit is not None else os.environ.get("UNITY_EDITOR")
    if specified:
        path = Path(specified).expanduser().resolve()
        if path.suffix.lower() == ".app":
            path = path / "Contents/MacOS/Unity"
        if not path.is_file():
            raise PreflightError("missing_editor", f"Editor executable not found: {path}")
        return path
    candidates = discover_editors(version)
    if not candidates:
        raise PreflightError("missing_editor", f"No Editor matching {version}; use --editor or UNITY_EDITOR")
    if len(candidates) != 1:
        raise PreflightError("ambiguous_editor", "Select --editor explicitly: " + ", ".join(map(str, candidates)))
    return candidates[0]


def run_process(command: list[str], stdout: Path, stderr: Path, timeout: float) -> dict:
    started = time.monotonic()
    result = {"command": command, "exit_code": None, "timed_out": False}
    with stdout.open("wb") as out, stderr.open("wb") as err:
        try:
            kwargs = {"start_new_session": True} if os.name != "nt" else {}
            process = subprocess.Popen(command, stdout=out, stderr=err, **kwargs)
            try:
                result["exit_code"] = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                result["timed_out"] = True
                if os.name == "nt":
                    # Kill the Editor process tree, not just its launcher.
                    try:
                        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
                    if process.poll() is None:
                        process.kill()
                else:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                result["exit_code"] = process.wait()
        except OSError as exc:
            result["launch_error"] = str(exc)
    result["duration_seconds"] = round(time.monotonic() - started, 3)
    return result


def validate_editor(editor: Path, version: str, run_dir: Path, timeout: float) -> dict:
    probe = run_process([str(editor), "-version"], run_dir / "version-stdout.txt",
                        run_dir / "version-stderr.txt", min(timeout, 30))
    probe_text = ((run_dir / "version-stdout.txt").read_text(encoding="utf-8", errors="replace") + "\n" +
                  (run_dir / "version-stderr.txt").read_text(encoding="utf-8", errors="replace"))
    versions = set(VERSION_RE.findall(probe_text))
    probe["versions"] = sorted(versions)
    atomic_json(run_dir / "version-probe.json", probe)
    if probe.get("launch_error") or probe["timed_out"] or probe["exit_code"] != 0 or len(versions) != 1:
        raise PreflightError("editor_version_unverified", "Editor -version failed or returned an ambiguous version; see version-probe.json")
    if versions != {version}:
        raise PreflightError("editor_version_mismatch", f"Project requires {version}; Editor reports {', '.join(versions)}")
    return probe


def module_paths(editor: Path, module: str) -> list[Path]:
    # Windows/Linux: Editor/Data. macOS: Unity.app/Contents/PlaybackEngines.
    return [editor.parent / "Data/PlaybackEngines" / module,
            editor.parent.parent / "PlaybackEngines" / module]


def canonical_target(value: str) -> str:
    for target, (cli, _) in TARGETS.items():
        if value.lower() in (target.lower(), cli.lower()):
            return target
    raise PreflightError("unsupported_target", "Supported targets: " + ", ".join(TARGETS))


def test_summary(path: Path) -> dict:
    """Read NUnit 3 (Unity Test Framework) and NUnit 2 aggregate results."""
    if not path.is_file():
        raise ValueError("missing_test_results")
    try:
        root = ET.parse(path).getroot()
        tag = root.tag.rsplit("}", 1)[-1]
        if tag not in ("test-run", "test-results"):
            raise ValueError("Unexpected NUnit root")
        total = int(root.attrib["total"])
        failures = int(root.get("failed", root.get("failures", "0"))) + int(root.get("errors", "0"))
        skipped = int(root.get("skipped", "0")) + int(root.get("inconclusive", "0")) + int(root.get("not-run", "0"))
        passed = int(root.get("passed", str(total - failures - skipped)))
        if min(total, failures, skipped, passed) < 0 or passed + failures + skipped != total:
            raise ValueError("Inconsistent NUnit totals")
        cases = [n for n in root.iter() if n.tag.rsplit("}", 1)[-1] == "test-case"]
        if len(cases) != total:
            raise ValueError("NUnit total differs from the number of test-case records")
        case_passed = 0
        for case in cases:
            outcome = case.get("result", "").lower()
            if outcome in ("passed", "success") or (not outcome and case.get("success", "").lower() == "true"):
                case_passed += 1
            elif outcome not in ("skipped", "ignored", "inconclusive", "notrunnable"):
                failures = max(failures, 1)
        if cases:
            passed = min(passed, case_passed)
        root_failed = root.get("result", "").lower() in ("failed", "failure", "cancelled", "inconclusive")
        status = "passed" if total > 0 and passed > 0 and failures == 0 and not root_failed else "failed"
        return {"total": total, "passed": passed, "failed": failures, "skipped": skipped,
                "status": status, "reason": "tests_passed" if status == "passed" else
                ("zero_tests" if total == 0 else "tests_not_passed")}
    except (ET.ParseError, KeyError, TypeError, ValueError) as exc:
        raise ValueError("malformed_test_results: " + str(exc)) from exc


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def file_record(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}


def input_snapshot(project: Path) -> dict:
    """Hash source/config, not Library/Temp/builds/evidence. This is not a full toolchain lock.

    Follow source symlinks (record their targets too), stopping cycles by inode.
    Local/embedded packages under Packages are covered; downloaded package cache
    content is not. Package manifest + lock record their declared resolutions.
    """
    def walk_error(error):
        raise error

    files, links = {}, {}
    for name in ("Assets", "Packages", "ProjectSettings"):
        visited = set()
        for directory, children, names in os.walk(project / name, followlinks=True, onerror=walk_error):
            current = Path(directory)
            info = current.stat()
            identity = (info.st_dev, info.st_ino)
            if identity in visited:
                children[:] = []
                continue
            visited.add(identity)
            children[:] = sorted(child for child in children if child != ".git")
            for child in [current] + [current / n for n in children + names]:
                if child.is_symlink():
                    links[child.relative_to(project).as_posix()] = os.readlink(child)
            for filename in sorted(names):
                path = current / filename
                if path.is_file():
                    files[path.relative_to(project).as_posix()] = digest(path)
    content = {"files": files, "symlinks": links}
    snapshot = {"schema_version": 1, "scope": ["Assets", "Packages", "ProjectSettings"], **content}
    try:
        head = subprocess.run(["git", "-C", str(project), "rev-parse", "HEAD"],
                              capture_output=True, timeout=10, check=False)
        dirty = subprocess.run(["git", "-C", str(project), "diff", "--binary", "HEAD", "--",
                                "Assets", "Packages", "ProjectSettings"],
                               capture_output=True, timeout=10, check=False)
        if head.returncode == dirty.returncode == 0:
            snapshot["git"] = {"head": head.stdout.decode().strip(),
                               "dirty_diff_sha256": hashlib.sha256(dirty.stdout).hexdigest()}
    except (OSError, subprocess.TimeoutExpired):
        pass  # Content snapshots remain available outside a Git checkout.
    snapshot["sha256"] = hashlib.sha256(json.dumps({**content, "git": snapshot.get("git")}, sort_keys=True).encode()).hexdigest()
    return snapshot


def source_changes(before: dict, after: dict) -> list[str]:
    changed = {path for key in ("files", "symlinks")
               for path in set(before[key]) | set(after[key])
               if before[key].get(path) != after[key].get(path)}
    if before.get("git") != after.get("git"):
        changed.add("<git-revision-or-diff>")
    return sorted(changed)


def tree_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    nodes = [path] + list(path.rglob("*")) if path.is_dir() else [path]
    if any(node.is_symlink() for node in nodes):
        raise ValueError("symlinked_build_artifact")
    return sorted(node for node in nodes if node.is_file())


def player_bundle_roots(path: Path, target: str) -> list[Path]:
    """Known player companions; avoids hashing unrelated older builds next door."""
    if target in ("StandaloneWindows", "StandaloneWindows64", "StandaloneLinux64"):
        names = ("UnityPlayer.dll", "UnityPlayer.so", "GameAssembly.dll", "GameAssembly.so",
                 "UnityCrashHandler32.exe", "UnityCrashHandler64.exe", "MonoBleedingEdge",
                 "baselib.dll", "WinPixEventRuntime.dll", "D3D12")
        return [path, path.with_name(path.stem + "_Data")] + [path.parent / n for n in names]
    return [path]


def build_artifacts(path: Path, target: str | None = None) -> dict:
    roots = player_bundle_roots(path, target) if target else [path]
    files = sorted(set(p for root in roots for p in tree_files(root)))
    records = [file_record(p) for p in files]
    return {"path": str(path), "files": len(records), "bytes": sum(r["bytes"] for r in records),
            "nonempty": any(r["bytes"] > 0 for r in records), "manifest": records,
            "profile": target, "format_status": "not_run", "runtime_status": "not_run"}


def validate_build(path: Path, target: str, artifacts: dict, report_path: Path) -> None:
    """Check target-specific *structure*, not launchability, signing or store acceptance.

    A project-owned entry may omit our optional report, but it still needs the
    structural profile. If it emits a report, target/output/result/hashes must agree.
    """
    def nonempty(p):
        return p.is_file() and p.stat().st_size > 0

    def has_data(p):
        return p.is_dir() and any(nonempty(p / n) for n in ("globalgamemanagers", "data.unity3d", "boot.config"))

    valid = False
    if target in ("StandaloneWindows", "StandaloneWindows64", "StandaloneLinux64"):
        if nonempty(path):
            with path.open("rb") as stream:
                header = stream.read(4)
            executable = (header.startswith(b"MZ") and path.suffix.lower() == ".exe") if target.startswith("StandaloneWindows") else header == b"\x7fELF"
            valid = executable and has_data(path.with_name(path.stem + "_Data"))
    elif target == "StandaloneOSX" and path.suffix.lower() == ".app":
        info_path = path / "Contents/Info.plist"
        if nonempty(info_path):
            with info_path.open("rb") as stream:
                info = plistlib.load(stream)
            name = info.get("CFBundleExecutable", "") if isinstance(info, dict) else ""
            if isinstance(name, str) and name and Path(name).name == name:
                executable = path / "Contents/MacOS" / name
                if nonempty(executable):
                    with executable.open("rb") as stream:
                        magic = stream.read(4)
                    valid = magic in (b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca", b"\xca\xfe\xba\xbf", b"\xbf\xba\xfe\xca") and has_data(path / "Contents/Resources/Data")
    elif target == "Android" and path.suffix.lower() in (".apk", ".aab") and nonempty(path):
        try:
            with zipfile.ZipFile(path) as archive:
                required = ("AndroidManifest.xml", "classes.dex") if path.suffix.lower() == ".apk" else ("base/manifest/AndroidManifest.xml", "BundleConfig.pb")
                valid = all(archive.getinfo(n).file_size > 0 for n in required)
        except (zipfile.BadZipFile, KeyError):
            valid = False
    elif target == "WebGL" and path.is_dir():
        build = path / "Build"
        names = [p.name for p in tree_files(build) if nonempty(p)]
        valid = nonempty(path / "index.html") and any(n.endswith(".js") for n in names) and any(n.endswith((".wasm", ".wasm.gz", ".wasm.br")) for n in names) and any(n.endswith((".data", ".data.gz", ".data.br")) for n in names)
    elif target == "iOS" and path.is_dir():
        valid = (any(nonempty(p / "project.pbxproj") for p in path.glob("*.xcodeproj"))
                 and any(nonempty(p) for p in tree_files(path / "Classes"))
                 and any(nonempty(p) for p in tree_files(path / "Data")))
    if not valid:
        raise ValueError("build_structure_mismatch")
    artifacts["format_status"] = "structure_verified"
    artifacts["build_report_status"] = "not_provided"
    if report_path.exists():
        artifacts["build_report_status"] = "failed"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or type(report.get("schema_version")) is not int or report["schema_version"] != 1:
            raise ValueError("invalid_build_report_schema")
        if (report.get("result") != "Succeeded" or report.get("target") != target
                or not isinstance(report.get("output"), str) or Path(report["output"]).resolve() != path
                or type(report.get("errors")) is not int or report["errors"] != 0):
            raise ValueError("build_report_mismatch")
        if not isinstance(report.get("scenes"), list) or not report["scenes"] or not all(isinstance(scene, str) and scene for scene in report["scenes"]):
            raise ValueError("build_report_missing_scenes")
        entries = report.get("files")
        expected = {r["path"]: r for r in artifacts["manifest"]}
        if not isinstance(entries, list) or len(entries) != len(expected):
            raise ValueError("build_report_manifest_mismatch")
        seen = set()
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise ValueError("build_report_manifest_mismatch")
            name = str(Path(entry["path"]).resolve())
            if name in seen or name not in expected or type(entry.get("bytes")) is not int or any(entry.get(k) != expected[name][k] for k in ("sha256", "bytes")):
                raise ValueError("build_report_manifest_mismatch")
            seen.add(name)
        artifacts["build_report_status"] = "verified"


def execute(args: argparse.Namespace) -> dict:
    project = Path(args.project).expanduser().resolve()
    result = {"schema_version": 1, "operation": args.operation, "project": str(project),
              "status": "not_run", "reason": "preflight", "command": [], "exit_code": None,
              "started_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    # For a nonexistent project, do not create a misleading Unity project skeleton.
    if not project.is_dir():
        result.update(reason="missing_project", detail=f"Project directory does not exist: {project}")
        return result
    state_root = project / ".unity-game"
    if any(path.is_symlink() for path in (state_root, state_root / "runs")):
        result.update(reason="symlinked_run_root", detail=".unity-game and its runs directory must be real project-local directories")
        return result
    run_dir = project / ".unity-game/runs" / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:10])
    try:
        for path in (state_root, state_root / "runs"):
            if path.exists() and not path.is_dir():
                raise NotADirectoryError(f"Expected a directory: {path}")
        run_dir.mkdir(parents=True)
        for name in ("stdout.txt", "stderr.txt", "editor.log"):
            (run_dir / name).touch()
    except OSError as exc:
        result.update(status="failed", reason="helper_error", detail=str(exc),
                      finished_at=dt.datetime.now(dt.timezone.utc).isoformat())
        return result
    result["run_dir"] = str(run_dir)
    lock = project / ".unity-game/editor-helper.lock"
    locked = False
    input_before = None
    try:
        result.update(project_info(project))
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise PreflightError("helper_busy", f"Another helper owns {lock}; inspect its PID before manually removing a stale lock") from exc
        locked = True
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"pid": os.getpid(), "run_dir": str(run_dir)}, stream)
        if (project / "Temp/UnityLockfile").exists():
            raise PreflightError("project_open", "Temp/UnityLockfile exists; close the project's Editor before running the helper")
        editor = resolve_editor(args.editor, result["project_version"])
        result["editor"] = str(editor)
        result["version_probe"] = validate_editor(editor, result["project_version"], run_dir, args.timeout)
        if args.operation == "doctor":
            result["modules"] = {target: any(p.is_dir() for p in module_paths(editor, module))
                                 for target, (_, module) in TARGETS.items()}
            result.update(status="passed", reason="project_and_editor_ready",
                          detail="Editor/project match. Test Framework availability is reported separately; no tests or build were run.")
        else:
            command = [str(editor), "-batchmode", "-projectPath", str(project), "-logFile", str(run_dir / "editor.log")]
            if args.operation == "test":
                if not result["test_framework"]:
                    raise PreflightError("missing_test_framework", "Packages/manifest.json has no com.unity.test-framework dependency")
                command += ["-runTests", "-testPlatform", "EditMode" if args.mode == "editmode" else "PlayMode",
                            "-testResults", str(run_dir / "results.xml")]
                result["mode"] = args.mode
            else:
                target = canonical_target(args.target)
                cli_target, module = TARGETS[target]
                result["target"] = target
                if not any(p.is_dir() for p in module_paths(editor, module)):
                    raise PreflightError("missing_platform_module", f"Editor installation has no {module}; install the matching platform module")
                if not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+", args.execute_method):
                    raise PreflightError("invalid_build_method", "Use a fully qualified static method, for example UnityGameBuild.Build")
                output = Path(args.output).expanduser()
                output = (project / output).resolve() if not output.is_absolute() else output.resolve()
                if output.exists():
                    raise PreflightError("build_output_exists", "Select a fresh --output path; existing files are preserved")
                # Never put builds inside tracked game resources or helper state.
                protected_roots = [(project / p).resolve() for p in ("Assets", "Packages", "ProjectSettings", ".unity-game")]
                if output == project or output in project.parents or any(output.is_relative_to(root) for root in protected_roots):
                    raise PreflightError("invalid_build_output", "Use an independent build output, such as Builds/release-001")
                output.parent.mkdir(parents=True, exist_ok=True)
                occupied = [p for p in player_bundle_roots(output, target)[1:] if p.exists() or p.is_symlink()]
                if occupied:
                    raise PreflightError("build_output_exists", "Existing player bundle companions are preserved; select a fresh bundle directory: " + ", ".join(map(str, occupied)))
                result["output"] = str(output)
                command += ["-quit", "-buildTarget", cli_target, "-executeMethod", args.execute_method,
                            "-buildOutput", str(output), "-buildReport", str(run_dir / "build-result.json")]
            input_before = input_snapshot(project)
            atomic_json(run_dir / "inputs-before.json", input_before)
            result.update(run_process(command, run_dir / "stdout.txt", run_dir / "stderr.txt", args.timeout))
            result.update(status="failed", reason="editor_failed")
            if result.get("launch_error"):
                result.update(status="not_run", reason="editor_launch_failed")
            elif result["timed_out"]:
                result["reason"] = "timeout"
            elif args.operation == "test":
                try:
                    result["tests"] = test_summary(run_dir / "results.xml")
                    if result["exit_code"] == 0:
                        result.update(status=result["tests"]["status"], reason=result["tests"]["reason"])
                except ValueError as exc:
                    result["xml_error"] = str(exc)
                    if result["exit_code"] == 0:
                        result.update(reason=str(exc).split(":", 1)[0], detail=str(exc))
            elif result["exit_code"] != 0:
                # Capture the Editor's real exit even if it produced partial artifacts.
                result["reason"] = "editor_failed"
            else:
                result["artifacts"] = build_artifacts(Path(result["output"]), result["target"])
                if result["artifacts"]["nonempty"]:
                    try:
                        validate_build(Path(result["output"]), result["target"], result["artifacts"], run_dir / "build-result.json")
                        result.update(status="passed", reason="build_artifact_verified")
                    except (OSError, ValueError, TypeError) as exc:
                        result.update(reason=str(exc).split(":", 1)[0], detail=str(exc))
                else:
                    result["reason"] = "missing_or_empty_build_artifact"
            if result["status"] == "passed":
                log = run_dir / "editor.log"
                if not log.is_file() or log.stat().st_size == 0:
                    result.update(status="failed", reason="missing_or_empty_editor_log")
    except PreflightError as exc:
        result.update(status="not_run", reason=exc.reason, detail=exc.detail)
    except (OSError, ValueError) as exc:
        result.update(status="failed", reason="helper_error", detail=str(exc))
    finally:
        if input_before is not None:
            try:
                after = input_snapshot(project)
                atomic_json(run_dir / "inputs-after.json", after)
                changes = source_changes(input_before, after)
                result["input_provenance"] = {
                    "before": {"manifest": str(run_dir / "inputs-before.json"), "sha256": input_before["sha256"], "git": input_before.get("git")},
                    "after": {"manifest": str(run_dir / "inputs-after.json"), "sha256": after["sha256"], "git": after.get("git")},
                    "unchanged": not changes, "changed_paths": changes,
                    "scope": input_before["scope"],
                    "limitations": "Excludes downloaded package cache, Editor/platform binaries and external services; runtime acceptance is separate."}
                if changes and result["status"] == "passed":
                    result.update(status="failed", reason="project_inputs_changed")
            except (OSError, ValueError) as exc:
                result.update(status="failed", reason="input_provenance_unavailable", detail=str(exc))
        try:
            result["evidence_files"] = [file_record(p) for p in sorted(run_dir.iterdir()) if p.is_file() and p.name != "result.json"]
        except OSError as exc:
            result.update(status="failed", reason="evidence_hashing_failed", detail=str(exc))
        if locked:
            lock.unlink(missing_ok=True)
        result["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        atomic_json(run_dir / "result.json", result)
    return result


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = root.add_subparsers(dest="operation", required=True)
    for name in ("doctor", "test", "build"):
        sub = commands.add_parser(name)
        sub.add_argument("--project", required=True, help="Existing Unity project directory")
        sub.add_argument("--editor", help="Exact Editor executable (or macOS Unity.app); overrides UNITY_EDITOR")
        sub.add_argument("--timeout", type=float, default=1800, help="Editor timeout in seconds (default 1800)")
        if name == "test":
            sub.add_argument("--mode", choices=("editmode", "playmode"), required=True)
        elif name == "build":
            sub.add_argument("--target", required=True, help="BuildTarget name or Unity CLI alias; e.g. StandaloneLinux64 / Linux64")
            sub.add_argument("--execute-method", required=True, help="Project-owned static Editor method")
            sub.add_argument("--output", required=True, help="Fresh output path; relative paths resolve inside --project")
    return root


def main(argv: list[str] | None = None) -> int:
    arg_parser = parser()
    args = arg_parser.parse_args(argv)
    if not 0 < args.timeout < float("inf"):
        arg_parser.error("--timeout must be a finite positive number")
    result = execute(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"passed": 0, "failed": 1, "not_run": 2}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
