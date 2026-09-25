#!/usr/bin/env bash
set -euo pipefail

MANIFEST_DIR="$(cd "$(dirname "$0")/.." && pwd)"

print_usage() {
  cat <<EOF
Usage: $(basename "$0") [target-dir] [options]

Initialize a research project with Auto-Research configuration.
When target-dir is omitted (as with \`vibe init\`), the current directory is used.

Options:
  -o, --owner <owner>     Default owner for CODEOWNERS (default: researcher)
  --org <org>             GitHub organization name (default: org)
  --repo <repo>           GitHub repository name (default: repo)
  -f, --force             Replace installed scaffold files (runtime records preserved)
  -n, --dry-run           Preview the target without writing
  -h, --help              Show this help message

Example:
  $(basename "$0") /path/to/research-project --owner pi-name --org lab --repo awesome-vit
EOF
  exit 0
}

DEFAULT_OWNER="researcher"
ORG_NAME="org"
REPO_NAME="repo"
TARGET_DIR="."
FORCE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--owner) DEFAULT_OWNER="$2"; shift 2 ;;
    --org) ORG_NAME="$2"; shift 2 ;;
    --repo) REPO_NAME="$2"; shift 2 ;;
    -f|--force) FORCE=true; shift ;;
    -n|--dry-run) DRY_RUN=true; shift ;;
    -h|--help) print_usage ;;
    -*)
      echo "Unknown option: $1"
      print_usage
      ;;
    *)
      if [[ "$TARGET_DIR" == "." ]]; then
        TARGET_DIR="$1"
        shift
      else
        echo "Unexpected argument: $1"
        print_usage
      fi
      ;;
  esac
done

if [[ ! -d "$TARGET_DIR" ]]; then
  if [[ "$DRY_RUN" == true ]]; then
    echo "[dry-run] Would initialize Auto-Research project in: $TARGET_DIR"
    exit 0
  fi
  mkdir -p "$TARGET_DIR"
fi

TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo "Initializing Auto-Research project in: $TARGET_DIR"

if [[ "$DRY_RUN" == true ]]; then
  echo "[dry-run] Would install GitHub configuration, manifest instructions, templates, references, and Writing Plan resources."
  exit 0
fi

# Create directory structure
mkdir -p "$TARGET_DIR/.github/ISSUE_TEMPLATE"
mkdir -p "$TARGET_DIR/.github/workflows"
mkdir -p "$TARGET_DIR/references"
mkdir -p "$TARGET_DIR/templates"
mkdir -p "$TARGET_DIR/paper"
mkdir -p "$TARGET_DIR/figures"
mkdir -p "$TARGET_DIR/data"
mkdir -p "$TARGET_DIR/code/src"
mkdir -p "$TARGET_DIR/code/scripts"
mkdir -p "$TARGET_DIR/code/tests"
mkdir -p "$TARGET_DIR/code/config"
mkdir -p "$TARGET_DIR/scripts"
mkdir -p "$TARGET_DIR/writing"
mkdir -p "$TARGET_DIR/.auto-research"

# Preserve project files unless replacement is explicitly requested.
install_file() {
  local src="$1" dst="$2"
  if [[ -e "$dst" && "$FORCE" != true ]]; then
    echo "  → Preserving $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

# Copy and substitute
substitute() {
  local src="$1"
  local dst="$2"
  if [[ -e "$dst" && "$FORCE" != true ]]; then return; fi
  sed \
    -e "s/\${DEFAULT_OWNER}/$DEFAULT_OWNER/g" \
    -e "s/\${ORG_NAME}/$ORG_NAME/g" \
    -e "s/\${REPO_NAME}/$REPO_NAME/g" \
    "$src" > "$dst"
}

# GitHub config
echo "  → Installing GitHub configuration..."
substitute "$MANIFEST_DIR/.github/ISSUE_TEMPLATE/config.yml" "$TARGET_DIR/.github/ISSUE_TEMPLATE/config.yml"

for tmpl in "$MANIFEST_DIR/.github/ISSUE_TEMPLATE/"0*.yml; do
  install_file "$tmpl" "$TARGET_DIR/.github/ISSUE_TEMPLATE/$(basename "$tmpl")"
done

# Manifest instructions
echo "  → Installing manifest instructions..."
install_file "$MANIFEST_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md"
install_file "$MANIFEST_DIR/AGENTS.md" "$TARGET_DIR/AGENTS.md"
install_file "$MANIFEST_DIR/MANIFEST.md" "$TARGET_DIR/MANIFEST.md"
install_file "$MANIFEST_DIR/README.md" "$TARGET_DIR/README.md"

for wf in "$MANIFEST_DIR/.github/workflows/"*.yml; do
  install_file "$wf" "$TARGET_DIR/.github/workflows/$(basename "$wf")"
done

# Templates
echo "  → Installing templates..."
for tmpl in "$MANIFEST_DIR/templates/"*; do
  install_file "$tmpl" "$TARGET_DIR/templates/$(basename "$tmpl")"
done

# Reference docs
echo "  → Installing reference documentation..."
for ref in "$MANIFEST_DIR/references/"*; do
  install_file "$ref" "$TARGET_DIR/references/$(basename "$ref")"
done

# Writing Plan runtime and resources
echo "  → Installing Writing Plan subsystem..."
install_file "$MANIFEST_DIR/scripts/writing_plan.py" "$TARGET_DIR/scripts/writing_plan.py"
chmod +x "$TARGET_DIR/scripts/writing_plan.py"
for resource in "$MANIFEST_DIR/writing/"*; do
  install_file "$resource" "$TARGET_DIR/writing/$(basename "$resource")"
done

# Lifecycle resources are templates only; runtime settings/history are never overwritten.
mkdir -p "$TARGET_DIR/lifecycle"
for lifecycle_file in "$MANIFEST_DIR/lifecycle/"*; do
  install_file "$lifecycle_file" "$TARGET_DIR/lifecycle/$(basename "$lifecycle_file")"
done
for script in research_workflow.py stage_contract.py table_plan.py table_ablation.py experiment_stats.py figure_smoke.py latex_template_gate.py; do
  install_file "$MANIFEST_DIR/scripts/$script" "$TARGET_DIR/scripts/$script"
done

echo ""
echo "✓ Auto-Research project initialized!"
echo ""
echo "Next steps:"
echo "  1. Initialize lifecycle tracking: python3 scripts/research_workflow.py init"
echo "     Configure verified model bindings and project Git identity before checkpointing."
echo "  2. Start the pipeline: aris/research-pipeline \"topic\""
echo "  3. Submit for review: use 'Paper Submission' issue template"
echo "  4. Generate figures: use 'Figure Request' issue template"
echo "  5. Create the writing plan after outlining:"
echo "     uv run scripts/writing_plan.py init --outline PAPER_OUTLINE.md --output .auto-research/writing-plan.yaml"
echo ""
echo "Project structure created:"
echo "  paper/        - Paper source files"
echo "  figures/      - Generated figures"
echo "  data/         - Experiment data"
echo "  code/         - Experiment code (src/, scripts/, tests/, config/)"
echo "  references/   - Research references"
echo "  templates/    - Research plan/paper templates"
echo "  writing/      - Writing Plan schema, profiles, examples, and documentation"
echo "  lifecycle/    - Three-level research stages and role defaults"
echo "  .auto-research/ - Runtime lifecycle, Writing Plan and review artifacts"
