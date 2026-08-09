# Skill distribution

**Date:** 2026-08-09 · **Release:** v3.3.0 · **Brand:** **HeyEddi Skills** (`heyeddi-skills`)

One SSOT hub ships **two public GitHub repos** (skills.sh indexes repos 1:1):

| Pack | GitHub (skills.sh) | Marketplace plugin | Contents |
|------|--------------------|--------------------|----------|
| `heyeddi-skills` | [`HeyEddi-com/heyeddi-skills`](https://github.com/HeyEddi-com/heyeddi-skills) | `plugins/heyeddi-skills/` | Full product + CI + QA |
| `heyeddi-ci-skills` | [`HeyEddi-com/heyeddi-ci-skills`](https://github.com/HeyEddi-com/heyeddi-ci-skills) | `plugins/heyeddi-ci-skills/` | CI-only published mirror |

Pack manifests: [`packs/`](../packs/). Plugin sync: `./scripts/sync-plugins.sh`. CI mirror: `./scripts/publish-ci-pack-repo.sh`.

**Legacy:** `HeyEddi-com/skills` was renamed to `heyeddi-skills` (GitHub redirects). Prefer the new slug everywhere.

## Vercel ecosystem (skills.sh + `npx skills`)

There is **no deploy step** and **no submission form**. Distribution is GitHub + the [Vercel `skills` CLI](https://github.com/vercel-labs/skills).

| Channel | How consumers get skills | Maintainer action |
|---------|--------------------------|-------------------|
| **Full pack CLI** | `npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'` | Keep hub public; tag releases |
| **CI pack CLI** | `npx skills add HeyEddi-com/heyeddi-ci-skills -a cursor -y --skill '*'` | Publish mirror via `publish-ci-pack-repo.sh` |
| **skills.sh** | Two pages (full + CI) | Root `skills.sh.json` on each repo |
| **Pinned version** | `…/tree/v3.3.0` (hub) or `…/tree/v1.1.0` (CI pack) | Tag releases on both repos |

### Automated releases (GitHub Actions)

On every push to `main` (and via **Actions → Release → Run workflow**), [`.github/workflows/release.yml`](../.github/workflows/release.yml):

1. Runs `./scripts/sync-plugins.sh --link`
2. Reads hub version from `skills-registry.json` (must match `packs/heyeddi-skills.json`)
3. If tag `vX.Y.Z` is **missing**, creates a GitHub Release with:
   - Notes covering **both** packs via `scripts/write-release-notes.py`
   - Assets: `heyeddi-skills.json`, `heyeddi-ci-skills.json`
4. Materializes + pushes the CI pack mirror to `HeyEddi-com/heyeddi-ci-skills` when `CI_PACK_PUSH_TOKEN` (or default `GITHUB_TOKEN` with cross-repo access) is available
5. If the hub tag **already exists**, no-ops (idempotent)

PR [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) also syncs packs and asserts registry ↔ full pack consistency before pytest.

**Maintainer flow:** bump version in the PR → `python3 scripts/sync-skill-frontmatter.py` → `./scripts/sync-plugins.sh` → merge to `main` → Release workflow tags hub + syncs CI mirror.

**CLI flag trap:** `--all` = all skills **and all agents**. For Cursor-only, use `-a cursor --skill '*'`.

**Updates:** consumers run `npx skills update` or re-run `npx skills add` **after approving** an agent prompt. `@heyeddi-orchestrator` `check_skills_update` detects a newer hub release and asks; it never silent-installs.

### skills.sh listing

- **Full:** [skills.sh/heyeddi-com/heyeddi-skills](https://www.skills.sh/heyeddi-com/heyeddi-skills)
- **CI-only:** [skills.sh/heyeddi-com/heyeddi-ci-skills](https://www.skills.sh/heyeddi-com/heyeddi-ci-skills)
- **Org page:** [skills.sh/heyeddi-com](https://www.skills.sh/heyeddi-com)
- **Customize layout:** hub [`skills.sh.json`](../skills.sh.json); CI mirror has its own grouping
- Reindex can lag after rename; GitHub redirects cover `HeyEddi-com/skills`

### Official listing (beyond index)

Indexed ≠ official. See [docs/skills-sh-official-listing.md](skills-sh-official-listing.md).

## Cursor Marketplace (separate from Vercel)

| Channel | Submit? | Repo needs |
|---------|---------|------------|
| **Team Marketplace** | Admin imports `https://github.com/HeyEddi-com/heyeddi-skills` | `.cursor-plugin/marketplace.json` + both plugins ✅ |
| **Public Marketplace** | [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) | Same plugin bundles + `LICENSE` ✅ |

Logos: `plugins/heyeddi-skills/assets/logo.svg` (and CI plugin assets). After editing skills, run `./scripts/sync-plugins.sh` before relying on plugin trees.

---

## Git subtrees (maintainer sync to per-skill repos)

**Date:** 2026-07-02

## Model

```
┌─────────────────────────┐     git subtree add/pull/push     ┌──────────────────────────┐
│  heyeddi-skills (hub)   │ ◄──────────────────────────────► │  my-skill-name (remote)  │
│  skills/name/           │                                   │  SKILL.md at repo root   │
└─────────────────────────┘                                   └──────────────────────────┘
                                      │
                                      │ npx skills add HeyEddi-com/heyeddi-skills --skill <name>
                                      ▼
                            ┌─────────────────────────┐
                            │  consumer Vue project   │
                            │  .agents/skills/name/   │
                            │  or ~/.cursor/skills/   │
                            └─────────────────────────┘
```

- **Standalone skill repo** — `SKILL.md` at repository root (not under `.cursor/`).
- **Collection hub** — aggregates under `skills/<name>/`.
- **CI publish repo** — mirror of CI pack only (`publish-ci-pack-repo.sh`).
- **Consumer project** — install via `scripts/install-skills.sh` or `npx skills add`.

## Prefix

```
skills/<skill-name>
```

## Commands

### Add a skill from a remote repository

```bash
./scripts/add-skill-subtree.sh <skill-name> <remote-url> [branch]
```

### Install into a project

```bash
./scripts/install-skills.sh <skill-name> --project /path/to/app
./scripts/install-skills.sh --all --global
```

### Push hub changes to standalone repo

```bash
./scripts/push-skill-subtree.sh <skill-name> [remote-url] [branch]
```

### Publish CI pack mirror

```bash
./scripts/publish-ci-pack-repo.sh --out ../heyeddi-ci-skills --push
```

**Consumers should install from the branded repos:**

```bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor --skill visual-auditor -y
npx skills add HeyEddi-com/heyeddi-ci-skills -a cursor -y --skill '*'
```
