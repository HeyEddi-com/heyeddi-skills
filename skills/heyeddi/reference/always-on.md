# Orchestrator always-on

**Date:** 2026-11-23

Always-on **policy** lives in consumer **`AGENTS.md`** (managed block) and **`.cursor/rules/heyeddi-always-on.mdc`** (`alwaysApply: true`). Cursor injects those every Agent chat. Skills stay playbooks + scripts.

`@heyeddi` **must** install/verify those files on every invoke by running a script, not by chatting about them.

## Required

0. **Hard gate on `@heyeddi`:** Before any reply or routing, run `ensure_always_on_agents.py` or `sync.py` for `--project-root .`. Confirm `AGENTS.md` + `.cursor/rules/heyeddi-always-on.mdc` exist (or `--check` passes). **No chat-only escape.**
1. **Session start** (or first HeyEddi task in a thin workspace): after (0), skills index current; know which `@skill` owns the work. Run `verify_setup --check`. If it fails, run `write_setup.py --defaults` (no questions), keep working, and mention the detected defaults in the final summary. Run the full `@heyeddi-setup` interview only when the user asks for it.
2. **Ambiguous prompts**: run `suggest_skills` (or read `.heyeddi/skills-index.md`) before coding or designing.
3. **Routing present**: follow `.heyeddi/docs/intake/skill-routing.json` order.
4. **Working agreement**: after routing, enforce the managed `AGENTS.md` block (`templates/always-on/AGENTS.section.md`): autonomy, setup, sessions and worktrees, permissions, tests, engineering, cost, browser platform, prose, ship. Enforce it as written. Do not restate it in a skill. Detail: `reference/autonomy.md`, `reference/testing.md`, `reference/session-worktrees.md`.
5. **Honor `stack.json`**: read git/tools prefs before branch or CI assumptions. Agent permissions come from `check_permission`, not from reading `agent.*` by hand.
6. **Host surfaces**: prefer native plan / data / visual tools when this session lists them; otherwise portable fallbacks. See `reference/host-surfaces.md`.
7. **`.heyeddi/` upkeep**: keep skills-index / routing coherent; do not re-scaffold workflow every message.

## Not required every message

- Full `sync` with workflow scaffold when `ensure_always_on_agents` already ran this turn and index is fresh
- Re-suggesting skills mid-tool-loop inside one skill
- Loading full skill bodies for setup/engineering/local-first when only the gate checklist applies

## Anti-pattern

Skipping orchestrator and inventing a custom pipeline when skills-index or skill-routing already defines the path. Stopping the task to run a setup interview when `write_setup.py --defaults` would do. Asking before an action `check_permission` allows. Relying only on skill `ALWAYS-ON` descriptions without project `AGENTS.md` / alwaysApply rules. **Invoking `@heyeddi` and answering without running `ensure_always_on_agents` / `sync`.**
