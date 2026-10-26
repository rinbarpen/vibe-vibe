#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(pwd)"

show_help() {
  cat << EOF
Usage: vibe init knowledge-learning [target] [options]

Initialize a knowledge-learning project in the current or target directory.
The target and options may appear in either order.

Options:
  --scenario <name>    Pre-configure for a specific scenario:
                       self-study | exam-prep | course-learning | research-reading
  --force              Overwrite matching template files; preserve extra files
  --help               Show this help

Example:
  vibe init knowledge-learning my-learning-project --scenario course-learning
EOF
}

fail() {
  echo "Error: $*" >&2
  exit 1
}

# Parse all arguments before creating or copying any project files.
SCENARIO=""
FORCE=false
TARGET_SET=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      show_help
      exit 0
      ;;
    --scenario)
      [[ $# -ge 2 && -n "$2" && "$2" != -* ]] || fail "--scenario requires a name"
      SCENARIO="$2"
      shift 2
      ;;
    --scenario=*)
      SCENARIO="${1#*=}"
      [[ -n "$SCENARIO" ]] || fail "--scenario requires a name"
      shift
      ;;
    --force|-f)
      FORCE=true
      shift
      ;;
    -*)
      fail "Unknown option: $1"
      ;;
    *)
      [[ "$TARGET_SET" = false ]] || fail "Unexpected argument: $1"
      [[ -n "$1" ]] || fail "Target directory must not be empty"
      PROJECT_ROOT="$1"
      TARGET_SET=true
      shift
      ;;
  esac
done

if [[ -n "$SCENARIO" ]]; then
  case "$SCENARIO" in
    self-study|exam-prep|course-learning|research-reading) ;;
    *) fail "Unknown scenario: $SCENARIO (available: self-study, exam-prep, course-learning, research-reading)" ;;
  esac
fi

PYTHON="$(command -v python3 || command -v python || true)"
[[ -n "$PYTHON" ]] || fail "Python is required to install manifest files"
mkdir -p "$PROJECT_ROOT"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd -P)"
echo "🚀 Initializing knowledge-learning project in: $PROJECT_ROOT"

PROJECT_DIRS=(materials/{slides,pdf,video,web,audio,images,exercises,epub}
  notes/{atoms,summaries} flashcards/{decks,reviews} projects
  .cursor/{rules,commands,templates} skills references agents)
# Check directory links before mkdir/copy can follow them outside the project.
"$PYTHON" - "$PROJECT_ROOT" "${PROJECT_DIRS[@]}" << 'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
for relative in sys.argv[2:]:
    path = root / relative
    try:
        path.resolve().relative_to(root)
    except ValueError:
        raise SystemExit(f"Error: destination directory leaves project: {path}")
    if path.exists() and not path.is_dir():
        raise SystemExit(f"Error: destination directory conflicts with a file: {path}")
PY

echo "📁 Creating directory structure..."
for dir in "${PROJECT_DIRS[@]}"; do
  mkdir -p "$PROJECT_ROOT/$dir"
done

# Merge files individually. Even --force never removes user-added files.
copy_file() {
  local src="$1"
  local dst="$2"
  [[ ! -d "$dst" || -L "$dst" ]] || fail "Destination file conflicts with a directory: $dst"
  if [[ -e "$dst" || -L "$dst" ]] && [[ "$FORCE" = false ]]; then
    echo "  ⏭️  Skipping $dst (exists, use --force to overwrite)"
    return
  fi
  # Replace the destination path, rather than following a file symlink or
  # truncating a shared hardlink. Refuse real directory/file collisions.
  "$PYTHON" - "$PROJECT_ROOT" "$src" "$dst" << 'PY'
from pathlib import Path
import os
import shutil
import sys
import tempfile

root, source, destination = map(Path, sys.argv[1:])
try:
    destination.parent.resolve().relative_to(root)
except ValueError:
    raise SystemExit(f"Error: destination parent leaves project: {destination}")
if destination.is_dir() and not destination.is_symlink():
    raise SystemExit(f"Error: destination file conflicts with a directory: {destination}")
destination.parent.mkdir(parents=True, exist_ok=True)
descriptor, temporary = tempfile.mkstemp(prefix=".vibe-install-", dir=destination.parent)
os.close(descriptor)
try:
    shutil.copy2(source, temporary)
    os.replace(temporary, destination)
finally:
    if os.path.lexists(temporary):
        os.unlink(temporary)
PY
  echo "  ✅ Copied ${dst#"$PROJECT_ROOT"/}"
}

