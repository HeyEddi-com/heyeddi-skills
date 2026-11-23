# Reproduce first

Not strict TDD. A bug fix starts from a failing test. A new behavior ships with a focused test in the same change. Full playbook for the always-on **Tests (this project)** line.

## Bug

1. Add or update a test that fails on the current code.
2. Run it and read the failure.
3. Fix the code.
4. Run the project's test command for what you touched.

## New behavior

Ship a focused test with the change. It does not have to fail first.

## Pure frontend bug

Write a Playwright test that:

- Opens the **local** app (dev server or local preview). Local comes before any hosted environment.
- Signs in with the project's test login (env var or local fixture the repo already documents). Do not invent a password. Do not commit secrets. Do not use a personal account.
- Walks the same navigation as the bug and asserts the broken outcome, so the test fails before the fix.

If the repo has no test login, create one in the local database or emulator through the project's seed or fixture path. If that is not possible, stub auth in the test, keep going, and list the gap in your final summary. Never use a shared environment for a signed-in test.

## When local cannot reproduce

Try in this order. Run `@heyeddi-local-first` `check_permission.py` on any command that reaches a hosted environment; it says whether to go ahead, ask once, or stop.

1. Local. Required first attempt.
2. Test or staging: logs, traces, and look-and-navigate. Allowed without a question under the `balanced` preset.
3. Production: the same, read-only. Allowed without a question under `balanced`; `cautious` asks once.

On any environment that is not local (test, staging, or production): look and navigate only. No destructive action whatsoever. Do not create, edit, delete, submit, send, pay, or change settings. Do not run a test that clicks a destructive control. If the bug only shows up after a write, do not perform the write. Reproduce the write path locally with the data you observed, and keep going.

## Skip

Docs, typos, or a case you cannot automate. Say which one.
