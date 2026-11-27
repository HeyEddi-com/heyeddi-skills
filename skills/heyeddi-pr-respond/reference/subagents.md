# Subagent delegation: heyeddi-pr-respond

| Step | Subagent | Readonly | Worker prompt |
|------|----------|----------|---------------|
| `fetch_pr_comments.py` | `shell` | yes | PR number; fixture path in evals |
| Analyze each comment (fix vs decline) | `generalPurpose` | yes | One batch or one subagent per thread for large PRs |
| Apply code fixes | `generalPurpose` | no | Scoped to approved fixes |
| Draft replies (`--replies-text`) | main | yes | One `## Comment <id>` per thread; Summary last. No draft file |
| `post_thread_replies.py` | `shell` | no | Posts EVERY individual reply; result is stdout JSON only |
| `verify_response.py --check [--live]` | `shell` | yes | Fails if any thread skipped |
| Summary comment | main | no | Only after verify passes |
| `pre_merge_gate.py --signoff` | `shell` | yes | Last, after replies: threads must be answered before it can pass |

Main chat owns the tracking table and ensures **every** comment gets a threaded reply before summary.
