---
name: project-engineering
description: "Ensures HeyEddi projects have the right engineering stack: Vue (Vite/Vitest), FastAPI backend, or Firebase tooling. Audits gaps, scaffolds as needed, installs deps, runs tests, documents local dev servers. Use when the repo is thin or before design/feature work on any HeyEddi app."
version: 1.1.1
product-version: 3.11.0
author: HeyEddi-com
paths:
  - "package.json"
  - "pyproject.toml"
  - "backend/**"
  - "firebase.json"
  - "firestore.rules"
  - "openapi.json"
  - ".heyeddi/**"
---

# Project Engineering

Baseline **code engineering** for HeyEddi **Vue** apps. For **Flutter** frontends use `@flutter-engineering` instead. Detects which stacks apply and adds the **correct tooling**: not one-size-fits-all.

## Subagents (default)

Delegate scaffold/audit/test scripts to **Task** `shell`; repo discovery to `explore`. Main chat picks stack from audit JSON. See `reference/subagents.md`.

## Stacks

| Stack | When | Tooling added |
|-------|------|----------------|
| **Vue** | Always for frontend work | Vite, Vitest, router, Quasar, PrimeVue Aura, spring motion, CSS tokens |
| **FastAPI** | REST API backend | `backend/`, pytest, `openapi.json`, uvicorn |
| **Firebase** | Firestore / Auth client | `firebase.json`, rules, emulators, env template |

The scaffold writes only the tech keys in `.heyeddi/stack.json`, and never replaces a value already there. Git, agent, and setup prefs belong to `@heyeddi-setup` (`write_setup.py --defaults` fills them from the repo).

```json
{ "frontend": "vue", "backends": ["fastapi"], "api_port": 8090 }
```

Flutter projects: `"frontend": "flutter"`, `"web_port": 8085`: see `@flutter-engineering`.

Or `"backends": ["firebase"]` or `["fastapi", "firebase"]`.  
`audit_scaffold` also infers from `openapi.json`, `firestore.rules`, and `.heyeddi/product.md` (or legacy `PRODUCT.md`).

## `.heyeddi/` workspace

Every HeyEddi app should have a **`.heyeddi/`** folder (created by `scaffold_stack` / `scaffold_heyeddi`):

| Path | Purpose |
|------|---------|
| `README.md` | HeyEddi intro (agents + humans workspace), free skills, [heyeddi.com/humans](https://heyeddi.com/humans) |
| `stack.json` | Stack + prefs (`@heyeddi-setup`) |
| `product.md` | Product brief |
| `design.md` | DESIGN.md format: tokens, rationale, Decision log |
| `designs/<feature>/` | Handoff PNGs, briefs, wireframes |
| `docs/` | Skill-generated reports (ship, PR tracking, drift audits) |

**Save all skill-created documents under `.heyeddi/docs/`** (or the paths above) so the team can reference them later. Root `PRODUCT.md` / `DESIGN.md` / `designs/` remain supported as legacy fallbacks.

## Workflow

1. **Prefs gate (always-on hard):** `@heyeddi-setup` `verify_setup --check` before git/CI/commit assumptions; incomplete → `write_setup.py --defaults` (no questions) and continue.
2. **`audit_scaffold`**: per-layer JSON (vue / fastapi / firebase).
3. **`scaffold_stack --stack auto`**: fills gaps (preferred over `scaffold_vue` alone).
4. **`ensure_npm`** + **`ensure_python`** as needed (`ensure_python` installs the dev extras: pytest and ruff).
5. **`dev_server_info`**: all local servers (Vue :5173, API :8090, Firebase emulators :4000).
6. **Plan gate (always-on):** `@engineering-excellence` `check_engineering_plan --check` before feature code; read reuse-catalog.
7. Per feature, write the failing test first (`@heyeddi` `reference/testing.md`; `write_test_stub` gives a starting file), then implement until it passes.
8. **`run_tests`** + **`run_backend_tests`**.
9. **Change gate (always-on):** `audit_engineering --check` (errors fail; warns advisory).
10. **`verify-build`** + **`pre-merge-gate`**.

## Local dev servers

| Stack | Command | URL |
|-------|---------|-----|
| Vue | `npm run dev` | http://localhost:5173 |
| FastAPI | `cd backend && poetry run uvicorn app.main:app --reload --port 8090` | http://localhost:8090/docs |
| Firebase | `firebase emulators:start` | http://localhost:4000 (UI) |

Run `dev_server_info` for project-specific steps. Each server needs its **own terminal**.

## References

- `reference/dev-server.md`: Vue
- `reference/fastapi-backend.md`: FastAPI
- `reference/firebase-backend.md`: Firebase emulators

## Related skills

- `backend-type-bridger`: OpenAPI / Firestore → TypeScript types
- `composable-patterns`: FastAPI JWT vs Firebase client composables
- `verify-build`: production frontend build
## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill project-engineering --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.
