# Skills index

**Generated:** 2026-07-15T04:42:41Z · **Maintained by:** `@heyeddi`

Cached catalog — read this instead of every `SKILL.md` at session start. Refresh after installing skills: `write_skills_index --project-root .`

**Installed:** 23 / 23 skills

| Skill | Invoke | Installed | Description |
|-------|--------|-----------|-------------|
| backend-type-bridger | @backend-type-bridger | yes | Syncs FastAPI OpenAPI schema to TypeScript types and reads Firestore schema hints. Use when writing Vue composables a... |
| composable-patterns | @composable-patterns | yes | Provides FastAPI JWT and Firebase client composable patterns for consistent auth and data layers. Context-first skill... |
| dart-type-bridger | @dart-type-bridger | yes | Syncs FastAPI OpenAPI schema to Dart model stubs and reads Firestore schema hints for Flutter projects. Use when writ... |
| design-handoff-flutter | @design-handoff-flutter | yes | Implements Flutter screens from designer screenshots and handoff notes using Material 3. Two-pass workflow — mockup-b... |
| design-system-generalizer | @design-system-generalizer | yes | Scans token and component usage patterns from a golden reference page and diffs violations on other routes. Use when ... |
| engineering-excellence | @engineering-excellence | yes | Audits code for KISS, YAGNI, DRY, SOLID, and testability; maintains living engineering notes under .heyeddi/docs/engi... |
| flutter-engineering | @flutter-engineering | yes | Ensures HeyEddi Flutter projects have the right engineering stack — Flutter (Riverpod, go_router, Material 3), FastAP... |
| flutter-patterns | @flutter-patterns | yes | Provides FastAPI Dio and Firebase client patterns for Flutter — repositories, Riverpod providers, auth. Context-first... |
| heyeddi-design | @heyeddi-design | yes | End-to-end UI design for HeyEddi stack (PrimeVue, DESIGN.md, semantic tokens — OpenProps on scaffold default). Use wh... |
| heyeddi-handoff | @heyeddi-handoff | yes | Implements screens from designer screenshots and handoff notes. Two-pass workflow — designer writes mockup-brief with... |
| heyeddi-intake | @heyeddi-intake | yes | Translates vague user prompts into HeyEddi product docs (personas, route intent, voice), route-specific handoff artif... |
| heyeddi | @heyeddi | yes | Discover HeyEddi skills, auto-sync .heyeddi/ (skills index), cross-pillar opinions, and suggest @skills. Use at sessi... |
| heyeddi-pr-respond | @heyeddi-pr-respond | yes | Addresses PR review feedback — fetch all comment types, fix-vs-decline decisions, apply fixes, re-run pre-merge gate,... |
| heyeddi-pr-review | @heyeddi-pr-review | yes | Reviews submitted PRs using only committed changes — product fit, docs drift, engineering quality, test coverage, and... |
| heyeddi-product | @heyeddi-product | yes | Product leadership — user stories, acceptance criteria, backlog, holistic reviews. Verifies the product works and is ... |
| no-duplicate-ui | @no-duplicate-ui | yes | Scans Vue files for duplicate component names and similar template overlap. Use during PR review or when refactoring ... |
| pre-merge-gate | @pre-merge-gate | yes | Runs pre-merge checks (tests, build, types, optional UI audit) and returns a markdown pass/fail report. Use when QA a... |
| primevue-openprops-architect | @primevue-openprops-architect | yes | Enforces PrimeVue + project design tokens when editing Vue or CSS. OpenProps rules apply only when the project alread... |
| project-engineering | @project-engineering | yes | Ensures HeyEddi projects have the right engineering stack — Vue (Vite/Vitest), FastAPI backend, or Firebase tooling. ... |
| update-pitches | @update-pitches | yes | Audits backend pitch stories in docs/_pitches/ against app/{models,routers,services}/ and syncs Summary.md and priori... |
| ux-flow-auditor | @ux-flow-auditor | yes | Traces user task flows with Playwright — click depth, step success, friction — and writes reports to .heyeddi/docs/ux... |
| verify-build | @verify-build | yes | Runs npm run build to catch Vite/Rollup failures before merge. Use when validating frontend changes or in CI pre-merg... |
| visual-auditor | @visual-auditor | yes | Captures screenshots, reviews UI against product.md and design.md, runs WCAG contrast checks, fixes visual issues in ... |

## Quick use

1. `suggest_skills --user-prompt "..."` — rank skills for the task
2. Read **one** chosen skill's `SKILL.md` (path in JSON index)
3. Follow `docs/intake/skill-routing.json` when present
