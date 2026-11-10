---
name: heyeddi
description: "ALWAYS-ON router named @heyeddi. On every invoke: first run ensure_always_on_agents (or sync) so project AGENTS.md + Cursor alwaysApply gates exist — never chat-only. Then discover skills, sync .heyeddi/, and route. Design talk goes to @taste-penpot first then @heyeddi-design. Vue UI follows @vue-design-system. @heyeddi-orchestrator is a deprecated alias. Use at every session start, on ambiguous tasks, and when connecting product, UX, and design."
version: 3.4.10
product-version: 3.8.17
author: HeyEddi-com
---

# HeyEddi

**The router.** Invoke `@heyeddi`. `@heyeddi-orchestrator` is a deprecated alias for this skill.

Routes work to the right `@skill`, refreshes `.heyeddi/`, installs **thin always-on** `AGENTS.md` + `.cursor/rules/heyeddi-always-on.mdc`, and **keeps product, UX, and design pillars in sync**.

**Every-chat policy** is delivered via those agent/rule files (not by pasting full skill bodies). This skill remains the router + sync playbook. See `reference/always-on.md` and hub `docs/always-on-skills.md`.

## Hard gate (first action — no exceptions)

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

**Forbidden:** Chat-only `@heyeddi` (explaining the skill, listing gates, or routing) without running a script that writes/verifies always-on files. Attaching the skill is not enough — a script must run.

## When to use

- **Every session start** on a HeyEddi project (`.heyeddi/` present or greenfield app request)
- User asks "what skills do we have?" or "which skill should handle this?"
- Before a multi-step pipeline (intake → scaffold → design → handoff → QA)
- **Design / look / polish:** `@taste-penpot` first. If no style/identity is pinned and this is not a refine of an existing `design.md` system, taste runs the **identity gate** (`references/identity-gate.md`): designer thinking (project, peers, follow vs unique) written under `.heyeddi/designs/`, clarifying questions when needed, then **3–5** What/Why/How options — and **waits for the user to choose** before tokens or pixels. Scaffolding / MVP never waives that. Then one pass for tokens. Prefer `@heyeddi/penpot-mcp-server` — **design system first** (colours/type/fonts), then boards; Flex only if reflow is real (else absolute 8px); PNG Gate D required (`taste-penpot/references/layout-hard-gates.md` A–G). Absolute-only MCP still needs `hifi.html`. Then `@heyeddi-design` records product context and **blocks handoff** on text-walls / empty phones / missing PNG. Vue implementation follows `@vue-design-system`. Do not let `@heyeddi-design` invent a second look. Never use unscoped `penpot-mcp-server` or `@penpot/mcp`.
- **Redesign / from scratch:** `@taste-penpot` loads `references/code-to-design.md`, then the **identity gate** (unless the user pinned the new identity). Scope is the whole app, the named pages, or one page. The pass writes the audit and the proposal. It does not edit Vue until the user asks to build.
- **Any time one pillar runs**: bookend with `load_workflow_context` / `append_pillar_opinion`
- After `@heyeddi-intake`: confirm `skill-routing.json` before downstream work

## Always-on siblings (every chat)

After routing, enforce:

1. **`@heyeddi-setup`** prefs gate (`verify_setup --check`) before git/CI/commit/push or agent autonomy — incomplete prefs **fail** those actions; route setup until pass (`reference/setup-always-on.md` on that skill)
2. **`@heyeddi-local-first`** for infra or account changes: edit locally, run `classify_command.py --check`, then `terraform plan` and warn. Exit 1 means do not run the command.
3. **`@engineering-excellence`** plan gate before coding; change gate (`audit_engineering --check`) after edits — errors fail; warns advisory
4. **Prose anti-slop** on **any prose you author** (chat, books, docs, UI, PRs) via `context/PROSE_ANTI_SLOP.md`; run `verify_prose --check` (add `--glob` for manuscripts/other paths) when files change. No "UI-only" or "not for books" exemption.
5. **Clarify-before-act** when product/design/stack intent is missing
6. **Host surfaces** — prefer this session's native plan / data / visual tools when listed; degrade to `.heyeddi` / scripts otherwise (`reference/host-surfaces.md`)

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
| `suggest_skills.py` | Rank skills for a prompt |
| `suggest_next_skill.py` | Next @skill + command after any skill finishes |
| `init_workflow_sync.py` | Scaffold `.heyeddi/docs/workflow/` |
| `load_workflow_context.py` | Sibling opinions + checklist for route |
| `append_pillar_opinion.py` | Log opinion; request UX/design/product response |

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill (not after every tool call or subagent phase), suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill heyeddi --project-root .
   ```

   Add `--route /path` if you worked a specific route.

2. Include the script's **`### Next step`** block in your **final** reply. The user copies the **Prompt** line into chat (e.g. `@heyeddi-design craft /settings`).

Pass `--mode shape` (or `craft`, `audit`, etc.) when you know which sub-command just finished.

See `@heyeddi` → `reference/next-skill-handoff.md`.

## Related

- `@heyeddi-product` · `@ux-flow-auditor` · `@heyeddi-design`: three pillars
- `@heyeddi-setup`: always-on prefs hard gate (`verify_setup --check`)
- `@engineering-excellence`: always-on plan + change gates
- `reference/reproduce-first.md`: bug test first; frontend bugs use Playwright on local, then ask before test or production. Non-local: look only, no destructive action
- `@heyeddi-intake`: upstream intake
- `reference/host-surfaces.md`: prefer host plan/data/visual tools; portable degrade
- `reference/next-skill-handoff.md`: next-skill block when a pipeline task completes
- `docs/cross-pillar-workflow.md`: hub summary
- `docs/always-on-skills.md`: hub always-on policy
