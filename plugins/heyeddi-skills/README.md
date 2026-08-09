# HeyEddi Skills (Cursor plugin)

Full **heyeddi-skills** Marketplace bundle. Skill trees under `skills/` are **per-skill links** generated from [`packs/heyeddi-skills.json`](../../packs/heyeddi-skills.json) via:

```bash
./scripts/sync-plugins.sh --pack heyeddi-skills
```

Do **not** replace `skills/` with a single symlink to `../../skills` (unsafe `rm -rf`).

Sister pack: **heyeddi-ci-skills** (CI-only) — [`../heyeddi-ci-skills/`](../heyeddi-ci-skills/).

## Install via CLI (consumers)

```bash
npx skills add HeyEddi-com/skills -a cursor -y --skill '*'
```

## Install via Cursor

- **Team Marketplace:** Settings → Plugins → Team Marketplaces → Import `https://github.com/HeyEddi-com/skills`
- Assign **heyeddi-skills** (full) and/or **heyeddi-ci-skills** (CI-only)

## Components

27 skills — see [skills-registry.json](../../skills-registry.json) and the [hub README](../../README.md).
