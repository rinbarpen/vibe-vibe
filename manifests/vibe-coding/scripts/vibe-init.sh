#!/bin/bash
# vibe-init: Unified initialization script for the Vibe Coding manifest.
# Supports scenario selection, cloud platform config, GitHub enterprise setup,
# git initialization, and more.
#
# Usage:
#   bash manifests/vibe-coding/scripts/vibe-init.sh [target-dir] [options]
#
# Examples:
#   bash vibe-init.sh . --scenario=fullstack-web,saas --cloud=vercel
#   bash vibe-init.sh /path/to/project --scenario=api-service --org mycompany --repo my-app
#   bash vibe-init.sh . --scenario=cli-tool --no-git --dry-run

set -euo pipefail

# ── Paths ──
MANIFEST_DIR="${VIBE_MANIFEST:-$(cd "$(dirname "$0")/.." && pwd)}"
RELATIVE_MANIFEST_DIR=$(realpath --relative-to="$(pwd)" "$MANIFEST_DIR" 2>/dev/null || echo "$MANIFEST_DIR")

# ── Defaults ──
SCENARIOS=""
CLOUD_PROVIDER=""
DEFAULT_OWNER="default-owner"
ORG_NAME=""
REPO_NAME=""
SECURITY_EMAIL="security@example.com"
FORCE=false
DRY_RUN=false
DO_GIT="auto"  # auto, yes, no
TARGET=""

# ── Help ──
print_usage() {
  cat <<EOF
Usage: $(basename "$0") [target-dir] [options]

Initialize a project with the Unified Vibe Coding Manifest.

Scenarios:
  --scenario=<name>[,<name>...]    One or more scenarios to activate
                                     agent-dev / api-service / cli-tool / cross-platform /
                                     data-pipeline / distributed / frontend / fullstack-web /
                                     llm-dev / research / saas /
                                     desktop-electron / desktop-tauri / desktop-flutter /
                                     wechat-miniprogram

Cloud Platform:
  --cloud=<provider>               Configure cloud deployment support
                                     vercel / cloudflare / tencent / alibaba / huawei

GitHub Enterprise:
  -o, --owner <owner>              Default owner/team for CODEOWNERS (default: default-owner)
  --org <org>                      GitHub organization name
  --repo <repo>                    GitHub repository name
  --email <email>                  Security contact email (default: security@example.com)

Git:
  --git                            Force git repository initialization
  --no-git                         Skip git initialization

General:
  -f, --force                      Overwrite existing files
  -n, --dry-run                    Preview what would be installed
  -h, --help                       Show this help message

Examples:
  $(basename "$0") . --scenario=fullstack-web --cloud=vercel --git
  $(basename "$0") /path/to/project --scenario=api-service --owner team-lead --org mycompany --repo my-app
  $(basename "$0") . --scenario=saas --cloud=tencent --org mycompany --repo my-saas
  $(basename "$0") . --scenario=cli-tool --no-git --dry-run
EOF
  exit 0
}

# ── Parse args ──
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scenario=*) SCENARIOS="${1#*=}" ; shift ;;
    --scenario) SCENARIOS="$2" ; shift 2 ;;
    --cloud=*) CLOUD_PROVIDER="${1#*=}" ; shift ;;
    --cloud) CLOUD_PROVIDER="$2" ; shift 2 ;;
    -o|--owner) DEFAULT_OWNER="$2" ; shift 2 ;;
    --org) ORG_NAME="$2" ; shift 2 ;;
    --repo) REPO_NAME="$2" ; shift 2 ;;
    --email) SECURITY_EMAIL="$2" ; shift 2 ;;
    --git) DO_GIT="yes" ; shift ;;
    --no-git) DO_GIT="no" ; shift ;;
    -f|--force) FORCE=true ; shift ;;
    -n|--dry-run) DRY_RUN=true ; shift ;;
    -h|--help) print_usage ;;
    -*)
      echo "Unknown option: $1"
      print_usage ;;
    *)
      if [[ -z "$TARGET" ]]; then TARGET="$1" ; shift
      else echo "Unexpected argument: $1"; print_usage ; fi ;;
  esac
done

TARGET="${TARGET:-$(pwd)}"
mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd)"
PROJECT_ROOT="$TARGET"

echo "=== Vibe Coding Unified Manifest Init ==="
echo "  Source:    $MANIFEST_DIR"
echo "  Target:    $TARGET"
echo "  Scenarios: ${SCENARIOS:-default}"
[[ -n "$CLOUD_PROVIDER" ]] && echo "  Cloud:     $CLOUD_PROVIDER"
$DRY_RUN && echo "  Mode:      DRY RUN (no files written)"
echo ""

# ── Helpers ──

