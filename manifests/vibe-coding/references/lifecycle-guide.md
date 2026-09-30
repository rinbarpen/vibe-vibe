# Engineering Lifecycle Guide

End-to-end guide for taking a software project from idea to deployed system, covering best practices for Go, Rust, Python, TypeScript, and Java.

---

## Phase 1: Research (when scope or uncertainty warrants it)

**Goal**: Validate the approach before writing code. Simple bounded changes can go directly to a focused implementation and relevant verification.

### Steps
1. **Problem definition**: State the problem in one sentence. Define success criteria.
2. **Existing solutions search**: Check GitHub, package registries, and internal libraries before writing new code.
3. **Language selection**: Follow the decision tree in `references/decision-trees/language-selection.md`.
4. **Dependency audit**: For each major dependency, check: maintenance status, security track record, license compatibility, community size.
5. **Risk assessment**: Identify risks (performance, security, complexity, learning curve) and mitigation strategies.

### Outputs
- Requirements document (concise — a few paragraphs, not a spec)
- Language selection rationale
- Dependency audit results
- Risk register

---

## Phase 2: Design (complex features and coordinated work)

**Goal**: Create an actionable plan when architecture, product decisions, or coordination warrant it.

### Steps
1. **Architecture selection**: Choose patterns from `references/decision-trees/architecture-patterns.md`.
2. **Data modeling**: Define entities, relationships, storage strategy (relational, document, key-value, etc.).
3. **API contract**: Specify interfaces BEFORE implementation. OpenAPI for REST, Protobuf for gRPC.
4. **Component breakdown**: List modules/services and their responsibilities.
5. **File manifest**: List files to be created or modified.
6. **Test strategy**: Define what to test at each level of the test pyramid.

### Outputs
- Plan document saved to `.cursor/plans/<name>.md`
- Architecture Decision Record (ADR) if the decision is non-trivial
- API contract (OpenAPI / Protobuf)
- Data model (ERD or schema definition)

---

## Phase 3: Implementation

**Goal**: Ship working code with tests.

### TDD Loop (when useful for the behavior and project)

```
RED   → Write a failing test that defines the desired behavior
GREEN → Write minimal code to make the test pass
IMPROVE → Refactor while keeping tests green, improve naming, extract helpers
```

### Per-Language Implementation Checklist

| Language | Test Runner | Linter | Formatter | Coverage |
|----------|-------------|--------|-----------|----------|
| Go | `go test ./...` | `golangci-lint run` | `gofmt` | `go test -coverprofile=coverage.out` |
| Rust | `cargo test` | `cargo clippy -- -D warnings` | `cargo fmt` | `cargo llvm-cov` |
| Python | `pytest` | `ruff check` | `ruff format` | `pytest --cov=src --cov-report=term-missing` |
| TypeScript | `vitest` or `jest` | `eslint` | `prettier` | `vitest --coverage` |
| Java | `mvn test` or `gradle test` | `checkstyle` | `spotless` | JaCoCo plugin |

### After a Substantive Change
Run the checks relevant to the changed behavior and project conventions:
- [ ] Relevant tests pass
- [ ] Applicable lint passes without new warnings
- [ ] Build succeeds when relevant
- [ ] No console.log or debug statements
- [ ] No hardcoded secrets

---

## Phase 4: Testing

**Goal**: Verify correctness at every level.

### Test Pyramid

```
     ╱╲
    ╱ E2E ╲         10% — critical user flows, full system integration
   ╱───────╲
  ╱Integration╲     20% — API endpoints, database operations, service boundaries
 ╱─────────────╲
╱   Unit Tests   ╲  70% — individual functions, utilities, pure logic
╱─────────────────╲
```

### Testing Per Language

| Language | Unit Framework | Integration | E2E | Property-Based |
|----------|---------------|-------------|-----|----------------|
| Go | `go test`, `testify` | `testcontainers-go` | Playwright | `testing/quick`, `go-fuzz` |
| Rust | `#[test]`, `rstest` | `sqlx` test fixtures, `testcontainers` | — | `proptest`, `quickcheck` |
| Python | `pytest` | `pytest-django`, `testcontainers-python` | Playwright | `hypothesis` |
| TypeScript | `vitest` | `supertest`, `MSW` | Playwright | `fast-check` |
| Java | `JUnit 5` | `TestContainers` | Playwright + Selenium | `jqwik` |

### Quality Gate
- [ ] All tests pass
- [ ] Coverage meets the project target when the change is large enough to affect meaningful coverage
- [ ] Performance-sensitive code has benchmarks
- [ ] Fuzz testing for parsing/decoding code
- [ ] Edge cases documented (empty state, error state, loading state)

---

## Phase 5: Deployment

**Goal**: Ship safely with rollback capability.

### Pre-Deploy Checklist
- [ ] All quality gates passed
- [ ] CI/CD pipeline is green
- [ ] Database migration is tested (can rollback?)
- [ ] Environment variables configured in target environment
- [ ] Docker image built (multi-stage, non-root user)
- [ ] Rollback plan exists and is tested
- [ ] Monitoring dashboards and alerts configured
- [ ] Release notes drafted

### Deployment Strategies
| Strategy | When to Use | Risk | Complexity |
|----------|-------------|------|------------|
| Rolling update | Standard stateless services | Low | Low |
| Blue-green | Zero-downtime required | Low | Medium |
| Canary | Risk-sensitive, gradual rollout | Medium | High |
| Feature flags | Decouple deploy from release | Low | Medium |

### Per-Language Deployment Considerations

| Language | Container Base | Startup | Memory | Key Concern |
|----------|---------------|---------|--------|-------------|
| Go | `golang:alpine` → `scratch` or `distroless` | ~10ms | ~10MB | Minimal |
| Rust | `rust:alpine` → `distroless` | ~5ms | ~5MB | Compile time |
| Python | `python:3.12-slim` | ~500ms | ~50MB | Cold start, dependency size |
| TypeScript | `node:22-alpine` or `bun` | ~200ms | ~40MB | `node_modules` size |
| Java | `eclipse-temurin:21` or `gradle:j21` → distroless | ~2s (JVM), ~50ms (native) | ~150MB (JVM), ~30MB (native) | JVM tuning, GraalVM for cold start |

---

## Phase 6: Maintenance

**Goal**: Keep the system healthy over time.

### Ongoing Tasks
- **Dependency updates**: Check for security updates monthly
- **Performance baselines**: Re-profile quarterly to catch regression
- **Tech debt tracking**: Keep a debt log in `.cursor/plans/debt.md`
- **Documentation**: Update CLAUDE.md and README.md when architecture changes
- **Test health**: Remove flaky tests, add tests for bugs found in production
- **Log review**: Check for recurring error patterns

### Triggers for Refactoring
- A module is consistently identified as "hard to work with"
- Test setup takes longer than test logic
- Same change needs to be made in multiple places
- A dependency is no longer maintained
- Performance no longer meets requirements
- The team has learned enough to design a better solution
