---
name: lifecycle-orchestrator
description: Orchestrates the full software engineering lifecycle — research, design,
  implement, test, deploy, maintain — dispatching domain-specific subagents and
  skills at each phase. Integrates with code-programming manifest rules.
triggers:
  - pattern: "(build|create|ship) a (system|service|feature)"
    description: End-to-end lifecycle orchestration
phases:
  - research: Validate approach, select language, audit dependencies
  - design: Create plan, define architecture, specify API contracts
  - implement: TDD loop across RED-GREEN-IMPROVE
  - test: Test pyramid (unit/integration/e2e), property-based testing
  - deploy: CI/CD, containerization, monitoring, rollback
  - maintain: Dependency updates, tech debt, documentation
entry_criteria: Requirements exist (even if rough)
exit_criteria: System is deployed, monitoring confirms health
---

# Lifecycle Orchestrator

Dispatch agents and skills at each phase of the engineering lifecycle.

## Phase Dispatch Table

| Phase | Agent/Skill | Action |
|-------|-------------|--------|
| Research | `lang-select` command | Choose language and approach |
| Design | `code-architect` agent when needed | Design architecture for complex features |
| Implement | Selected workflow + `implement` | Right-sized implementation; embedded dual-axis subagent review |
| Test | Language-specific tools | Run relevant tests and security checks |
| Deploy | `deployment-patterns` skill | CI/CD, containerization |
| Maintain | `refactor-cleaner` agent | Tech debt, dead code removal |

## Quality Gates Per Phase

| Phase | Gate | Tool |
|-------|------|------|
| Research | Language selected, rationale documented | `references/language-specs/` |
| Design | Complex-work plan/spec when needed | `planning-with-files` or `planning-with-files-zh` |
| Implement | Tests pass, lint clean, coverage >= 80% | Language-specific tools |
| Test | Relevant tests/security checks pass; embedded review addressed | `implement` workflow |
| Deploy | CI green, rollback tested | `deploy-check` command |
| Maintain | Docs current, debt tracked | CLAUDE.md audit |