copy_file() {
  local src="$1" dst="$2"
  local label="${dst#$TARGET/}"
  mkdir -p "$(dirname "$dst")"

  if [[ -f "$dst" && "$FORCE" != true ]]; then
    echo "  SKIP  $label (exists)"
    return
  fi

  if $DRY_RUN; then
    echo "  WILL  $label"
    return
  fi

  cp "$src" "$dst"
  echo "  COPY  $label"
}

link_file() {
  local src="$1" dst="$2"
  local label="${dst#$TARGET/}"
  mkdir -p "$(dirname "$dst")"

  if { [[ -e "$dst" ]] || [[ -L "$dst" ]]; } && [[ "$FORCE" != true ]]; then
    echo "  SKIP  $label (exists)"
    return
  fi

  if $DRY_RUN; then
    echo "  WILL  $label -> $src"
    return
  fi

  ln -sfn "$src" "$dst"
  echo "  LINK  $label -> $src"
}

copy_with_subst() {
  local src="$1" dst="$2"
  local label="${dst#$TARGET/}"
  mkdir -p "$(dirname "$dst")"

  if [[ -f "$dst" && "$FORCE" != true ]]; then
    echo "  SKIP  $label (exists)"
    return
  fi

  if $DRY_RUN; then
    echo "  WILL  $label"
    return
  fi

  sed \
    -e "s|\${DEFAULT_OWNER}|$DEFAULT_OWNER|g" \
    -e "s|\${ORG_NAME}|${ORG_NAME:-org}|g" \
    -e "s|\${REPO_NAME}|${REPO_NAME:-repo}|g" \
    -e "s|\${SECURITY_EMAIL}|$SECURITY_EMAIL|g" \
    -e "s|{{VIBE_MANIFEST}}|$RELATIVE_MANIFEST_DIR|g" \
    "$src" > "$dst"
  echo "  COPY  $label"
}

# ── Zone 1: Directory Structure ──
echo "── Zone 1: Directory Structure ──"
if ! $DRY_RUN; then
  mkdir -p \
    "$TARGET/src" \
    "$TARGET/tests" \
    "$TARGET/docs" \
    "$TARGET/scripts" \
    "$TARGET/infra" \
    "$TARGET/cloud" \
    "$TARGET/.cursor/plans" \
    "$TARGET/.cursor/rules" \
    "$TARGET/.cursor/commands" \
    "$TARGET/.cursor/references/language-specs" \
    "$TARGET/.cursor/references/decision-trees" \
    "$TARGET/.cursor/references/cloud-platforms" \
    "$TARGET/.cursor/references"
  echo "  CREATE  directories"
else
  echo "  WILL CREATE directories"
fi

# ── Zone 2: Core Files ──
echo ""
echo "── Zone 2: Core Files ──"
copy_file "$MANIFEST_DIR/MANIFEST.md"   "$TARGET/MANIFEST.md"
link_file "MANIFEST.md"                 "$TARGET/CLAUDE.md"
link_file "MANIFEST.md"                 "$TARGET/AGENTS.md"
copy_file "$MANIFEST_DIR/README.md"      "$TARGET/README.md"
copy_file "$MANIFEST_DIR/CONTRIBUTING.md" "$TARGET/CONTRIBUTING.md"
copy_file "$MANIFEST_DIR/.cursorrules"   "$TARGET/.cursorrules"
copy_file "$MANIFEST_DIR/.editorconfig"  "$TARGET/.editorconfig"
copy_file "$MANIFEST_DIR/.gitignore"     "$TARGET/.gitignore"

