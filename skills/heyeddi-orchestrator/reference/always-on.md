# Orchestrator always-on

**Date:** 2026-09-04

`@heyeddi-orchestrator` is **always on** as the router bookend for every chat.

## Required

1. **Session start** (or first HeyEddi task in a thin workspace): sync / skills index current; know which `@skill` owns the work.
2. **Ambiguous prompts**: run `suggest_skills` (or read `.heyeddi/skills-index.md`) before coding or designing.
3. **Routing present**: follow `.heyeddi/docs/intake/skill-routing.json` order.
4. **Always-on siblings**: after routing, enforce `@engineering-excellence` plan/change gates and prose anti-slop. See hub `docs/always-on-skills.md`.

## Not required every message

- Full `sync` with workflow scaffold (optional; auto-sync covers index refresh)
- Re-suggesting skills mid-tool-loop inside one skill

## Anti-pattern

Skipping orchestrator and inventing a custom pipeline when skills-index or skill-routing already defines the path.
