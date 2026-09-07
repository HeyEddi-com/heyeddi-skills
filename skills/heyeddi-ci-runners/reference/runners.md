# Spot runners (shipped)

**Date:** 2026-09-04

Ground truth from HeyEddi CI product (`heyeddi-ci`): sealed Spot + GHA overflow are live under entitlement. Skills must not say PLACEHOLDER.

## GHA on Spot (preferred when workflows exist)

| Mode (`gha_spot_mode`) | Behavior |
|------------------------|----------|
| `off` | Linux jobs stay on `ubuntu-latest` |
| `overflow` | Use included GitHub minutes first; then set `vars.HEYEDDI_RUNS_ON=heyeddi-linux` and JIT Spot |
| `always` | Linux jobs on Spot from the first run |

Required workflow hook (every Linux job):

```yaml
runs-on: ${{ vars.HEYEDDI_RUNS_ON || 'ubuntu-latest' }}
```

- Same workflow Check name — not a second CI system
- Linux only; macOS/Windows stay on GitHub-hosted
- Private repos; fork PRs skip unless `policy.allow_external_prs`
- Keep `pipeline: {}` in `eddi-ci.yaml` when using GHA

Human docs: https://ci.heyeddi.com/docs (Runners section).

## Sealed `pipeline:` (no-GHA / niche)

Jobs in `eddi-ci.yaml` `pipeline:` run on isolated Spot VMs (gVisor catalog argv) when:

- Workspace is entitled (prepaid / runner-enabled; mode not `off`)
- Spot substrate env is live
- Policy has non-empty argv-safe jobs with catalog images

Each job posts a separate Check: **`HeyEddi Runner: {job_id}`**.

Do **not** mirror existing GHA test/build commands here — double CI burns twice.

## Agent messaging

**Allowed:** Spot can execute sealed jobs / GHA overflow for entitled workspaces.

**Allowed only with evidence:** “Job X passed/failed on this PR” — cite Check name, conclusion, or Spot logs.

**Forbidden:** Claiming execution from YAML lint alone; inventing invoke APIs; promising overflow always succeeds without evidence.

## Still Coming soon / partial

- Correlated AI findings + runner logs on one timeline
- Full verify/apply/coding loops — knobs exist; treat apply paths as guarded; fail-closed when Spot unavailable

## Authoring rules

1. `load_policy_contract` every run
2. `inspect_repo` for evidenced commands and path prefixes
3. GHA-first when `.github/workflows/` exists
4. Empty `pipeline: {}` unless user opted into sealed jobs and commands are known
5. No secrets in YAML
6. `assert_runners_claims --check` before summaries that imply a run
