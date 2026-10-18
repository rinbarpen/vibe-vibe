#!/usr/bin/env python3
"""Initialize host-independent release files without overwriting project data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from version_guard import GuardError, changelog_sections, metadata_versions, version

INITIAL_CHANGELOG = """# Changelog

All notable changes to this project are documented here.

## [Unreleased]

"""


def initialize(root: Path, dry_run: bool = False) -> str:
    candidates = metadata_versions(root)
    unique = set(candidates.values())
    if len(unique) > 1:
        raise GuardError(f"conflicting package versions: {candidates}")
    if (root / "VERSION").exists():
        chosen = version(root)
    else:
        chosen = next(iter(unique), "0.1.0")
        # Validate the derived value before touching the target.
        from version_guard import SEMVER

        if not SEMVER.fullmatch(chosen):
            raise GuardError(f"invalid package version: {chosen!r}")
    if unique and chosen not in unique:
        raise GuardError(f"VERSION {chosen!r} conflicts with package versions: {candidates}")
    if (root / "CHANGELOG.md").exists():
        changelog_sections(root)
    if not dry_run:
        root.mkdir(parents=True, exist_ok=True)
        if not (root / "VERSION").exists():
            (root / "VERSION").write_text(chosen + "\n", encoding="utf-8")
        if not (root / "CHANGELOG.md").exists():
            (root / "CHANGELOG.md").write_text(INITIAL_CHANGELOG, encoding="utf-8")
    return chosen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        chosen = initialize(args.target.resolve(), args.dry_run)
    except GuardError as exc:
        print(f"init-version: {exc}", file=sys.stderr)
        return 1
    prefix = "WILL USE" if args.dry_run else "USE"
    print(f"  {prefix} VERSION {chosen}; preserve existing VERSION/CHANGELOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
