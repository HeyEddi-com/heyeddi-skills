# Testing: test first, at the layers the change can break

**Date:** 2026-11-23

Every HeyEddi skill that changes code follows this. TDD is the default. It is not a ritual: write the tests that matter for this change.

## Loop

1. Write or update the test that states the behavior. For a bug, the test reproduces it.
2. Run it and read the failure.
3. Write the code.
4. Run it green, then refactor.
5. Run the project's test command for everything you touched. Run the full suite before the PR when it is fast.

## Pick the layers

| The change touches | Test it with |
|--------------------|-------------|
| Logic: a function, composable, store, service method, parser | Unit test |
| A boundary: API route, DB query, Firestore or security rules, queue, auth, an external client | Integration test against a local emulator, test DB, or test client |
| A component's states and events | Component test |
| A user flow: navigation, form, sign-in, visible state across screens | Playwright on the **local** app, signed in with the project's test login |
| A bug | A failing test at the lowest layer that reproduces it |
| Terraform | `terraform validate` and `terraform plan` (summarize it); policy tests when the repo has them |

Use the layers the change can break, not every layer every time. A new API field with a form needs an integration test and a component or Playwright test. A pure function needs a unit test.

Skip a test only for docs, copy, typos, or pure styling that visual QA covers. Say which layers you skipped and why in the final summary. A layer the change can break is not skippable because it takes longer or needs setup: set it up and run it.

## Test login

Use the project's documented test login (env var or local fixture). If there is none, create one in the local database or emulator through the project's seed or fixture path. If that is not possible, stub auth in the test and list the gap in the final summary. Never use a personal account. Never commit a secret.

## When local cannot reproduce

1. Local first. Always.
2. Test or staging, then production: logs, traces, look and navigate. Run `@heyeddi-local-first` `check_permission.py` on the command; the `balanced` preset allows reads without a question.

On any hosted environment: look and navigate only. Do not create, edit, delete, submit, send, pay, or change settings. Do not run a test that clicks a destructive control. If the bug only shows after a write, reproduce the write locally with the data you observed.
