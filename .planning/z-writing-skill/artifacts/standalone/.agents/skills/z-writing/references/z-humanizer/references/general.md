# Ordinary prose via unslop

This route covers `general`, `blog`, `kb-doc`, and `tutorial`. Academic, journal,
conference, and patent writing stay on z-humanizer's specialized routes.

## Load the actual engine

Read [unslop/SKILL.md](unslop/SKILL.md), then its
[core contract](unslop/references/core-contract.md) and the chosen command file.
Resolve every upstream script, reference, preset, and asset from the directory
containing that bundled SKILL.md, not from z-humanizer's outer directory.
The source bundle links to the canonical `skills/unslop` submodule; the normal
vibe installer follows that link and copies a self-contained local payload.

## Select the command by user intent

- Audit, review, or "只标记/保留原文": use `cleanup` in report-only mode.
- "去AI味/说人话/改自然一点" and `/humanize <text>`: use `rewrite`, retaining
  diagnosis, reconstruction, and preservation checks.
- `--quick`: keep the same rewrite guards, but make the report compact.
- Learn a reusable voice from supplied writing samples: use `teach`.
- Write in an already taught voice: use `mimic`; obtain samples when absent.

Read the corresponding `unslop/references/commands/<command>.md` before acting.
Cleanup suggestions remain suggestions unless the user asks to apply them.
Do not apply the old general humanizer libraries on top of this route, enforce
punctuation quotas, deliberately retain errors, or use the specialized 0–60
score as an unslop quality gate.

## Preserve language and meaning

Keep the original language and requested register. Protect facts, numbers,
quotes, citation keys, URLs, code, commands, and terminology. Avoid inventing
examples or adding claims just to make a sentence sound personal.

Review the preservation constraints extracted from the source before validating.
The upstream extractor can omit ordinary small counts such as "64 entries".
Include omitted load-bearing quantities, citations, code, and commands in an
explicit constraints JSON file and pass it as the third argument to
`unslop/scripts/validate_preservation.py`. Check numeric tokens and their roles
directly as well; a substring match or `passed: true` with zero extracted
constraints is not proof that the facts survived.

The upstream lexical scanners primarily target English. For Chinese or mixed
prose, use context-sensitive editorial judgment alongside relevant structural
checks; zero English phrase hits do not establish Chinese writing quality.
A scanner flag is a review candidate, not proof of AI authorship. Leave already
effective prose unchanged and disclose any checks that were not run.
