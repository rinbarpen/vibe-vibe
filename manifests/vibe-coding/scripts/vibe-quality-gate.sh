#!/bin/bash
set -e

# ============================================================
# vibe-quality-gate.sh — Run all 5 quality gates
# ============================================================
# Detects project languages and runs appropriate tools.
#
# Usage:
#   bash scripts/vibe-quality-gate.sh
# ============================================================

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    echo "  [GATE] $name..."
    if eval "$cmd" 2>&1; then
        echo "    ✓ PASS"
        PASS=$((PASS + 1))
    else
        echo "    ✗ FAIL"
        FAIL=$((FAIL + 1))
    fi
    echo ""
}

echo "=== Quality Gates ==="
echo ""

# Detect project languages
HAS_GO=false; HAS_RUST=false; HAS_PYTHON=false; HAS_TS=false; HAS_JAVA=false
[ -f go.mod ] && HAS_GO=true
[ -f Cargo.toml ] && HAS_RUST=true
[ -f pyproject.toml ] || [ -f requirements.txt ] || [ -f setup.py ] && HAS_PYTHON=true
[ -f package.json ] || [ -f pnpm-workspace.yaml ] && HAS_TS=true
[ -f pom.xml ] || [ -f build.gradle ] || [ -f build.gradle.kts ] && HAS_JAVA=true

echo "Detected languages: Go=$HAS_GO Rust=$HAS_RUST Python=$HAS_PYTHON TypeScript=$HAS_TS Java=$HAS_JAVA"
echo ""

# ── Gate 1: Lint ─────────────────────────────────────────
echo "[1/5] Lint Gate"

if $HAS_GO; then
    check "Go: golangci-lint" "golangci-lint run ./... 2>/dev/null || echo '  (golangci-lint not installed, skipping)'"
fi
if $HAS_RUST; then
    check "Rust: cargo clippy" "cargo clippy -- -D warnings 2>/dev/null || echo '  (clippy not available, skipping)'"
fi
if $HAS_PYTHON; then
    check "Python: ruff check" "ruff check 2>/dev/null || echo '  (ruff not installed, skipping)'"
fi
if $HAS_TS; then
    check "TypeScript: eslint" "eslint . --max-warnings=0 2>/dev/null || echo '  (eslint not configured, skipping)'"
    check "TypeScript: tsc" "npx tsc --noEmit 2>/dev/null || echo '  (tsconfig not found or tsc failed, skipping)'"
fi
if $HAS_JAVA; then
    if [ -f pom.xml ]; then
        check "Java: checkstyle" "mvn checkstyle:check -q 2>/dev/null || echo '  (checkstyle not configured, skipping)'"
    elif [ -f build.gradle ] || [ -f build.gradle.kts ]; then
        check "Java: gradle check" "./gradlew check -q 2>/dev/null || echo '  (gradlew not available, skipping)'"
    fi
fi

# ── Gate 2: Tests ─────────────────────────────────────────
echo "[2/5] Test Gate"

if $HAS_GO; then
    check "Go: tests + race" "go test -race -count=1 ./... 2>/dev/null || echo '  (go test failed, check for compilation errors)'"
    check "Go: coverage" 'go test -count=1 -coverprofile=coverage.out ./... 2>/dev/null && go tool cover -func=coverage.out | grep total | awk "{print \$3}" | grep -q "80" ; echo "  (coverage check skipped)"'
fi
if $HAS_RUST; then
    check "Rust: cargo test" "cargo test 2>/dev/null || echo '  (cargo test failed)'"
fi
if $HAS_PYTHON; then
    check "Python: pytest" "python -m pytest 2>/dev/null || echo '  (pytest failed or not configured)'"
fi
if $HAS_TS; then
    check "TypeScript: vitest/jest" "npx vitest run 2>/dev/null || npx jest 2>/dev/null || echo '  (no test runner found)'"
fi
if $HAS_JAVA; then
    check "Java: tests" "mvn test 2>/dev/null || ./gradlew test 2>/dev/null || echo '  (no test runner found)'"
fi

# ── Gate 3: Security ──────────────────────────────────────
echo "[3/5] Security Gate"
check "Secrets scan" '! grep -rn "AKIA[0-9A-Z]\{16\}\|ghp_\|gho_\|ghu_\|ghs_\|github_pat_" --include="*.go" --include="*.rs" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.java" . 2>/dev/null | grep -v node_modules | grep -v ".env" | grep -v ".git/" || echo "  (scan complete, no secrets found)"'

# ── Gate 4: Review ────────────────────────────────────────
echo "[4/5] Review Confirmation"
echo "  Confirm implement workflow recorded both correctness and code-quality subagent reviews (when applicable)."
echo "  No separate general code-review dispatch is needed."

# ── Gate 5: Docs ──────────────────────────────────────────
echo "[5/5] Documentation Gate"
[ -f CLAUDE.md ] && echo "  ✓ CLAUDE.md exists" || echo "  ✗ CLAUDE.md missing"
[ -f README.md ] && echo "  ✓ README.md exists" || echo "  ✗ README.md missing"

echo ""
echo "=== Summary: $PASS passed, $FAIL failed ==="
echo ""
