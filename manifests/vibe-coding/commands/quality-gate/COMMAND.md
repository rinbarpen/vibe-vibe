# /quality-gate

Run applicable quality checks at a commit or release boundary. A simple change does not need this full workflow unless requested or required by the project.

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
- **Exit**: Relevant tests pass and project coverage targets are maintained

### 3. Security Gate
- Dispatch `security-reviewer` agent for changed files
- Check for: hardcoded secrets, injection vulnerabilities, auth bypasses
- **Exit**: No CRITICAL or HIGH security issues

### 4. Review Confirmation
- For changes implemented through `implement`, confirm both included subagent reviews are complete: correctness (requirements, behavior, tests) and code quality (design, maintainability).
- Do not dispatch a separate general code reviewer. Use the conditional security review in Gate 3 for sensitive changes.
- **Exit**: Any material findings are resolved or documented

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
