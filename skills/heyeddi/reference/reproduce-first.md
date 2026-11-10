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

If the repo has no test login, ask for a local test account before aiming the test at a shared environment.

## When local cannot reproduce

Stop and ask. Do not leave local on your own.

1. Local. Required first attempt.
2. Test or staging, only after the user says local is not enough.
3. Production, only after the user explicitly allows it.

On any environment that is not local (test, staging, or production): look and navigate only. No destructive action whatsoever. Do not create, edit, delete, submit, send, pay, or change settings. Do not run a test that clicks a destructive control. If the bug only shows up after a write, stop and ask. Do not perform the write.

## Skip

Docs, typos, or a case you cannot automate. Say which one.
