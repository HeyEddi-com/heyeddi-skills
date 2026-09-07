# Examples: eddi-ci.yaml shapes

Always re-check keys against `load_policy_contract` output before writing.

## Reviewer-only (prefer when GHA owns CI)

```yaml
version: "1.0"
policy:
  allow_external_prs: false
ai_review:
  validation_max_attempts: 5
  on_ci_failure: false
pipeline: {}
```

Pair with `@heyeddi-ci-runners` for the `HEYEDDI_RUNS_ON` workflow hook + workspace mode.

## Sealed pipeline (only with evidence + user intent + no GHA duplicate)

```yaml
version: "1.0"
policy:
  allow_external_prs: false
ai_review:
  validation_max_attempts: 5
  on_ci_failure: false
pipeline:
  test-python:
    stage: test
    image: python:3.12
    run: pytest
    filter:
      paths: ["backend/**"]
  test-node:
    stage: test
    image: node:22
    run: npm test
    filter:
      paths: ["src/**"]
```

Path filters and `run` commands must match `inspect_repo` evidence. Checks appear as `HeyEddi Runner: {job_id}` when entitled.