copy_tree() {
  local src="$1"
  local dst="$2"
  local file
  [[ -d "$src" ]] || return 0
  while IFS= read -r -d '' file; do
    copy_file "$file" "$dst/${file#"$src"/}"
  done < <(find "$src" -type f -print0)
}

echo "📄 Copying manifest files..."
for file in CLAUDE.md AGENTS.md README.md .cursorrules; do
  copy_file "$MANIFEST_DIR/$file" "$PROJECT_ROOT/$file"
done

echo "📏 Installing rules..."
copy_tree "$MANIFEST_DIR/rules" "$PROJECT_ROOT/.cursor/rules"
echo "⚙️  Installing commands..."
copy_tree "$MANIFEST_DIR/commands" "$PROJECT_ROOT/.cursor/commands"
echo "📝 Installing templates..."
copy_tree "$MANIFEST_DIR/templates" "$PROJECT_ROOT/.cursor/templates"
echo "📚 Installing built-in skills, references, and role descriptions..."
copy_tree "$MANIFEST_DIR/skills" "$PROJECT_ROOT/skills"
copy_tree "$MANIFEST_DIR/references" "$PROJECT_ROOT/references"
copy_tree "$MANIFEST_DIR/agents" "$PROJECT_ROOT/agents"

if [[ -n "$SCENARIO" ]]; then
  SCENARIO_DIR="$MANIFEST_DIR/scenarios/$SCENARIO"
  echo "🎯 Applying scenario: $SCENARIO"
  copy_file "$SCENARIO_DIR/CLAUDE.md" "$PROJECT_ROOT/.cursor/scenario.md"
  copy_tree "$SCENARIO_DIR/rules" "$PROJECT_ROOT/.cursor/rules"
fi

# This is learning data once created, not a template to reset on --force.
echo "📖 Creating initial knowledge index..."
if [[ ! -e "$PROJECT_ROOT/notes/_index.md" && ! -L "$PROJECT_ROOT/notes/_index.md" ]]; then
  cat > "$PROJECT_ROOT/notes/_index.md" << 'INDEX'
# Knowledge Index

## Materials

Import and indexing counts only; these do not measure learning or mastery.

| Type | Imported | Indexed | Last Import |
|------|----------|---------|-------------|
| slides | 0 | 0 | — |
| pdf | 0 | 0 | — |
| video | 0 | 0 | — |
| web | 0 | 0 | — |
| audio | 0 | 0 | — |
| images | 0 | 0 | — |
| exercises | 0 | 0 | — |
| epub | 0 | 0 | — |

## Material Maps and Learning Paths

Project-specific material maps and chapter routes belong in
`projects/<教材或主题>/MATERIAL_INDEX.md` and `LEARNING_PATH.md`.

| Project | Material Map | Learning Path |
|---------|--------------|---------------|
INDEX
  echo "  ✅ Created notes/_index.md"
else
  echo "  ⏭️  Preserving existing notes/_index.md (learning data)"
fi

for dir in materials/{slides,pdf,video,web,audio,images,exercises,epub} flashcards/{decks,reviews}; do
  [[ -e "$PROJECT_ROOT/$dir/.gitkeep" || -L "$PROJECT_ROOT/$dir/.gitkeep" ]] || touch "$PROJECT_ROOT/$dir/.gitkeep"
done

echo ""
echo "✅ Knowledge-learning project initialized!"
echo ""
echo "Next steps:"
echo "  1. /import path/to/textbook.pdf            — 索引教材并展示教材地图"
echo "  2. /learn --plan --material path/to/textbook.pdf — 生成章节学习路线"
echo "  3. /study path/to/material                 — 深入学习所选章节"
echo "  4. /learn <topic>                          — 启动学习会话"
echo "  5. /flashcard <topic>                      — 按需生成闪卡"
echo "  6. /review                                — 间隔重复复习"
echo "  7. /exam <topic>                           — 生成试卷/习题"
echo "  8. /diagram <concept> or /mindmap <topic>   — 生成图表或思维导图"
echo "  9. /track                                 — 查看进度"
echo ""
echo "Built-in skills: skills/ (see skills/SKILL.md)"
echo "Settings:"
echo "  STRICT_SOURCE_MODE=true   (default, ensures source citation)"
echo "  NOTEBOOKLM_ENGINE=false   (enable with 'export NOTEBOOKLM_ENGINE=true')"
