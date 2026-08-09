# HeyEddi CI skills

**Date:** 2026-08-09

Stack-agnostic skills for HeyEddi CI. Authored in this **monorepo** under pack [`heyeddi-ci-skills`](../packs/heyeddi-ci-skills.json). No separate publish repo.

## Install

```bash
# Full hub (includes CI)
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'

# CI skills only
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y \
  --skill heyeddi-ci-config \
  --skill heyeddi-ci-guide \
  --skill heyeddi-ci-respond \
  --skill heyeddi-ci-fails \
  --skill heyeddi-ci-runners
```

**Cursor Team Marketplace:** import `https://github.com/HeyEddi-com/heyeddi-skills` → plugin **heyeddi-ci-skills**.

Browse hub: [skills.sh/heyeddi-com/heyeddi-skills](https://www.skills.sh/heyeddi-com/heyeddi-skills)

## Skills

| Skill | Role |
|-------|------|
| `@heyeddi-ci-config` | Living-contract `eddi-ci.yaml` authoring |
| `@heyeddi-ci-respond` | HeyEddi CI findings only |
| `@heyeddi-ci-fails` | Failing Checks diagnosis |
| `@heyeddi-ci-runners` | PLACEHOLDER pipeline YAML (Spot fail-closed) |
| `@heyeddi-ci-guide` | Commands, auth, feedback |

Human reviews: `@heyeddi-pr-review` / `@heyeddi-pr-respond` (full pack).

## Rules

- Never merge without **authorize merge** in the current turn
- Never commit `.heyeddi/docs/pr-*` scratch (gitignored; GitHub is SSOT)
- Never invent knobs — `load_policy_contract`
- Feedback: debate / `support@heyeddi.com` (no FP API yet)
- Runners: do not claim execution

## Maintainer

```bash
./scripts/sync-plugins.sh --pack heyeddi-ci-skills
```

See also [pr-workflows.md](./pr-workflows.md).
