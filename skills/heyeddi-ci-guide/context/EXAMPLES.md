# Examples: HeyEddi CI guide

## User asks how to disagree with a finding

Point them to `/heyeddi ask …` or a threaded reply on the inline finding. Offer to draft a `support@heyeddi.com` note for product feedback. Do not invent an FP endpoint.

## User asks to merge after CI respond

Only if they said **authorize merge** this turn. Otherwise refuse and explain the auth matrix.

## User asks if Spot ran their pipeline job

Say runners are placeholder / fail-closed; YAML may be linted but jobs did not execute.
