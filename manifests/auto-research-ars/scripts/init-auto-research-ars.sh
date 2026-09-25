#!/usr/bin/env bash
set -euo pipefail

MANIFEST_DIR="$(cd "$(dirname "$0")/.." && pwd)"

print_usage() {
  cat <<EOF
Usage: $(basename "$0") <target-dir>

Initialize a research project with ARS Auto-Research configuration.

Example:
  $(basename "$0") /path/to/research-project
EOF
  exit 0
}

TARGET_DIR="${1:-}"
if [[ -z "$TARGET_DIR" ]]; then
  echo "Error: target directory is required"
  print_usage
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  mkdir -p "$TARGET_DIR"
fi

TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
echo "Initializing ARS Auto-Research project in: $TARGET_DIR"

for file in CLAUDE.md AGENTS.md MANIFEST.md README.md; do
  if [[ ! -e "$TARGET_DIR/$file" ]]; then cp "$MANIFEST_DIR/$file" "$TARGET_DIR/$file"; fi
done

mkdir -p "$TARGET_DIR/references"
mkdir -p "$TARGET_DIR/templates"
mkdir -p "$TARGET_DIR/paper"
mkdir -p "$TARGET_DIR/figures"

# Templates
echo "  → Installing templates..."
for tmpl in "$MANIFEST_DIR/templates/"*; do
  cp "$tmpl" "$TARGET_DIR/templates/"
done

# References
echo "  → Installing reference documentation..."
for ref in "$MANIFEST_DIR/references/"*; do
  cp "$ref" "$TARGET_DIR/references/"
done

echo ""
echo "✓ ARS Auto-Research project initialized!"
echo ""
echo "Quick start:"
echo "  1. Research:    ars/deep-research \"research question\""
echo "  2. Write paper: ars/academic-paper \"paper topic\""
echo "  3. Review:      ars/academic-paper-reviewer \"paper\""
echo "  4. Full pipe:   ars/academic-pipeline \"topic\""
