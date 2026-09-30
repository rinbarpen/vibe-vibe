---
name: lifecycle-orchestrator
description: Selects a proportionate software workflow by task size, then applies domain-specific expertise only where useful.
triggers:
  - pattern: "(build|create|ship) a (system|service|feature)"
    description: Classify task size before choosing a workflow
workflow_routing:
  simple: Direct vibe coding; relevant verification; no planning artifact by default
  bug_fix: grilling → implement
  complex_feature: grill-with-docs → to-spec → to-tickets → implement
  planning_files: Medium/large tasks only; choose planning-with-files-zh for Chinese or planning-with-files for English
review: Implement includes separate correctness and code-quality subagent review; no manual code-review step
---

# Lifecycle Orchestrator

Choose the task-sized route first; dispatch technical agents and skills only for relevant phases.

## Phase Dispatch Table (only relevant phases; skip non-applicable orchestration for simple changes)

| Phase | Agent/Skill | Action |
|-------|-------------|--------|
| Research | `lang-select` command | Choose language and approach |
| Design | `code-architect` agent | Design architecture, create plan |
| Implement | `implement` workflow | Focused implementation and proportional verification; TDD when appropriate |
| Test/review | `implement` workflow | Two-axis correctness and code-quality subagent review; add security review when sensitive |
| Deploy | `deployment-patterns` skill | CI/CD, containerization |
| Maintain | `refactor-cleaner` agent | Tech debt, dead code removal |

## Quality Gates Per Phase

| Phase | Gate | Tool |
|-------|------|------|
| Research | Language selected, rationale documented | `references/language-specs/` |
| Design | Complex feature decisions captured | Spec/tickets; planning files for medium/large work |
| Implement | Relevant tests and checks pass | Language-specific tools |
| Test/review | Both review axes completed | `implement` workflow |
| Deploy | CI green, rollback tested | `deploy-check` command |
| Maintain | Docs current, debt tracked | CLAUDE.md audit |
