
# Examples: PR review

## Fetch comments

```bash
python scripts/fetch_pr_comments.py --pr 42 --project-root .
```

## Draft replies (required shape)

`.heyeddi/docs/pr-42-replies.md`:

```markdown
# PR #42 replies

## Comment 9001001 (inline)
Fixed - Added count_assets method for proper pagination

## Comment 9001002 (inline)
Fixed - Removed redundant Depends() wrapper

## Summary
Responded to 2/2 comments. Ready for re-review.
```

## Post every thread (in-thread only)

```bash
python scripts/post_thread_replies.py --pr 42 --project-root .
# evals:
python scripts/post_thread_replies.py --pr 42 --dry-run --project-root .
```

Uses `.../pulls/<N>/comments/<ID>/replies`. Does **not** call `gh pr comment` per reply.

## Verify hard gate

```bash
python scripts/verify_response.py --pr 42 --check --live --project-root .
```

## Response template (correct comment)

```
Fixed - Added count_assets method for proper pagination
```

## Commit + push before replies

1. Apply fixes
2. Commit + push to the PR branch
3. Then `post_thread_replies`

Wrong order: post “Fixed” while changes are local-only → reviewer/bot cannot verify remote HEAD.

