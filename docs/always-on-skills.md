# Always-on skills (every chat)

**Date:** 2026-11-23

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
| **`@heyeddi-setup`** | Prefs before the first git action (`verify_setup --check`). | Incomplete: `write_setup --defaults`, keep working. Never a stop |
| **`@heyeddi-local-first`** | Permission gate for commit, push, PR, merge, release, and dev / staging / prod reads and writes. `terraform plan` is allowed and must be summarized. | `check_permission --check`: 0 run, 2 ask once, 1 never run |
| **`@engineering-excellence`** | **Plan gate** before coding; **change gate** after edits (`audit_engineering --check`); **cost estimate** after edits (`estimate_change_cost`). | Audit errors fail. Cost never stops the work: over budget leads the final summary, and `@pre-merge-gate` blocks the merge until the user approves |
| **Prose anti-slop** | **Any prose the agent authors** (chat, books, docs, UI, PRs, `.heyeddi`): follow `context/PROSE_ANTI_SLOP.md`. Run `verify_prose --check` on default app surfaces; add `--glob` for manuscripts/other paths when those files were edited | Fail on em/en dashes and high-signal filler in authored text; no "not for books" carve-out |

Plus **autonomy** (`@heyeddi` `reference/autonomy.md`): run the request to completion; when intent is missing, read `.heyeddi/` and the repo, take the documented default, record it, keep going.

Plus **host surfaces** (`@heyeddi` → `reference/host-surfaces.md`): prefer this session's native plan / data / visual tools when listed; never require IDE-only surfaces on CLI or Cloud Run.

Incomplete prefs never stop work: `write_setup.py --defaults` detects the default branch and sets the `balanced` agent preset.

## Trigger matrix (not every chat)

| Skill | When |
|-------|------|
| `@heyeddi-setup` | User asks for setup / preferences (missing prefs get `--defaults` automatically) |
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

The checklist is the managed block in `skills/heyeddi/templates/always-on/AGENTS.section.md`, synced into every project's `AGENTS.md` and `.cursor/rules/heyeddi-always-on.mdc`. It is the only copy. Detail: `@heyeddi` `reference/autonomy.md` and `reference/testing.md`.

## Related

- `@heyeddi-local-first` → `reference/process.md`
- `@heyeddi-setup` → `reference/setup-always-on.md`
- `@engineering-excellence` → `reference/engineering-always-on.md`
- `@heyeddi` → `reference/always-on.md` · `reference/host-surfaces.md` · `reference/browser-platform.md`
- `@pre-merge-gate` runs `verify_setup --check`, `audit_engineering --check`, `estimate_change_cost --check`, and `verify_prose --check` by default; `--signoff` / `--pr` also require git-clean, green PR checks, and no unresolved review threads
