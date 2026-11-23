<!-- heyeddi-always-on:start -->
## HeyEddi always-on

Thin gates for **every Agent chat** in this project. Full playbooks and scripts stay in skills — load them when a gate says so (or via `/skill`).

### Checklist

1. **Router / `.heyeddi/`** — Session start or ambiguous task: `@heyeddi`. Keep `.heyeddi/skills-index` current; follow `.heyeddi/docs/intake/skill-routing.json` when present. Do not freestyle the pipeline. Do not re-scaffold workflow every message.
2. **Setup** — Before the first git action of a session: `@heyeddi-setup` → `verify_setup --check`. If incomplete, run `write_setup.py --defaults` (no questions), keep working, and mention it in your final summary. Missing prefs never block work.
3. **Permissions** — Before commit, push, PR, merge, release, or any command that touches dev / staging / prod: `@heyeddi-local-first` → `check_permission.py --command "<cmd>" --check`. Exit 0 → run it, no question. Exit 2 → ask once (batch it with other open questions), then rerun with `--approved`. Exit 1 → never run it; hand that step to the user or the pipeline and keep working on the rest. Policy: `agent.preset` in `.heyeddi/stack.json` (default `balanced`). `terraform plan` is allowed and must be summarized.
4. **Engineering** — Before feature code: `@engineering-excellence` plan gate. After edits: `audit_engineering --check` (errors fail; warns advisory) and `estimate_change_cost --check` (state the $/month; over budget needs the user's yes).
5. **Browser platform (frontend and design)** — When a frontend or design skill runs (`@taste-penpot`, `@heyeddi-design`, `@vue-design-system` and the skills it routes, handoff, `@visual-verification`, `@visual-auditor`, `@ux-flow-auditor`): load `@heyeddi` `reference/browser-platform.md`. On existing UI, run Modern Web Guidance `legacy-scan` on the files you will touch (find problems) and verify hits before editing. Quasar, PrimeVue Aura, and Aura tokens stay the component source. Chrome DevTools MCP is for local performance, memory, and reduced-motion checks. Playwright stays the screenshot and signed-in test tool. Fresh Chrome profile, localhost only. Non-local: look and navigate only.
6. **Tests (this project)** — Not strict TDD. When you **fix a bug**: add or update a test that would have failed, run it, then fix. A **pure frontend** bug is a Playwright test: sign in with the project's test login and navigate the flow on the **local** app. If local cannot reproduce, look at test, staging, or production when `check_permission` allows reads there (the `balanced` default does). On those environments: look and navigate only. No destructive action whatsoever. When you **add behavior**: ship a focused test with the change. Skip only for pure docs/typos or unautomatable cases (say so). Run the project's test command for what you touched. Detail: `@heyeddi` `reference/reproduce-first.md`.
7. **Prose** — Any prose you author (chat, books, docs, UI, PRs): follow skill `PROSE_ANTI_SLOP`. Run `verify_prose --check` on touched surfaces; add `--glob` for non-default paths. No "not for books" carve-out.
8. **Ship** — Before merge-ready claims: `@pre-merge-gate --signoff` (exit 0 required).

### On demand (not every chat)

`@heyeddi-intake`, `@heyeddi-product`, `@taste-penpot`, `@heyeddi-design`, visual/UX auditors, `@heyeddi-pr-review`, `@heyeddi-pr-respond`, scaffolders / handoff.

Managed by `@heyeddi` sync / auto-sync. Edit outside this block freely; content between the markers is replaced on sync.
<!-- heyeddi-always-on:end -->
