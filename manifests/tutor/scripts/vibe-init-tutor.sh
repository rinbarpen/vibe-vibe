#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(command -v python3 || command -v python || true)"
[[ -n "$PYTHON" ]] || { echo "Error: Python is required to install Tutor" >&2; exit 1; }
exec "$PYTHON" -B "$SCRIPT_DIR/install-tutor.py" "$@"
