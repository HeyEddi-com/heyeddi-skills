# Skill distribution

**Date:** 2026-08-09 · **Release:** v3.3.0 · **Brand:** **HeyEddi Skills** (`heyeddi-skills`)

**Monorepo:** one GitHub hub ships **two packs** from a single SSOT (`skills/<name>/`). There is **no** second skills repo / skills.sh mirror.

| Pack | Marketplace plugin | Contents |
|------|--------------------|----------|
| `heyeddi-skills` | `plugins/heyeddi-skills/` | Full product + CI + QA |
| `heyeddi-ci-skills` | `plugins/heyeddi-ci-skills/` | CI-only subset |

Pack manifests: [`packs/`](../packs/). Sync: `./scripts/sync-plugins.sh`.

**GitHub:** [`HeyEddi-com/heyeddi-skills`](https://github.com/HeyEddi-com/heyeddi-skills) (legacy `HeyEddi-com/skills` redirects here). Local clone folder may still be named `skills`.

## Vercel ecosystem (skills.sh + `npx skills`)

| Channel | How consumers get skills | Maintainer action |
|---------|--------------------------|-------------------|
| **CLI full** | `npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'` | Keep hub public; tag releases |
| **CLI CI subset** | Same repo + `--skill heyeddi-ci-*` names | Keep `packs/heyeddi-ci-skills.json` in sync |
| **skills.sh** | One page for the hub | Root `skills.sh.json` |
| **Pinned** | `…/tree/v3.3.0` | Tag releases on GitHub |

### Automated releases

On push to `main`, [`.github/workflows/release.yml`](../.github/workflows/release.yml) tags `vX.Y.Z` when missing and attaches both pack JSON assets. Notes from `scripts/write-release-notes.py`.

**Maintainer flow:** bump versions → `sync-skill-frontmatter.py` → `./scripts/sync-plugins.sh` → merge → Release tags.

**CLI flag trap:** `--all` = all skills **and all agents**. For Cursor-only, use `-a cursor --skill '*'`.

### skills.sh

- **Hub page:** [skills.sh/heyeddi-com/heyeddi-skills](https://www.skills.sh/heyeddi-com/heyeddi-skills)
- **Org:** [skills.sh/heyeddi-com](https://www.skills.sh/heyeddi-com)
- Customize via [`skills.sh.json`](../skills.sh.json)

## Cursor Marketplace

| Channel | Repo |
|---------|------|
| **Team Marketplace** | Import `https://github.com/HeyEddi-com/heyeddi-skills` → plugins **heyeddi-skills** and/or **heyeddi-ci-skills** |
| **Public Marketplace** | Same plugin bundles |

After editing skills: `./scripts/sync-plugins.sh`.

## Install examples

```bash
# Full pack
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'

# CI skills only (same monorepo)
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y \
  --skill heyeddi-ci-config \
  --skill heyeddi-ci-guide \
  --skill heyeddi-ci-respond \
  --skill heyeddi-ci-fails \
  --skill heyeddi-ci-runners
```
