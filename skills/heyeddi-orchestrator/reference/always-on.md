# Orchestrator always-on

**Date:** 2026-09-08

`@heyeddi-orchestrator` is **always on** as the router bookend for every chat.

## Required

1. **Session start** (or first HeyEddi task in a thin workspace): sync / skills index current; know which `@skill` owns the work. Run `verify_setup --check`. If it fails, **hard-route `@heyeddi-setup`** before git/CI/agent assumptions — do not invent prefs.
2. **Ambiguous prompts**: run `suggest_skills` (or read `.heyeddi/skills-index.md`) before coding or designing.
3. **Routing present**: follow `.heyeddi/docs/intake/skill-routing.json` order.
4. **Always-on siblings**: after routing, enforce `@heyeddi-setup` prefs gate (when git/agent actions apply), `@engineering-excellence` plan/change gates, and prose anti-slop. See hub `docs/always-on-skills.md`.
5. **Honor `stack.json`**: read git/tools/agent prefs before commit, push, or CI assumptions — only after `verify_setup --check` passes.
6. **Host surfaces**: prefer native plan / data / visual tools when this session lists them; otherwise portable fallbacks. See `reference/host-surfaces.md`.

## Not required every message

- Full `sync` with workflow scaffold (optional; auto-sync covers index refresh)
- Re-suggesting skills mid-tool-loop inside one skill

## Anti-pattern

Skipping orchestrator and inventing a custom pipeline when skills-index or skill-routing already defines the path. Treating incomplete setup as a soft suggestion when the agent is about to commit, push, or assume branches.
