# HeyEddi CI skills

**Date:** 2026-09-04

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
| `@heyeddi-ci-config` | Living-contract `eddi-ci.yaml` authoring (GHA-first; sealed pipeline opt-in) |
| `@heyeddi-pr-respond` | All PR review feedback (human + HeyEddi CI root summaries + inline) |
| `@heyeddi-ci-fails` | Failing Checks diagnosis |
| `@heyeddi-ci-runners` | Spot: GHA overflow/always + sealed `pipeline:` (evidence before claims) |
| `@heyeddi-ci-guide` | Commands, auth, feedback |
| `@heyeddi` | Router, working agreement, next step |
| `@heyeddi-setup` | Repo preferences |
| `@heyeddi-local-first` | Permission check for commit, push, PR, merge |
| `@pre-merge-gate` | Merge readiness |
| `@engineering-excellence` | Engineering and cost audits |
| `@heyeddi-product` | Backlog and product review |

Human + HeyEddi CI reviews: `@heyeddi-pr-respond` only (one skill).

## Rules

- Below production, merge once `@pre-merge-gate --signoff` exits 0. A production merge takes **authorize merge** in the current turn
- Never commit `.heyeddi/docs/pr-*` scratch (gitignored; GitHub is SSOT)
- Never invent knobs - `load_policy_contract`
- Feedback: debate / `support@heyeddi.com` (no FP API yet)
- Runners: Spot is shipped; claim execution only with Check/Spot evidence

## Maintainer

```bash
./scripts/sync-plugins.sh --pack heyeddi-ci-skills
./scripts/publish-ci-pack-repo.sh --out ../heyeddi-ci-skills --push
```

After `--push`, the script also ensures GitHub topics for skills.sh discovery. The CI sibling still needs **real install telemetry** (same as the hub) before [skills.sh/heyeddi-com/heyeddi-ci-skills](https://www.skills.sh/heyeddi-com/heyeddi-ci-skills) and the README badge populate - listing (`-l`) alone is not enough.


See also [pr-workflows.md](./pr-workflows.md).
