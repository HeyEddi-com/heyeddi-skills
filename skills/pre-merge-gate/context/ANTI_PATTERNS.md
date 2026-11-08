# Anti-patterns: Pre-merge gate

- NEVER claim merge-ready without `pre_merge_gate.py` exit 0 under `--signoff` or `--pr <N>`
- NEVER merge on FAIL status for build, test, analyze, CI checks, or unresolved review threads
- NEVER treat SKIP as PASS when the project has that stack (e.g. Flutter without dart → FAIL, not SKIP)
- NEVER use emergency `--skip-backend` / `--skip-setup-audit` / `--skip-engineering-audit` for real sign-off (they FAIL under `--signoff`)
- NEVER substitute this skill for `@heyeddi-pr-review` (inline findings) or `@heyeddi-pr-respond` (thread replies)
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
