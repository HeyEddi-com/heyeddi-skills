#!/usr/bin/env bash
# Pre-release verification gate for HeyEddi Skills.
# Usage:
#   ./scripts/release-gate.sh           # pytest + skill-security + smoke + full eval-all
#   ./scripts/release-gate.sh --quick   # pytest + skill-security + smoke + orchestrator eval only
set -euo pipefail
export PYTHONUNBUFFERED=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

QUICK=false
for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=true ;;
    -h|--help)
      sed -n '2,6p' "$0"
      exit 0
      ;;
  esac
done

echo "==> 0/4 sync marketplace plugins from packs/"
./scripts/sync-plugins.sh --link

echo "==> 1/4 pytest"
uv run pytest tests/ -q --tb=line

echo "==> 2/4 skill security (skill-trust + skills-check)"
./scripts/skill-security-scan.sh

echo "==> 3/4 skill smoke (poe test)"
uv run poe test

echo "==> 4/4 agent evals"
if $QUICK; then
  uv run python scripts/run-evals.py --keep-sandbox --judge-timeout 900 heyeddi-orchestrator-suggest
else
  # --all defaults to continue-on-error so one flake does not abort the suite
  uv run python scripts/run-evals.py --all --keep-sandbox --judge-timeout 900
fi

echo
echo "Release gate PASSED."
