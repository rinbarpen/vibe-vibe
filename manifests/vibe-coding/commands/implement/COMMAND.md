# /implement

Implement a bug fix or feature with verification proportional to its scope. This workflow includes two-axis subagent review; do not start a separate code-review workflow.

## Execution

1. Read accepted tickets/spec or the bug investigation notes when provided; a plan artifact is not required for a small fix.
2. Inspect the affected code and tests; reproduce the bug or establish the requested behavior.
3. Make the smallest coherent change and add/update focused tests where appropriate. Use RED-GREEN-IMPROVE when it fits the behavior and project conventions.
4. Run relevant tests, then the broader suite as scope warrants; run applicable lint/type checks.
5. Refactor only where it improves clarity without broadening scope.
6. Delegate two independent reviews: (a) requirement correctness, behavior boundaries, and test coverage; (b) code quality, design, and maintainability.
7. Resolve material findings and report exact verification performed.

## Per-Implementation Checklist

- [ ] Bug reproduced or requested behavior grounded in the existing code
- [ ] Focused tests added/updated where appropriate; existing relevant tests pass
- [ ] Relevant lint/type/build checks run for the change
- [ ] Correctness/behavior/test review subagent completed
- [ ] Code quality/design/maintainability review subagent completed
- [ ] Material findings resolved; no debug artifacts or hardcoded secrets
- [ ] Report verification and remaining caveats
