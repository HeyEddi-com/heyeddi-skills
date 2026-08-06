# Skill distribution

**Date:** 2026-08-05 · **Release:** v3.1.0

## Vercel ecosystem (skills.sh + `npx skills`)

There is **no deploy step** and **no submission form**. Distribution is GitHub + the [Vercel `skills` CLI](https://github.com/vercel-labs/skills).

| Channel | How consumers get skills | Maintainer action |
|---------|--------------------------|-------------------|
| **CLI** (`npx skills`) | `npx skills add HeyEddi-com/skills -a cursor -y --skill '*'` | Keep repo public; tag releases |
| **skills.sh** | Same install command; leaderboard from [install telemetry](https://www.skills.sh/privacy) | `skills.sh.json` at repo root; share repo page URL |
| **Pinned version** | `npx skills add https://github.com/HeyEddi-com/skills/tree/v3.1.0 -a cursor -y --skill '*'` | Tag releases on GitHub |

### Automated releases

On every push to `main` (and via **Actions → Release → Run workflow**), [`.github/workflows/release.yml`](../.github/workflows/release.yml):

1. Reads hub version from `skills-registry.json`
2. If tag `vX.Y.Z` is **missing**, creates a GitHub Release for that tag at the push SHA
3. If the tag **already exists**, no-ops (idempotent)

**Maintainer flow:** bump version in the PR (`skills-registry.json`, README, plugin `plugin.json`, orchestrator when needed) → `python3 scripts/sync-skill-frontmatter.py` → merge to `main` → release workflow tags. CI on the PR is the quality gate; release does **not** re-run the full eval suite.

**CLI flag trap:** `--all` = all skills **and all agents** (creates `agent/skills/` for Eve, etc.). For Cursor-only, use `-a cursor --skill '*'`, not `--all`.

**Repo requirements (v1.0.0):** public GitHub repo, `skills/<name>/SKILL.md` layout, `LICENSE`, README with install commands. No Vercel project or hosting needed.

**Updates:** consumers run `npx skills update` or re-run `npx skills add` **after approving** an agent prompt. `@heyeddi-orchestrator` `check_skills_update` (also via `sync`) detects a newer hub release and asks; it never silent-installs. Kill switch: `check_skills_update --disable` or `HEYEDDI_SKILLS_UPDATE_CHECK=off`.

### skills.sh listing

- **Canonical page:** [skills.sh/heyeddi-com/skills](https://www.skills.sh/heyeddi-com/skills) — install command and GitHub link point at `github.com/HeyEddi-com/skills`.
- **Org page:** [skills.sh/heyeddi-com](https://www.skills.sh/heyeddi-com) — GitHub button goes to the org profile only (platform limitation).
- **Customize layout:** root [`skills.sh.json`](../skills.sh.json) groups Pipeline / Engineering / Design & QA ([docs](https://skills.sh/docs/customize)).
- **Install counts** on the leaderboard come from the Vercel CLI's own [install telemetry](https://www.skills.sh/privacy); this repo collects nothing.

### Official listing (beyond index)

Indexed ≠ official. See [docs/skills-sh-official-listing.md](skills-sh-official-listing.md) for GitHub topics, frontmatter sync (`scripts/sync-skill-frontmatter.py`), security score hygiene, and when to open a [vercel-labs/skills](https://github.com/vercel-labs/skills) review request.

## Cursor Marketplace (separate from Vercel)

| Channel | Submit? | Repo needs |
|---------|---------|------------|
| **Team Marketplace** | Admin imports `https://github.com/HeyEddi-com/skills` | `.cursor-plugin/marketplace.json` + `plugins/heyeddi-skills/` ✅ |
| **Public Marketplace** | [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) | Same plugin bundle + `LICENSE` ✅ |

Logo for Cursor plugin: `plugins/heyeddi-skills/assets/logo.svg`.

---

## Git subtrees (maintainer sync to per-skill repos)

**Date:** 2026-07-02

## Model

```
┌─────────────────────────┐     git subtree add/pull/push     ┌──────────────────────────┐
│  skills (this hub)      │ ◄──────────────────────────────► │  my-skill-name (remote)  │
│  skills/name/           │                                   │  SKILL.md at repo root   │
└─────────────────────────┘                                   └──────────────────────────┘
                                      │
                                      │ npx skills add HeyEddi-com/skills --skill <name>
                                      ▼
                            ┌─────────────────────────┐
                            │  consumer Vue project   │
                            │  .agents/skills/name/   │
                            │  or ~/.cursor/skills/   │
                            └─────────────────────────┘
```

- **Standalone skill repo** — `SKILL.md` at repository root (not under `.cursor/`).
- **Collection hub** — aggregates under `skills/<name>/`.
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

## Standalone repo shape (after push)

```
visual-auditor/          # GitHub repo root = skill root
├── SKILL.md
├── manifest.json
├── context/
└── scripts/
```

**Consumers should install from this hub:**

```bash
npx skills add HeyEddi-com/skills -a cursor --skill visual-auditor -y
```

Standalone subtree repos are maintainer sync targets only — not the primary skills.sh source.

## Registry

`skills-registry.json` lists each skill's name, remote URL, and description.
