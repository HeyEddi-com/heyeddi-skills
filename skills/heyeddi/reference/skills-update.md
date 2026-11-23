# Skills update check

**Date:** 2026-11-23

## Policy

Detect newer HeyEddi hub releases. **Never install without the user's yes**, and never stop the task for it.

## Flow

1. `check_skills_update` or `sync` (unless `--skip-update-check`)
2. Compare max installed `product-version` to latest GitHub release (`gh`) or `--latest` override
3. If newer: emit `ask_user` + `user_block` with install Prompt
4. Agent keeps working on the request and puts the block under **Needs you** in the final summary
5. On approve (a later turn): run install command; on skip: `--dismiss --latest <ver>`

## Kill switch

- `check_skills_update --disable`
- `.heyeddi/sync-state.json` → `"skills_update_check": false`
- Env `HEYEDDI_SKILLS_UPDATE_CHECK=off`

## Throttle

Once per 24h unless `--force`. Not run from per-tool auto-sync (no network spam).
