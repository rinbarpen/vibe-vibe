#!/usr/bin/env bash
# UI Testing Manifest — initialization script
# Installs rules, commands, and scenario configs into a target project.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_DIR="$(dirname "$SCRIPT_DIR")"
TARGET_DIR="${1:-.}"
SCENARIO=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --scenario=*)
            SCENARIO="${1#*=}"
            shift
            ;;
        --help|-h)
            echo "Usage: ui-testing-init.sh [target-dir] [--scenario=<name>]"
            echo ""
            echo "Scenarios:"
            echo "  web-e2e           Web E2E testing (Playwright)"
            echo "  component         Component testing (Vitest + Testing Library)"
            echo "  mobile            Mobile UI testing (Detox/Appium)"
            echo "  visual-regression Visual regression testing"
            echo "  accessibility     Accessibility testing (axe-core)"
            exit 0
            ;;
        *)
            TARGET_DIR="$1"
            shift
            ;;
    esac
done

TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")"

echo "[ui-testing-init] Installing UI Testing Manifest to: $TARGET_DIR"
echo ""

for file in CLAUDE.md AGENTS.md MANIFEST.md README.md; do
    if [[ -f "$MANIFEST_DIR/$file" && ! -f "$TARGET_DIR/$file" ]]; then
        cp "$MANIFEST_DIR/$file" "$TARGET_DIR/$file"
    fi
done

# Create .cursor/rules if it doesn't exist
mkdir -p "$TARGET_DIR/.cursor/rules"

# Install core rules
echo "[ui-testing-init] Installing core rules..."
for rule in "$MANIFEST_DIR"/rules/*.mdc; do
    rule_name=$(basename "$rule")
    # Replace {{UI_TESTING_MANIFEST}} placeholder with relative path
    sed "s|{{UI_TESTING_MANIFEST}}|../manifests/ui-testing|g" "$rule" > "$TARGET_DIR/.cursor/rules/$rule_name"
    echo "  → .cursor/rules/$rule_name"
done

# Install scenario rules if specified
if [[ -n "$SCENARIO" ]]; then
    SCENARIO_DIR="$MANIFEST_DIR/scenarios/$SCENARIO"
    if [[ -d "$SCENARIO_DIR" ]]; then
        echo ""
        echo "[ui-testing-init] Installing scenario: $SCENARIO..."
        mkdir -p "$TARGET_DIR/.cursor/rules"
        for rule in "$SCENARIO_DIR"/rules/*.mdc; do
            rule_name=$(basename "$rule")
            sed "s|{{UI_TESTING_MANIFEST}}|../manifests/ui-testing|g" "$rule" > "$TARGET_DIR/.cursor/rules/$rule_name"
            echo "  → .cursor/rules/$rule_name"
        done

        # Copy scenario CLAUDE.md as override
        if [[ -f "$SCENARIO_DIR/CLAUDE.md" ]]; then
            cp "$SCENARIO_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.ui-testing.md"
            echo "  → CLAUDE.ui-testing.md (scenario context)"
        fi
    else
        echo "[ui-testing-init] Warning: Scenario '$SCENARIO' not found at $SCENARIO_DIR"
        echo "  Available scenarios:"
        for d in "$MANIFEST_DIR"/scenarios/*/; do
            echo "    - $(basename "$d")"
        done
    fi
fi

echo ""
echo "[ui-testing-init] Installing native agents..."
for runtime_agents in ".claude/agents" ".codex/agents"; do
    SOURCE_DIR="$MANIFEST_DIR/$runtime_agents"
    if [[ -d "$SOURCE_DIR" ]]; then
        mkdir -p "$TARGET_DIR/$runtime_agents"
        for agent_file in "$SOURCE_DIR"/*; do
            [[ -f "$agent_file" ]] || continue
            agent_name="$(basename "$agent_file")"
            if [[ ! -f "$TARGET_DIR/$runtime_agents/$agent_name" ]]; then
                cp "$agent_file" "$TARGET_DIR/$runtime_agents/$agent_name"
                echo "  -> $runtime_agents/$agent_name"
            fi
        done
    fi
done

echo ""
echo "[ui-testing-init] Done. UI Testing Manifest installed."
echo ""
echo "Next steps:"
echo "  1. Review .cursor/rules/ui-testing-core.mdc"
echo "  2. Install test dependencies: npm install -D @playwright/test vitest @testing-library/react"
echo "  3. Create playwright.config.ts or vitest.config.ts"
if [[ -z "$SCENARIO" ]]; then
    echo "  4. Optionally add a scenario: bash $(basename "$0") --scenario=<name>"
fi
