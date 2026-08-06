# Subagent delegation: heyeddi-pr-respond

| Step | Subagent | Readonly | Worker prompt |
|------|----------|----------|---------------|
| `fetch_pr_comments.py` | `shell` | yes | PR number; fixture path in evals |
| Analyze each comment (fix vs decline) | `generalPurpose` | yes | One batch or one subagent per thread for large PRs |
| Apply code fixes | `generalPurpose` | no | Scoped to approved fixes |
| `pre_merge_gate.py` | `shell` | yes | After all fixes: must pass before summary |
| Draft `pr-<N>-replies.md` | main |: | One `## Comment <id>` per thread; Summary last |
| `post_thread_replies.py` | `shell` | no | Posts EVERY individual reply; writes posted.json |
| `verify_response.py --check [--live]` | `shell` | yes | Fails if any thread skipped |
| Summary comment | main |: | Only after verify passes |

Main chat owns the tracking table and ensures **every** comment gets a threaded reply before summary.
