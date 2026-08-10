#!/usr/bin/env python3
"""Write GitHub Release notes for heyeddi-skills hub packs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HUB_REPO = "HeyEddi-com/heyeddi-skills"
CI_REPO = "HeyEddi-com/heyeddi-ci-skills"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--repo", default=HUB_REPO)
    parser.add_argument("--ci-repo", default=CI_REPO)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    full = json.loads((root / "packs" / "heyeddi-skills.json").read_text(encoding="utf-8"))
    ci = json.loads((root / "packs" / "heyeddi-ci-skills.json").read_text(encoding="utf-8"))

    full_skills = "\n".join(f"- `{n}`" for n in full["skills"])
    ci_skills = "\n".join(f"- `{n}`" for n in ci["skills"])
    ci_ver_raw = ci.get("version")
    ci_ver = str(ci_ver_raw).strip() if ci_ver_raw is not None else ""
    if not ci_ver:
        ci_ver = "—"
    ci_tag = f"v{ci_ver}" if ci_ver[:1].isdigit() else ci_ver

    tree = f"https://github.com/{args.repo}/tree/{args.tag}"
    notes = f"""## HeyEddi Skills {args.tag}

Hub version **{args.version}** (`skills-registry.json`). Two public skills.sh packs:

| Pack | GitHub | skills.sh |
|------|--------|-----------|
| Full | `{args.repo}` | https://www.skills.sh/heyeddi-com/heyeddi-skills |
| CI-only | `{args.ci_repo}` | https://www.skills.sh/heyeddi-com/heyeddi-ci-skills |

### Install — full pack (`heyeddi-skills`)

```bash
npx skills add {args.repo} -a cursor -y --skill '*'
```

Pin this release:

```bash
npx skills add https://github.com/{args.repo}/tree/{args.tag} -a cursor -y --skill '*'
```

**{len(full["skills"])} skills** (pack version {full.get("version", args.version)}):

{full_skills}

### Install — CI pack (`heyeddi-ci-skills`)

Published mirror repo (same skill SSOT as this hub):

```bash
npx skills add {args.ci_repo} -a cursor -y --skill '*'
```

Pin CI pack **{ci_tag}**:

```bash
npx skills add https://github.com/{args.ci_repo}/tree/{ci_tag} -a cursor -y --skill '*'
```

**{len(ci["skills"])} skills** (pack version {ci_ver}):

{ci_skills}

### Cursor Team Marketplace

Import `{tree}` (or `{args.repo}` URL) → install plugin **heyeddi-skills** (full) and/or **heyeddi-ci-skills** (CI-only).

### Pack manifests

Attached as release assets: `heyeddi-skills.json`, `heyeddi-ci-skills.json`.

### Changelog

See generated commit notes on this release page.
"""
    Path(args.output).write_text(notes, encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
