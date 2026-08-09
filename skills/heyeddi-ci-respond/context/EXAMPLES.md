# Examples: HeyEddi CI respond

## Correct finding

1. Filter keeps the inline with `<!-- heyeddi-ci-review -->`
2. Mark **fix** in `pr-42-ci-tracking.md`
3. Apply code change; `discover_and_verify --run`
4. Draft `## Comment <id>` Fixed note; `post_thread_replies`; `verify_response --check`

## False positive

1. Mark **decline**; reply with PR-goal reasoning
2. Suggest `/heyeddi ask` if they want App clarification
3. Optionally draft support email body — do not call a nonexistent FP endpoint

## Wrong skill

Human reviewer comment without HeyEddi markers → stop and invoke `@heyeddi-pr-respond` instead.
