# Orchestrator always-on

**Date:** 2026-11-08

Always-on **policy** lives in consumer **`AGENTS.md`** (managed block) and **`.cursor/rules/heyeddi-always-on.mdc`** (`alwaysApply: true`). Cursor injects those every Agent chat. Skills stay playbooks + scripts.

`@heyeddi` **must** install/verify those files on every invoke by running a script — not by chatting about them.

## Required

0. **Hard gate on `@heyeddi`:** Before any reply or routing, run `ensure_always_on_agents.py` or `sync.py` for `--project-root .`. Confirm `AGENTS.md` + `.cursor/rules/heyeddi-always-on.mdc` exist (or `--check` passes). **No chat-only escape.**
1. **Session start** (or first HeyEddi task in a thin workspace): after (0), skills index current; know which `@skill` owns the work. Run `verify_setup --check`. If it fails, **hard-route `@heyeddi-setup`** before git/CI/agent assumptions — do not invent prefs.
2. **Ambiguous prompts**: run `suggest_skills` (or read `.heyeddi/skills-index.md`) before coding or designing.
3. **Routing present**: follow `.heyeddi/docs/intake/skill-routing.json` order.
4. **Always-on siblings**: after routing, enforce `@heyeddi-setup` prefs gate (when git/agent actions apply), `@heyeddi-local-first` on infra or account changes, `@engineering-excellence` plan/change gates, tests-with-fixes, and prose anti-slop. See hub `docs/always-on-skills.md`.
5. **Honor `stack.json`**: read git/tools/agent prefs before commit, push, or CI assumptions — only after `verify_setup --check` passes.
6. **Host surfaces**: prefer native plan / data / visual tools when this session lists them; otherwise portable fallbacks. See `reference/host-surfaces.md`.
7. **`.heyeddi/` upkeep**: keep skills-index / routing coherent; do not re-scaffold workflow every message.
8. **Browser platform**: frontend and design skills load `reference/browser-platform.md`. Existing UI: Modern Web Guidance `legacy-scan` on the files in scope before edits. Chrome DevTools MCP for local traces, memory, and reduced motion. Playwright remains screenshots and signed-in tests.
9. **Tests (this project)**: bug fix → failing test, run it, then fix. Pure frontend → Playwright login + navigation on the local app; ask before a test env, and again before production. On those environments: look and navigate only, no destructive action (`reference/reproduce-first.md`). New behavior → focused test with the change. Always-on AGENTS/rule, not a separate skill.

## Not required every message

- Full `sync` with workflow scaffold when `ensure_always_on_agents` already ran this turn and index is fresh
- Re-suggesting skills mid-tool-loop inside one skill
- Loading full skill bodies for setup/engineering/local-first when only the gate checklist applies

## Anti-pattern

Skipping orchestrator and inventing a custom pipeline when skills-index or skill-routing already defines the path. Treating incomplete setup as a soft suggestion when the agent is about to commit, push, or assume branches. Relying only on skill `ALWAYS-ON` descriptions without project `AGENTS.md` / alwaysApply rules. **Invoking `@heyeddi` and answering without running `ensure_always_on_agents` / `sync`.**
