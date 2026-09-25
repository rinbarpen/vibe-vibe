---
name: domain-dispatcher
description: Routes development tasks to the correct domain (UI, Frontend, Backend,
  Optimization, Testing, Deployment, Refactoring) and dispatches the appropriate
  subagents, skills, and rule sets from the code-programming manifest.
triggers:
  - pattern: "(design|implement|fix|improve|optimize|refactor) (the |this |our )?(ui|frontend|backend|API|test|deploy)"
    description: Domain-specific task dispatch
---

# Domain Dispatcher

## Dispatch Logic

Map task keywords to domain, then select relevant resources. Dispatch a subagent only for complex work with a bounded, independent task; simple/local tasks remain with the main agent. Follow the bounded-subagent protocol in `AGENTS.md`.

| Task Keywords | Domain | Agent | Skill | Rule File |
|---------------|--------|-------|-------|-----------|
| "UI", "design", "component", "layout", "accessibility", "responsive" | UI Design | `design-taste-frontend` | `awesome-design-md`, `frontend-design`, `canvas-design`, `ui-ux-pro-max-skill`, `taste-skill` | `vibe-coding-ui-design.mdc` |
| "Three.js", "WebGL", "3D", "image-to-3D", "procedural model" | 3D Frontend | `frontend-patterns` | `img2threejs` | `vibe-coding-frontend.mdc` |
| "frontend", "state", "data fetching", "routing", "bundle", "CWV" | Frontend | `frontend-patterns` | `frontend-patterns` | `vibe-coding-frontend.mdc` |
| "backend", "API", "service", "database", "auth", "middleware" | Backend | `code-architect` | `backend-patterns`, `api-design` | `vibe-coding-backend.mdc` |
| "slow", "optimize", "profile", "performance", "cache", "bottleneck" | Optimization | `performance-optimizer` | — | `vibe-coding-optimization.mdc` |
| "test", "coverage", "TDD", "integration", "e2e" | Testing | `tdd-guide` | Language-specific testing skills | `vibe-coding-testing.mdc` |
| "deploy", "CI/CD", "Docker", "release", "rollout" | Deployment | — | `deployment-patterns`, `docker-patterns` | `vibe-coding-deployment.mdc` |
| "refactor", "clean", "migrate", "extract", "dead code" | Refactoring | `refactor-cleaner` | — | `vibe-coding-refactoring.mdc` |
| "agent", "eval", "prompt quality", "llm eval" | Agent Eval | `eval-harness` | `prompt-optimizer` | `vibe-coding-agent-dev.mdc` |
| "agent", "context engineering", "multi-agent", "agent architecture" | Agent Dev | `code-architect` | `Agent-Skills-for-Context-Engineering`, `agent-skills` | `vibe-coding-agent-dev.mdc` |
| "desktop", "electron", "tauri", "flutter desktop", "native app" | Desktop | `build-error-resolver` + framework reviewer | `dart-flutter-patterns` | `vibe-coding-desktop.mdc` |
| "frontend", "css", "i18n", "a11y", "component library" | Frontend | `frontend-patterns` | `design-taste-frontend`, `frontend-design`, `ui-ux-pro-max-skill`, `taste-skill` | `vibe-coding-frontend.mdc` |

## Cross-Domain Dispatch

When a complex task spans multiple domains (e.g., "refactor the backend API and add tests"):

1. Identify all domains involved
2. Identify dependencies: run independent discovery/checks concurrently; implement dependent steps in order (backend change before integration tests).
3. Give each delegated task explicit context, non-overlapping ownership, output, and verification; coordinate integration and final tests centrally.
4. Each domain uses its own rule set and relevant skills. `implement` owns embedded parallel two-axis review; do not dispatch a duplicate generic reviewer.

## Language Dispatch

After domain is determined, dispatch the language-specific agent:

| Language | Reviewer | Build Resolver | Patterns Skill |
|----------|----------|----------------|----------------|
| Go | `go-reviewer` | `go-build-resolver` | `golang-patterns` |
| Rust | `rust-reviewer` | `rust-build-resolver` | `rust-patterns` |
| Python | `python-reviewer` | — | `python-patterns` |
| TypeScript | `typescript-reviewer` | `build-error-resolver` | `frontend-patterns` |
| Java | `java-reviewer` | `java-build-resolver` | `java-coding-standards` |
