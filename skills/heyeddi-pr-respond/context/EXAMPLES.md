
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

## Post every thread (do not skip)

```bash
python scripts/post_thread_replies.py --pr 42 --project-root .
# evals:
python scripts/post_thread_replies.py --pr 42 --dry-run --project-root .
```

## Verify hard gate

```bash
python scripts/verify_response.py --pr 42 --check --live --project-root .
```

## Response template (correct comment)

```
Fixed - Added count_assets method for proper pagination
```
