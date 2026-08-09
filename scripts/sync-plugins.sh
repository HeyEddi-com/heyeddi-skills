#!/usr/bin/env bash
# Sync pack manifests → plugins/<plugin>/skills/ from SSOT skills/<name>/.
#
# Default: per-skill relative symlinks (safe; rm of a link does not delete SSOT).
# --copy:  materialize copies (release / CI).
#
# NEVER replace plugins/*/skills with a single symlink to ../../skills.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

MODE="link"
PACK_FILTER=""

usage() {
  cat <<EOF
Usage: $0 [--link|--copy] [--pack <pack-id>]

  --link   Per-skill symlinks into plugins/<plugin>/skills/ (default)
  --copy   Copy skill trees (no symlinks)
  --pack   Only sync this pack id (filename stem under packs/, e.g. heyeddi-ci-skills)
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --link) MODE="link"; shift ;;
    --copy) MODE="copy"; shift ;;
    --pack)
      PACK_FILTER="${2:-}"
      [[ -n "$PACK_FILTER" ]] || usage
      shift 2
      ;;
    -h|--help) usage ;;
    *) usage ;;
  esac
done

PACKS_DIR="${REPO_ROOT}/packs"
PLUGINS_DIR="${REPO_ROOT}/plugins"
SKILLS_DIR="${REPO_ROOT}/skills"

if [[ ! -d "$PACKS_DIR" ]]; then
  echo "Error: packs/ not found at ${PACKS_DIR}" >&2
  exit 1
fi

sync_pack() {
  local pack_file="$1"
  local pack_id plugin version
  pack_id="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['pack'])" "$pack_file")"
  plugin="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['plugin'])" "$pack_file")"
  version="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('version',''))" "$pack_file")"

  local plugin_dir="${PLUGINS_DIR}/${plugin}"
  local dest_skills="${plugin_dir}/skills"
  local plugin_json="${plugin_dir}/.cursor-plugin/plugin.json"

  if [[ ! -d "$plugin_dir" ]]; then
    echo "Error: plugin dir missing: ${plugin_dir}" >&2
    exit 1
  fi

  # Replace whole-dir symlink with a real directory (legacy footgun).
  if [[ -L "$dest_skills" ]]; then
    echo "Removing legacy whole-dir symlink: ${dest_skills}"
    rm -f "$dest_skills"
  fi
  mkdir -p "$dest_skills"

  # Drop entries not in pack (only managed skill dirs / links).
  mapfile -t wanted < <(python3 -c "import json,sys; print('\n'.join(json.load(open(sys.argv[1]))['skills']))" "$pack_file")
  declare -A want_set=()
  local name
  for name in "${wanted[@]}"; do
    want_set["$name"]=1
  done
  if [[ -d "$dest_skills" ]]; then
    local existing
    for existing in "$dest_skills"/*; do
      [[ -e "$existing" || -L "$existing" ]] || continue
      local base
      base="$(basename "$existing")"
      if [[ -z "${want_set[$base]+x}" ]]; then
        echo "  prune ${plugin}/skills/${base}"
        rm -rf "$existing"
      fi
    done
  fi

  for name in "${wanted[@]}"; do
    local src="${SKILLS_DIR}/${name}"
    local dest="${dest_skills}/${name}"
    if [[ ! -d "$src" ]]; then
      echo "Error: SSOT skill missing: ${src}" >&2
      exit 1
    fi
    rm -rf "$dest"
    if [[ "$MODE" == "link" ]]; then
      # plugins/<plugin>/skills/<name> → ../../../skills/<name>
      ln -s "../../../skills/${name}" "$dest"
      echo "  link ${plugin}/skills/${name}"
    else
      cp -a "$src" "$dest"
      echo "  copy ${plugin}/skills/${name}"
    fi
  done

  if [[ -f "$plugin_json" && -n "$version" ]]; then
    python3 - "$plugin_json" "$version" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
version = sys.argv[2]
data = json.loads(path.read_text())
if data.get("version") != version:
    data["version"] = version
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  plugin.json version → {version}")
PY
  fi

  echo "Synced pack ${pack_id} → plugins/${plugin}/skills/ (${MODE}, ${#wanted[@]} skills)"
}

shopt -s nullglob
for pack_file in "${PACKS_DIR}"/*.json; do
  stem="$(basename "$pack_file" .json)"
  if [[ -n "$PACK_FILTER" && "$stem" != "$PACK_FILTER" ]]; then
    continue
  fi
  echo "==> ${stem}"
  sync_pack "$pack_file"
done

echo "Done. SSOT remains skills/<name>/ only."
