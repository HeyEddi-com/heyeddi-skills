# Examples: PR code review

## Fetch context

```bash
python scripts/fetch_pr_context.py --pr 42 --project-root .
gh pr diff 42
```

## Post findings on exact lines

```bash
cat > /tmp/findings.json <<'EOF'
[
  {
    "path": "src/api/auth.py",
    "line": 88,
    "body": "**Severity:** high\n**Issue:** Token compared with `==`.\n**Why:** Timing side channel on secrets.\n**Fix:** Use `hmac.compare_digest`."
  }
]
EOF
python scripts/post_inline_review.py --pr 42 --findings-file /tmp/findings.json --project-root .
```

## Clean approve (no findings)

```bash
python scripts/post_inline_review.py --pr 42 --findings-json '[]' --project-root .
```

## Dry-run / eval fixture

```bash
python scripts/post_inline_review.py --pr 42 --findings-file /tmp/findings.json \
  --fixture-out /tmp/posted.json --project-root .
python scripts/verify_inline_review.py --pr 42 --findings-file /tmp/findings.json \
  --posted-file /tmp/posted.json --check --project-root .
```
