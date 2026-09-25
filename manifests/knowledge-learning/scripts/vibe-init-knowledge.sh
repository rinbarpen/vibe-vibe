#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT=$(pwd)

# Display help
show_help() {
  cat << EOF
Usage: vibe init knowledge-learning [target] [options]

Initialize a knowledge-learning project in the current or target directory.

Options:
  --scenario <name>    Pre-configure for a specific scenario:
                       self-study | exam-prep | course-learning | research-reading
  --strict             Enable strict source mode (default: true)
  --notebooklm         Enable NotebookLM Engine (default: false)
  --force              Overwrite existing files
  --help               Show this help

Example:
  vibe init knowledge-learning my-learning-project --scenario course-learning
EOF
  exit 0
}

# Parse arguments
SCENARIO=""
FORCE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --help) show_help ;;
    --scenario) SCENARIO="$2"; shift 2 ;;
    --force) FORCE=true; shift ;;
    --strict) shift ;; # default is true
    --notebooklm) shift ;; # default is false
    *) break ;;
  esac
done

# Determine project root
if [ -n "$1" ]; then
  PROJECT_ROOT="$1"
  mkdir -p "$PROJECT_ROOT"
fi

echo "🚀 Initializing knowledge-learning project in: $PROJECT_ROOT"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "$PROJECT_ROOT"/materials/{slides,pdf,video,web,audio,images,exercises,epub}
mkdir -p "$PROJECT_ROOT"/notes/{atoms,summaries}
mkdir -p "$PROJECT_ROOT"/flashcards/{decks,reviews}
mkdir -p "$PROJECT_ROOT"/projects
mkdir -p "$PROJECT_ROOT"/.cursor/{rules,commands}

# Copy core files
echo "📄 Copying manifest files..."
copy_file() {
  local src="$1"
  local dst="$2"
  if [ -f "$dst" ] && [ "$FORCE" = false ]; then
    echo "  ⏭️  Skipping $dst (exists, use --force to overwrite)"
  else
    cp "$src" "$dst"
    echo "  ✅ Copied $(basename $dst)"
  fi
}

copy_file "$MANIFEST_DIR/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md"
copy_file "$MANIFEST_DIR/AGENTS.md" "$PROJECT_ROOT/AGENTS.md"
copy_file "$MANIFEST_DIR/MANIFEST.md" "$PROJECT_ROOT/MANIFEST.md"
copy_file "$MANIFEST_DIR/README.md" "$PROJECT_ROOT/README.md"

# Copy rules
echo "📏 Installing rules..."
for file in "$MANIFEST_DIR/rules"/*.mdc; do
  copy_file "$file" "$PROJECT_ROOT/.cursor/rules/$(basename "$file")"
done

# Copy commands
echo "⚙️  Installing commands..."
copy_file "$MANIFEST_DIR/commands/COMMANDS.md" "$PROJECT_ROOT/.cursor/commands/COMMANDS.md"

# Copy templates
echo "📝 Installing templates..."
mkdir -p "$PROJECT_ROOT/.cursor/templates"
for file in "$MANIFEST_DIR/templates"/*.example; do
  copy_file "$file" "$PROJECT_ROOT/.cursor/templates/$(basename "$file")"
done

# Handle scenario
if [ -n "$SCENARIO" ]; then
  SCENARIO_DIR="$MANIFEST_DIR/scenarios/$SCENARIO"
  if [ -d "$SCENARIO_DIR" ]; then
    echo "🎯 Applying scenario: $SCENARIO"
    copy_file "$SCENARIO_DIR/CLAUDE.md" "$PROJECT_ROOT/.cursor/scenario.md"
    for rule_file in "$SCENARIO_DIR/rules"/*.mdc; do
      if [ -f "$rule_file" ]; then
        copy_file "$rule_file" "$PROJECT_ROOT/.cursor/rules/$(basename "$rule_file")"
      fi
    done
  else
    echo "⚠️  Unknown scenario: $SCENARIO"
    echo "   Available: self-study, exam-prep, course-learning, research-reading"
  fi
fi

# Create initial knowledge index
echo "📖 Creating initial knowledge index..."
if [ ! -f "$PROJECT_ROOT/notes/_index.md" ] || [ "$FORCE" = true ]; then
cat > "$PROJECT_ROOT/notes/_index.md" << 'INDEX'
# Knowledge Index

## Materials

| Type | Count | Last Import |
|------|-------|-------------|
| slides | 0 | — |
| pdf | 0 | — |
| video | 0 | — |
| web | 0 | — |
| audio | 0 | — |
| exercises | 0 | — |

## Stats

- Total notes: 0
- Total flashcards: 0
- Review completion rate: —
INDEX
  echo "  ✅ Created notes/_index.md"
fi

# Create .gitkeep files
touch "$PROJECT_ROOT/materials/slides/.gitkeep"
touch "$PROJECT_ROOT/materials/pdf/.gitkeep"
touch "$PROJECT_ROOT/materials/video/.gitkeep"
touch "$PROJECT_ROOT/materials/web/.gitkeep"
touch "$PROJECT_ROOT/materials/audio/.gitkeep"
touch "$PROJECT_ROOT/materials/images/.gitkeep"
touch "$PROJECT_ROOT/materials/exercises/.gitkeep"
touch "$PROJECT_ROOT/materials/epub/.gitkeep"
touch "$PROJECT_ROOT/flashcards/decks/.gitkeep"
touch "$PROJECT_ROOT/flashcards/reviews/.gitkeep"

echo ""
echo "✅ Knowledge-learning project initialized!"
echo ""
echo "Next steps:"
echo "  1. /import path/to/your/material.pptx   — 导入学习材料"
echo "  2. /study path/to/material                — 开始学习"
echo "  3. /learn <topic>                         — 启动学习会话"
echo "  4. /flashcard <topic>                     — 生成闪卡"
echo "  5. /review                                — 间隔重复复习"
echo "  6. /exam <topic>                          — 生成试卷/习题 (--difficulty, --format)"
echo "  7. /diagram <concept>                     — 生成图表 (--type flowchart/mindmap/...)"
echo "  8. /track                                 — 查看进度"
echo ""
echo "Settings:"
echo "  STRICT_SOURCE_MODE=true   (default, ensures source citation)"
echo "  NOTEBOOKLM_ENGINE=false   (enable with 'export NOTEBOOKLM_ENGINE=true')"
