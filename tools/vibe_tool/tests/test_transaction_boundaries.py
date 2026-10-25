"""Fail before writes at backup and atomic leaf-replacement boundaries."""

from pathlib import Path

import pytest

from vibe_tool import transaction


@pytest.mark.parametrize("relative", [".vibe-tool", ".vibe-tool/backups", ".vibe-tool/other", ".git/config"])
def test_reserved_paths_fail_before_backup(tmp_path: Path, relative: str) -> None:
    target = tmp_path / "project"
    target.mkdir()
    source = tmp_path / "new"
    source.write_text("replacement")
    assert transaction.apply_update(
        target, [transaction.Change(Path(relative), source)], label="reserved",
    ) == 1
    assert list(target.iterdir()) == []


def test_atomic_file_replace_failure_preserves_original_node(tmp_path: Path, monkeypatch) -> None:
    source, dest = tmp_path / "source", tmp_path / "dest"
    source.write_text("replacement")
    dest.write_text("original")

    def fail_replace(*args):
        raise OSError("injected rename failure")

    monkeypatch.setattr(transaction.os, "replace", fail_replace)
    with pytest.raises(OSError, match="rename failure"):
        transaction._replace(source, dest)
    assert dest.read_text() == "original"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["dest", "source"]


def test_directory_to_leaf_link_conflict_is_preflighted(tmp_path: Path) -> None:
    target = tmp_path / "project"
    (target / "CLAUDE.md").mkdir(parents=True)
    (target / "CLAUDE.md/valuable.txt").write_text("project content")
    source = tmp_path / "new-link"
    source.symlink_to("MANIFEST.md")
    assert transaction.apply_update(
        target, [transaction.Change(Path("CLAUDE.md"), source)], label="conflict",
    ) == 1
    assert (target / "CLAUDE.md/valuable.txt").read_text() == "project content"
    assert not (target / ".vibe-tool").exists()
