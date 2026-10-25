#!/usr/bin/env python3
"""Read-only Office dependency inventory. No installation or config changes."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys


def inspect() -> dict:
    python = {
        package: {"available": importlib.util.find_spec(module) is not None}
        for package, module in {
            "python-docx": "docx", "openpyxl": "openpyxl", "xlsxwriter": "xlsxwriter",
            "python-pptx": "pptx", "pypdf": "pypdf", "Pillow": "PIL",
        }.items()
    }
    commands = {name: shutil.which(name) for name in
                ("node", "libreoffice", "soffice", "pdftoppm", "pdfinfo", "fc-list", "pandoc", "tesseract")}
    node = {}
    for package in ("docx", "pptxgenjs", "sharp"):
        available = False
        if commands["node"]:
            result = subprocess.run(
                [commands["node"], "-e", "require.resolve(process.argv[1])", package],
                capture_output=True, text=True, timeout=15,
            )
            available = result.returncode == 0
        node[package] = {"available": available}
    families = []
    if commands["fc-list"]:
        result = subprocess.run([commands["fc-list"], ":lang=zh", "family"],
                                capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            families = sorted(set(result.stdout.splitlines()))
    missing = [name for name, info in python.items() if not info["available"]]
    missing += [f"node:{name}" for name, info in node.items() if not info["available"]]
    if not (commands["libreoffice"] or commands["soffice"]):
        missing.append("LibreOffice")
    missing += [name for name in ("pdftoppm", "pdfinfo") if not commands[name]]
    if not families:
        missing.append("CJK fonts (or fontconfig evidence)")
    return {
        "status": "ready" if not missing else "dependencies_missing",
        "python_executable": sys.executable, "python": python, "node": node,
        "commands": commands, "cjk_fonts": families, "missing": missing,
        "notes": ["Inventory only; no document QA has run.",
                  "pandoc and tesseract are optional; required only for routes that use them.",
                  "Run from the project root so Node resolution uses the project's node_modules."],
        "setup": ["uv run --with python-docx --with openpyxl --with xlsxwriter --with python-pptx --with pypdf --with pillow python office/scripts/doctor.py",
                  "For JS authoring install docx, pptxgenjs and sharp in an isolated project environment.",
                  "Install LibreOffice, Poppler and appropriate CJK fonts through your OS package manager when needed."],
    }


if __name__ == "__main__":
    try:
        report = inspect()
    except (OSError, subprocess.SubprocessError) as exc:
        report = {"status": "inspection_failed", "error": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"] == "ready" else 1)
