#!/usr/bin/env bash
# Install skills from this hub into a project or globally via npx skills (Cursor by default).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

usage() {
  cat >&2 <<'EOF'
Usage:
  install-skills.sh --all [--global] [--agent <name>] [--project <path>]
  install-skills.sh <skill-name> [--global] [--agent <name>] [--project <path>]

Installs from skills/<name>/ in this hub using: npx skills add <path> -a <agent>

Options:
  --agent <name>    Target agent for the skills CLI (default: cursor; e.g. claude-code)
  --global          Install for all projects (cursor: ~/.cursor/skills/, claude-code: ~/.claude/skills/)
  --project <path>  Target project directory (default: current directory)
  --copy            Pass --copy to skills CLI (no symlinks)
  -y                Skip confirmation prompts

Examples:
  ./scripts/install-skills.sh visual-auditor --global
  ./scripts/install-skills.sh --all --project ~/Projects/my-vue-app
  ./scripts/install-skills.sh --all --global --agent claude-code
EOF
  exit 1
}

GLOBAL=false
PROJECT="."
AGENT="cursor"
COPY_FLAG=()
YES_FLAG=()
SKILLS=()
ALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) ALL=true; shift ;;
    --global) GLOBAL=true; shift ;;
    --project) PROJECT="$2"; shift 2 ;;
    --agent)
      [[ $# -ge 2 ]] || usage
      if [[ ! "$2" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
        echo "Error: agent must be lowercase kebab-case (e.g. cursor, claude-code)" >&2
        exit 1
      fi
      AGENT="$2"; shift 2 ;;
    --copy) COPY_FLAG=(--copy); shift ;;
    -y) YES_FLAG=(-y); shift ;;
    -h|--help) usage ;;
    *)
      validate_skill_name "$1"
      SKILLS+=("$1")
      shift
      ;;
  esac
done

if $ALL; then
  for dir in "${REPO_ROOT}/skills"/*/; do
    [[ -d "$dir" ]] || continue
    name="$(basename "$dir")"
    [[ "$name" == .* ]] && continue
    SKILLS+=("$name")
  done
fi

[[ ${#SKILLS[@]} -eq 0 ]] && usage

PROJECT="$(cd "$PROJECT" && pwd)"
GLOBAL_FLAG=()
$GLOBAL && GLOBAL_FLAG=(-g)

for name in "${SKILLS[@]}"; do
  src="${REPO_ROOT}/skills/${name}"
  if [[ ! -f "${src}/SKILL.md" ]]; then
    echo "Error: missing ${src}/SKILL.md" >&2
    exit 1
  fi
  echo "Installing ${name} from ${src} → ${PROJECT} [${AGENT}] ($($GLOBAL && echo global || echo project))..."
  (
    cd "$PROJECT"
    npx skills add "$src" -a "$AGENT" "${GLOBAL_FLAG[@]}" "${COPY_FLAG[@]}" "${YES_FLAG[@]}"
  )
done

echo "Done."
