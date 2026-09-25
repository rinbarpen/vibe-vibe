# Office Document Automation Suite

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

Unified manifest for operating Microsoft Office three-piece suite — Word (docx), Excel (xlsx), and PowerPoint (pptx) — through specialised sub-manifests. Quality first, instructions 100% followed.

## Planning Phase (MANDATORY)

Before any task, invoke `planning-with-files` to understand requirements:

1. Create `task_plan.md` — phase breakdown, progress, decisions
2. Create `findings.md` — research results, requirement analysis
3. Create `progress.md` — session log, test results

See `office/planning/` for full workflow.

## Sub-Manifests

| Sub-Manifest | Format | Approach | Reference |
|-------------|--------|----------|-----------|
| `docx/` | Word (.docx) | docx-polar pipeline + industry rules | `office/docx/CLAUDE.md` |
| `xlsx/` | Excel (.xlsx) | uv+python (xlsxwriter/openpyxl/pandas) | `office/xlsx/CLAUDE.md` |
| `pptx/` | PowerPoint (.pptx) | ppt-master pipeline + aesthetic design | `office/pptx/CLAUDE.md` |

## Data Safety (CRITICAL)

1. **NEVER modify original files directly.**
2. **ALWAYS copy**: `cp original.docx working.docx` before any modification.
3. **ALWAYS validate** the working copy before replacing the original.
4. **ALWAYS keep a backup**: `mv original.docx _backups/original-{date}.docx`.
5. **EVERY modification on a git branch.**

## Architecture

```
office/
  docx/             docx-polar pipeline
    rules/patent.md — 中国三种专利规则集
  xlsx/             uv+python 代码式表格处理
    scripts/        — create.py, analyze.py, recalc.sh
  pptx/             ppt-master + aesthetic design
  planning/         planning-with-files 需求理解
```

## Workflow

1. **Plan** — `planning-with-files`: task_plan.md → findings.md → progress.md
2. **Select** — Choose sub-manifest: docx / xlsx / pptx
3. **Execute** — Run sub-manifest pipeline
4. **Validate** — Format-specific quality gates
5. **Backup** — Timestamp original, commit changes

## Gotchas

- **docx-polar**: Must run from `/home/rczx/workspace/rinbarpen/work/docx-polar`; requires Node.js v18+ for `docx` npm package
- **xlsx**: `data_only=True` save permanently replaces formulas with values — NEVER save a data_only workbook
- **pptx**: ppt-master is a strict serial pipeline — no cross-phase bundling, no sub-agent SVG generation
- **Planning**: Always create `task_plan.md` before starting execution; never write external content into `task_plan.md`
- **Dependencies**: python-docx/openpyxl/xlsxwriter/pandas via uv; ppt-master via skills/ submodule
