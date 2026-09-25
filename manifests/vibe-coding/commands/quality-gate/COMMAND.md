# /quality-gate

Execute all 5 quality gates before committing.

## Gates

### 1. Lint Gate
- Go: `golangci-lint run`
- Rust: `cargo clippy -- -D warnings`
- Python: `ruff check`
- TypeScript: `eslint && tsc --noEmit`
- Java: `mvn checkstyle:check` or `gradle checkstyleMain`
- **Exit**: Zero warnings

### 2. Test Gate
- Run full test suite with coverage
- **Exit**: All tests pass, coverage >= 80%

### 3. Security Gate
- Check changed files for hardcoded secrets, injection vulnerabilities, and auth bypasses; invoke focused security review when warranted by the change.
- **Exit**: No CRITICAL or HIGH security issues

### 4. Review Gate
- Implementation review is included in `implement` as two-axis subagent review; do not launch a separate generic code-review workflow.
- **Exit**: Embedded review findings addressed; no CRITICAL or HIGH issues remain.

### 5. Doc Gate
- Verify CLAUDE.md reflects current architecture
- Verify README.md is current
- **Exit**: Documentation is accurate

## Manual Checklist

Before calling `/quality-gate`, confirm:
- [ ] No uncommitted debug code
- [ ] No commented-out code
- [ ] No hardcoded URLs or IPs
- [ ] Error handling covers failure paths
- [ ] Inputs are validated at system boundaries
