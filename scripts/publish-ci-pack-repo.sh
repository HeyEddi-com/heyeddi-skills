#!/usr/bin/env bash
# Materialize packs/heyeddi-ci-skills into a skills.sh-ready publish tree
# (and optionally push to HeyEddi-com/heyeddi-ci-skills).
#
# SSOT remains this hub. The CI repo is a published mirror for skills.sh / npx.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

PACK_FILE="${REPO_ROOT}/packs/heyeddi-ci-skills.json"
OUT_DIR=""
PUSH=0
REMOTE_REPO="HeyEddi-com/heyeddi-ci-skills"
BRANCH="main"

usage() {
  cat <<EOF
Usage: $0 --out <dir> [--push] [--repo owner/name] [--branch main]

  --out     Destination directory (will be created / refreshed)
  --push    git add/commit/push to --repo (requires gh + write access)
  --repo    GitHub repo (default: HeyEddi-com/heyeddi-ci-skills)
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

VERSION="$(python3 -c "import json; print(json.load(open('${PACK_FILE}'))['version'])")"
mapfile -t SKILL_NAMES < <(python3 -c "import json; print('\n'.join(json.load(open('${PACK_FILE}'))['skills']))")

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

# skills.sh grouping for CI pack only
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
            "title": "HeyEddi CI",
            "description": "Configure eddi-ci.yaml, respond to HeyEddi findings, diagnose failing checks, and author pipeline YAML (Spot fail-closed).",
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
    "name": "heyeddi-ci-skills",
    "version": version,
    "description": "CI-only HeyEddi agent skills (published mirror; SSOT is HeyEddi-com/heyeddi-skills).",
    "skills": skills,
}
(out / "skills-registry.json").write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
PY

cat > "${OUT_DIR}/README.md" <<EOF
# HeyEddi CI Skills

CI-only [Cursor Agent Skills](https://cursor.com/docs/context/skills) for [HeyEddi CI](https://ci.heyeddi.com).

**skills.sh:** [skills.sh/heyeddi-com/heyeddi-ci-skills](https://www.skills.sh/heyeddi-com/heyeddi-ci-skills)

**SSOT:** authored in [\`HeyEddi-com/heyeddi-skills\`](https://github.com/HeyEddi-com/heyeddi-skills) (pack \`heyeddi-ci-skills\`). This repo is the **published mirror** for skills.sh / \`npx skills\`.

## Install

\`\`\`bash
npx skills add HeyEddi-com/heyeddi-ci-skills -a cursor -y --skill '*'
\`\`\`

Pin a release:

\`\`\`bash
npx skills add https://github.com/HeyEddi-com/heyeddi-ci-skills/tree/v${VERSION} -a cursor -y --skill '*'
\`\`\`

Full product pack (design, handoff, PR review, …):

\`\`\`bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'
\`\`\`

## Pack (v${VERSION})

| Skill | Role |
|-------|------|
| \`@heyeddi-ci-config\` | Author \`eddi-ci.yaml\` from the live policy contract |
| \`@heyeddi-ci-respond\` | Reply to HeyEddi CI findings (not human review) |
| \`@heyeddi-ci-fails\` | Diagnose failing GitHub Checks |
| \`@heyeddi-ci-runners\` | PLACEHOLDER — \`pipeline:\` YAML only (Spot not executing) |
| \`@heyeddi-ci-guide\` | Commands, auth, feedback paths |

## Product honesty

- **No unauthorized merge** — agents need explicit **authorize merge**
- **No structured FP API yet** — use PR debate / \`support@heyeddi.com\`
- **Runners fail-closed** — do not claim jobs ran
- **PR scratch** under \`.heyeddi/docs/pr-*\` is ephemeral / gitignored

## Hub maintainer

\`\`\`bash
# from HeyEddi-com/heyeddi-skills
./scripts/publish-ci-pack-repo.sh --out /path/to/heyeddi-ci-skills --push
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

echo "Materialized CI pack v${VERSION} → ${OUT_DIR}"

if [[ "$PUSH" -eq 1 ]]; then
  if [[ ! -d "${OUT_DIR}/.git" ]]; then
    git -C "$OUT_DIR" init -b "$BRANCH"
    git -C "$OUT_DIR" remote add origin "git@github.com:${REMOTE_REPO}.git" 2>/dev/null \
      || git -C "$OUT_DIR" remote set-url origin "git@github.com:${REMOTE_REPO}.git"
  fi
  git -C "$OUT_DIR" add -A
  if git -C "$OUT_DIR" diff --cached --quiet; then
    echo "No CI pack changes to commit"
  else
    git -C "$OUT_DIR" commit -m "chore: sync heyeddi-ci-skills pack v${VERSION} from hub"
  fi
  # Tag if missing
  TAG="v${VERSION}"
  if ! git -C "$OUT_DIR" rev-parse -q --verify "refs/tags/${TAG}" >/dev/null; then
    git -C "$OUT_DIR" tag -a "$TAG" -m "HeyEddi CI Skills ${TAG}"
  fi
  git -C "$OUT_DIR" push -u origin "HEAD:${BRANCH}"
  git -C "$OUT_DIR" push origin "$TAG" || true
  # GitHub Release (idempotent)
  if ! gh release view "$TAG" --repo "$REMOTE_REPO" >/dev/null 2>&1; then
    gh release create "$TAG" --repo "$REMOTE_REPO" \
      --title "HeyEddi CI Skills ${TAG}" \
      --notes "Published mirror of pack \`heyeddi-ci-skills\` v${VERSION} from HeyEddi-com/heyeddi-skills.

\`\`\`bash
npx skills add HeyEddi-com/heyeddi-ci-skills -a cursor -y --skill '*'
\`\`\`
"
  fi
  echo "Pushed ${REMOTE_REPO}@${BRANCH} (${TAG})"
fi
