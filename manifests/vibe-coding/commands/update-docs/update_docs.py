#!/usr/bin/env python3
"""Read-only Markdown structure/link audit; review signals are not quality scores."""
from __future__ import annotations

import argparse
from collections import Counter
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
LINK = re.compile(r'!?\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\s*\)')
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")


def prose_lines(text):
    """Keep source line numbers; ignore fenced examples and HTML comments."""
    result = []
    opened = None
    comment = False
    for number, line in enumerate(text.splitlines(), 1):
        fence = FENCE.match(line) if not comment else None
        if fence:
            marker, tail = fence.groups()
            if opened is None:
                opened = (marker[0], len(marker), number)
            elif marker[0] == opened[0] and len(marker) >= opened[1] and not tail.strip():
                opened = None
            continue
        if opened:
            continue
        visible = []
        while line:
            if comment:
                _, separator, line = line.partition("-->")
                if not separator:
                    break
                comment = False
            else:
                before, separator, after = line.partition("<!--")
                visible.append(before)
                if not separator:
                    break
                comment, line = True, after
        result.append((number, "".join(visible)))
    return result, opened


def anchors(text):
    seen = Counter()
    result = set(re.findall(r'<a\b[^>]*\b(?:id|name)=["\']([^"\']+)', text, re.I))
    for _, line in prose_lines(text)[0]:
        match = HEADING.match(line)
        if not match:
            continue
        heading = html.unescape(match[2])
        heading = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"<[^>]+>", "", heading).lower()
        slug = re.sub(r"[^\w\- ]", "", heading.replace("`", "")).replace(" ", "-")
        count = seen[slug]
        result.add(f"{slug}-{count}" if count else slug)
        seen[slug] += 1
    return result


def collect(root, inputs):
    files = set()
    for value in inputs or ["README.md"]:
        path = Path(value)
        path = path if path.is_absolute() else root / path
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError(f"Input leaves the selected root: {value}")
        if not path.exists():
            raise ValueError(f"Missing input: {value}")
        if path.is_dir():
            for item in path.rglob("*.md"):
                relative = item.relative_to(path)
                if not any(part.startswith(".") or part in {"node_modules", "vendor"} for part in relative.parts):
                    if not item.resolve().is_relative_to(root):
                        raise ValueError(f"Input symlink leaves the selected root: {item}")
                    files.add(item)
        elif path.is_file():
            files.add(path)
        else:
            raise ValueError(f"Unsupported input: {value}")
    if not files:
        raise ValueError("No Markdown files selected")
    return sorted(files)


def inspect_document(path, root):
    text = path.read_text(encoding="utf-8")
    lines, opened = prose_lines(text)
    errors, warnings = [], []
    external = 0
    relative = str(path.relative_to(root))

    def issue(bucket, code, line, message):
        bucket.append({"file": relative, "line": line, "code": code, "message": message})

    if opened:
        issue(errors, "unclosed-fence", opened[2], "Close the fenced code example with the same marker.")
    if not any(HEADING.match(line) and HEADING.match(line)[1] == "#" for _, line in lines):
        issue(warnings, "missing-title", 1, "Review whether this document needs a clear title.")
    paragraph, paragraph_line, table_rows, table_line = [], 0, 0, 0

    def flush_paragraph():
        if len(" ".join(paragraph)) > 420:
            issue(warnings, "long-paragraph", paragraph_line,
                  "Review for multiple ideas; length alone does not establish readability.")
        paragraph.clear()

    def flush_table():
        nonlocal table_rows
        if table_rows > 12:
            issue(warnings, "long-table", table_line,
                  "Review whether this is reference material that belongs off the landing page.")
        table_rows = 0

    for number, line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            flush_paragraph()
            if not table_rows:
                table_line = number
            table_rows += 1
        else:
            flush_table()
            if not stripped or HEADING.match(line) or re.match(r"^\s*(?:[-*>]|\d+[.)])\s", line) or stripped.startswith("<"):
                flush_paragraph()
            else:
                if not paragraph:
                    paragraph_line = number
                paragraph.append(stripped)
        visible = re.sub(r"`+[^`]*`+", "", line)
        for match in LINK.finditer(visible):
            href = html.unescape(match[1].strip("<>"))
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                external += 1
                continue
            if not parsed.path and not parsed.fragment:
                continue
            target = path.parent / unquote(parsed.path) if parsed.path else path
            resolved = target.resolve()
            if not resolved.is_relative_to(root):
                issue(errors, "outside-link", number, f"Local link leaves the selected root: {href}")
            elif not target.exists():
                issue(errors, "missing-link", number, f"Missing local link target: {href}")
            elif parsed.fragment and target.is_file() and target.suffix.lower() in {".md", ".mdc"}:
                if unquote(parsed.fragment) not in anchors(target.read_text(encoding="utf-8")):
                    issue(errors, "missing-anchor", number, f"Missing heading anchor: {href}")
    flush_paragraph()
    flush_table()
    return errors, warnings, external


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Markdown files/directories, relative to --root")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Explicit local documentation root")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    errors, warnings, external = [], [], 0
    try:
        root = args.root.resolve()
        if not root.is_dir():
            raise ValueError(f"Missing root: {root}")
        files = collect(root, args.paths)
        for path in files:
            found_errors, found_warnings, skipped = inspect_document(path, root)
            errors.extend(found_errors)
            warnings.extend(found_warnings)
            external += skipped
        status, code = ("STRUCTURE_ERRORS", 1) if errors else ("STRUCTURE_OK", 0)
    except (OSError, ValueError, UnicodeError) as error:
        status, code, files = "INPUT_ERROR", 2, []
        errors.append({"code": "input-error", "message": str(error)})
    report = {"status": status, "files_checked": len(files), "errors": errors,
              "warnings": warnings, "external_links_not_checked": external,
              "limits": "Read-only structure checks; no readability score, code execution, or external-link validation."}
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{status}: {len(files)} document(s), {len(errors)} structural error(s), {len(warnings)} review signal(s).")
        for level, values in (("ERROR", errors), ("REVIEW", warnings)):
            for item in values:
                location = f'{item.get("file", "input")}:{item.get("line", 0)}'
                print(f'{level} {location} [{item["code"]}] {item["message"]}')
        print(report["limits"])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
