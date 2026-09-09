---
name: heyeddi-ci-runners
description: "Configure HeyEddi Spot runners — prefer GHA overflow/always with the HEYEDDI_RUNS_ON hook; author sealed eddi-ci.yaml pipeline jobs only for no-GHA or niche checks. Use when wiring runners, pipeline YAML, or Spot CI."
version: 2.0.0
product-version: 3.4.9
author: HeyEddi-com
---

# HeyEddi CI Runners

Spot is **shipped**. Help the user wire the right runner path and never invent execution claims.

## Two job kinds (do not collapse)

| Kind | Where | Check name | When to use |
|------|--------|------------|-------------|
| **GHA on Spot** | `.github/workflows/*.yml` + workspace `gha_spot_mode` | Same workflow Check | Repos that already have Actions (default) |
| **Sealed `pipeline:`** | `eddi-ci.yaml` `pipeline:` jobs | `HeyEddi Runner: {job_id}` | No (or minimal) GHA, or niche sealed checks |

**Golden rule:** Never duplicate the same test/build in GHA and `pipeline:`. Prefer GHA + Spot routing; keep `pipeline: {}`.

Product docs: https://ci.heyeddi.com/docs · hub mirrors: see `reference/runners.md`.

## Prefer GHA overflow / always

1. Confirm `.github/workflows/` exists (or user wants Actions-based CI).
2. Ensure every Linux job uses:

```yaml
runs-on: ${{ vars.HEYEDDI_RUNS_ON || 'ubuntu-latest' }}
```

3. Tell the user to set workspace **Runners** mode on ci.heyeddi.com:
   - **`overflow`** — GitHub minutes first; Spot JIT when exhausted
   - **`always`** — Linux jobs on Spot from the first run
   - **`off`** — hosted only
4. Keep `eddi-ci.yaml` Reviewer-only with `pipeline: {}` (use `@heyeddi-ci-config`).
5. Limits: Linux only; private repos; prepaid/entitled workspace; platform kill switch is ops-owned. Overflow reliability can still gap — do not promise “always works.”

## Sealed `pipeline:` (advanced / no-GHA)

1. `load_policy_contract` — living knobs only.
2. `inspect_repo` — evidenced commands + path prefixes; never invent `pytest` / `npm test`.
3. Explicit user opt-in (billable runner time).
4. Author argv-safe `run` (no shell operators, `sudo`, `curl`, `wget`), catalog `image`, `filter.paths` when possible.
5. Jobs run on Spot when the workspace is entitled and Spot env is live; they post **`HeyEddi Runner: {job_id}`** Checks.

Prefer `@heyeddi-ci-config` for the create/update decision gate.

## Evidence rule (mandatory)

- Jobs **can** run under entitlement + Spot substrate.
- A job **did** run only when you have Check / Spot evidence (`HeyEddi Runner: …`, workflow Check conclusion, Ops/logs).
- YAML lint ≠ execution. Unknown → say so and use `@heyeddi-ci-fails`.
- Before any summary that implies execution, run:

```
assert_runners_claims --check --agent-text "<your summary>"
```

## Pipeline

```
load_policy_contract
inspect_repo
→ choose GHA-first vs sealed pipeline (never both for the same CI)
→ wire HEYEDDI_RUNS_ON hook and/or author pipeline: jobs
assert_runners_claims --check --agent-text "<your summary>"
```

## Tools

| Tool | Purpose |
|------|---------|
| `load_policy_contract` | Living knobs / guide |
| `inspect_repo` | Languages + evidenced commands |
| `assert_runners_claims` | Block unsubstantiated execution claims |

## Safety

- Never secrets in YAML
- Never invent test commands
- Never `auto_merge`
- Never merge without **authorize merge**
- Never claim correlated AI+runner timeline (Coming soon)
