# Engineering habits: do we need an engineering skill set?

Date: 2026-11-27.

## Answer

Yes, we want these habits in skills. Not as a new set.

* **Every-change habits** go into `@engineering-excellence`, which already runs on every change: one reference file with the [lessons](engineering-lessons.md) that apply to code and infrastructure work, plus script checks where a rule can be checked. A second always-on skill would compete with it.
* **Operating documents** (threat model, runbook, restore, incident, teardown) go into one on-demand skill, `heyeddi-ops`.
* **Learning for a person** is the lessons document. A skill changes what an agent does; it does not teach its owner.

## Source and coverage

The [Enterprise engineering habits](https://github.com/ChiefGyk3D/Clouds-Against-Humanity/wiki/Enterprise-Engineering-Habits) page is part of the [Clouds-Against-Humanity wiki](https://github.com/ChiefGyk3D/Clouds-Against-Humanity/wiki) (Apache-2.0, by ChiefGyk3D), a teaching repository for a small cloud lab. The wiki has 176 pages and about 1.2 million words.

* All 176 pages were read, split into ten batches, one agent each. Every page has an entry in the [page notes](wiki-notes/), and all are listed in the [page catalog](clouds-against-humanity-wiki-catalog.md).
* The recurring habits are collected in [engineering lessons](engineering-lessons.md).

The notes are agent summaries. The wiki's claims about vendors were not re-checked.

## The ten habits against our skills

"Covered" was judged from skill descriptions and a keyword search of `skills/`, not from a full read of every skill.

| Habit | What we have | Gap |
| --- | --- | --- |
| Everything is code and reviewed | Feature branches, `@heyeddi-pr-review`, `@pre-merge-gate` | Nothing flags a change made by hand in a console |
| The checker is not the changer | `@heyeddi-local-first` allow / ask / deny | No rule for how the project's own CI and scripts are split |
| Least privilege | PR review looks for authz gaps and leaked secrets | No guidance on token scope, expiry, or rotation |
| Default deny, protection first | None found | Whole habit |
| Written threat model with accepted risks | None found | Whole habit |
| Stage gates, each costed | Plan gate, cost budget | No numbered stages with a verified exit. Low value for app work |
| Runbooks | None found | Setup, verify, failure, rotation, teardown |
| Blameless post-mortems | `append_decision.py --type gotcha` | No incident form: symptom, cause, fix, lesson |
| Verify, then record how and when | Test rules, gate reports | No rule to date a claim about a vendor or a live system |
| Boring, replaceable choices | KISS and YAGNI audit | No "what would leaving cost" question |

## More habits from the other pages

| Habit | Source | Fits |
| --- | --- | --- |
| Exit code 0 is not proof: check the end state | Lessons 1 | `@engineering-excellence` |
| Do not pipe a downloaded script into a shell; use `pipefail` | Lessons 1 | CI check |
| Check that a feature exists on your plan before designing around it | Lessons 7 and 10 | `@engineering-excellence` plan gate |
| A check that can only fail must not run | Lessons 10 | `@heyeddi-ci-fails` |
| Reference shared long-lived resources; do not own them | Lessons 3 | New ops skill |
| Pin actions by commit SHA, start with `permissions: {}`, one gate job | CI page | CI check |
| Never print the matched value in a leak scanner | CI page | CI check |
| Leaked secret: revoke, rotate, check logs, then clean history | Secrets page | New ops skill |
| Read the plan for replace and destroy before applying | Plans page | New ops skill |
| Destroy in reverse order, prove zero billable resources, then revoke | Teardown page | New ops skill |
| A test that should fail without the change was shown to fail | Planning page | Already covered: test first |
| A change record names its rollback and its trigger | Company page | New ops skill |

## Proposal

### 1. New skill: `heyeddi-ops` (on demand)

Triggers: infra changes, a new hosted service, a leaked secret, a production failure, a teardown.

| Output under `.heyeddi/docs/ops/` | Content |
| --- | --- |
| `threat-model.md` | Assets, threats, controls, accepted risks with reasons |
| `runbooks/<service>.md` | Setup, verify, failure handling, rotation, rollback, teardown |
| `lessons.md` | Symptom, cause, fix, lesson, date. No names |

It should write these from the repository, not hand the user a blank form. Keep it small: three templates and one script that fails when a runbook or accepted risk is missing a required field.

### 2. Additions to `@engineering-excellence` (always on, so keep them short)

Put them in `reference/engineering-habits.md`, loaded for every change:

* Check the end state, not the exit code.
* Anything new that listens or grants access starts denied, with the narrowest scope.
* Confirm a platform feature is available on this account before designing on it.
* A claim about a vendor or live system carries the date and how it was checked.
* A new check or guard is shown to fail on bad input before it counts.
* A scheduled job or alert is visible when it stops running.
* Name the way back before a change that is hard to undo.
* Say what a passing result does not cover.

### 3. CI hardening check in `audit_engineering.py`

Warn on: an action pinned by tag, a workflow with no `permissions` block, `curl` piped into a shell, and a shell step with a pipe and no `pipefail`.

This repository would trip it today: [ci.yml](../../.github/workflows/ci.yml) pins `actions/checkout@v4`, `actions/setup-python@v5`, `astral-sh/setup-uv@v5` and `actions/setup-node@v4` by tag and has no `permissions` block.

## Order

1. CI check, and fix this repository's workflows. Smallest, and it is enforced by a script.
2. The four lines in `@engineering-excellence`.
3. `heyeddi-ops`, tried on one real project before it is routed by default.

## Not worth copying

* Change advisory boards and change tickets. The source says it does not use them either.
* Sprint boards and capacity planning. That is project management; `@heyeddi-product` owns the backlog.
* The wiki's tool picks (OpenTofu, Spacelift, Doppler, Twingate). The habits do not depend on them.
