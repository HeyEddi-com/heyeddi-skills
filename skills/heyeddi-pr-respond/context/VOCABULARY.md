# Vocabulary: HeyEddi PR respond

- **Root summary**: review submission body listing findings (HeyEddi "Commented on the diff")
- **Inventory**: output of `build_comment_inventory` — every item needing fix/decline + reply
- **Postable ID**: root id of an unresolved pull-request review thread. Gets `## Comment <id>` and `/replies` with no quote. Issue comments are not postable
- **Orphan finding**: path:line in a root summary with no matching inline thread
- **Comment cache**: temp JSON from `fetch_pr_comments` (not in `.heyeddi/docs/`)
