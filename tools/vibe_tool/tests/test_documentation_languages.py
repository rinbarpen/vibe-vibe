"""Chinese and English documentation have independent, linked entry points."""

from __future__ import annotations

import re
import shlex
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from vibe_tool.skill import add_skill


ROOT = Path(__file__).resolve().parents[3]
PAIRS = (
    ("README.md", "README_EN.md"),
    ("mine/omnidraw/references/visualization-scenarios.md",
     "mine/omnidraw/references/visualization-scenarios_EN.md"),
    ("docs/manifest-workflow.md", "docs/manifest-workflow_EN.md"),
)


def markdown_links(text):
    prose = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.S)
    return re.findall(r"\[([^\]]*)\]\(([^)]+)\)", prose)


def bash_commands(text):
    return [shlex.split(block, comments=True)
            for block in re.findall(r"```bash\n(.*?)```", text, re.S)]


@pytest.mark.parametrize("chinese,english", PAIRS)
def test_language_pairs_are_separate_and_switch_to_their_counterpart(chinese, english):
    cn, en = ROOT / chinese, ROOT / english
    assert cn.resolve() != en.resolve()
    cn_text, en_text = cn.read_text(), en.read_text()
    assert "**简体中文**" in cn_text.splitlines()[2]
    assert "**English**" in en_text.splitlines()[2]
    assert ("English", en.name) in markdown_links(cn_text)
    assert ("简体中文", cn.name) in markdown_links(en_text)
    assert any("\u4e00" <= char <= "\u9fff" for char in cn_text.splitlines()[0] + cn_text.splitlines()[4])


@pytest.mark.parametrize("chinese,english", PAIRS)
def test_translations_preserve_executable_examples(chinese, english):
    assert bash_commands((ROOT / chinese).read_text()) == bash_commands((ROOT / english).read_text())


@pytest.mark.parametrize("chinese,english", PAIRS)
def test_translations_keep_corresponding_section_structure(chinese, english):
    def shape(name):
        text = re.sub(r"```[^\n]*\n.*?```", "", (ROOT / name).read_text(), flags=re.S)
        return [len(level) for level in re.findall(r"^(#{2,6})\s+", text, re.M)]

    assert shape(chinese) == shape(english)


@pytest.mark.parametrize("english", [pair[1] for pair in PAIRS])
def test_english_prose_keeps_chinese_only_in_the_language_switch(english):
    text = (ROOT / english).read_text()
    text = re.sub(r"\[简体中文\]\([^)]+\)", "", text)
    assert not re.search(r"[\u4e00-\u9fff]", text)


def test_readme_normal_reading_links_use_the_corresponding_language():
    for name, preferred, alternate in (
        ("README.md", {p[0] for p in PAIRS[1:]}, {p[1] for p in PAIRS[1:]}),
        ("README_EN.md", {p[1] for p in PAIRS[1:]}, {p[0] for p in PAIRS[1:]}),
    ):
        links = markdown_links((ROOT / name).read_text())
        # The language table offers both editions. Outside that table, each
        # preferred guide is linked again by the corresponding usage section.
        for destination in preferred:
            assert sum(urlsplit(href).path == destination for _, href in links) >= 2
        for label, href in links:
            if urlsplit(href).path in alternate:
                assert re.search(r"English|英文|Chinese|中文", label), (name, label, href)


def test_all_document_links_and_readme_anchors_resolve():
    for relative in (p for pair in PAIRS for p in pair):
        document = ROOT / relative
        for _, href in markdown_links(document.read_text()):
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            target = document.parent / unquote(parsed.path) if parsed.path else document
            assert target.exists(), (relative, href)
            if parsed.fragment and target.is_file():
                headings = re.findall(r"^#{1,6}\s+(.+)$", target.read_text(), re.M)
                anchors = {re.sub(r"[^\w\- ]", "", h.lower().replace("`", "")).replace(" ", "-")
                           for h in headings}
                assert unquote(parsed.fragment) in anchors, (relative, href)


def test_both_scene_guides_ship_with_omnidraw_and_cross_links_work(tmp_path):
    target = tmp_path / "installed project"
    assert add_skill((ROOT / "skills", ROOT / "mine"), "omnidraw", target) == 0
    installed = target / ".agents/skills/omnidraw/references"
    for name in ("visualization-scenarios.md", "visualization-scenarios_EN.md"):
        assert (installed / name).read_bytes() == (ROOT / "mine/omnidraw/references" / name).read_bytes()
        for _, href in markdown_links((installed / name).read_text()):
            parsed = urlsplit(href)
            if not parsed.scheme and parsed.path:
                assert (installed / parsed.path).exists(), (name, href)
