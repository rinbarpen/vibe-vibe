"""Versioned, project-local provenance for installed manifests and skills."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

SCHEMA_VERSION = 1
INSTALLATIONS_RELATIVE_PATH = Path(".vibe-tool/installations.json")

# Only options that alter generated template resources belong in provenance.
_MANIFEST_OPTION_KEYS: dict[str, tuple[str, ...]] = {
    "vibe-coding": ("provider", "scenario", "owner", "org", "repo", "email"),
    "github-enterprise": ("owner", "org", "repo", "email"),
    "auto-research": ("owner", "org", "repo"),
    "knowledge-learning": ("scenario",),
    "ui-testing": ("scenario",),
}


def manifest_option_keys(name: str) -> tuple[str, ...]:
    """Return the generation options supported by the named template."""
    return _MANIFEST_OPTION_KEYS.get(name, ())


def normalized_options(name: str, options: dict) -> dict[str, str]:
    """Keep applicable options, including empty values for template defaults."""
    result: dict[str, str] = {}
    for key in manifest_option_keys(name):
        value = options.get(key, "github" if key == "provider" else "")
        if value is None:
            value = "github" if key == "provider" else ""
        if not isinstance(value, str):
            raise ValueError(f"Manifest option {key!r} must be a string")
        result[key] = value
    return result


def _validate_name(name: object) -> None:
    if (
        not isinstance(name, str) or not name or name in (".", "..")
        or any(char in name for char in ("/", "\\", "\x00"))
    ):
        raise ValueError(f"Invalid installation name: {name!r}")


def _validate_source(source: object) -> None:
    if not isinstance(source, str) or not source or "\\" in source or "\x00" in source:
        raise ValueError(f"Invalid installation source: {source!r}")
    path = PurePosixPath(source)
    if path.is_absolute() or PureWindowsPath(source).drive or source != path.as_posix() or any(
        part in ("", ".", "..") for part in source.split("/")
    ):
        raise ValueError(f"Installation source must be a repository-relative path: {source!r}")


def _validate_installations(data: object) -> dict:
    if not isinstance(data, dict) or set(data) != {"schema_version", "skills", "manifests"}:
        raise ValueError("Invalid installations record: expected schema_version, skills and manifests")
    if type(data["schema_version"]) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"Unsupported installations schema: {data['schema_version']!r}")
    for group in ("skills", "manifests"):
        entries = data[group]
        if not isinstance(entries, dict):
            raise ValueError(f"Invalid installations {group}: expected an object")
        for name, entry in entries.items():
            _validate_name(name)
            keys = {"source", "options"} if group == "manifests" else {"source"}
            if not isinstance(entry, dict) or set(entry) != keys:
                raise ValueError(f"Invalid installation entry for {name!r}")
            _validate_source(entry["source"])
            if group == "manifests":
                options = entry["options"]
                if not isinstance(options, dict) or set(options) != set(manifest_option_keys(name)):
                    raise ValueError(f"Invalid manifest options for {name!r}")
                if any(not isinstance(value, str) for value in options.values()):
                    raise ValueError(f"Manifest options for {name!r} must be strings")
    return data


def _metadata_path(target: Path) -> Path:
    """Reject linked provenance paths, including links outside the project."""
    target = Path(target).resolve()
    metadata = target / INSTALLATIONS_RELATIVE_PATH
    for path in (metadata.parent, metadata):
        if not path.resolve().is_relative_to(target):
            raise ValueError(f"Installation metadata path leaves target project: {path}")
        if path.is_symlink():
            raise ValueError(f"Installation metadata must not be a symbolic link: {path}")
    if metadata.parent.exists() and not metadata.parent.is_dir():
        raise ValueError(f"Installation metadata directory is not a directory: {metadata.parent}")
    if metadata.exists() and not metadata.is_file():
        raise ValueError(f"Installation metadata is not a file: {metadata}")
    return metadata


def load_installations(target: Path) -> dict:
    """Read validated provenance, or return an empty v1 record if absent."""
    metadata = _metadata_path(target)
    if not metadata.exists():
        return {"schema_version": SCHEMA_VERSION, "skills": {}, "manifests": {}}
    try:
        data = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid installations record at {metadata}: {error}") from error
    return _validate_installations(data)


def write_installations(target: Path, data: dict) -> None:
    """Validate and atomically replace provenance; never truncate prior data."""
    _validate_installations(data)
    metadata = _metadata_path(target)
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if metadata.exists() and metadata.read_text(encoding="utf-8") == payload:
        return
    metadata.parent.mkdir(parents=True, exist_ok=True)
    _metadata_path(target)
    mode = stat.S_IMODE(metadata.stat().st_mode) if metadata.exists() else 0o600
    fd, temporary = tempfile.mkstemp(prefix=".installations-", suffix=".json", dir=metadata.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        _metadata_path(target)
        os.replace(temporary, metadata)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def source_ref(root: Path, source: Path) -> str:
    """Describe a source lexically relative to its repository, preserving aliases."""
    root = Path(os.path.abspath(root))
    source = Path(os.path.abspath(source))
    try:
        relative = source.relative_to(root).as_posix()
    except ValueError as error:
        raise ValueError(f"Installation source is outside the repository: {source}") from error
    _validate_source(relative)
    return relative


def skill_entry(root: Path, source: Path) -> dict:
    return {"source": source_ref(root, source)}


def record_skill(
    root: Path, target: Path, name: str, source: Path, *, force: bool = False,
) -> None:
    data = load_installations(target)
    if name in data["skills"] and not force:
        return
    data["skills"][name] = skill_entry(root, source)
    write_installations(target, data)


def record_manifest(
    root: Path, target: Path, name: str, source: Path, options: dict,
    *, force: bool = False,
) -> None:
    data = load_installations(target)
    if name in data["manifests"] and not force:
        return
    data["manifests"][name] = {
        "source": source_ref(root, source), "options": normalized_options(name, options),
    }
    write_installations(target, data)