# ── Zone 3: Install Rules ──
echo ""
echo "── Zone 3: Rules ──"
for file in "$MANIFEST_DIR/rules"/*.mdc; do
  [[ -f "$file" ]] || continue
  filename=$(basename "$file")
  dest="$TARGET/.cursor/rules/$filename"
  if $DRY_RUN; then
    copy_with_subst "$file" "$dest"
  else
    mkdir -p "$TARGET/.cursor/rules"
    if [[ -f "$dest" && "$FORCE" != true ]]; then
      echo "  SKIP  rules/$filename (exists)"
    else
      sed "s|{{VIBE_MANIFEST}}|$RELATIVE_MANIFEST_DIR|g" "$file" > "$dest"
      echo "  COPY  rules/$filename"
    fi
  fi
done

# ── Zone 4: Scenario-specific Rules ──
if [[ -n "$SCENARIOS" ]]; then
  echo ""
  echo "── Zone 4: Scenario Rules ──"
  IFS=',' read -ra SCENARIO_LIST <<< "$SCENARIOS"
  for scenario in "${SCENARIO_LIST[@]}"; do
    scenario_dir="$MANIFEST_DIR/scenarios/$scenario"
    if [[ -d "$scenario_dir" ]]; then
      echo "  Scenario: $scenario"

      # Copy scenario-specific rules
      if [[ -d "$scenario_dir/rules" ]]; then
        for rule_file in "$scenario_dir/rules"/*.mdc; do
          [[ -f "$rule_file" ]] || continue
          rname=$(basename "$rule_file")
          rdest="$TARGET/.cursor/rules/$rname"
          if $DRY_RUN; then
            echo "    WILL  rules/$rname"
          elif [[ -f "$rdest" && "$FORCE" != true ]]; then
            echo "    SKIP  rules/$rname (exists)"
          else
            sed "s|{{VIBE_MANIFEST}}|$RELATIVE_MANIFEST_DIR|g" "$rule_file" > "$rdest"
            echo "    COPY  rules/$rname"
          fi
        done
      fi

      # Copy scenario CLAUDE.md as project CLAUDE.md if no CLAUDE.md yet
      if [[ -f "$scenario_dir/CLAUDE.md" && ! -f "$TARGET/CLAUDE.md" ]]; then
        if ! $DRY_RUN; then
          cp "$scenario_dir/CLAUDE.md" "$TARGET/CLAUDE.md"
          echo "    COPY  CLAUDE.md (from scenario: $scenario)"
        fi
      fi
    else
      echo "  WARN: Scenario '$scenario' not found in $MANIFEST_DIR/scenarios/"
    fi
  done
fi

# ── Zone 5: GitHub Enterprise (.github/) ──
echo ""
echo "── Zone 5: GitHub Enterprise Governance ──"

install_github_file() {
  local src="$1" dst="$2" needs_subst="${3:-false}"
  local label="${dst#$TARGET/}"

  if [[ -f "$dst" && "$FORCE" != true ]]; then
    echo "  SKIP  $label (exists)"
    return
  fi
  if $DRY_RUN; then
    echo "  WILL  $label"
    return
  fi

  mkdir -p "$(dirname "$dst")"
  if [[ "$needs_subst" == true ]]; then
    sed \
      -e "s|\${DEFAULT_OWNER}|$DEFAULT_OWNER|g" \
      -e "s|\${ORG_NAME}|${ORG_NAME:-org}|g" \
      -e "s|\${REPO_NAME}|${REPO_NAME:-repo}|g" \
      -e "s|\${SECURITY_EMAIL}|$SECURITY_EMAIL|g" \
      "$src" > "$dst"
  else
    cp "$src" "$dst"
  fi
  echo "  COPY  $label"
}

if [[ -d "$MANIFEST_DIR/.github" ]]; then
  install_github_file "$MANIFEST_DIR/.github/CODEOWNERS"             "$TARGET/.github/CODEOWNERS" true
  install_github_file "$MANIFEST_DIR/.github/SECURITY.md"            "$TARGET/.github/SECURITY.md" true
  install_github_file "$MANIFEST_DIR/.github/CODE_OF_CONDUCT.md"     "$TARGET/.github/CODE_OF_CONDUCT.md" true
  install_github_file "$MANIFEST_DIR/.github/dependabot.yml"         "$TARGET/.github/dependabot.yml" true
  install_github_file "$MANIFEST_DIR/.github/ISSUE_TEMPLATE/config.yml" "$TARGET/.github/ISSUE_TEMPLATE/config.yml" true

  for tmpl in "$MANIFEST_DIR/.github/ISSUE_TEMPLATE"/*.yml; do
    [[ -f "$tmpl" && "$(basename "$tmpl")" != "config.yml" ]] || continue
    install_github_file "$tmpl" "$TARGET/.github/ISSUE_TEMPLATE/$(basename "$tmpl")" false
  done

  install_github_file "$MANIFEST_DIR/.github/PULL_REQUEST_TEMPLATE/default.md" "$TARGET/.github/PULL_REQUEST_TEMPLATE/default.md" false

  for wf in "$MANIFEST_DIR/.github/workflows"/*.yml; do
    [[ -f "$wf" ]] || continue
    install_github_file "$wf" "$TARGET/.github/workflows/$(basename "$wf")" false
  done
fi

# ── Zone 6: References ──
echo ""
echo "── Zone 6: References ──"

# Language specs
if [[ -d "$MANIFEST_DIR/references/language-specs" ]]; then
  for spec in "$MANIFEST_DIR/references/language-specs"/*.md; do
    [[ -f "$spec" ]] || continue
    copy_file "$spec" "$TARGET/.cursor/references/language-specs/$(basename "$spec")"
  done
fi

# Decision trees
if [[ -d "$MANIFEST_DIR/references/decision-trees" ]]; then
  for dt in "$MANIFEST_DIR/references/decision-trees"/*.md; do
    [[ -f "$dt" ]] || continue
    copy_file "$dt" "$TARGET/.cursor/references/decision-trees/$(basename "$dt")"
  done
fi

# Enterprise references
for ref in branching-strategy pages-guide pr-conventions readme-guide release-process tag-convention lifecycle-guide; do
  ref_file="$MANIFEST_DIR/references/${ref}.md"
  [[ -f "$ref_file" ]] || continue
  copy_file "$ref_file" "$TARGET/.cursor/references/${ref}.md"
done

# ── Zone 7: Cloud Platform References ──
if [[ -n "$CLOUD_PROVIDER" ]]; then
  echo ""
  echo "── Zone 7: Cloud Platform ($CLOUD_PROVIDER) ──"

  # Install the specific cloud platform reference
  cloud_file="$MANIFEST_DIR/references/cloud-platforms/${CLOUD_PROVIDER}.md"
  if [[ -f "$cloud_file" ]]; then
    copy_file "$cloud_file" "$TARGET/.cursor/references/cloud-platforms/${CLOUD_PROVIDER}.md"
    echo "  Cloud platform reference installed: $CLOUD_PROVIDER"
  else
    echo "  WARN: Cloud platform '$CLOUD_PROVIDER' reference not found"
  fi

  # Optionally install all cloud references
  for cloud_doc in "$MANIFEST_DIR/references/cloud-platforms"/*.md; do
    [[ -f "$cloud_doc" ]] || continue
    copy_file "$cloud_doc" "$TARGET/.cursor/references/cloud-platforms/$(basename "$cloud_doc")"
  done
fi

# ── Zone 8: Commands ──
echo ""
echo "── Zone 8: Commands ──"
if [[ -d "$MANIFEST_DIR/commands" ]]; then
  for cmd_dir in "$MANIFEST_DIR/commands"/*/; do
    [[ -d "$cmd_dir" ]] || continue
    cmd_name=$(basename "$cmd_dir")
    cmd_dest="$TARGET/.cursor/commands/$cmd_name"
    if ! $DRY_RUN; then
      mkdir -p "$cmd_dest"
      cp "$cmd_dir"* "$cmd_dest/" 2>/dev/null || true
    fi
    echo "  COPY  commands/$cmd_name"
  done
