#!/usr/bin/env python3
"""Render every page using an isolated LibreOffice profile and Poppler."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from verify import sha256, write_json


def run(command: list[str], timeout: int, record: list) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                                env={**os.environ, "LC_ALL": "C"})
    except subprocess.TimeoutExpired as exc:
        record.append({"command": command, "exit_status": None, "timed_out": True,
                       "stdout": str(exc.stdout or ""), "stderr": str(exc.stderr or "")})
        raise ValueError(f"Command timed out after {timeout}s") from exc
    record.append({"command": command, "exit_status": result.returncode,
                   "stdout": result.stdout, "stderr": result.stderr})
    if result.returncode:
        raise ValueError(f"Command exited {result.returncode}: {command[0]}")
    return result.stdout


def render(source: Path, out: Path, timeout: int = 120) -> dict:
    source, out = source.resolve(), out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("Render destination must be empty; use a fresh directory for each revision")
    before = sha256(source)
    if source.suffix.lower() not in (".docx", ".xlsx", ".pptx", ".pdf"):
        raise ValueError("Expected .docx, .xlsx, .pptx or .pdf")
    out.mkdir(parents=True, exist_ok=True)
    report = {"file": str(source), "sha256": before, "status": "failed", "quality_status": "pending",
              "commands": [], "pages": [], "note": "Rendering is evidence, not a visual review. Inspect every image."}
    try:
        pdf = out / (source.stem + ".pdf")
        if source.suffix.lower() == ".pdf":
            shutil.copy2(source, pdf)
        else:
            office = shutil.which("libreoffice") or shutil.which("soffice")
            if not office:
                raise ValueError("Missing LibreOffice")
            with tempfile.TemporaryDirectory(prefix="office-render-") as temp:
                work = Path(temp)
                incoming = work / "input"
                incoming.mkdir()
                copied = incoming / source.name
                shutil.copy2(source, copied)
                run([office, f"-env:UserInstallation={(work / 'profile').as_uri()}", "--headless",
                     "--convert-to", "pdf", "--outdir", str(out), str(copied)], timeout, report["commands"])
        if not pdf.is_file() or pdf.stat().st_size == 0:
            raise ValueError("Conversion produced no PDF (exit status alone is insufficient)")
        info = run(["pdfinfo", str(pdf)], timeout, report["commands"])
        match = re.search(r"^Pages:\s+(\d+)", info, re.M)
        if not match or int(match.group(1)) < 1:
            raise ValueError("PDF has no verifiable pages")
        run(["pdftoppm", "-png", "-r", "120", str(pdf), str(out / "page")], timeout, report["commands"])
        pages = sorted(out.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        if len(pages) != int(match.group(1)) or any(p.stat().st_size == 0 for p in pages):
            raise ValueError("Rendered page coverage differs from PDF page count")
        report.update(status="rendered", pdf=str(pdf), page_count=len(pages),
                      pages=[{"file": str(p), "sha256": sha256(p)} for p in pages])
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    report["input_unchanged"] = sha256(source) == before
    if not report["input_unchanged"]:
        report["status"] = "failed"
        report["error"] = "Input hash changed during rendering"
    write_json(out / "render.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    try:
        if args.timeout <= 0:
            raise ValueError("Timeout must be positive")
        result = render(args.file, args.out_dir, args.timeout)
    except Exception as exc:
        result = {"status": "failed", "quality_status": "pending", "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "rendered" else 1)
