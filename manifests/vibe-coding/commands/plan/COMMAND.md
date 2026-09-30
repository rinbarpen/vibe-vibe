# /plan

Create an implementation plan for work with meaningful architecture, coordination, or cross-module decisions. For simple changes use direct vibe coding instead.

## Execution

Use this command for complex feature planning or medium/large coordinated work, not as a required entry step for every coding task. Complex feature work follows `grill-with-docs` → `to-spec` → `to-tickets` before implementation. Use the matching `planning-with-files-zh` (Chinese) or `planning-with-files` (English) skill for medium/large progress tracking.


1. Determine the domain (ui, frontend, backend, optimization, testing, deployment, refactoring)
2. Determine the target language(s) (see `references/decision-trees/language-selection.md`)
3. Research existing implementations (no reinventing wheels)
4. Invoke `code-architect` or `planner` agent for architecture design
5. Create plan document in `.cursor/plans/<feature-name>.md`

## Plan Template

```markdown
# Plan: <Title>

## Problem
<What needs to be solved, one sentence>

## Approach
<High-level approach>

## Files to Create/Modify
- `path/to/file.go` — what will change

## Test Strategy
- Unit tests: <what>
- Integration tests: <what>
- E2E tests: <what>

## Risks
- <risk> → <mitigation>
```

## Exit Criteria

- [ ] Plan includes: problem statement, approach, file manifest, test strategy, risks
- [ ] Open product/architecture decisions confirmed before implementation
