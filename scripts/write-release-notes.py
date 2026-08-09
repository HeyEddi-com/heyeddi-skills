#!/usr/bin/env python3
"""Write GitHub Release notes for heyeddi-skills hub packs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--repo", default="HeyEddi-com/skills")
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    full = json.loads((root / "packs" / "heyeddi-skills.json").read_text(encoding="utf-8"))
    ci = json.loads((root / "packs" / "heyeddi-ci-skills.json").read_text(encoding="utf-8"))

    full_skills = "\n".join(f"- `{n}`" for n in full["skills"])
    ci_skills = "\n".join(f"- `{n}`" for n in ci["skills"])

    tree = f"https://github.com/{args.repo}/tree/{args.tag}"
    notes = f"""## HeyEddi Skills {args.tag}

Hub version **{args.version}** (`skills-registry.json`). One codebase, two packs.

### Install — full pack (`heyeddi-skills`)

```bash
npx skills add https://github.com/{args.repo}/tree/{args.tag} -a cursor -y --skill '*'
```

Or latest main:

```bash
npx skills add {args.repo} -a cursor -y --skill '*'
```

**{len(full["skills"])} skills** (pack version {full.get("version", args.version)}):

{full_skills}

### Install — CI pack (`heyeddi-ci-skills`)

```bash
npx skills add https://github.com/{args.repo}/tree/{args.tag} -a cursor -y --skill heyeddi-ci-config
npx skills add https://github.com/{args.repo}/tree/{args.tag} -a cursor -y --skill heyeddi-ci-respond
npx skills add https://github.com/{args.repo}/tree/{args.tag} -a cursor -y --skill heyeddi-ci-fails
npx skills add https://github.com/{args.repo}/tree/{args.tag} -a cursor -y --skill heyeddi-ci-runners
npx skills add https://github.com/{args.repo}/tree/{args.tag} -a cursor -y --skill heyeddi-ci-guide
```

**{len(ci["skills"])} skills** (pack version {ci.get("version", "—")}):

{ci_skills}

### Cursor Team Marketplace

Import `{tree}` (or repo URL) → install plugin **heyeddi-skills** (full) and/or **heyeddi-ci-skills** (CI-only).

### Pack manifests

Attached as release assets: `heyeddi-skills.json`, `heyeddi-ci-skills.json`.

### Changelog

See generated commit notes on this release page.
"""
    Path(args.output).write_text(notes, encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
