---
name: heyeddi
description: "ALWAYS-ON router named @heyeddi. On every invoke: first run ensure_always_on_agents (or sync) so project AGENTS.md + Cursor alwaysApply gates exist: never chat-only. Then discover skills, sync .heyeddi/, and route. Design talk goes to @taste-penpot first then @heyeddi-design. Vue UI follows @vue-design-system. @heyeddi-orchestrator is a deprecated alias. Use at every session start, on ambiguous tasks, and when connecting product, UX, and design."
version: 3.6.0
product-version: 3.10.0
author: HeyEddi-com
---

# HeyEddi

**The router.** Invoke `@heyeddi`. `@heyeddi-orchestrator` is a deprecated alias for this skill.

Routes work to the right `@skill`, refreshes `.heyeddi/`, installs **thin always-on** `AGENTS.md` + `.cursor/rules/heyeddi-always-on.mdc`, and **keeps product, UX, and design pillars in sync**.

**Every-chat policy** is delivered via those agent/rule files (not by pasting full skill bodies). This skill remains the router + sync playbook. See `reference/always-on.md` and hub `docs/always-on-skills.md`.

## Hard gate (first action, no exceptions)

When this skill is invoked (`@heyeddi`, session start, or “what should we run”), **before** answering, routing, or reading other skills:

1. Run **one** of these (project root = the workspace you are in):

   ```bash
   python .agents/skills/heyeddi/scripts/ensure_always_on_agents.py --project-root .
   # preferred when index/workflow may also be stale:
   python .agents/skills/heyeddi/scripts/sync.py --project-root .
   ```

   Fallbacks if skills live under Cursor: `~/.agents/skills/heyeddi/scripts/…` or `.cursor/skills/heyeddi/scripts/…`.

2. Confirm `AGENTS.md` and `.cursor/rules/heyeddi-always-on.mdc` exist (or `--check` passes).
3. **Only then** continue: `verify_setup`, `suggest_skills` / `load_catalog`, routing, design, etc.

**Forbidden:** Chat-only `@heyeddi` (explaining the skill, listing gates, or routing) without running a script that writes/verifies always-on files. Attaching the skill is not enough: a script must run.

## When to use

- **Every session start** on a HeyEddi project (`.heyeddi/` present or greenfield app request)
- User asks "what skills do we have?" or "which skill should handle this?"
- Before a multi-step pipeline (intake → scaffold → design → handoff → QA)
- **Design / look / polish:** `@taste-penpot` first. If no style/identity is pinned and this is not a refine of an existing `design.md` system, taste runs the **identity gate** (`references/identity-gate.md`): designer thinking (project, peers, follow vs unique) written under `.heyeddi/designs/`, clarifying questions when needed, then **3-5** What/Why/How options. In a design request it waits for the user's pick. In a build request it picks the recommended option, records why, and keeps going (`reference/autonomy.md`). Then one pass for tokens. Prefer `@heyeddi/penpot-mcp-server`: **design system first** (colours/type/fonts), then boards; Flex only if reflow is real (else absolute 8px); PNG Gate D required (`taste-penpot/references/layout-hard-gates.md` A-G). Absolute-only MCP still needs `hifi.html`. Then `@heyeddi-design` records product context and **blocks handoff** on text-walls / empty phones / missing PNG. Vue implementation follows `@vue-design-system`. Do not let `@heyeddi-design` invent a second look. Never use unscoped `penpot-mcp-server` or `@penpot/mcp`.
- **Redesign / from scratch:** `@taste-penpot` loads `references/code-to-design.md`, then the **identity gate** (unless the user pinned the new identity). Scope is the whole app, the named pages, or one page. The pass writes the audit and the proposal. It does not edit Vue until the user asks to build (the request was for a design, not code).
- **Any time one pillar runs**: bookend with `load_workflow_context` / `append_pillar_opinion`
- After `@heyeddi-intake`: follow `skill-routing.json` downstream

## Always-on siblings (every chat)

