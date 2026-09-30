# /quality-gate

Run applicable quality checks at an appropriate commit or release boundary; use the full gate when scope or repository requirements warrant it.

## Gates

### 1. Lint Gate
- Go: `golangci-lint run`
- Rust: `cargo clippy -- -D warnings`
- Python: `ruff check`
- TypeScript: `eslint && tsc --noEmit`
- Java: `mvn checkstyle:check` or `gradle checkstyleMain`
- **Exit**: Zero warnings

### 2. Test Gate
- Run relevant tests; run the full suite when the change warrants it
- **Exit**: Relevant tests pass and project coverage targets are maintained

### 3. Security Gate
- Check changed files for hardcoded secrets, injection vulnerabilities, and auth bypasses; invoke focused security review when warranted by the change.
- **Exit**: No CRITICAL or HIGH security issues

### 4. Review Confirmation
- If `implement` was used, confirm both embedded axes completed: correctness (requirements, behavior, tests) and code quality (design, maintainability).
- Do not dispatch a separate generic code-review workflow.
- **Exit**: Material findings addressed or documented.

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
