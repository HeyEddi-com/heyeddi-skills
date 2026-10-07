#!/usr/bin/env bash
# Materialize packs/heyeddi-design-skills into a skills.sh-ready publish tree
# (and optionally push to HeyEddi-com/heyeddi-design-skills).
#
# SSOT remains this hub. The CI repo is a published mirror for skills.sh / npx.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

PACK_FILE="${REPO_ROOT}/packs/heyeddi-design-skills.json"
OUT_DIR=""
PUSH=0
REMOTE_REPO="HeyEddi-com/heyeddi-design-skills"
BRANCH="main"

usage() {
  cat <<EOF
Usage: $0 --out <dir> [--push] [--repo owner/name] [--branch main]

  --out     Destination directory (will be created / refreshed)
  --push    git add/commit/push to --repo (requires gh + write access)
  --repo    GitHub repo (default: HeyEddi-com/heyeddi-design-skills)
  --branch  Branch to push (default: main)
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_DIR="${2:-}"; shift 2 ;;
    --push) PUSH=1; shift ;;
    --repo) REMOTE_REPO="${2:-}"; shift 2 ;;
    --branch) BRANCH="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) usage ;;
  esac
done

[[ -n "$OUT_DIR" ]] || usage
[[ -f "$PACK_FILE" ]] || { echo "Missing ${PACK_FILE}" >&2; exit 1; }

VERSION="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1], encoding='utf-8'))['version'])" "$PACK_FILE")"
mapfile -t SKILL_NAMES < <(python3 -c "import json,sys; print('\n'.join(json.load(open(sys.argv[1], encoding='utf-8'))['skills']))" "$PACK_FILE")

mkdir -p "$OUT_DIR"
# Refresh skills/ only; keep .git if present
rm -rf "${OUT_DIR}/skills"
mkdir -p "${OUT_DIR}/skills"

for name in "${SKILL_NAMES[@]}"; do
  src="${REPO_ROOT}/skills/${name}"
  [[ -d "$src" ]] || { echo "SSOT missing: ${src}" >&2; exit 1; }
  cp -a "$src" "${OUT_DIR}/skills/${name}"
  echo "  copy skills/${name}"
done

cp -a "${REPO_ROOT}/LICENSE" "${OUT_DIR}/LICENSE"

