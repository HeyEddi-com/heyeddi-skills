# Vocabulary: HeyEddi PR respond

- **Root summary**: review submission body listing findings (HeyEddi "Commented on the diff")
- **Inventory**: output of `build_comment_inventory` — every item needing fix/decline + reply
- **Postable ID**: inline or discussion comment ID that gets `## Comment <id>` + `/replies`
- **Orphan finding**: path:line in a root summary with no matching inline thread
- **Comment cache**: temp JSON from `fetch_pr_comments` (not in `.heyeddi/docs/`)
