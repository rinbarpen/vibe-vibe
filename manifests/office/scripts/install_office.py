#!/usr/bin/env python3
"""Install the self-contained Office manifest without touching project data.

Dependencies listed by skills.txt are installed by the vibe dispatcher, not by
this script. Direct invocation installs only the manifest's own resources.
"""

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path


INSTALLER_FILES = {"init-office.sh", "install_office.py"}
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"}


def _files(directory: Path):
    if directory.is_dir():
        for source in sorted(directory.rglob("*")):
            relative = source.relative_to(directory)
            if source.is_file() and not EXCLUDED_PARTS.intersection(relative.parts):
                yield source, relative


def installation_files(manifest: Path):
    """Yield source/destination pairs; do not inspect or create the target."""
    for name in ("CLAUDE.md", "AGENTS.md", "README.md", "MANIFEST.md"):
        source = manifest / name
        if source.is_file():
            yield source, Path(name)

    # This entry survives conflicts with a project's existing root instructions.
    readme = manifest / "README.md"
    if readme.is_file():
        yield readme, Path("office/README.md")

    for name in ("docx", "xlsx", "pptx", "pdf", "planning", "assets"):
        for source, relative in _files(manifest / name):
            yield source, Path("office") / name / relative

    for source, relative in _files(manifest / "rules"):
        if source.suffix == ".mdc":
            yield source, Path(".cursor/rules") / relative
        elif source.suffix == ".md":
            yield source, Path("office/rules") / relative

    for source, relative in _files(manifest / "scripts"):
        if relative.parts[0] not in INSTALLER_FILES:
            yield source, Path("office/scripts") / relative

    for source, relative in _files(manifest / "agents"):
        yield source, Path("office/agents") / relative
    for name in (".claude/agents", ".codex/agents"):
        for source, relative in _files(manifest / name):
            yield source, Path(name) / relative


def _atomic_copy(source: Path, destination: Path, *, content: bytes | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with source.open("rb") as src, tempfile.NamedTemporaryFile(
            dir=destination.parent, prefix=f".{destination.name}.", delete=False
        ) as dst:
            temporary = Path(dst.name)
            if content is None:
                shutil.copyfileobj(src, dst)
            else:
                dst.write(content)
        shutil.copystat(source, temporary)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Install Office manifest resources")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("-f", "--force", action="store_true", help="Replace managed files")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Preview without any writes")
    args = parser.parse_args(argv)
    manifest = Path(__file__).resolve().parents[1]
    target = Path(args.target).expanduser().resolve()
    copied = skipped = 0
    try:
        if target.exists() and not target.is_dir():
            raise NotADirectoryError(str(target))
        for source, relative in installation_files(manifest):
            destination = target / relative
            if os.path.lexists(destination) and (not args.force or relative == Path("MANIFEST.md")):
                skipped += 1
                reason = "project output ledger; preserve history" if relative == Path("MANIFEST.md") else "exists; use --force to replace"
                print(f"  SKIP  {relative} ({reason})")
                continue
            if args.dry_run:
                print(f"  WILL  {relative}")
            else:
                # The stable office/README.md and repository source use
                # assets/...; the optional project-root README is one level up.
                content = None
                if relative == Path("README.md"):
                    content = source.read_text(encoding="utf-8").replace(
                        "](assets/", "](office/assets/"
                    ).encode("utf-8")
                _atomic_copy(source, destination, content=content)
                print(f"  COPY  {relative}")
            copied += 1
    except OSError as exc:
        print(f"Office install error: {exc}", file=sys.stderr)
        return 1

    label = "[dry-run] Would install" if args.dry_run else "Installed"
    print(f"{label} {copied} Office files; {skipped} preserved; target: {target}")
    print("Office entry: office/README.md. For existing CLAUDE.md/AGENTS.md, add:")
    print("  For Office tasks, read office/README.md and the referenced office/rules/*.md.")
    print("Required skills: vibe init office / vibe add manifest office installs skills.txt dependencies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
