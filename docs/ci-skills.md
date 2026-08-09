# HeyEddi CI skills

**Date:** 2026-08-09

Stack-agnostic skills for HeyEddi CI, shipped from the **heyeddi-skills** hub as pack **`heyeddi-ci-skills`** ([packs/heyeddi-ci-skills.json](../packs/heyeddi-ci-skills.json)). Sync into the Marketplace plugin with `./scripts/sync-plugins.sh --pack heyeddi-ci-skills`.

## Install

```bash
npx skills add HeyEddi-com/skills -a cursor -y --skill '*'
# or CI skills individually / Team Marketplace plugin heyeddi-ci-skills
```

## Skills

| Skill | Role |
|-------|------|
| `@heyeddi-ci-config` | Living-contract `eddi-ci.yaml` authoring |
| `@heyeddi-ci-respond` | HeyEddi CI findings only |
| `@heyeddi-ci-fails` | Failing Checks diagnosis |
| `@heyeddi-ci-runners` | PLACEHOLDER pipeline YAML (Spot fail-closed) |
| `@heyeddi-ci-guide` | Commands, auth, feedback |

Human reviews: `@heyeddi-pr-review` / `@heyeddi-pr-respond`.

## Rules

- Never merge without **authorize merge** in the current turn
- Never commit `.heyeddi/docs/pr-*` scratch (gitignored; GitHub is SSOT)
- Never invent knobs — `load_policy_contract`
- Feedback: debate / `support@heyeddi.com` (no FP API yet)
- Runners: do not claim execution

See also [pr-workflows.md](./pr-workflows.md).
