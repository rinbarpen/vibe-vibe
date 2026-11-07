#!/usr/bin/env bash
# Installs .claude/agents and .codex/agents with ledger ownership and rollback.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "$SCRIPT_DIR/install_manifest.py" "$@"
