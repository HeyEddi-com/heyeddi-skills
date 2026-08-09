#!/usr/bin/env python3
"""Write GitHub Release notes for heyeddi-skills hub packs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HUB_REPO = "HeyEddi-com/heyeddi-skills"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--repo", default=HUB_REPO)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    full = json.loads((root / "packs" / "heyeddi-skills.json").read_text(encoding="utf-8"))
    ci = json.loads((root / "packs" / "heyeddi-ci-skills.json").read_text(encoding="utf-8"))

    full_skills = "\n".join(f"- `{n}`" for n in full["skills"])
    ci_skills = "\n".join(f"- `{n}`" for n in ci["skills"])
    ci_ver = ci.get("version", "—")

    tree = f"https://github.com/{args.repo}/tree/{args.tag}"
    ci_skill_flags = " ".join(f"--skill {n}" for n in ci["skills"])
    notes = f"""## HeyEddi Skills {args.tag}

Hub version **{args.version}** (`skills-registry.json`). **Monorepo:** one GitHub repo, two Cursor packs (Marketplace plugins + pack JSON assets).

| Pack | How to get it |
|------|----------------|
| Full (`heyeddi-skills`) | `npx skills add {args.repo} -a cursor -y --skill '*'` |
| CI-only (`heyeddi-ci-skills`) | Marketplace plugin **heyeddi-ci-skills**, or install CI skills by name from this hub |

skills.sh: https://www.skills.sh/heyeddi-com/heyeddi-skills

### Install — full pack

```bash
npx skills add {args.repo} -a cursor -y --skill '*'
```

Pin this release:

```bash
npx skills add https://github.com/{args.repo}/tree/{args.tag} -a cursor -y --skill '*'
```

**{len(full["skills"])} skills** (pack version {full.get("version", args.version)}):

{full_skills}

### Install — CI skills only (same monorepo)

```bash
npx skills add {args.repo} -a cursor -y {ci_skill_flags}
```

Or import this repo in Cursor Team Marketplace → plugin **heyeddi-ci-skills**.

**{len(ci["skills"])} CI skills** (pack version {ci_ver}):

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
