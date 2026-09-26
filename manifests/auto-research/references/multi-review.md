# Parallel independent paper review

## Default review dispatch

For a complete pre-submission review, start three independent reviewers in parallel:

| Reviewer | Skill / route | Independent output |
|---|---|---|
| `paper-reviewer-paper-review` | `paper-review` | Evidence-based review with claim/evidence locations and frontier/baseline analysis |
| `paper-reviewer-academic` | `academic-paper-reviewer full` | Full academic reviewer report |
| `paper-reviewer-gptweb` | `scripts/gptweb_review.py` + `references/iclr-review-prompt.md` | General review plus target-venue rubric when supplied |

Each reviewer starts a fresh session and receives the original manuscript plus appendices/supplementary files directly. Do not pass a runner-written summary, a filtered concern list, or any other reviewer's conclusions. Preserve each report separately under the research project's `outputs/` (for example, `review_<id>_paper-review.md`, `review_<id>_academic.md`, and `review_<id>_gptweb.md`). Include timestamp, route/skill, model identity when available, input file list, and status in `MANIFEST.md`.

The third route takes UTF-8 text or Markdown. For PDFs, first extract text while preserving page boundaries and labels, for example `pdftotext -layout paper.pdf paper.txt`; extract supplementary PDFs separately and pass all files as inputs. Include tables, captions, references, and appendix content. A reviewer should cite the source filename and page/section/table/figure/equation/appendix label where available. Binary PDFs are not sent as raw bytes by the helper.

## gptweb API configuration and invocation

Configure credentials outside the repository; never commit or print the API key:

```bash
export GPTWEB_BASE_URL="https://<gptweb-host>/v1"
export GPTWEB_API_KEY="<secret>"
export GPTWEB_MODEL="<model-id>"
python3 manifests/auto-research/scripts/gptweb_review.py \
  paper.txt supplement.txt --output outputs/review_<id>_gptweb.md
```

For a venue-specific review, provide the journal/conference, cycle, track or article type,
and an official reviewer-guidelines page. The helper fetches and snapshots the page text;
the reviewer extracts criteria and scoring semantics from that source before assessing
the manuscript. The URL is fetched but its ownership is not automatically certified, so
use the venue/publisher's official domain and preserve that provenance. Keep the snapshot
with the report for reproducibility:

```bash
python3 manifests/auto-research/scripts/gptweb_review.py \
  paper.txt supplement.txt --venue "VENUE_NAME" --year 2026 --track "TRACK_OR_ARTICLE_TYPE" \
  --guidelines-url "https://OFFICIAL_VENUE_HOST/reviewer-guidelines" \
  --requirements-output outputs/review_<id>_venue-requirements.json \
  --output outputs/review_<id>_gptweb.md
```

If guidelines are behind login, available only as a PDF, or already extracted, pass a
JSON requirements snapshot with `--requirements-file` (see
`venue-review-requirements.example.json`). The JSON must identify the venue and provide
an explicit `requirements` array; cite the official source URL and section in each item.
Only use venue-published reviewer forms/guidelines or official calls/instructions. CCF-A
or SCI Q1 classification can identify the venue context, but is not a substitute for its
review rubric. When no official rubric is available, the prompt marks venue criteria as
unavailable and does not invent a venue score. Without `--venue`, existing ICLR behavior
is preserved.

The helper sends an OpenAI-compatible `POST {GPTWEB_BASE_URL}/chat/completions` request, unless `GPTWEB_BASE_URL` already ends in `/chat/completions`. It uses Bearer authentication and writes the assistant message to the requested output path. On missing configuration it reports `GPTWEB_NOT_RUN` and exits 2; on transport/response failure it reports `GPTWEB_REVIEW_FAILED` and exits 1. In either case record the gptweb route as not completed and proceed with the other independent reviews; do not invent a report.

## Synthesis

Only after all completed reviewers have saved their reports, create a synthesis that:

1. Preserves each reviewer's score, recommendation, strengths, weaknesses, and evidence-based reasoning verbatim or by clearly attributed summary.
2. Identifies substantive agreement and disagreement, tying disputed judgments to manuscript evidence and distinguishing factual disputes from different value judgments.
3. Compares the magnitude of supported contributions with the severity of limitations, explicitly choosing contribution-greater, roughly-equal/moderate, or weakness-greater.
4. Gives an overall recommendation using the target venue's official scale when available; otherwise use a reasoned qualitative synthesis without inventing a venue score. Do not compute a simple mean. Retain individual scores and explain any difference from them.
5. Lists actionable revision priorities. Mark unavailable reviewers as not completed and do not treat missing reviews as positive or negative evidence.

Keep the synthesis as a separate artifact (for example, `review_<id>_synthesis.md`) and append it to `MANIFEST.md`. The individual reviews remain independent records.
