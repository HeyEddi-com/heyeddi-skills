# Examples: HeyEddi CI respond

## Fix one inline finding

1. `fetch_pr_comments --pr 42` → read temp cache path from stdout
2. `filter_heyeddi_comments --pr 42` → note kept comment IDs in chat
3. Mark **fix** in your tracking table (chat only)
4. Apply code fix
5. **Commit + push** to the PR branch (ask user if needed)
6. `assert_fixes_pushed --check`
7. `post_thread_replies --pr 42 --replies-text $'## Comment 991001\n\n✅ Fixed - ...\n\n## Summary\n\nResponded to 1/1 findings.'`
8. `verify_response --pr 42 --replies-text '...' --live --check`

## Decline-only (no code changes)

1. Same fetch/filter
2. Draft decline reply in chat
3. `post_thread_replies --pr 42 --replies-text '...' --allow-unpushed`
4. `verify_response --pr 42 --replies-text '...' --allow-draft-only --check`
