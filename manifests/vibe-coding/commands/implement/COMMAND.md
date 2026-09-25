# /implement

Implement a feature following TDD (RED-GREEN-IMPROVE).

## Execution

1. Follow the workflow selected by request scope; a plan is not required for simple/local requests.
2. Write failing test first (RED) — define the expected behavior
3. Run test — confirm it fails
4. Write minimal code to pass (GREEN) — do not optimize yet
5. Run full test suite — confirm all pass
6. Run language-appropriate linter — confirm zero warnings
7. Run type checker if applicable (tsc, mypy)
8. Refactor (IMPROVE) — improve naming, extract helpers, remove duplication
9. Verify coverage >= 80%
10. Complete the embedded subagent review across two independent axes

## Per-Implementation Checklist

- [ ] RED: failing test written first
- [ ] GREEN: minimal implementation passes test
- [ ] All existing tests still pass
- [ ] Linter: zero warnings
- [ ] Type checker passes (for typed languages)
- [ ] IMPROVE: code refactored
- [ ] Coverage >= 80%
- [ ] No console.log / debug statements
- [ ] No hardcoded secrets
- [ ] Embedded dual-axis subagent review completed
- [ ] Commit with conventional message
