#!/usr/bin/env bash
# Recalculate a working COPY, preserving it on any failure.
# Usage: recalc.sh working.xlsx [timeout_seconds]
# Python dependencies: openpyxl (or: uv run --script recalc.py ...).
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "$SCRIPT_DIR/recalc.py" "$@"
