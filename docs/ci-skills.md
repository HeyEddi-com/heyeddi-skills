# HeyEddi CI skills

**Date:** 2026-08-09

Stack-agnostic skills for HeyEddi CI. **SSOT** lives in this hub under pack [`heyeddi-ci-skills`](../packs/heyeddi-ci-skills.json). **Published** for skills.sh as [`HeyEddi-com/heyeddi-ci-skills`](https://github.com/HeyEddi-com/heyeddi-ci-skills).

## Install

```bash
# CI-only (recommended for CI workflows)
npx skills add HeyEddi-com/heyeddi-ci-skills -a cursor -y --skill '*'

# Or full hub (includes CI + product/design/engineering)
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'
```

Browse: [skills.sh/heyeddi-com/heyeddi-ci-skills](https://www.skills.sh/heyeddi-com/heyeddi-ci-skills)

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
./scripts/publish-ci-pack-repo.sh --out ../heyeddi-ci-skills --push
```

After `--push`, the script also ensures GitHub topics for skills.sh discovery. The CI sibling still needs **real install telemetry** (same as the hub) before [skills.sh/heyeddi-com/heyeddi-ci-skills](https://www.skills.sh/heyeddi-com/heyeddi-ci-skills) and the README badge populate — listing (`-l`) alone is not enough.


See also [pr-workflows.md](./pr-workflows.md).
