---
name: heyeddi-orchestrator
description: Discover HeyEddi skills, auto-sync .heyeddi/ (skills index), detect hub updates (ask before install), cross-pillar opinions, and suggest @skills. Use at session start, after reinstalling skills, or when connecting heyeddi-product, ux-flow-auditor, and heyeddi-design on a route.
version: 3.1.0
product-version: 3.4.2
author: HeyEddi-com
---

# HeyEddi Orchestrator

**Skill discovery and workspace sync**: routes work to the right `@skill`, refreshes `.heyeddi/`, and **keeps product, UX, and design pillars in sync**.

## When to use

- Session start on a HeyEddi project (`.heyeddi/` present or greenfield app request)
- User asks "what skills do we have?" or "which skill should handle this?"
- Before a multi-step pipeline (intake → scaffold → design → handoff → QA)
- **Any time one pillar runs**: bookend with `load_workflow_context` / `append_pillar_opinion`
- After `@heyeddi-intake`: confirm `skill-routing.json` before downstream work

## Automatic `.heyeddi/` upkeep

**You do not need a manual sync command.** Every HeyEddi skill tool call runs auto-sync first:

1. **Refreshes** `.heyeddi/skills-index.{json,md}` when missing

Reinstall skills (`npx skills add`) and keep working: the next `@heyeddi-intake`, `@heyeddi-product`, or orchestrator tool updates `.heyeddi/` automatically.

Optional explicit full sync (includes workflow scaffold + update check): `sync --project-root .`

## Skills update check (detect and ask)

**Never silent self-update.** `sync` and `check_skills_update` compare the installed hub `product-version` to the latest GitHub release (`gh`), then ask the user.

```
check_skills_update --project-root .
# or: sync --project-root .   (includes the check unless --skip-update-check)
```

If `update_available` / `ask_user` is true:

1. Show the tool's `user_block` to the user.
2. Wait for explicit approval (`update` / `yes` / `proceed`).
3. Only then run the install command from the payload.
4. On `skip` / `no`: `check_skills_update --dismiss --latest <ver> --project-root .`

**Kill switch:** `check_skills_update --disable` or `.heyeddi/sync-state.json` → `"skills_update_check": false`, or env `HEYEDDI_SKILLS_UPDATE_CHECK=off`.

Checks are throttled to once per 24h (`--force` to bypass). No network on every skill invoke.

## Cross-pillar sync (mandatory for product · UX · design)

Read **`reference/cross-pillar-workflow.md`**.

```
init_workflow_sync                    (once per project)
load_workflow_context --route /path   (start of pillar session)
… @heyeddi-product | @ux-flow-auditor | @heyeddi-design work …
append_pillar_opinion --pillar …      (end: triggers sibling opinions)
```

## Skill discovery pipeline

```
load_catalog / suggest_skills   → auto-sync runs first
read one SKILL.md               → follow that skill's pipeline
```

If `.heyeddi/docs/intake/skill-routing.json` exists, **follow route order**.

## Tools

| Script | Purpose |
|--------|---------|
| *(auto)* | Every tool: refresh index when missing |
| `sync.py` | Optional full sync + workflow scaffold + update check |
| `check_skills_update.py` | Detect hub updates; ask before `npx skills add` |
| `write_skills_index.py` | Scan → `.heyeddi/skills-index.*` |
| `load_catalog.py` | Read cached index |
| `suggest_skills.py` | Rank skills for a prompt |
| `suggest_next_skill.py` | Next @skill + command after any skill finishes |
| `init_workflow_sync.py` | Scaffold `.heyeddi/docs/workflow/` |
| `load_workflow_context.py` | Sibling opinions + checklist for route |
| `append_pillar_opinion.py` | Log opinion; request UX/design/product response |

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill (not after every tool call or subagent phase), suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py --current-skill heyeddi-orchestrator --project-root .
   ```

   Add `--route /path` if you worked a specific route.

2. Include the script's **`### Next step`** block in your **final** reply. The user copies the **Prompt** line into chat (e.g. `@heyeddi-design craft /settings`).

Pass `--mode shape` (or `craft`, `audit`, etc.) when you know which sub-command just finished.

See `@heyeddi-orchestrator` → `reference/next-skill-handoff.md`.

## Related

- `@heyeddi-product` · `@ux-flow-auditor` · `@heyeddi-design`: three pillars
- `@heyeddi-intake`: upstream intake
- `reference/next-skill-handoff.md`: next-skill block when a pipeline task completes
- `docs/cross-pillar-workflow.md`: hub summary
