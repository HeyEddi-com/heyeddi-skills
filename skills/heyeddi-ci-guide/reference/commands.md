# HeyEddi CI commands and safety

**Date:** 2026-08-09

## PR comment commands

| Command | Purpose |
|---------|---------|
| `/heyeddi review` | Request a review pass |
| `/heyeddi again` / `check` / `recheck` | Another pass |
| `/heyeddi deep` / `deepci` / `deep-fails` | Deeper / CI-oriented paths |
| `/heyeddi overview` | Bounded overview |
| `/heyeddi ci` / `/heyeddi fails` | Analyze failed GitHub Checks for this head (billable when App path applies) |
| `/heyeddi ask …` / `/heyeddi debate …` | Interactive Q&A |

Also: `@heyeddi-ci` / `@heyeddi` mention when it looks like a real question (not an ack ping).

Inline: reply on a finding whose parent has `<!-- heyeddi-ci-review -->` or a HeyEddi bot author.

## Markers

- Review: `<!-- heyeddi-ci-review -->` (often with `sha:…`)
- Debate reply: `<!-- heyeddi-ci-debate:… -->`

## Auth

- **authorize merge** (exact phrase, current turn) required before any merge
- Never write `auto_merge` into `eddi-ci.yaml`
- Push ≠ merge; still needs an explicit push ask
- Billable: `ai_review.on_ci_failure`, Spot `pipeline` jobs — opt-in only

## Feedback

| Need | Channel |
|------|---------|
| Disagree / clarify a finding | Debate / `/heyeddi ask` on the thread |
| Product / skill feedback | `support@heyeddi.com` |

No FP intake API exists yet. Do not invent one.

## Reactions / Apply

Product may offer Apply suggestions and reaction shortcuts. Apply is **not** merge. Follow App docs at https://ci.heyeddi.com/docs when present.

## Runners

Declared `pipeline:` jobs are validated by App lint when present. Execution is **fail-closed** until Spot ships. `@heyeddi-ci-runners` is the placeholder skill.

## Related agent skills

- `@heyeddi-ci-config` — living contract → YAML
- `@heyeddi-ci-respond` — author agent vs CI findings
- `@heyeddi-ci-fails` — local Check diagnosis
- `@heyeddi-pr-respond` — human reviewer threads only
