# Examples: eddi-ci.yaml shapes

Always re-check keys against `load_policy_contract` output before writing.

## Reviewer-only (prefer this unless runners are requested)

```yaml
version: "1.0"
policy:
  allow_external_prs: false
ai_review:
  validation_max_attempts: 5
  on_ci_failure: false
pipeline: {}
```

## Python + Node runners (only with evidence + user intent)

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
    image: node:20
    run: npm test
    filter:
      paths: ["src/**"]
```

Path filters and `run` commands must match `inspect_repo` evidence for the target repository.
