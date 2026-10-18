#!/usr/bin/env python3
"""Host-independent VERSION, changelog, tag, and release-note checks."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
HEADING = re.compile(r"^## \[([^\]]+)\](?:\s+-\s+\d{4}-\d{2}-\d{2})?\s*$")
SECTION = re.compile(r"^### (Added|Changed|Deprecated|Removed|Fixed|Security)\s*$")
PLACEHOLDER = re.compile(r"^(?:TODO|TBD|\.\.\.|待填写|示例|新功能描述|功能变更描述|Bug 修复描述|安全修复描述)(?:\b|\s|$)", re.IGNORECASE)


class GuardError(Exception):
    """A release precondition failed."""


def version(root: Path) -> str:
    path = root / "VERSION"
    if not path.is_file():
        raise GuardError("VERSION is missing")
    value = path.read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(value):
        raise GuardError(f"VERSION must contain one SemVer value without v: {value!r}")
    for part in (SEMVER.fullmatch(value).group(4) or "").split("."):
        if part.isdigit() and len(part) > 1 and part.startswith("0"):
            raise GuardError("numeric prerelease identifiers cannot have leading zeroes")
    return value


def metadata_versions(root: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    package = root / "package.json"
    if package.is_file():
        try:
            value = json.loads(package.read_text(encoding="utf-8")).get("version")
        except (ValueError, OSError) as exc:
            raise GuardError(f"package.json is invalid: {exc}") from exc
        if isinstance(value, str):
            found["package.json"] = value
    for name, sections in (
        ("pyproject.toml", ("project", "tool.poetry")),
        ("Cargo.toml", ("package", "workspace.package")),
    ):
        path = root / name
        if not path.is_file():
            continue
        active: str | None = None
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("["):
                section = stripped.strip("[]")
                active = section if section in sections else None
            elif active:
                match = re.match(r'^version\s*=\s*["\']([^"\']+)["\']', stripped)
                if match:
                    found[f"{name}[{active}]"] = match.group(1)
                    active = None
    pom = root / "pom.xml"
    if pom.is_file():
        try:
            xml_root = ET.parse(pom).getroot()
        except ET.ParseError as exc:
            raise GuardError(f"pom.xml is invalid: {exc}") from exc
        namespace = xml_root.tag.partition("}")[0] + "}" if "}" in xml_root.tag else ""
        element = xml_root.find(f"{namespace}version")
        if element is not None and element.text and not element.text.strip().startswith("${"):
            found["pom.xml"] = element.text.strip()
    return found


def changelog_sections(root: Path) -> dict[str, list[str]]:
    path = root / "CHANGELOG.md"
    if not path.is_file():
        raise GuardError("CHANGELOG.md is missing")
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            match = HEADING.fullmatch(line)
            if not match:
                current = None
                continue
            current = match.group(1)
            if current in sections:
                raise GuardError(f"duplicate CHANGELOG heading: {current}")
            sections[current] = [line]
        elif current is not None:
            sections[current].append(line)
    return sections


def release_section(root: Path, value: str) -> str:
    lines = changelog_sections(root).get(value)
    if not lines:
        raise GuardError(f"CHANGELOG.md lacks [{value}] section")
    category = False
    meaningful = False
    for line in lines[1:]:
        if line.startswith("### "):
            category = bool(SECTION.fullmatch(line))
        elif category and re.match(r"^\s*[-*] \S", line):
            item = re.sub(r"^\s*[-*] ", "", line).strip()
            if item and not PLACEHOLDER.match(item):
                meaningful = True
    if not meaningful:
        raise GuardError(f"CHANGELOG.md [{value}] needs a substantive categorized bullet")
    return "\n".join(lines).strip() + "\n"


def git_show(root: Path, ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=root, text=True, capture_output=True, check=False
    )
    return result.stdout if result.returncode == 0 else None


def check(root: Path, base_ref: str | None, tag: str | None) -> str:
    value = version(root)
    for name, actual in metadata_versions(root).items():
        if actual != value:
            raise GuardError(f"{name} version {actual!r} differs from VERSION {value!r}")
    changelog_sections(root)
    if base_ref:
        valid_ref = subprocess.run(
            ["git", "rev-parse", "--verify", f"{base_ref}^{{commit}}"],
            cwd=root, capture_output=True, check=False,
        )
        if valid_ref.returncode:
            raise GuardError(f"Git base ref does not exist: {base_ref}")
        old = git_show(root, base_ref, "VERSION")
        if old is not None and old.strip() != value:
            old_changelog = git_show(root, base_ref, "CHANGELOG.md") or ""
            if (root / "CHANGELOG.md").read_text(encoding="utf-8") == old_changelog:
                raise GuardError("VERSION changed without a CHANGELOG.md change")
            if re.search(rf"^## \[{re.escape(value)}\](?:\s|$)", old_changelog, re.MULTILINE):
                raise GuardError(f"[{value}] CHANGELOG section must be added with this version bump")
            release_section(root, value)
    if tag:
        if tag != f"v{value}":
            raise GuardError(f"tag {tag!r} differs from v{value}")
        release_section(root, value)
    return value


def publish_gitee(root: Path, tag: str, owner: str, repo: str, api_base: str) -> None:
    value = check(root, None, tag)
    token = os.environ.get("GITEE_TOKEN", "")
    if not token:
        raise GuardError("GITEE_TOKEN is missing")
    body = release_section(root, value)
    url = f"{api_base.rstrip('/')}/repos/{urllib.parse.quote(owner, safe='')}/{urllib.parse.quote(repo, safe='')}/releases"
    data = urllib.parse.urlencode({"access_token": token, "tag_name": tag, "name": tag, "body": body}).encode()
    request = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            if not isinstance(result, dict) or not result.get("id"):
                raise GuardError("Gitee release API returned no release id")
    except urllib.error.HTTPError as exc:
        raise GuardError(f"Gitee release API returned HTTP {exc.code}") from exc
    for artifact in sorted((root / "dist").glob("*")) if (root / "dist").is_dir() else []:
        if not artifact.is_file():
            continue
        boundary = uuid.uuid4().hex
        body_bytes = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"access_token\"\r\n\r\n{token}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{artifact.name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + artifact.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        upload = urllib.request.Request(
            f"{url}/{result['id']}/attach_files", data=body_bytes, method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        try:
            with urllib.request.urlopen(upload, timeout=60) as response:
                response.read()
        except urllib.error.HTTPError as exc:
            raise GuardError(f"Gitee asset upload returned HTTP {exc.code}") from exc
    print(f"Created Gitee release {tag}")


def publish_gitlab(root: Path, tag: str, project_id: str, api_base: str, project_url: str) -> None:
    value = check(root, None, tag)
    token = os.environ.get("CI_JOB_TOKEN", "")
    if not token:
        raise GuardError("CI_JOB_TOKEN is missing")
    payload: dict[str, object] = {"tag_name": tag, "name": tag, "description": release_section(root, value)}
    if project_url and (root / "dist").is_dir() and any((root / "dist").iterdir()):
        payload["assets"] = {"links": [{
            "name": "Build artifacts",
            "url": f"{project_url.rstrip('/')}/-/jobs/artifacts/{tag}/download?job=build",
            "link_type": "package",
        }]}
    url = f"{api_base.rstrip('/')}/projects/{urllib.parse.quote(project_id, safe='')}/releases"
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", "JOB-TOKEN": token},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status not in (200, 201):
                raise GuardError(f"GitLab release API returned HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        raise GuardError(f"GitLab release API returned HTTP {exc.code}") from exc
    print(f"Created GitLab release {tag}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    check_p = sub.add_parser("check")
    check_p.add_argument("--base-ref")
    check_p.add_argument("--tag")
    notes_p = sub.add_parser("notes")
    notes_p.add_argument("--tag", required=True)
    notes_p.add_argument("--output", type=Path, required=True)
    gitee_p = sub.add_parser("publish-gitee")
    gitee_p.add_argument("--tag", required=True)
    gitee_p.add_argument("--owner", required=True)
    gitee_p.add_argument("--repo", required=True)
    gitee_p.add_argument("--api-base", default="https://gitee.com/api/v5")
    gitlab_p = sub.add_parser("publish-gitlab")
    gitlab_p.add_argument("--tag", required=True)
    gitlab_p.add_argument("--project-id", required=True)
    gitlab_p.add_argument("--api-base", required=True)
    gitlab_p.add_argument("--project-url", default="")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "check":
            value = check(root, args.base_ref, args.tag)
            print(f"Version and changelog OK: {value}")
        elif args.command == "notes":
            value = check(root, None, args.tag)
            args.output.write_text(release_section(root, value), encoding="utf-8")
            print(f"Wrote {args.output}")
        elif args.command == "publish-gitee":
            publish_gitee(root, args.tag, args.owner, args.repo, args.api_base)
        else:
            publish_gitlab(root, args.tag, args.project_id, args.api_base, args.project_url)
    except GuardError as exc:
        print(f"version-guard: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
