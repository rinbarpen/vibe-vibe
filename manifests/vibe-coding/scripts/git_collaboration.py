#!/usr/bin/env python3
"""Inspect local branches/worktrees and optional hosted collaboration, without writes or network."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit


class InspectionError(ValueError):
    pass


def git(root: Path, *args: str, allowed=(0,)) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(root), *args],
        capture_output=True, check=False, timeout=30,
        env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1"),
    )
    if result.returncode not in allowed:
        raise InspectionError(result.stderr.decode("utf-8", "replace").strip() or "Git query failed")
    return result.stdout.decode("utf-8", "replace").strip("\r\n")


def remote_info(name: str, url: str) -> dict:
    """Return provider metadata, never remote credentials, userinfo, or query strings."""
    host = None
    repository = None
    if "://" in url or url.startswith("file:"):
        try:
            parsed = urlsplit(url)
            host = parsed.hostname if parsed.scheme != "file" else None
            repository = parsed.path.strip("/") if host else None
        except ValueError:
            pass
    elif not re.match(r"^[A-Za-z]:[\\/]", url):
        match = re.fullmatch(r"(?:[^@/:]+@)?([^/:]+):(.+)", url)
        if match:
            host, repository = match.groups()
    host = host.lower() if host else None
    repository = repository.split("?", 1)[0].split("#", 1)[0] if repository else None
    provider = {"github.com": "github", "gitlab.com": "gitlab", "gitee.com": "gitee"}.get(
        host, "unknown" if host else "git",
    )
    return {"name": name, "host": host, "repository": repository.removesuffix(".git") if repository else None,
            "provider": provider}


def worktrees(root: Path) -> list[dict]:
    result, current = [], {}
    line_format = False
    try:
        fields = git(root, "worktree", "list", "--porcelain", "-z").split("\0")
    except InspectionError:
        # Older Git (including 2.34) has stable porcelain output but no -z.
        # Reject ambiguous records rather than inventing an occupied path.
        fields = git(root, "worktree", "list", "--porcelain").split("\n")
        line_format = True
    for field in fields:
        if line_format:
            field = field.removesuffix("\r")
        if not field:
            if current:
                result.append(current)
                current = {}
            continue
        key, _, value = field.partition(" ")
        if key == "worktree":
            current["path"] = value
        elif key == "branch":
            current["branch"] = value.removeprefix("refs/heads/")
        elif key == "HEAD":
            current["commit"] = value
        elif key in ("bare", "detached", "locked", "prunable"):
            current[key] = value or True
        else:
            raise InspectionError("Ambiguous worktree record; use Git with NUL worktree output for unusual paths")
    if current:
        result.append(current)
    return result


def inspect_repo(root: Path | str, *, mode="local", remote=None, provider="auto",
                 branch=None, base=None, issue=None) -> dict:
    if mode not in ("local", "hosted") or provider not in ("auto", "github", "gitlab", "gitee"):
        raise InspectionError("Select local/hosted mode and a supported provider")
    root = Path(git(Path(root).resolve(), "rev-parse", "--show-toplevel")).resolve()
    current = git(root, "symbolic-ref", "--quiet", "--short", "HEAD", allowed=(0, 1)) or None
    commit = git(root, "rev-parse", "--verify", "HEAD", allowed=(0, 1, 128)) or None
    entries = []
    refs = git(root, "for-each-ref", "--format=%(refname:short)%00%(objectname)%00%(upstream:short)", "refs/heads")
    for row in refs.splitlines():
        name, sha, upstream = row.split("\0")
        entries.append({"name": name, "commit": sha, "upstream": upstream or None})
    occupied = worktrees(root)
    for entry in entries:
        entry["worktrees"] = [w["path"] for w in occupied if w.get("branch") == entry["name"]]
    remotes = []
    for name in git(root, "remote").splitlines():
        entry = remote_info(name, git(root, "remote", "get-url", name))
        entry["push_target"] = remote_info(name, git(root, "remote", "get-url", "--push", name))
        remotes.append(entry)
    if remote and remote not in {r["name"] for r in remotes}:
        raise InspectionError("Selected remote is not configured; no remote was created")
    selected = next((r for r in remotes if r["name"] == remote), None)
    if selected is None and len(remotes) == 1:
        selected = remotes[0]
    if mode == "hosted":
        if not remotes:
            raise InspectionError("Hosted mode needs a configured remote; local mode remains available")
        if selected is None:
            raise InspectionError("Multiple remotes: select --remote before hosted collaboration")
        if not selected["host"]:
            raise InspectionError("This remote is a local Git path; use local mode for plain Git collaboration")
        if provider == "auto" and selected["provider"] == "unknown":
            raise InspectionError("Unknown host: select --provider github, gitlab, or gitee explicitly")
    if selected is not None and provider != "auto":
        selected = dict(selected, provider=provider)
    names = {e["name"] for e in entries}
    if base is None:
        base = next((name for name in ("main", "master", current) if name in names), None)
    if base is not None:
        git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}")
    if branch:
        git(root, "check-ref-format", "--branch", branch)
    dirty = bool(git(root, "status", "--porcelain=v1", "-z", "--untracked-files=normal"))
    decisions = []
    if dirty:
        decisions.append("Preserve existing changes; isolate this task or choose an existing worktree before switching")
    if current is None or commit is None:
        decisions.append("Choose a branch/base for detached or unborn HEAD before implementation")
    if branch in names:
        decisions.append("Requested branch exists; reuse only its confirmed task context, never reset it")
    if mode == "local" and remotes:
        decisions.append("A remote is available; hosted PR/Issue interaction remains opt-in")
    if selected and any(selected.get(key) != selected["push_target"].get(key)
                        for key in ("host", "repository")):
        decisions.append("Fetch and push targets differ; confirm the publication target and PR base")
    return {
        "schema_version": 1, "root": str(root), "mode": mode, "network_performed": False,
        "head": {"branch": current, "commit": commit, "detached": current is None, "unborn": commit is None},
        "dirty": dirty, "base": base, "requested_branch": branch,
        "branches": entries, "worktrees": occupied, "remotes": remotes,
        "selected_remote": selected, "hosted_available": any(r["host"] for r in remotes),
        "issue": {"reference": issue, "verified": False} if issue else None,
        "decisions": decisions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True).add_parser("inspect")
    sub.add_argument("--root", type=Path, default=Path.cwd())
    sub.add_argument("--mode", choices=("local", "hosted"), default="local")
    sub.add_argument("--remote")
    sub.add_argument("--provider", choices=("auto", "github", "gitlab", "gitee"), default="auto")
    sub.add_argument("--branch")
    sub.add_argument("--base")
    sub.add_argument("--issue", help="Optional existing reference; inspection does not contact its host")
    args = parser.parse_args(argv)
    try:
        report = inspect_repo(args.root, **{key: getattr(args, key) for key in
                              ("mode", "remote", "provider", "branch", "base", "issue")})
    except (OSError, InspectionError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc), "network_performed": False}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