# skills.sh grouping for design pack only
python3 - "$OUT_DIR" "${SKILL_NAMES[@]}" <<'PY'
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
skills = sys.argv[2:]
data = {
    "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
    "notGrouped": "bottom",
    "groupings": [
        {
            "title": "HeyEddi Design",
            "description": "Taste owns the look in one pass. heyeddi-design records product context and hands off to code.",
            "skills": skills,
        }
    ],
}
(out / "skills.sh.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY

python3 - "$OUT_DIR" "$VERSION" "${SKILL_NAMES[@]}" <<'PY'
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
version = sys.argv[2]
skills = sys.argv[3:]
# Minimal registry so consumers / agents can see pack version
reg = {
    "name": "heyeddi-design-skills",
    "version": version,
    "description": "Design-only HeyEddi agent skills (published mirror; SSOT is HeyEddi-com/heyeddi-skills).",
    "skills": skills,
}
(out / "skills-registry.json").write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
PY

cat > "${OUT_DIR}/README.md" <<EOF
# HeyEddi Design Skills

[![skills.sh](https://skills.sh/b/HeyEddi-com/heyeddi-design-skills)](https://skills.sh/HeyEddi-com/heyeddi-design-skills)

Badge populates after skills.sh indexes the first installs.

Design skills for HeyEddi. \`@taste-penpot\` owns the look in one pass. \`@heyeddi-design\` records personas and tokens, then hands off to Vue or Flutter. Penpot is optional.

**skills.sh:** [skills.sh/heyeddi-com/heyeddi-design-skills](https://www.skills.sh/heyeddi-com/heyeddi-design-skills)

**SSOT:** skills are authored in [\`HeyEddi-com/heyeddi-skills\`](https://github.com/HeyEddi-com/heyeddi-skills) (pack \`heyeddi-design-skills\`). This repo is the **published skills.sh package** (mirror), not a second authoring tree.

For the broader open toolkit (design, handoff, human PR review, …), install the hub instead.

## Install

\`\`\`bash
npx skills add HeyEddi-com/heyeddi-design-skills -a cursor -y --skill '*'
\`\`\`

Pin a release:

\`\`\`bash
npx skills add https://github.com/HeyEddi-com/heyeddi-design-skills/tree/v${VERSION} -a cursor -y --skill '*'
\`\`\`

Full open toolkit (design, handoff, human PR review, …):

\`\`\`bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'
\`\`\`

## Pack (v${VERSION})

| Skill | Role |
|-------|------|
| \`@taste-penpot\` | Look. One pass. Penpot when connected. |
| \`@heyeddi-design\` | Product context, design.md, handoff |
| \`@heyeddi-handoff\` | Vue implementation |
| \`@design-handoff-flutter\` | Flutter implementation |
| \`@visual-auditor\` | Screenshots and contrast |
| \`@design-system-generalizer\` | Token and component spread |

## Hub maintainer

\`\`\`bash
# from HeyEddi-com/heyeddi-skills
./scripts/publish-design-pack-repo.sh --out /path/to/heyeddi-design-skills --push
\`\`\`
EOF

# .gitignore for local agent residue
cat > "${OUT_DIR}/.gitignore" <<'EOF'
.agents/
.cursor/
skills-lock.json
__pycache__/
*.pyc
.DS_Store
EOF

echo "Materialized design pack v${VERSION} → ${OUT_DIR}"

if [[ "$PUSH" -eq 1 ]]; then
  if [[ ! -d "${OUT_DIR}/.git" ]]; then
    git -C "$OUT_DIR" init -b "$BRANCH"
    git -C "$OUT_DIR" remote add origin "git@github.com:${REMOTE_REPO}.git" 2>/dev/null \
      || git -C "$OUT_DIR" remote set-url origin "git@github.com:${REMOTE_REPO}.git"
  fi
  git -C "$OUT_DIR" add -A
  if git -C "$OUT_DIR" diff --cached --quiet; then
    echo "No design pack changes to commit"
  else
    git -C "$OUT_DIR" commit -m "chore: sync heyeddi-design-skills pack v${VERSION} from hub"
  fi
  # Tag if missing
  TAG="v${VERSION}"
  if ! git -C "$OUT_DIR" rev-parse -q --verify "refs/tags/${TAG}" >/dev/null; then
    git -C "$OUT_DIR" tag -a "$TAG" -m "HeyEddi Design Skills ${TAG}"
  fi
  git -C "$OUT_DIR" push -u origin "HEAD:${BRANCH}"
  git -C "$OUT_DIR" push origin "$TAG" || true
  # GitHub Release (idempotent)
  if ! gh release view "$TAG" --repo "$REMOTE_REPO" >/dev/null 2>&1; then
    gh release create "$TAG" --repo "$REMOTE_REPO" \
      --title "HeyEddi Design Skills ${TAG}" \
      --notes "Published mirror of pack \`heyeddi-design-skills\` v${VERSION} from HeyEddi-com/heyeddi-skills.

\`\`\`bash
npx skills add HeyEddi-com/heyeddi-design-skills -a cursor -y --skill '*'
\`\`\`
"
  fi
  # Idempotent skills.sh discovery topics (required for indexing)
  if ! gh api --method PUT "repos/${REMOTE_REPO}/topics" \
    -H "Accept: application/vnd.github.mercy-preview+json" \
    --input - <<'TOPICS_EOF'
{"names":["agent-skills","skills-sh","ai-agents","cursor","claude-code","heyeddi","design"]}
TOPICS_EOF
  then
    echo "Warning: failed to set GitHub topics on ${REMOTE_REPO}" >&2
  else
    echo "Ensured GitHub topics on ${REMOTE_REPO}"
  fi
  echo "Pushed ${REMOTE_REPO}@${BRANCH} (${TAG})"
fi
