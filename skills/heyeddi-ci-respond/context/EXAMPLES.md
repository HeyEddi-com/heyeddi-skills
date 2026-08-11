# Examples: HeyEddi CI respond

## Correct finding

1. Filter keeps the inline with `<!-- heyeddi-ci-review -->`
2. Mark **fix** in `pr-42-ci-tracking.md`
3. Apply code change; `discover_and_verify --run`
4. **Commit + push** to the PR branch (ask user if needed; never include `pr-*-ci-*` scratch)
5. `assert_fixes_pushed --check`
6. Draft `## Comment <id>` Fixed note; `post_thread_replies`; `verify_response --check`

## False positive

1. Mark **decline**; reply with PR-goal reasoning
2. Suggest `/heyeddi ask` if they want App clarification
3. Optionally draft support email body — do not call a nonexistent FP endpoint
4. No code change → `post_thread_replies` may use `--allow-unpushed` if the tree is clean

## Wrong order (anti-example)

1. Apply fix locally
2. Post “Fixed” on GitHub
3. Bot debates remote HEAD → “could not verify” / “not fixed yet”

**Fix:** push first, then reply.

## Wrong skill

Human reviewer comment without HeyEddi markers → stop and invoke `@heyeddi-pr-respond` instead.