After routing, the working agreement is the managed `AGENTS.md` block (`templates/always-on/AGENTS.section.md`): autonomy, setup, sessions and worktrees, permissions, tests, engineering, cost, browser platform, prose, ship. Enforce it as written. Do not restate it in a skill. The gates it names: `@heyeddi-setup` `verify_setup`, `@heyeddi-local-first` `check_permission`, `@engineering-excellence` `check_engineering_plan` before code and `audit_engineering` plus `estimate_change_cost` after, `verify_prose`, `@pre-merge-gate --signoff`. Detail lives in `reference/autonomy.md` (run to completion, the only pauses, final summary) and `reference/testing.md` (test first, relevant layers). Host surfaces: `reference/host-surfaces.md`.

## Automatic `.heyeddi/` + always-on upkeep

**On `@heyeddi` itself:** use the **Hard gate** above (must run `ensure_always_on_agents` or `sync` first).

**Other HeyEddi skill tool calls** still auto-sync first:

1. **Ensures** `.heyeddi/` and refreshes `.heyeddi/skills-index.{json,md}` when missing
2. **Installs/updates** project `AGENTS.md` (managed block) and `.cursor/rules/heyeddi-always-on.mdc` (`alwaysApply: true`)

Reinstall skills (`npx skills add`) and keep working: the next tool that resolves the project root updates `.heyeddi/` + always-on files. That does **not** excuse skipping the Hard gate when the user invoked `@heyeddi` alone.

```bash
python .agents/skills/heyeddi/scripts/ensure_always_on_agents.py --project-root .
python .agents/skills/heyeddi/scripts/ensure_always_on_agents.py --project-root . --check
python .agents/skills/heyeddi/scripts/sync.py --project-root .
```

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
| *(auto)* | Every tool: `.heyeddi/` + always-on AGENTS/rule when missing/stale |
| `sync.py` | Optional full sync + workflow scaffold + always-on files |
| `ensure_always_on_agents.py` | Install/update `AGENTS.md` + Cursor alwaysApply rule |
| `write_skills_index.py` | Scan → `.heyeddi/skills-index.*` |
| `load_catalog.py` | Read cached index |
| `context_index.py` | One line per entry in `decisions.md` and the design Decision log; `--query`, `--type`, `--check` for secrets, `--hook` at session start (`reference/context-recall.md`) |
| `suggest_skills.py` | Rank skills for a prompt |
| `suggest_next_skill.py` | Next @skill + command after any skill finishes |
| `init_workflow_sync.py` | Scaffold `.heyeddi/docs/workflow/` |
| `load_workflow_context.py` | Sibling opinions + checklist for route |
| `append_pillar_opinion.py` | Log opinion; request UX/design/product response |
| `session_worktree.py` | Mark which session owns a worktree; gate commit, merge, and delete by role (`reference/session-worktrees.md`) |

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill heyeddi --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.

## Related

- `@heyeddi-product` · `@ux-flow-auditor` · `@heyeddi-design`: three pillars
- `@heyeddi-setup`: always-on prefs hard gate (`verify_setup --check`)
- `@engineering-excellence`: always-on plan + change gates
- `reference/autonomy.md`: run the request to completion; the only pauses; one final summary
- `reference/context-recall.md`: read the project's decisions and gotchas back; record new ones
- `reference/testing.md`: test first at the layers the change can break; hosted environments are look-only
- `reference/session-worktrees.md`: act only on worktrees your session owns; the session marker and its roles
- `reference/browser-platform.md`: frontend and design skills load Modern Web Guidance (`legacy-scan` finds problems) and Chrome DevTools for agents. Quasar and PrimeVue stay the components. Playwright stays the screenshot tool. Localhost only.
- `@heyeddi-intake`: upstream intake
- `reference/host-surfaces.md`: prefer host plan/data/visual tools; portable degrade
- `reference/next-skill-handoff.md`: next-skill block when a pipeline task completes
- `docs/cross-pillar-workflow.md`: hub summary
- `docs/always-on-skills.md`: hub always-on policy
