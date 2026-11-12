# Always-on skills (every chat)

**Date:** 2026-11-07

These guards apply on **every Agent chat** that plans or changes work. They are not optional suggestions.

## How always-on is delivered

Skills alone are **opt-in by relevance**. True every-chat enforcement uses:

| Surface | Role |
|---------|------|
| **`AGENTS.md`** (project root, managed `<!-- heyeddi-always-on:* -->` block) | Portable always-on checklist (Cursor, Zed, other AGENTS.md hosts) |
| **`.cursor/rules/heyeddi-always-on.mdc`** (`alwaysApply: true`) | Cursor injects the same checklist every Agent chat |
| **Skills** (`@heyeddi-setup`, `@engineering-excellence`, …) | Playbooks + scripts when a gate fires |

`@heyeddi` auto-sync / `sync` / `ensure_always_on_agents.py` install and refresh those files when `.heyeddi/` is ensured. Full skill bodies are **not** pasted every turn.

## Always-on guards

| Guard | Role | Fail rule |
|-------|------|-----------|
| **`@heyeddi`** | Session start + ambiguous tasks: sync `.heyeddi/`, keep always-on files, rank skills, route. Do not freestyle the pipeline. | Soft: must load catalog / follow routing before multi-step work |
| **`@heyeddi-setup`** | **Prefs gate** before git/CI/commit/push or agent autonomy assumptions (`verify_setup --check`). | **Incomplete prefs fail** those actions; run setup until check passes |
| **`@heyeddi-local-first`** | Infra and account changes stay in the repo. `terraform plan` is allowed and must be summarized. `classify_command.py --check` exits 1 on apply and other live cloud writes. | **Exit 1** means do not run the command |
| **`@engineering-excellence`** | **Plan gate** before coding; **change gate** after edits (`audit_engineering --check`). | **Errors fail**; warns stay advisory |
| **Prose anti-slop** | **Any prose the agent authors** (chat, books, docs, UI, PRs, `.heyeddi`): follow `context/PROSE_ANTI_SLOP.md`. Run `verify_prose --check` on default app surfaces; add `--glob` for manuscripts/other paths when those files were edited | Fail on em/en dashes and high-signal filler in authored text; no "not for books" carve-out |

Plus **clarify-before-act** ([clarify-before-act.md](clarify-before-act.md)): ask when product/design/stack intent is missing. Never guess.

Plus **host surfaces** (`@heyeddi` → `reference/host-surfaces.md`): prefer this session's native plan / data / visual tools when listed; never require IDE-only surfaces on CLI or Cloud Run.

Non-git work may continue when prefs are incomplete. Never invent branch names, PR bases, or auto-commit/push until `verify_setup --check` passes.

## Trigger matrix (not every chat)

| Skill | When |
|-------|------|
| `@heyeddi-setup` | Incomplete `stack.json` prefs (hard for git/agent), or user asks for setup / preferences |
| `@heyeddi-intake` | Greenfield / thin `product.md` |
| `@heyeddi-product` | Specs, backlog, usefulness review |
| `@taste-penpot` | Design look. One pass. Loaded with `@heyeddi-design`. Penpot only when `design.penpot` is `on` or `auto` and Penpot is connected. |
| `@heyeddi-design` | Product side of design: personas, `design.md`, handoff. Consumes taste tokens. Does not invent a second look. |
| `@visual-auditor` | After UI changes; flagship done = `--preset done` (6 widths) |
| `@ux-flow-auditor` | Task flows / friction |
| `@pre-merge-gate` | Before merge or ship claim — use `--signoff` (setup + engineering + prose + CI/threads) |
| PR / CI skills | Review or respond loops only |

Scaffolders, bridgers, and stack implementers run when the stack/task needs them.

## Agent checklist (every chat)

1. **Orchestrator** — on `@heyeddi` / session start: **first** run `ensure_always_on_agents.py` or `sync.py` (no chat-only). Then `load_catalog` / `suggest_skills`; follow `skill-routing.json` when present.
2. **Setup (hard)** — before git/CI/agent assumptions: `verify_setup --check`. On fail: `@heyeddi-setup` until pass. Honor existing keys when complete.
3. **Local first** — for Terraform, gcloud, Firebase, Kubernetes, or Google account changes: `classify_command.py --check` before the command. Exit 1: do not run it. Plan: run it and warn.
4. **Plan gate** — before implementing: `check_engineering_plan --check` (docs ready + plan smells); read `reuse-catalog.md`.
5. **Work** — follow the routed `@skill`.
6. **Change gate** — after code changes: `audit_engineering --check` (errors only).
7. **Browser platform** — frontend or design work loads `@heyeddi` `reference/browser-platform.md`. Existing UI: `npx modern-web-guidance legacy-scan <path> --json` on the files you will touch, then verify hits. Chrome DevTools MCP on a fresh profile at localhost for traces, memory, and reduced motion. Playwright stays screenshots and signed-in tests. Non-local: look and navigate only.
8. **Tests (this project)** — bug fix → test that would have failed, run it, then fix. Pure frontend → Playwright test that signs in with the project test login and navigates the flow on the local app. If local cannot reproduce, ask before a test env, and ask again before production. On those environments: look and navigate only. No destructive action whatsoever (`@heyeddi` `reference/reproduce-first.md`). New behavior → focused test with the change. Not strict TDD. Skip only docs/typos/unautomatable (say so). Run the project test command for what you touched.
9. **Prose** — apply `PROSE_ANTI_SLOP.md` to every sentence you author. If you edited Vue/locale/`.heyeddi` copy: `verify_prose --check`. If you edited books/docs outside defaults: `verify_prose --check --glob '<path>'`. Never skip because the surface is "not UI."
10. **Ship** — `@pre-merge-gate --signoff` before merge-ready claims (exit 0 required).

## Related

- `@heyeddi-local-first` → `reference/process.md`
- `@heyeddi-setup` → `reference/setup-always-on.md`
- `@engineering-excellence` → `reference/engineering-always-on.md`
- `@heyeddi` → `reference/always-on.md` · `reference/host-surfaces.md` · `reference/browser-platform.md`
- `@pre-merge-gate` runs `verify_setup --check`, `audit_engineering --check`, and `verify_prose --check` by default; `--signoff` / `--pr` also require git-clean, green PR checks, and no unresolved review threads
