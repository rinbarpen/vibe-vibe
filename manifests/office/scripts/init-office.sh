#!/usr/bin/env bash
# Entry point used by vibe init/add manifest; skill installation stays in vibe.
# Delegated Python installation includes native .claude/agents and .codex/agents.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/install_office.py" "$@"
