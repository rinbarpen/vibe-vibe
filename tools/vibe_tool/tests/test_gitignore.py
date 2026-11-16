"""Use Git itself to check cache exclusions and preserve meaningful project files."""
from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from vibe_tool.discovery import resolve_manifest
from vibe_tool.portable import render
from vibe_tool.setup import setup


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests/vibe-coding"
COMMON_CACHES = (
    ".cache/tool/item", "pkg/.cache/tool/item",
    ".coverage", ".coverage.host.123", "htmlcov/index.html",
    ".DS_Store", "Thumbs.db",
    "draft.swp", "draft.swo", "draft~", ".codegraph/index.db",
    ".vibe-tool/backups/example/original", ".claude/settings.local.json",
)
LANGUAGE_CACHES = {
    "python": (
        ".mypy_cache/result.json", ".tox/py/marker", ".nox/test/marker",
        ".hypothesis/examples/item", ".venv/pyvenv.cfg",
        "pkg/__pycache__/module.pyc", "module.pyo",
        ".pytest_cache/v/cache/nodeids", ".ruff_cache/result",
    ),
    "javascript-typescript": (
        "node_modules/package/index.js", ".vite/deps/item.js",
        ".next/cache/item", ".nuxt/cache/item", ".svelte-kit/generated/item",
        ".parcel-cache/item", ".turbo/cache/item", ".eslintcache",
        ".stylelintcache", "tsconfig.tsbuildinfo",
    ),
    "go": (".gocache/ab/hash", "service/.gocache/ab/hash"),
    "rust": ("target/debug/deps/item", "native/target/release/item"),
    "java-kotlin": (
        ".gradle/caches/item", "app/.gradle/caches/item",
        ".kotlin/sessions/item", "module/target/classes/App.class",
    ),
    "dotnet": (
        ".vs/solution/cache", ".nuget/packages/example/package.nupkg",
        "App/.nuget/packages/example/package.nupkg", "App/obj/project.assets.json",
    ),
    "dart-flutter": (
        ".dart_tool/package_config.json", ".pub-cache/hosted/item",
        ".pub/cache/item", ".flutter-plugins", ".flutter-plugins-dependencies",
    ),
    "c-cpp": (
        "native/CMakeFiles/cache/item", "native/CMakeCache.txt",
        "native/cmake_install.cmake", "native/CMakeUserPresets.json",
        ".ccls-cache/index",
    ),
}
CACHES = COMMON_CACHES + tuple(path for paths in LANGUAGE_CACHES.values() for path in paths)
TRACKABLE = (
    "src/cache.py", "src/cache/index.ts", "cache/README.md",
    "tests/fixtures/cache/data.json", ".cache-policy.md",
    "package-lock.json", "pnpm-lock.yaml", "uv.lock", "Cargo.lock", "go.sum",
    ".python-version", ".env.example", ".claude/settings.json",
    ".agents/skills/example/SKILL.md", ".claude/agents/reviewer.md",
    "AGENTS.md", "VERSION", "CHANGELOG.md", ".vibe-setup.json",
    ".planning/task/notes.md",
    "go.mod", "go.work", "go.work.sum", "Cargo.toml", "rust-toolchain.toml",
    ".cargo/config.toml", "pom.xml", "build.gradle.kts", "settings.gradle.kts",
    "gradle.lockfile", "gradlew", "gradle/wrapper/gradle-wrapper.jar",
    "App/App.csproj", "Directory.Build.props", "global.json",
    "packages.lock.json", ".nuget/NuGet.Config", "pubspec.yaml", "pubspec.lock",
    "CMakeLists.txt", "CMakePresets.json", ".clangd", ".clang-format",
)


class GitIgnoreTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="vibe ignore ")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        # Global user excludes and Git templates must not mask missing rules.
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1",
                        GIT_CONFIG_GLOBAL=os.devnull, PYTHONDONTWRITEBYTECODE="1")

    def git(self, root, *args, input=None):
        return subprocess.run(
            ["git", "-c", "core.excludesFile=" + os.devnull, "-C", str(root), *args],
            input=input, text=True, capture_output=True, env=self.env,
            check=False, timeout=60,
        )

    def repository(self, ignore, name):
        root = self.root / name
        root.mkdir()
        result = self.git(root, "init", "--quiet", "--template=")
        self.assertEqual(result.returncode, 0, result.stderr)
        (root / ".gitignore").write_bytes(ignore.read_bytes())
        return root

    def assert_ignored(self, root, paths):
        result = self.git(root, "check-ignore", "--no-index", "--stdin",
                          input="\n".join(paths) + "\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.splitlines()), set(paths))

    def source_repo(self):
        root = self.root / "source repo"
        source = root / "manifests/vibe-coding"
        source.parent.mkdir(parents=True)
        shutil.copytree(MANIFEST, source,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (source / "skills.txt").write_text("# Unrelated skills omitted in this fixture.\n")
        (root / "skills").mkdir()
        (root / "mine").mkdir()
        return root

    def install(self, source, target):
        with mock.patch.dict(os.environ, {
            "VIBE_PROJECTS_FILE": str(self.root / "projects.json"),
        }), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup(source, "vibe-coding", target,
                                   agent="generic", provider="git"), 0)

    def test_repository_caches_are_ignored_without_global_excludes(self):
        root = self.repository(ROOT / ".gitignore", "repository")
        self.assert_ignored(root, CACHES)

    def test_manifest_caches_are_ignored_without_global_excludes(self):
        root = self.repository(MANIFEST / ".gitignore", "manifest")
        self.assert_ignored(root, CACHES)

    def test_each_language_cache_family_is_covered_in_both_ignore_files(self):
        for name, source in (("repository", ROOT), ("manifest", MANIFEST)):
            root = self.repository(source / ".gitignore", name)
            for language, paths in LANGUAGE_CACHES.items():
                with self.subTest(source=name, language=language):
                    self.assert_ignored(root, paths)

    def test_sources_lockfiles_and_shared_configuration_remain_trackable(self):
        for name, source in (("repository", ROOT), ("manifest", MANIFEST)):
            with self.subTest(source=name):
                root = self.repository(source / ".gitignore", name)
                result = self.git(root, "check-ignore", "--no-index", "--stdin",
                                  input="\n".join(TRACKABLE) + "\n")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "")

    def test_status_hides_caches_without_deleting_files_or_hiding_source(self):
        for name, source in (("repository", ROOT), ("manifest", MANIFEST)):
            with self.subTest(source=name):
                root = self.repository(source / ".gitignore", name)
                for relative in (*CACHES, *TRACKABLE):
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("preserve content\n")
                result = self.git(root, "status", "--porcelain=v1", "--untracked-files=all")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual({line[3:] for line in result.stdout.splitlines()},
                                 {".gitignore", *TRACKABLE})
                for relative in CACHES:
                    self.assertEqual((root / relative).read_text(), "preserve content\n")

    def test_ignore_does_not_hide_modifications_to_already_tracked_cache(self):
        root = self.repository(MANIFEST / ".gitignore", "tracked")
        cache = root / ".cache/tracked.txt"
        cache.parent.mkdir()
        cache.write_text("baseline\n")
        result = self.git(root, "add", "-f", "--", ".cache/tracked.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        cache.write_text("changed\n")
        result = self.git(root, "status", "--porcelain=v1", "--", ".cache/tracked.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AM .cache/tracked.txt", result.stdout)

    def test_portable_render_distributes_the_manifest_ignore_file(self):
        stage = self.root / "stage"
        render(resolve_manifest(ROOT / "manifests", "vibe-coding"),
               stage, self.root / "project", {"provider": "git"})
        self.assertEqual((stage / ".gitignore").read_bytes(),
                         (MANIFEST / ".gitignore").read_bytes())

    def test_setup_installs_cache_rules_in_a_new_project(self):
        source = self.source_repo()
        target = self.root / "new project"
        self.install(source, target)
        result = self.git(target, "init", "--quiet", "--template=")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((target / ".gitignore").read_bytes(),
                         (MANIFEST / ".gitignore").read_bytes())
        self.assert_ignored(target, CACHES)

    def test_setup_preserves_existing_custom_rules_and_negation_order(self):
        source = self.source_repo()
        target = self.root / "existing project"
        target.mkdir()
        original = b"# Project policy\r\n*.scratch\r\n!important.scratch\r\n"
        (target / ".gitignore").write_bytes(original)
        self.install(source, target)
        self.assertEqual((target / ".gitignore").read_bytes(), original)
        result = self.git(target, "init", "--quiet", "--template=")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_ignored(target, ("temporary.scratch",))
        result = self.git(target, "check-ignore", "--no-index", "--", "important.scratch")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