fi

# ── Zone 9: Git Init ──
echo ""
echo "── Zone 9: Git Repository ──"

if [[ "$DO_GIT" == "no" ]]; then
  echo "  SKIP  git init (--no-git)"
elif $DRY_RUN; then
  echo "  WILL  git init"
elif [[ ! -d "$TARGET/.git" ]]; then
  git -C "$TARGET" init
  echo "  INIT  git repository"
else
  echo "  SKIP  .git already exists"
fi

# ── Zone 10: Agents ──
echo ""
echo "── Zone 10: Agents ──"
for runtime_agents in ".claude/agents" ".codex/agents"; do
    SOURCE_DIR="$MANIFEST_DIR/$runtime_agents"
    if [ -d "$SOURCE_DIR" ]; then
        echo "  Installing $runtime_agents..."
        mkdir -p "$runtime_agents"
        for agent_file in "$SOURCE_DIR"/*; do
            [ -f "$agent_file" ] || continue
            agent_name=$(basename "$agent_file")
            if [ ! -f "$runtime_agents/$agent_name" ]; then
                $DRY_RUN || cp "$agent_file" "$runtime_agents/$agent_name"
            fi
        done
    fi
done

# ── Zone 11: Templates ──
echo ""
echo "── Zone 11: Templates ──"
if [[ -d "$MANIFEST_DIR/templates" ]]; then
  for tmpl in "$MANIFEST_DIR/templates"/*; do
    [[ -f "$tmpl" ]] || continue
    copy_file "$tmpl" "$TARGET/.cursor/templates/$(basename "$tmpl")"
  done
fi

# ── Summary ──
echo ""
echo "=== Initialization Complete ==="
echo ""
if [[ -n "$SCENARIOS" ]]; then
  echo "Scenarios activated: $SCENARIOS"
else
  echo "Scenarios activated: default (all core rules)"
fi
[[ -n "$CLOUD_PROVIDER" ]] && echo "Cloud platform: $CLOUD_PROVIDER"
[[ -n "$ORG_NAME" ]] && echo "GitHub org: $ORG_NAME"
echo ""
echo "Next steps:"
echo "  1. Review CLAUDE.md and customize for your project"
echo "  2. Update .github/CODEOWNERS with your actual teams"
echo "  3. Update .github/SECURITY.md with your security contact"
echo "  4. Configure branch protection rules in GitHub Web UI"
echo "  5. Run /lang-select to choose languages (if not yet decided)"
echo "  6. Run /plan to create your first implementation plan"
echo "  7. Commit and push:"
echo "       git add -A && git commit -m 'feat: initialize project with Vibe Coding manifest'"
echo "       git remote add origin https://github.com/${ORG_NAME:-org}/${REPO_NAME:-repo}.git"
echo "       git push -u origin main"
