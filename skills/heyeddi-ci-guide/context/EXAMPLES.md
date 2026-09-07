# Examples: HeyEddi CI guide

## Default PR workflow

User opens a PR or asks to handle review feedback → run `@heyeddi-ci-fails` then `@heyeddi-pr-respond` automatically. Fix, commit, push, and post threaded replies without asking.

## User asks how to disagree with a finding

Point them to `/heyeddi ask …` or a threaded reply on the inline finding. Offer to draft a `support@heyeddi.com` note for product feedback. Do not invent an FP endpoint.

## User asks to merge after CI respond

Only if they said **authorize merge** this turn. Otherwise refuse and explain the auth matrix.

## User asks if Spot ran their pipeline job

Look up Checks (`gh pr checks` / `@heyeddi-ci-fails`). Cite `HeyEddi Runner: …` or the workflow Check conclusion. If none, say unknown — YAML lint is not execution. See `@heyeddi-ci-runners`.
