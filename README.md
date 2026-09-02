# HeyEddi Skills

[![skills.sh](https://skills.sh/b/HeyEddi-com/heyeddi-skills)](https://skills.sh/HeyEddi-com/heyeddi-skills)

**HeyEddi’s open agent toolkit** for [Cursor](https://cursor.com) — free, public, and opinionated. Product intake → design → engineering → QA → PR review in one coherent pack, with a shared `.heyeddi/` workspace so agents and humans stay aligned.

**Status:** **v3.4.7** · 27 skills · [skills-registry.json](skills-registry.json)

### Who this is for

- Teams shipping on **HeyEddi** (or adopting its `.heyeddi/` conventions)
- Apps on **Vue + FastAPI + Firebase** and/or **Flutter** that want structured agent workflows
- Anyone who wants open, battle-tested skills for handoff, visual QA, engineering audits, and PR loops — and is fine with an opinionated stack

### Who this is not

- A stack-agnostic “any framework” skills marketplace
- A substitute for [HeyEddi CI](https://ci.heyeddi.com) product docs — for CI-only agents use the sibling pack [`heyeddi-ci-skills`](https://github.com/HeyEddi-com/heyeddi-ci-skills)

This hub is the **SSOT** for the full pack. Marketplace plugins for both packs ship from here (`./scripts/sync-plugins.sh`). The CI skills.sh package is published to [`HeyEddi-com/heyeddi-ci-skills`](https://github.com/HeyEddi-com/heyeddi-ci-skills) via `./scripts/publish-ci-pack-repo.sh`.

## About HeyEddi

**HeyEddi** is a **collaborative workspace for agents and humans** — not just a dev agency. Skills and `.heyeddi/` in your repo give agents and your team shared product, design, and engineering context. Need vetted humans for design, engineering, or product work? See **[heyeddi.com/humans](https://heyeddi.com/humans)**.

## Install (consumers)

**Requirements:** Node.js 18+ (for `npx skills`), [Cursor](https://cursor.com)

### Install all skills (recommended)

Into your **project** (`.agents/skills/` — shared with other agents):

```bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'
```

Into **global** Cursor skills (`~/.cursor/skills/`):

```bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor -g -y --skill '*'
```

> **Note:** Do **not** use `--all` with `-a cursor`. In the Vercel CLI, `--all` means *all skills **and** all 72 agents* (including Eve → `agent/skills/`). Use `--skill '*'` to install every skill for Cursor only.

From a local clone of this hub:

```bash
git clone git@github.com:HeyEddi-com/heyeddi-skills.git
cd heyeddi-skills
./scripts/install-skills.sh --all --project /path/to/your-app
./scripts/install-skills.sh --all --global
```

### Install CI-only pack (sibling skills.sh repo)

For [HeyEddi CI](https://ci.heyeddi.com) workflows (config, respond, fails, runners placeholder, guide):

```bash
npx skills add HeyEddi-com/heyeddi-ci-skills -a cursor -y --skill '*'
```

- Repo: [`HeyEddi-com/heyeddi-ci-skills`](https://github.com/HeyEddi-com/heyeddi-ci-skills)
- Browse: [skills.sh/heyeddi-com/heyeddi-ci-skills](https://www.skills.sh/heyeddi-com/heyeddi-ci-skills)
- Policy: [ci.heyeddi.com/docs#policy](https://ci.heyeddi.com/docs#policy)

Local folder for this hub may stay named `skills`; the GitHub remote is **heyeddi-skills**.

### Install one skill from the bundle

```bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor --skill heyeddi-handoff -y
npx skills add HeyEddi-com/heyeddi-skills -a cursor --skill heyeddi-intake -g -y
```

List names in [skills-registry.json](skills-registry.json) or the catalog below.

### Pin a release tag

```bash
npx skills add https://github.com/HeyEddi-com/heyeddi-skills/tree/v3.4.5 -a cursor -y --skill '*'
```

### Cursor Team Marketplace (teams / enterprise)

Admins can import this repo as a **Team Marketplace** plugin source (Cursor 2.6+):

1. **Settings → Plugins → Team Marketplaces → Import**
2. Paste `https://github.com/HeyEddi-com/heyeddi-skills`
3. Assign plugins to access groups; members install from **Customize**

Plugins (from this hub; CI skills.sh package is the sibling repo):

| Plugin | Pack |
|--------|------|
| **heyeddi-skills** | Full set |
| **heyeddi-ci-skills** | CI-only (`packs/heyeddi-ci-skills.json`) |

Maintainer: after adding/removing skills, update `packs/*.json` and run `./scripts/sync-plugins.sh`. See [docs/distribution.md](docs/distribution.md) and [docs/ci-skills.md](docs/ci-skills.md). Merges to `main` publish a GitHub Release (both packs) when the hub version tag is new.

Invoke skills in chat with `@skill-name` (e.g. `@heyeddi-intake`, `@heyeddi-handoff`).

### skills.sh listing

- **Full pack:** [skills.sh/heyeddi-com/heyeddi-skills](https://www.skills.sh/heyeddi-com/heyeddi-skills)
- **CI-only pack:** [skills.sh/heyeddi-com/heyeddi-ci-skills](https://www.skills.sh/heyeddi-com/heyeddi-ci-skills)

Install counts on the leaderboard come from the Vercel CLI's own [install telemetry](https://www.skills.sh/privacy) — nothing is collected by this repo.

**Official listing playbook:** see [docs/skills-sh-official-listing.md](docs/skills-sh-official-listing.md) (topics, frontmatter, security score, Vercel core review).

## Skills catalog

| Skill | Role |
|-------|------|
| `heyeddi-orchestrator` | Discover @skills and suggest pipelines from `skill-routing.json` |
| `heyeddi-intake` | User prompt → `product.md`, mockups, intake JSON, routing |
| `heyeddi-product` | PM review — stories, AC, usefulness; orchestrates UX/design/engineering research |
| `heyeddi-design` | Design from scratch — briefs, wireframes, craft (Vue) |
| `heyeddi-handoff` | Screenshot-first Vue implementation (PrimeVue + tokens) |
| `design-handoff-flutter` | Screenshot-first Flutter / Material 3 implementation |
| `primevue-openprops-architect` | PrimeVue + OpenProps guardrails for Vue/CSS edits |
| `project-engineering` | Vue + FastAPI + Firebase scaffold, deps, dev servers |
| `flutter-engineering` | Flutter + FastAPI scaffold, analyze/test, dev servers |
| `backend-type-bridger` | OpenAPI / Firestore → TypeScript types |
| `dart-type-bridger` | OpenAPI / Firestore → Dart model stubs |
| `composable-patterns` | Vue composables for FastAPI / Firebase access |
| `flutter-patterns` | Riverpod repositories — Dio + Firebase patterns |
| `engineering-excellence` | KISS/YAGNI/DRY/SOLID audits + `.heyeddi/docs/engineering/` |
| `heyeddi-ci-config` | Author `eddi-ci.yaml` from the live policy contract (Reviewer + optional runners) |
| `heyeddi-ci-guide` | HeyEddi CI commands, auth matrix, runners placeholder, feedback paths |
| `@heyeddi-pr-respond` | Respond to all PR review feedback (human + HeyEddi CI) |
| `@heyeddi-ci-fails` | Diagnose failing GitHub Checks; optional `/heyeddi fails` |
| `heyeddi-ci-runners` | PLACEHOLDER — author `pipeline:` YAML; Spot fail-closed |
| `ux-flow-auditor` | Task-flow traces — friction, click depth — `.heyeddi/docs/ux-flows/` |
| `visual-auditor` | Review screenshots vs spec, fix visual issues, document fixes |
| `verify-build` | Vite static build validator |
| `pre-merge-gate` | QA merge-readiness checklist |
| `heyeddi-pr-review` | Review submitted PR — diff, product, docs, engineering, tests |
| `design-system-generalizer` | Spread golden-page patterns across routes |
| `no-duplicate-ui` | Detect duplicate Vue UI |

## Hub development (this repo)

**Requirements:** Python 3.11+, [uv](https://docs.astral.sh/uv/), Node.js 18+ (skill-security CLIs + eval templates), [Cursor agent CLI](https://cursor.com) for agent evals.

```bash
git clone git@github.com:HeyEddi-com/heyeddi-skills.git
cd skills
uv sync --group dev --group evals

uv run poe test                    # smoke tests (no agent API)
uv run poe skill-security          # skill-trust lint + skills-check audit
uv run poe eval-list               # list eval cases
uv run poe eval-heyeddi-handoff     # one agent eval
./scripts/release-gate.sh          # pytest + skill-security + smoke + eval-all

# Full suite (~50+ min; continues on case errors; judge timeout 900s)
PYTHONUNBUFFERED=1 uv run poe eval-all
```

See [docs/agent-evals.md](docs/agent-evals.md) and [docs/agent-eval-results.md](docs/agent-eval-results.md).

## Repository layout

```
.
├── skills/<name>/          # All skills in one package (skills/*/SKILL.md)
│   ├── SKILL.md
│   ├── manifest.json
│   ├── context/
│   └── scripts/
├── evals/                  # Agent eval cases, prompts, project templates
├── docs/                   # Architecture, distribution, eval philosophy
├── scripts/                # install, test, eval, subtree push/pull
├── fixtures/               # sample-vue-app for script smoke tests
└── skills-registry.json    # Catalog metadata
```

Skill sources live under `skills/`, not `.cursor/skills/`, so `npx skills add HeyEddi-com/heyeddi-skills` can install the whole catalog into consumer projects.

## Maintainer workflow (optional per-skill repos)

This hub uses **git subtrees** to sync individual skills to standalone GitHub repos when needed (e.g. for skills.sh per-repo installs). **Consumers should install from this hub**, not from separate repos.

```bash
./scripts/new-skill.sh my-skill-name
./scripts/push-skill-subtree.sh my-skill-name git@github.com:HeyEddi-com/my-skill-name.git
```

Details: [docs/distribution.md](docs/distribution.md)

## `.heyeddi/` in app projects

Consumer apps store product context, design assets, and skill-generated docs under `.heyeddi/`. See [docs/heyeddi-folder.md](docs/heyeddi-folder.md).

## Eval philosophy

Evals give the agent a **goal**, not a script. Each skill must run its real workflow (context → docs → assumptions → work → validate). See [docs/eval-philosophy.md](docs/eval-philosophy.md).

## Documentation

| Doc | Topic |
|-----|--------|
| [docs/skills-roadmap.md](docs/skills-roadmap.md) | Build plan |
| [docs/distribution.md](docs/distribution.md) | Single-package install + marketplaces |
| [docs/skills-sh-official-listing.md](docs/skills-sh-official-listing.md) | skills.sh index + official listing playbook |
| [docs/v2-skill-naming.md](docs/v2-skill-naming.md) | Historical ADR — v2 `heyeddi-*` spine renames (aliases removed in v3.0.0) |
| [docs/pr-workflows.md](docs/pr-workflows.md) | Two PR workflows — submission review vs respond |
| [docs/team-cheat-sheet.md](docs/team-cheat-sheet.md) | Designer + QA reference |
| [docs/cloud-agent-integration.md](docs/cloud-agent-integration.md) | Pydantic AI / LangChain |
| [docs/testing-skills.md](docs/testing-skills.md) | Script smoke tests |
| [docs/subagent-delegation.md](docs/subagent-delegation.md) | Task tool + cloud delegation |

## Contributing

1. Branch from `main`, keep changes focused.
2. Run `uv run poe test` and `uv run poe skill-security` before opening a PR (CI runs both).
3. For skill behavior changes, run the relevant `uv run poe eval-*` case or the full suite.

---

**Last updated:** 2026-08-09
