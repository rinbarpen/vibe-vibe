#!/usr/bin/env bash
set -euo pipefail
ART_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$ART_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo 'Checking that task files have not changed since verification...'
sha256sum -c "$ART_DIR/modified.sha256" >/dev/null
python3 - "$ART_DIR/new_files.list" <<'PY'
from pathlib import Path
import sys
for name in Path(sys.argv[1]).read_text().splitlines():
    Path(name).unlink(missing_ok=True)
for name in (
    'manifests/vibe-coding/platforms/gitee/.workflow',
    'manifests/vibe-coding/platforms/gitee',
    'manifests/vibe-coding/platforms/gitlab',
    'manifests/vibe-coding/platforms',
):
    try:
        Path(name).rmdir()
    except OSError:
        pass
PY
tar -xf "$ART_DIR/originals.tar" -T "$ART_DIR/tracked_files.list"
sha256sum -c "$ART_DIR/baseline_changed.sha256" >/dev/null
echo 'Rollback verified: original task files restored; unrelated files untouched.'
