# skills.sh official listing playbook

**Date:** 2026-07-24

HeyEddi skills are already **indexed** on [skills.sh/heyeddi-com/heyeddi-skills](https://www.skills.sh/heyeddi-com/heyeddi-skills) via install telemetry. **Official** status (Vercel-verified, featured alongside primary product teams) is a separate bar that requires traction plus a core-team review.

## Where you are today

| Stage | Status |
|-------|--------|
| Public GitHub repo | Yes — `HeyEddi-com/heyeddi-skills` |
| skills.sh index page | Yes — bundle + grouped `skills.sh.json` |
| Install telemetry | Depends on real `npx skills add` usage |
| GitHub topics | `agent-skills`, `skills-sh` (+ add `ai-agents`) |
| Frontmatter compliance | Enforced via `scripts/sync-skill-frontmatter.py` |
| Security score | CI runs skill-trust + skills-check on every PR |
| Vercel core review | Not yet — open after traction |

## Path to official status

```
[ Public repo ] → [ User installs ] → [ Telemetry indexing ] → [ Quality + security ] → [ Core review ] → [ Official ]
```

### Step 1 — Drive installs (telemetry)

The directory does not rank empty repos. Every real install via:

```bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'
```

…feeds anonymous CLI telemetry that powers the leaderboard and search index.

**Actions:**
- Share the **repo** page URL (`skills.sh/heyeddi-com/heyeddi-skills`), not only the org page.
- Pin a release tag in docs/README (`v3.0.5` or latest).
- Add the install block to heyeddi.com, `.heyeddi/README.md` scaffold, and onboarding docs.
- Use `@heyeddi-orchestrator` in demos so consumers install the full bundle.

### Step 2 — GitHub repository topics

Required crawler tags:

- `agent-skills`
- `skills-sh`
- `ai-agents`

Set on the hub repo (maintainers):

```bash
gh api repos/HeyEddi-com/heyeddi-skills/topics -X PUT \
  -f names='["agent-skills","skills-sh","ai-agents","cursor","claude-code"]'
```

### Step 3 — Frontmatter compliance

Every `skills/<name>/SKILL.md` must expose parseable YAML frontmatter:

```yaml
---
name: heyeddi-handoff
description: "Short, distinct description with trigger terms."
version: 1.2.0
product-version: 3.0.5
author: HeyEddi-com
---
```

| Field | Source |
|-------|--------|
| `name` | Skill folder name (already required) |
| `description` | Third-person; when-to-use triggers (already required) |
| `version` | `skills/<name>/manifest.json` |
| `product-version` | Root `skills-registry.json` hub version |
| `author` | `HeyEddi-com` |

**Sync after version bumps:**

```bash
python3 scripts/sync-skill-frontmatter.py
```

Run in CI or release checklist before tagging.

### Step 4 — Quality and security metrics

skills.sh assigns a **Security Score (0–100)** per skill. Maintain:

- Green CI: pytest, smoke tests, skill-trust lint, skills-check audit (`./scripts/skill-security-scan.sh`)
- No `# nosec` bypasses; real mitigations only (see `learnings.md` security entries)
- High install volume and positive post-run feedback loop (platform-side)

### Step 5 — Request core review (official badge)

Official designation is reserved for established product teams and vetted community pillars. After meaningful install traction:

1. Open a listing query or PR on [vercel-labs/skills](https://github.com/vercel-labs/skills).
2. Include: repo URL, skills.sh page, install counts, security scan summary, and why HeyEddi is a cohesive product bundle (22 skills, `.heyeddi/` workspace, eval suite).
3. Link to [heyeddi.com/humans](https://heyeddi.com/humans) as the product home.

There is no separate submission form — the PR/discussion is the formal ask.

## Maintainer release checklist (listing hygiene)

Before each hub release:

1. Bump `skills-registry.json` + README + plugin version
2. `python3 scripts/sync-skill-frontmatter.py`
3. `./scripts/release-gate.sh --quick` (or full before major)
4. Merge to `main` → auto-tag → share pinned install URL

## Related

- [docs/distribution.md](distribution.md) — CLI, skills.sh, Cursor marketplace
- [skills.sh customize docs](https://skills.sh/docs/customize) — `skills.sh.json` groupings
- [skills.sh privacy / telemetry](https://www.skills.sh/privacy)
