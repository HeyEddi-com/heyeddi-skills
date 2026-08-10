# HeyEddi Skills (Cursor plugin)

**HeyEddi open agent toolkit** — full **heyeddi-skills** Marketplace bundle (opinionated product → design → engineering → QA → PR). Skill trees under `skills/` are **per-skill links** from [`packs/heyeddi-skills.json`](../../packs/heyeddi-skills.json):

```bash
./scripts/sync-plugins.sh --pack heyeddi-skills
```

Do **not** replace `skills/` with a single symlink to `../../skills` (unsafe `rm -rf`).

Sister pack: **heyeddi-ci-skills** (CI-only for [ci.heyeddi.com](https://ci.heyeddi.com)) — [`../heyeddi-ci-skills/`](../heyeddi-ci-skills/) or sibling repo [`HeyEddi-com/heyeddi-ci-skills`](https://github.com/HeyEddi-com/heyeddi-ci-skills).

## Install via CLI (consumers)

```bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'
```

## Install via Cursor

- **Team Marketplace:** Settings → Plugins → Team Marketplaces → Import `https://github.com/HeyEddi-com/heyeddi-skills`
- Assign **heyeddi-skills** (full) and/or **heyeddi-ci-skills** (CI-only)

## Components

27 skills — see [skills-registry.json](../../skills-registry.json) and the [hub README](../../README.md).
