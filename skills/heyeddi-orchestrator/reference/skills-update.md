# Skills update check

**Date:** 2026-08-05

## Policy

Detect newer HeyEddi hub releases. **Ask the user before installing.** Never silent self-update.

## Flow

1. `check_skills_update` or `sync` (unless `--skip-update-check`)
2. Compare max installed `product-version` to latest GitHub release (`gh`) or `--latest` override
3. If newer: emit `ask_user` + `user_block` with install Prompt
4. Agent shows the block and waits for approval
5. On approve: run install command; on skip: `--dismiss --latest <ver>`

## Kill switch

- `check_skills_update --disable`
- `.heyeddi/sync-state.json` → `"skills_update_check": false`
- Env `HEYEDDI_SKILLS_UPDATE_CHECK=off`

## Throttle

Once per 24h unless `--force`. Not run from per-tool auto-sync (no network spam).
