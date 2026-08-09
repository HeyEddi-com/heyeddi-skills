# Spot runners placeholder

**Date:** 2026-08-09

## Status

Isolated Spot runners are **not shipped**. Skills may write `pipeline:` jobs that match the live `eddi-ci-policy` contract. The App may validate YAML. **Jobs do not execute.**

## Agent messaging (required)

Tell the user clearly:

> Pipeline jobs are declared for when Spot runners ship. Today execution is fail-closed — nothing ran.

## When runners ship (reserved)

Future skill updates will add:

- Invoke / dispatch hooks (product API only — do not invent)
- Status / log fetch for completed jobs
- Cost / entitlement checks tied to the living contract

Until then, keep this section as a stub and refuse execution claims (`assert_runners_placeholder`).

## Authoring rules

1. `load_policy_contract` every run
2. `inspect_repo` for evidenced commands and path prefixes
3. Empty `pipeline: {}` unless the user opted into runners and commands are known
4. No secrets in YAML
