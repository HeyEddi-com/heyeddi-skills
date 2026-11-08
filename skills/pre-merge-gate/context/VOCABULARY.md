# Vocabulary: Pre-merge gate

- Gate report: markdown table with check name, status, summary; optional `--json` payload after the markdown.
- Sign-off mode: `--signoff` or `--pr <N>` — merge claim; enables git-clean, PR CI/threads when a PR is known; emergency skips become FAIL.
- Local mode: no `--signoff` / `--pr` — stack + audit smoke without attaching the open PR.
- PASS: check succeeded.
- FAIL: blocking; process exits 1; must fix before merge.
- SKIP: tool or tree absent, or optional tooling unavailable outside sign-off.
- Emergency skip: `--skip-backend`, `--skip-setup-audit`, `--skip-engineering-audit` — local triage only; banned under sign-off.
