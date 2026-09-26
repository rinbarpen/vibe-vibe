from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gptweb_review  # noqa: E402
from review_requirements import fetch_guidelines, load_requirements, make_snapshot, venue_prompt  # noqa: E402


def test_fetch_guidelines_extracts_page_text_and_omits_script_content() -> None:
    class Response:
        headers = {"Content-Type": "text/html; charset=utf-8"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self, _limit):
            return b"<html><h1>Review form</h1><script>secret()</script><p>Assess novelty.</p></html>"

        def geturl(self):
            return "https://venue.example/review"

    with patch("review_requirements.urlopen", return_value=Response()):
        result = fetch_guidelines("https://venue.example/review")
    assert "Review form" in result["text"]
    assert "Assess novelty." in result["text"]
    assert "secret" not in result["text"]


def test_requirements_snapshot_and_prompt_preserve_source_and_criteria(tmp_path: Path) -> None:
    path = tmp_path / "requirements.json"
    path.write_text(json.dumps({"venue": "Fixture Journal", "source_url": "https://fixture.example/review",
                                "requirements": [{"criterion": "Assess reproducibility"}]}), encoding="utf-8")
    data = load_requirements(path)
    text = venue_prompt(data)
    assert "Fixture Journal" in text
    assert "Assess reproducibility" in text
    assert "https://fixture.example/review" in text
    assert make_snapshot("Fixture Journal", "2026", "research", {"url": "https://fixture.example/review", "text": "rubric"})["year"] == "2026"


def test_cli_fetches_and_attaches_venue_guidelines(tmp_path: Path, monkeypatch, capsys) -> None:
    paper = tmp_path / "paper.txt"
    paper.write_text("Manuscript text", encoding="utf-8")
    output = tmp_path / "review.md"
    snapshot = tmp_path / "venue.json"

    class Response:
        headers = {"Content-Type": "text/html"}

        def __init__(self, data: bytes, url: str):
            self.data, self.url = data, url

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self, *_args):
            return self.data

        def geturl(self):
            return self.url

    seen: dict[str, str] = {}

    def fake_urlopen(request, timeout):
        if request.data is None:
            return Response(b"<p>Evaluate contribution and rigor</p>", request.full_url)
        payload = json.loads(request.data.decode("utf-8"))
        seen["prompt"] = payload["messages"][1]["content"]
        return Response(json.dumps({"choices": [{"message": {"content": "Venue-specific review"}}]}).encode(), "https://api.example")

    monkeypatch.setenv("GPTWEB_BASE_URL", "https://api.example/v1")
    monkeypatch.setenv("GPTWEB_API_KEY", "fixture-key")
    monkeypatch.setenv("GPTWEB_MODEL", "fixture-model")
    monkeypatch.setattr(sys, "argv", ["gptweb_review.py", str(paper), "--output", str(output), "--venue", "Fixture Conference",
                                      "--year", "2026", "--guidelines-url", "https://venue.example/review",
                                      "--requirements-output", str(snapshot)])
    with patch("review_requirements.urlopen", side_effect=fake_urlopen), patch("gptweb_review.urllib.request.urlopen", side_effect=fake_urlopen):
        assert gptweb_review.main() == 0
    assert "Fixture Conference" in seen["prompt"]
    assert "Evaluate contribution and rigor" in seen["prompt"]
    assert "target venue" in seen["prompt"]
    assert "不给虚构的 venue score" in seen["prompt"]
    assert "贡献大于缺陷时给 6–10 分" not in seen["prompt"]
    assert json.loads(snapshot.read_text(encoding="utf-8"))["source_url"] == "https://venue.example/review"
    assert output.read_text(encoding="utf-8") == "Venue-specific review\n"
