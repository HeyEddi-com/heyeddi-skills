# Subagent delegation (Cursor + future cloud backend)

**Date:** 2026-07-03  
**Status:** Cursor-native via Task tool; cloud backend maps `delegate_to_skill` later.

HeyEddi skills **orchestrate** by default. The main chat plans, delegates focused work to **subagents**, merges results, and continues. Do not run delegated phases inline unless the user asks to stay in one thread or Task is unavailable.

---

## Cursor (works today)

Use the **Task** tool with `subagent_type` and a self-contained prompt (include `@skill`, route, paths, stop rules). Subagent returns a summary; orchestrator verifies artifacts and runs the next phase.

| `subagent_type` | Use for |
|-----------------|---------|
| `explore` | Read-only codebase search — catalog components, routes, existing patterns |
| `shell` | Skill scripts, `npm test`, `npm run build`, `gh`, `verify_*.py`, Playwright capture |
| `generalPurpose` | Single focused phase — mockup interpret, critique report, one view implementation |
| `bugbot` | Post-implementation diff review (optional) |
| `security-review` | Auth, settings, secrets, Firestore rules |
| `ci-watcher` | Watch PR checks after fixes |

### Prompt shape (copy pattern)

```
@heyeddi-handoff
Project root: /path/to/app
Route: /settings

Phase: interpret (Pass 1 only)
- Read .heyeddi/designs/settings/desktop.png and mobile.png
- Write mockup-brief.md with Implementation spec table
- Run describe_handoff.py --sync-design
- Do NOT write Vue files

Return: brief path + Implementation spec summary
```

---

## Skill → default delegation

| Skill | Orchestrator (main) | Delegate by default |
|-------|---------------------|---------------------|
| **heyeddi-handoff** | Pass sequencing, merge brief + verify results | Pass 1 interpret → `generalPurpose`; catalog scan → `explore`; verify scripts + build → `shell`; visual capture → `shell` + `@visual-auditor` |
| **heyeddi-design** | Routing, brief confirmation, Decision log | `research` / web → `generalPurpose`; `critique` → `generalPurpose`; `craft` (large route) → `generalPurpose`; validate → `shell`; visual → `@visual-auditor` |
| **visual-auditor** | *(often invoked as subagent)* | Playwright/layout scripts → `shell` |
| **project-engineering** | Stack choice, audit interpretation | `audit_scaffold`, `scaffold_stack`, tests → `shell` |
| **pre-merge-gate** | Report triage | `pre_merge_gate.py` → `shell` |
| **heyeddi-pr-respond** | Tracking table, fix vs decline, re-gate | `fetch_pr_comments` + `post_thread_replies` + `verify_response` → `shell`; comment analysis → `generalPurpose` |
| **heyeddi-pr-review** | Verdict on committed diff | `fetch_pr_context` + drift/audit → `shell`; PM delegates → `shell` |
| **primevue-openprops-architect** | — | `validate_vue.py` → `shell` |
| **verify-build** | — | build script → `shell` |
| **backend-type-bridger** | — | `sync_openapi` / schema scripts → `shell` |

Skills not listed run inline unless their `reference/subagents.md` says otherwise.

---

## Cloud backend (future)

Same phases; replace Task with `delegate_to_skill`:

```json
{
  "skill": "heyeddi-handoff",
  "phase": "interpret",
  "subagent_type": "generalPurpose",
  "prompt": "...",
  "project_root": "/workspace",
  "readonly": false
}
```

Orchestrator service loads parent skill `SKILL.md`, registers only tools needed for that phase, and returns structured output to the parent run. **Same prompt text** as Cursor — no second workflow.

---

## Anti-patterns

- Running Playwright + full implement + verify in one monolithic turn when phases are defined
- Subagent writes outside declared phase (e.g. interpret agent editing `.vue`)
- Skipping subagent return summary before next phase
- Duplicating `@visual-auditor` inline instead of delegating

---

## Related

- Per-skill routing: `skills/<name>/reference/subagents.md`
- [cloud-agent-integration.md](./cloud-agent-integration.md)
- [skill-authoring](../.cursor/rules/skill-authoring.mdc)
