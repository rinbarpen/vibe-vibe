#!/usr/bin/env python3
"""Submit manuscript text to an OpenAI-compatible gptweb chat-completions API."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from review_requirements import fetch_guidelines, load_requirements, make_snapshot, venue_prompt


PROMPT_PATH = Path(__file__).resolve().parents[1] / "references" / "iclr-review-prompt.md"
REQUIRED_ENV = ("GPTWEB_BASE_URL", "GPTWEB_API_KEY", "GPTWEB_MODEL")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="UTF-8 manuscript/supplement text or Markdown files")
    parser.add_argument("--output", type=Path, required=True, help="Path for the independent review report")
    parser.add_argument("--venue", help="Target journal or conference")
    parser.add_argument("--year", help="Submission year or cycle")
    parser.add_argument("--track", help="Conference track or journal article type")
    parser.add_argument("--guidelines-url", help="Official reviewer-guidelines page URL (HTTP/HTTPS)")
    parser.add_argument("--requirements-file", type=Path, help="JSON snapshot containing venue and explicit criteria")
    parser.add_argument("--requirements-output", type=Path, help="Write fetched guideline source snapshot as JSON")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        print("GPTWEB_NOT_RUN: missing configuration: " + ", ".join(missing), file=sys.stderr)
        return 2

    try:
        manuscript_parts = []
        for path in args.inputs:
            manuscript_parts.append(f"\n\n===== SOURCE: {path.name} =====\n{path.read_text(encoding='utf-8')}")
        prompt = PROMPT_PATH.read_text(encoding="utf-8")
        if args.requirements_file and args.guidelines_url:
            raise ValueError("choose either --requirements-file or --guidelines-url")
        snapshot = None
        venue = args.venue
        if args.requirements_file:
            snapshot = load_requirements(args.requirements_file)
            if venue and venue.casefold() != str(snapshot["venue"]).casefold():
                raise ValueError("--venue does not match the venue in --requirements-file")
            venue = venue or str(snapshot["venue"])
        elif args.guidelines_url:
            if not venue:
                raise ValueError("--venue is required with --guidelines-url")
            source = fetch_guidelines(args.guidelines_url, timeout=min(args.timeout, 60))
            snapshot = make_snapshot(venue, args.year, args.track, source)
            if args.requirements_output:
                args.requirements_output.parent.mkdir(parents=True, exist_ok=True)
                args.requirements_output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif args.requirements_output:
            raise ValueError("--requirements-output requires --guidelines-url")
        if venue:
            prompt = prompt.replace("ICLR", "target venue")
            prompt = re.sub(
                r"随后给出 target venue 风格 1–10 分：.*?评分必须与上述评审一致，不得只给分数或以单一小问题决定结论。",
                "评分与建议优先采用已提供的官方 venue rubric；若来源未定义评分量表，则不给虚构的 venue score，只提供定性判断。",
                prompt,
                count=1,
                flags=re.DOTALL,
            )
            prompt += venue_prompt(snapshot, venue)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    base_url = os.environ["GPTWEB_BASE_URL"].rstrip("/")
    endpoint = base_url if base_url.endswith("/chat/completions") else base_url + "/chat/completions"
    payload = {
        "model": os.environ["GPTWEB_MODEL"],
        "messages": [
            {"role": "system", "content": "你是独立审稿人。直接依据用户提供的完整论文材料评审；不要接收或假定存在其他审稿意见。"},
            {"role": "user", "content": prompt + "\n\n以下是论文原始材料：" + "".join(manuscript_parts)},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {os.environ['GPTWEB_API_KEY']}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        review = result["choices"][0]["message"]["content"]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(review.rstrip() + "\n", encoding="utf-8")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, OSError) as exc:
        print(f"GPTWEB_REVIEW_FAILED: {exc}", file=sys.stderr)
        return 1

    print(f"GPTWEB_REVIEW_SAVED: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
