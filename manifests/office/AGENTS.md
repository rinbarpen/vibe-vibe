# AGENTS.md (Office Suite)

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

Instructions for AI agents working on Office document automation tasks across Word, Excel, and PowerPoint.

## Repository Overview

Office Document Automation Suite — four sub-manifests: docx (docx-polar pipeline + patent rules), xlsx (uv+python code), pptx (ppt-master + aesthetic design), and planning (planning-with-files).

## Iron Rule: Data Safety First

Every file modification follows this mandatory sequence:

1. **Branch**: Create a git branch (`office/<task>`).
2. **Copy**: Work on a copy, never the original.
3. **Validate**: Verify structural integrity after every modification.
4. **Backup**: Timestamp the original before replacing it.
5. **Commit**: Checkpoint after each successful replacement.
6. **Merge**: Only merge after full validation.

## Agent Roles

### 1. Document Engineer
- **Scope**: Word document generation with docx-polar pipeline, patent writing
- **Skills**: `docx-polar` project, python-docx, docx npm package
- **Patterns**: Template-extract → write → review → iterate

### 2. Spreadsheet Analyst
- **Scope**: Excel data processing, chart generation, formula application
- **Skills**: xlsxwriter (create), openpyxl (edit), pandas (analyze)
- **Patterns**: Hybrid library dispatch, formula integrity, recalculation verification

### 3. Presentation Designer
- **Scope**: PowerPoint creation with ppt-master, aesthetic slide design
- **Skills**: `ppt-master` pipeline, SVG generation, color theory
- **Patterns**: Strategist → Executor → QA → Export

### 4. Planning Specialist
- **Scope**: Requirements analysis and task decomposition
- **Skills**: `planning-with-files-zh`
- **Patterns**: task_plan.md → findings.md → progress.md → 3-failure protocol

## Subagent Dispatching

| Domain | Tool/Skill | Trigger |
|--------|-----------|---------|
| **Requirements** | `planning` sub-manifest | Before any task |
| **Document Authoring** | `docx` sub-manifest | Word document creation/modification |
| **Spreadsheet Processing** | `xlsx` sub-manifest | Excel data/chart tasks |
| **Presentation Creation** | `pptx` sub-manifest | PowerPoint generation |
| **Format Conversion** | `pandoc` | Cross-format conversion |
| **Visual Design** | `canvas-design` skill | Chart/table visual polish |

## Office Processing Standards

- **Template Over Content**: Reuse templates for consistent formatting; avoid ad-hoc styling.
- **Validation Before Replace**: Always run validate before replacing original.
- **Batch Safety**: Batch operations use dry-run mode first (`--dry-run`).
- **Encoding**: All text files are UTF-8; specify encoding explicitly in scripts.
- **CRITICAL**: Always use formulas in xlsx, never hardcoded values.

## Git Branch Workflow

- **Branch naming**: `office/<task>` (e.g., `office/generate-patent`, `office/create-charts`)
- **Commit frequency**: After each successful validate → backup → replace cycle
- **Never work on main**: All modifications on feature branches
