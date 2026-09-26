"""Venue-aware review prompt and official-guideline snapshot helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


def fetch_guidelines(url: str, timeout: int = 30) -> dict[str, str]:
    """Fetch a text/HTML official guideline page, retaining source metadata."""
    if not url.startswith(("https://", "http://")):
        raise ValueError("guidelines URL must use http(s)")
    request = Request(url, headers={"User-Agent": "auto-research-venue-review/1.0"})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read(2_000_000)
        content_type = response.headers.get("Content-Type", "")
        source_url = response.geturl()
    if "pdf" in content_type.lower() or raw.startswith(b"%PDF"):
        raise ValueError("PDF guideline URL detected; provide extracted text via --requirements-file")
    text = raw.decode("utf-8", errors="replace")
    if "html" in content_type.lower() or re.search(r"<\s*html\b", text, re.I):
        parser = _TextExtractor()
        parser.feed(text)
        text = "\n".join(parser.parts)
    return {"url": source_url, "content_type": content_type, "text": text[:100_000]}


def load_requirements(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("requirements JSON must contain an object")
    if not data.get("venue") or not isinstance(data.get("requirements"), list):
        raise ValueError("requirements JSON needs 'venue' and a 'requirements' list")
    return data


def make_snapshot(venue: str, year: str | None, track: str | None, source: dict[str, str]) -> dict:
    return {
        "venue": venue,
        "year": year,
        "track": track,
        "source_url": source["url"],
        "source_validation": "user-supplied URL; domain not automatically verified",
        "content_type": source.get("content_type", "text/plain"),
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "source-fetched-requirements-to-be-extracted-by-reviewer",
        "source_text": source["text"],
    }


def venue_prompt(snapshot: dict | None, venue: str | None = None) -> str:
    if snapshot is None:
        if not venue:
            return ""
        return (f"\n\n## Venue context: {venue}\n"
                "No official reviewer-guideline snapshot was supplied. Do not invent venue-specific requirements or scoring rules. "
                "Perform the general scholarly review and explicitly mark venue-specific criteria as unavailable.")
    payload = json.dumps(snapshot, ensure_ascii=False, indent=2)
    return (
        "\n\n## Target-venue review requirements\n"
        "Target venue/year/track and source snapshot follow. First extract the applicable review criteria, "
        "questions, score labels, and recommendation semantics from the supplied source. Check whether the source "
        "domain is plausibly controlled by the venue/publisher; if that cannot be established from the material, "
        "mark it unverified. Apply verified criteria in addition to the general scholarly review. Preserve source "
        "wording where useful, distinguish requirements from "
        "your interpretation, cite the source URL and relevant source section, and mark ambiguous or unavailable "
        "items rather than guessing. Do not infer that a venue rank is itself an acceptance criterion.\n\n"
        "```json\n" + payload + "\n```\n"
        "Report: (1) the extracted venue rubric, (2) criterion-by-criterion assessment with manuscript evidence "
        "locations, (3) the venue's scoring/recommendation only when explicitly supported by the source, and "
        "(4) source coverage and any uncertainty. Keep the venue-specific judgment separate from generic quality judgment."
    )
