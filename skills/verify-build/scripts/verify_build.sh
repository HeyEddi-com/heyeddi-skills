#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="."
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done
cd "$PROJECT_ROOT"
if ! command -v npm >/dev/null 2>&1; then
  echo "[error] npm not found: install Node.js" >&2
  exit 1
fi
if [[ ! -f package.json ]]; then
  echo "[error] package.json not found in $PROJECT_ROOT" >&2
  exit 1
fi
npm run build 2>&1
