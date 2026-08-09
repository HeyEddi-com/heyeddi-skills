# Learnings

Project-specific rules and preferences, appended over time.

## 2026-07-02 — Skills collection uses git subtrees

**Context:** This repository aggregates independently distributable Cursor skills.

**Decision:** Use **git subtrees** (not submodules) to vendor each skill from its own repository into `skills/<skill-name>/`.

**Install:** Consumers use `npx skills add heyeddi/<name>` or `./scripts/install-skills.sh` — skills land in `.agents/skills/` or `~/.cursor/skills/`, not in this hub's `.cursor/` folder.

**Rationale:**
- Single clone includes all skills — no `submodule update` step.
- Edits happen in the hub without detached-HEAD submodule confusion.
- `git subtree push` publishes changes back to the skill's standalone repo.

**Process:**
- Scaffold: `./scripts/new-skill.sh <name>`
- Link remote: `./scripts/add-skill-subtree.sh <name> <url>`
- Sync: `pull-skill-subtree.sh` / `push-skill-subtree.sh`
- Register remotes in `skills-registry.json`

**Notes:** Individual skill repos remain the distribution unit for consumers who want only one skill.

## 2026-07-02 — Dual-runtime skills (Cursor + Cloud Run)

**Context:** HeyEddi runs a custom agent on Cloud Run (Pydantic AI + LangChain). Skills must work locally in Cursor and in the cloud agent.

**Decision:** Every skill ships the **triad**: `SKILL.md`, `manifest.json` (flat tool schemas), `context/` + `scripts/`. Python scripts preferred for Cloud Run parity; Node via subprocess when needed.

**Process:** See `docs/skills-roadmap.md` for phased build plan and `docs/cloud-agent-integration.md` for Pydantic AI / LangChain registration.

**Notes:** `heyeddi-handoff` v1 uses screenshots only; Penpot export → API → MCP in later phases. **`heyeddi-design` v2 replaces impeccable** — discovery, web research, explore, wireframes, DESIGN.md, craft (Phase 5, 2026-07-02).

## 2026-07-02 — All 11 skills scaffolded

**Context:** Bootstrap of full skill library per `docs/skills-roadmap.md`.

**Skills:** `project-engineering`, `primevue-openprops-architect`, `verify-build`, ...

**Process:** `./scripts/new-skill.sh` for one-offs; `python3 scripts/bootstrap-all-skills.py` to regenerate all. Eval Vue templates: `python3 scripts/apply-eval-vue-scaffold.py --all-vue`.

**Notes:** Scripts degrade gracefully without Playwright/gh/npm. Tune per app repo; push standalone repos via subtree when ready.

## 2026-07-02 — Skill testing in hub

**Context:** Skills live in `skills/` as installable packages; need tests without a full Vue app.

**Decision:** `fixtures/sample-vue-app/` + `scripts/test-skills.py` (structure, smoke, cloud invoker). 54 checks across 11 skills.

**Process:** `./scripts/test-skills.py` before publish; extend fixture when skills need new file types; manual tests in real apps for Playwright/gh/npm.

## 2026-07-02 — Agent-based skill evals

**Context:** Smoke tests do not verify SKILL.md instructions or agent behavior.

**Decision:** `scripts/run-evals.py` + `evals/cases/*.yaml` — copy fresh project template, install skills, run local Cursor Agent CLI (`agent` binary) with specific prompt, assert on files.

**Backends:** `local` (default — `agent` CLI on your PC), `cursor` (optional cursor-sdk + CURSOR_API_KEY for CI), `pydantic` (EVAL_MODEL + provider key, mirrors Cloud Run tools).

**Process:** `./scripts/verify-agent-cli.sh` → `./scripts/setup-evals.sh` → `uv run python scripts/run-evals.py <case-id>`. See `docs/agent-evals.md`.

## 2026-07-02 — Eval Python deps via uv

**Context:** Quality gates need Playwright, Pillow, PyYAML.

**Decision:** Root `pyproject.toml` `[dependency-groups]`: `evals`, `evals-quality`, `evals-pydantic`, `evals-cursor`, `hub-tools`. Setup: `./scripts/setup-evals.sh`.

**Process:** `uv sync --group evals --group evals-quality` → `uv run playwright install chromium` → `uv run python scripts/run-evals.py`.

## 2026-07-02 — project-engineering multi-stack

**Context:** HeyEddi uses Vue + FastAPI or Vue + Firebase; thin eval repos had no backend tooling.

**Decision:** `project-engineering` detects stack via `.heyeddi/stack.json`, `openapi.json`, `firestore.rules`, `PRODUCT.md`. Tools: `scaffold_stack` (auto/vue/fastapi/firebase/full), `ensure_python`, `run_backend_tests`, multi-server `dev_server_info`.

**Process:** `audit_scaffold` → `scaffold_stack --stack auto` → `ensure_npm` / `ensure_python` → implement → test.

## 2026-07-02 — heyeddi-design v2 replaces impeccable

**Context:** Designer wants vague briefs ("enterprise view") without design jargon; full human design flow automated.

**Decision:** Expand `heyeddi-design` to v2 with pipeline: **discover → research → explore → shape (brief) → craft → polish**. Removed `disable-model-invocation` so Agent Decides on plain-language design intent.

**Sub-commands:** `init`, `discover`, `research`, `explore`, `shape`, `document`, `craft`, `polish`.

**Artifacts:** `designs/<feature>/research.md`, `wireframes/`, `brief.md`; project `PRODUCT.md` + `DESIGN.md`.

**Process:** Uninstall impeccable; use plain language or `@heyeddi-design shape`. Mockups → `@heyeddi-handoff` only.

**Notes:** Web search mandatory in shape unless user opts out. Concept images when harness supports generation.

## 2026-07-03 — `.heyeddi/` workspace folder

**Context:** User liked `.heyeddi/stack.json`; wanted README + central place for all skill-generated docs.

**Decision:** Every HeyEddi app uses `.heyeddi/` for README (agents + humans workspace + free skills + heyeddi.com/humans), `stack.json`, `product.md`, `design.md`, `designs/`, `docs/`, `audits/`. `scaffold_heyeddi.py` runs with `scaffold_stack`. Skills resolve `.heyeddi/` first, legacy root `PRODUCT.md` / `DESIGN.md` / `designs/` as fallback.

**Process:** See `docs/heyeddi-folder.md`. Eval templates and fixtures migrated to `.heyeddi/designs/`.

## 2026-07-03 — DESIGN.md Decision log (single file)

**Context:** Design skills should "talk design" like the [DESIGN.md ecosystem](https://getdesign.md/what-is-design-md) — not a separate `getdesign.md` file.

**Decision:** One `.heyeddi/design.md` matching [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) density — gold example: [Superhuman DESIGN.md](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/superhuman/DESIGN.md). YAML frontmatter + token refs in prose + component variants. HeyEddi adds **Decision log** at the end. Scaffold: `scaffold/heyeddi/design.md`.

**Process:** Normative values in frontmatter/sections; episodic handoff/polish rationale in Decision log only.

## 2026-07-03 — Design foundations (always on)

**Context:** User wants baseline defaults in every design: responsive, system light/dark, en+es i18n with browser detection, accessibility, dyslexia-friendly reading mode.

**Decision:** `heyeddi-design/reference/foundations.md` + **Foundations (always on)** section in scaffold `design.md` and locale table in `product.md`. Waivers only via explicit `product.md` table.

**Defaults:** mobile-first 375/768/1024/1440; `prefers-color-scheme`; vue-i18n en+es; WCAG 2.2 AA; `data-reading-mode="dyslexia"` toggle with Atkinson Hyperlegible/OpenDyslexic.

## 2026-07-03 — Handoff mockups are layout-only

**Context:** `heyeddi-handoff-only` eval failed partly because the judge compared button/toggle **color** to mockup PNGs. Captures also showed weak shell (flat sidebar, unstyled cards).

**Decision:** Mockup PNGs define **layout regions** (shell topology, cards, field order, CTA placement, responsive structure). **Colors** come from `.heyeddi/design.md` + OpenProps tokens — never sampled from PNG pixels.

**Process:**
- `heyeddi-handoff/reference/mockup-contract.md` — normative handoff contract
- App shell (`AppShell`, sidebar, top bar) required before route content when mockup shows in-app UI
- PrimeVue + `Card`/`InputText`/`Button` — not bare unstyled forms
- Eval judges compare **hierarchy/structure**, not mockup hue
- `handoff.json` includes `"mockup_contract": "layout_only"`

**Notes:** `generate-handoff-mockups.py` palette is illustrative for eval fixtures only.

## 2026-07-03 — heyeddi-handoff is designer + frontend developer

**Context:** Handoff agent must resolve layout and component architecture, not only map pixels to PrimeVue.

**Decision:** `@heyeddi-handoff` explicitly owns **component strategy** per mockup region: reuse catalog | PrimeVue as-is | thin wrapper | custom `.vue`. Document in Decision log under **Component strategy**. Custom when PrimeVue can't match layout; reuse when catalog fits.

**Process:** `mockup-contract.md` decision table; `SKILL.md` step 6; judge checks strategy is logged.

## 2026-07-03 — Mockup brief before implementation

**Context:** Eval run `heyeddi-handoff-only` produced shell components but ugly layout — agents read PNGs without a designer-eye brief (gray nav pills, poor CTA placement).

**Decision:** Handoff pipeline is **interpret (agent writes brief from PNGs) → sync design.md → implement**:
1. `mockup-brief.md` — **authored by `@heyeddi-handoff`** from `desktop.png` / `mobile.png` (designer-eye + region map). Hub `poe mockups` ships PNGs only — **not** the brief.
2. `describe_handoff.py --sync-design` merges agent brief into `.heyeddi/design.md`
3. `load_handoff.py` sets `interpret_required: true` when brief missing

**Process:** `load_handoff` → interpret PNGs → write `mockup-brief.md` → `describe_handoff --sync-design` → implement. Eval judges brief existence + layout compliance.

## 2026-07-03 — Critique before improve (@heyeddi-design)

**Context:** Improving existing UI without diagnosing first repeats mistakes. Impeccable had `critique` → `polish`; heyeddi-design only had `polish`.

**Decision:** Add **`critique`** sub-command and routing — natural language ("what's wrong", "looks bad") hits critique, not discover. **`polish` requires critique first** (`.heyeddi/docs/<feature>-critique.md`). Handoff **`interpret`** = critique of target mockups, then brief, then code.

**Process:** Existing UI: critique → polish. Mockup handoff: interpret (critique mockups) → brief → implement.

## 2026-07-03 — Surface completeness (generalized)

**Context:** Login eval shipped minimal fields-only UI; auth-specific `auth-surfaces.md` was too narrow.

**Decision:** `reference/surface-completeness.md` — general audit (hierarchy, states, spacing, affordances, **Deferred wiring**) + archetype table (sign-in, settings, list, dashboard, …). Applies to all routes; auth is one archetype row.

**Process:** shape/craft/critique → surface-completeness.md → full brief → implement UI chrome → deferred wiring table.

## 2026-07-03 — Design-handoff designer vs implementer (`handoff-to-code.md`)

**Context:** Eval `08-33-59Z` wrote a decent `mockup-brief.md` but sidebar spacing wrong — no `margin-top: auto` on user chip, cramped cards. Designer prose without measurable **Implementation spec**; same pass rushed into Vue.

**Decision:** Two explicit passes in `@heyeddi-handoff`: (1) designer → brief + **Implementation spec** table (tokens, flex, PrimeVue overrides); (2) implementer → tokens → shell → `verify_handoff --phase shell` → route → `verify_handoff --phase full`. `describe_handoff --check` requires Implementation spec section.

**Process:** `handoff-to-code.md` + `verify_handoff.py` — closes gap between mockup interpretation and CSS.

## 2026-07-03 — OpenProps optional

**Context:** OpenProps is HeyEddi scaffold default but not mandatory for every client or brownfield repo.

**Decision:** Detect token source from `package.json`, `tokens.css`, `design.md` before styling. Use OpenProps when already present; custom `:root` semantic vars (`--surface-1`, `--brand`) when not. Never add `open-props` mid-project without user/scaffold intent.

**Process:** `heyeddi-design/reference/token-strategy.md`; updated `heyeddi-handoff`, `primevue-openprops-architect`, `foundations.md`.

## 2026-07-03 — Eval hard gates for heyeddi-handoff (tokens + rendered spacing)

**Context:** Eval `08-45-17Z` passed agentic judge with cramped UI. Root cause: circular `tokens.css` aliases (`--size-6: var(--size-6)`) zeroed padding; `verify_handoff` only matched source strings; pixel similarity 0.97 on mostly-white layouts; LLM judge trusted file contents over PNG spacing.

**Decision:** (1) Remove same-name OpenProps aliases from all eval Vue scaffolds + `project-engineering` scaffold. (2) `verify_tokens.py` skill tool. (3) Eval **hard gates** before agentic judge: `verify_tokens`, `verify_handoff`, Playwright computed spacing (sidebar ≥ 220px, card padding/gap ≥ 16px).

**Process:** `evals/lib/hard_gates.py` + `visual_capture.py` spacing checks; `heyeddi-handoff-only.yaml` verify_commands include both scripts.

## 2026-07-03 — Wireframe handoff evals + theme coherence

**Context:** User wants to test generalization from ASCII/sketch wireframes on other pages; dark-mode mismatch (dark PrimeVue cards on light shell).

**Decision:** `low-fidelity-mockups.md` + `wireframe.md` inputs; eval cases `heyeddi-handoff-wireframe-dashboard` / `-team` on `vue-handoff-lowfi` template. `theme-coherence.md` + `verify_theme.py`; tokens use `light-dark()` + global `.p-card`/`.p-inputtext` semantic overrides in scaffolds.

**Process:** `uv run poe eval-heyeddi-handoff-wireframe` or per-case poe tasks.

## 2026-07-03 — Subagents default in skills

**Context:** Cursor supports Task/subagents natively; custom Cloud Run backend will mirror delegation later.

**Decision:** Multi-phase skills **orchestrate in main chat** and **delegate by default** via Task (`explore`, `shell`, `generalPurpose`, etc.). Hub spec: `docs/subagent-delegation.md`; per-skill `reference/subagents.md`.

**Process:** heyeddi-handoff (two-pass), heyeddi-design (critique/craft/visual), visual-auditor (worker target), project-engineering, pre-merge-gate, heyeddi-pr-respond, primevue-openprops-architect. Cloud: same prompt → `delegate_to_skill` API.

## 2026-07-03 — PrimeVue Card slot gates (eval hardening)

**Context:** `heyeddi-handoff-only` eval @ `22-07-26Z` failed with empty Profile/Notifications cards — fields were direct children of `Card`, not `<template #content>`. `verify_handoff` regex passed; judge caught it.

**Decision:** Three-layer fix:
1. **Skill docs** — `reference/primevue-card-slots.md`; ANTI_PATTERNS in heyeddi-handoff + primevue-openprops-architect
2. **Static verify** — `verify_handoff.py` scans all `<Card>` blocks for loose body elements
3. **Playwright content gates** — route-specific DOM checks (settings inputs/toggle, dashboard stats/table); optional `color_schemes: [light, dark]` captures

**Process:** Eval YAML adds `color_schemes`; `SettingsView.spec.ts` asserts form controls after handoff (placeholder-aware).

## 2026-07-03 — engineering-excellence + ux-flow-auditor skills

**Context:** User wanted UX task tracing (clicks, ease of use) and engineering excellence (KISS, DRY, SOLID, YAGNI) with all notes under `.heyeddi/`.

**Decision:** Two new skills:
- **`engineering-excellence`** — `init_engineering_docs`, `audit_engineering`, `append_decision` → `.heyeddi/docs/engineering/` + `engineering-audit-<date>.md`
- **`ux-flow-auditor`** — `init_ux_flows`, `trace_flow` → `.heyeddi/docs/ux-flows/` + `ux-flows.md` index

**Process:** Chain after design/handoff; distinct from `@heyeddi-design critique` (static) and `@pre-merge-gate` (CI). Docs: `docs/heyeddi-folder.md` updated.

## 2026-07-03 — Integration eval process proof (visual_audit per turn)

**Context:** `full-product-integration` step 5 had no audit screenshots until judge ran; steps 3–4 had no harness captures at all.

**Decision:** Playwright proof after **each UI turn** (3–6). Saves to `.heyeddi/audits/eval-process/<step-name>/` + rolling `manifest.json`. `hard_gates: visual` for heyeddi-design turns; `handoff` for settings only.

**Process:** `visual_audit.routes` supports multi-route turns; `references_by_route` for settings mockups on step 6.

## 2026-07-03 — Agent turn scope vs harness (integration step 6 hang)

**Context:** After `npm run build` exit 0, agent turn ran 20+ min (`still running` heartbeat). Build was done; agent kept running Playwright/`@visual-auditor` manually while harness also captures post-turn.

**Decision:** Worker prompts for integration steps 5–6: **no dev server / Playwright in agent turn** (same as `heyeddi-handoff-only`). Harness runs visual QA + hard gates. Step 6 capped at `agent_timeout: 480`. Fixed `local_agent.py` to enforce timeout during stdout read (was only on `proc.wait` after EOF).

## 2026-07-03 — Dashboard turn must not bind port 8000

**Context:** Step 4 agent curled `:8000`, tried backend, hung 6+ min; port often owned by stale uvicorn from prior eval.

**Decision:** Step 2/4 prompts: no long-running uvicorn; `useUsers()` renders with demo/empty when API down. **HeyEddi API default port is 8090** (`.heyeddi/stack.json` `api_port`) — not 8000. Harness warns on busy 8090/4173; preview picks free port 4173–4182.

## 2026-07-03 — API default port 8090 (migration complete)

**Context:** User asked to avoid `:8000` conflicts during integration evals.

**Process:** `dev_server_info.py` default + `stack.json` `api_port`; Vite `/api` proxy → `127.0.0.1:8090`; `warn_busy_eval_ports((8090, 4173))`; scaffolds `stack-fastapi.json` / `stack-full.json`; eval templates `product-app`, `api-vue`; docs/prompts/bootstrap examples updated.

## 2026-07-03 — Flutter stack (engineering agent + skills)

**Context:** User wanted Flutter as frontend with FastAPI, Firebase, or both — not phased.

**Decision:** Four new skills:
- **`flutter-engineering`** — scaffold (Riverpod, go_router, Material 3), audit, `ensure_flutter`, `dev_server_info` (web **8085**, API **8090`), `verify_build`
- **`flutter-patterns`** — Dio/Firestore repositories + Riverpod providers
- **`dart-type-bridger`** — OpenAPI → `lib/models/api_models.dart`
- **`design-handoff-flutter`** — Material 3 handoff + `verify_handoff`

**Process:** `.heyeddi/stack.json` `"frontend": "flutter"`; `@visual-auditor` supports `FLUTTER_WEB_URL`; eval cases `flutter-engineering-scaffold`, `flutter-backend-bridger-users`; fixture `sample-flutter-app`. Default Flutter web port **8085** (`web_port` in stack.json).

## 2026-07-03 — Dashboard eval gate + modern design reference

**Context:** Integration eval failed dashboard turn: harness required 3 stat cards; agent built correct TaskFlow roster (2 stats + 4 table rows). Generic hard-gate advice blamed tokens/Card slots incorrectly. User noted outputs look like plain PrimeVue admin.

**Decision:**
1. **`visual_capture.py`** — roster dashboards pass on table rows + optional stats; 3-stat rule only for KPI wireframe pattern without table.
2. **`hard_gates.recommendations_for_issues()`** — conditional fixes keyed to failed gate.
3. **`step-4-dashboard.md` / judge** — align with product.md (table primary).
4. **`heyeddi-design/reference/modern-reference.md`** — named product anchors + concrete PrimeVue/CSS techniques; required read for craft/shape on flagship routes.

**Process:** Research step cites Linear/Vercel/Stripe/etc.; craft anti-slop checklist before visual-auditor.

## 2026-07-03 — heyeddi-intake skill (intake agent)

**Context:** User wanted an upstream agent that interprets prompts into product docs, professional mockups when none supplied, seeded briefs, and routing for downstream skills.

**Decision:** New `@heyeddi-intake` skill — `load_intake`, `write_product`, `write_translation`, `ingest_mockups`, `generate_mockups`, `seed_brief`, `write_routing`. Outputs under `.heyeddi/docs/intake/` + `designs/`. Differs from hub eval mockups (PNG only): translator **seeds mockup-brief.md** for `@heyeddi-handoff`.

**Eval:** `heyeddi-intake-intake` case + `uv run poe eval-translator` — thin template `evals/projects/translator-thin/`, assertions on product.md, skill-routing.json, settings mockups/brief.

## 2026-07-03 — heyeddi-orchestrator (skill discovery + routing)

**Context:** Agent needs to know which HeyEddi skills exist and when to use them; Cursor cannot load all SKILL.md bodies at session start.

**Decision:** New `@heyeddi-orchestrator` skill — `load_catalog` (reads `skills-registry.json` + installed SKILL.md paths), `suggest_skills` (prompt keyword triggers + merge `.heyeddi/docs/intake/skill-routing.json`). Broad SKILL.md description for proactive discovery; agent must still **read** chosen skill's SKILL.md before invoking tools.

**Process:** Session start or ambiguous task → orchestrator → read top 1–3 SKILL.md files → invoke `@skill`. Greenfield without product.md → `@heyeddi-intake` first.

## 2026-07-04 — Skills completeness pass (except Penpot)

**Context:** Audit found 8 PARTIAL skills vs roadmap; user requested full implementation.

**Completed:**
- `backend-type-bridger`: `sync_openapi.py` writes `src/types/api.ts` from OpenAPI schemas
- `composable-patterns`: full composable validator (reactivity, auth, loading/error)
- `design-system-generalizer`: golden-route scan + diff violations (tokens, hex, PrimeVue components)
- `pre-merge-gate`: wires `no-duplicate-ui` + optional `visual-auditor` per route
- `heyeddi-intake`: vendored `reference/clarify-before-act.md` + `product-translation.template.json`
- `design-handoff-flutter`: `verify_tokens.py`, `verify_theme.py`, route-generic `verify_handoff.py`
- `docs/skills-roadmap.md`: added 8 missing skills to inventory
- Agent eval cases: `engineering-excellence-audit`, `ux-flow-auditor-init`, `heyeddi-orchestrator-suggest`, `design-handoff-flutter-settings`

**Deferred:** Penpot mode (`heyeddi-handoff/reference/penpot-mode.md` Phase 6 only).

**Verify:** `python3 scripts/test-skills.py` — 210/210 passed.

## 2026-07-04 — Eval case cleanup (no legacy)

**Context:** Too many overlapping poe tasks (composite bundles, wireframe cases, deprecated craft login, 2-turn combined handoff).

**Removed cases:** `heyeddi-design-craft-login`, `heyeddi-handoff-settings`, `heyeddi-handoff-wireframe-dashboard`, `heyeddi-handoff-wireframe-team`.

**Removed poe tasks:** `eval-case`, `eval-design`, `eval-heyeddi-design`, `eval-heyeddi-handoff-combined`, `eval-heyeddi-design-craft`, all wireframe tasks.

**Kept:** 15 cases — one `uv run poe eval-*` each + `eval-integration`, `eval-all`, `eval-list`, `eval-dry-run`. See `evals/README.md`.

**Notes:** Auto-load is **catalog + routing**, not literal injection of every skill body. Works with Cursor skill discovery and Cloud Run tool registration.

**Update (same day):** `suggest_skills` is **fully agnostic** — scores every installed skill from SKILL.md description + name tokens + optional `reference/triggers.md`. Removed hardcoded `TRIGGER_PATTERNS` map.

**Update (same day):** **`write_skills_index`** writes `.heyeddi/skills-index.json` + `skills-index.md`. `load_catalog` / `suggest_skills` read the cache by default — rescan with `--refresh` after skill installs. Agent reads one SKILL.md, not all.

## 2026-07-04 — Audience-driven design excellence (all layers)

**Context:** User wanted world-class design tied to product needs and target audiences — beyond `modern-reference.md` technique layer.

**Decision:** Ten-layer stack documented in `docs/design-excellence.md`:

1. `@heyeddi-intake` — extended `product.md` schema: **Personas**, **Per-route intent**, Competitors, Anti-audience, Voice & tone
2. `@heyeddi-orchestrator` — skills index cache
3. `@heyeddi-design discover/shape/research` — audience sections in brief + research
4. `reference/audience-design.md` — persona → aesthetic direction map
5. `reference/audience-fit.md` — post-build rubric (PASS/REVISE)
6. `load_context.py` — `audience_ready` + `audience_blocker` gates
7. `@heyeddi-handoff` — reads product personas before interpret pass
8. `docs/clarify-before-act.md` — hub-wide ask-before-guess convention
9. Integration eval **step 0 intake** + richer `product-app` product.md; steps 3–4 require shape + audience-fit
10. `heyeddi-intake-intake` asserts Personas + Per-route intent sections

**Process:** Read `.heyeddi/product.md` personas → pick direction row → brief with Audience section → craft → audience-fit critique → polish. Decision log cites persona + pattern borrowed.

**Notes:** World-class quality still requires running the full pipeline — skipping shape caps at "nice admin UI."

## 2026-07-04 — Spec-compliance fixes after agent eval audit

**Context:** 15 agent evals; 4 failed due to skill/eval gaps (not just agent mistakes).

**Fixes:**
- `verify_intake`: baseline `src/App.vue` allowed; block `src/views/**`; `repo-buildable` gate when `node_modules` present
- Backend templates: `[tool.poetry] package-mode = false` for `ensure_python`
- `verify_theme.py`: fail raw Aura when `--brand` defined without `definePreset`
- Eval Vue templates: `definePreset` indigo primary in `main.ts`
- API eval: `useUsers()` composable + `validate_composable --check`
- Flutter handoff judge aligned to Flutter skill (no Vue Decision log)
- `scaffold_fastapi.py`: patch CORS from `stack.json`; merge `fastapi` into `backends`

**Verify:** `python3 scripts/test-skills.py` (210/210) + `pytest tests/test_spec_compliance_fixes.py`

## 2026-07-06 — Product-translator mockups: wireframe-first, not cookie-cutter PNGs

**Context:** `@heyeddi-intake` always called `generate_mockups` → identical settings-app-shell PNG with only product name changed. Wrong for varied products/routes.

**Decision:**
- **User images** → `ingest_mockups` (screenshots, sketches, competitor refs)
- **No images (default)** → `generate_wireframe` — layout from `product-translation.json` page purpose (marketing, login, dashboard table, settings, generic)
- **PNG preset** → `generate_mockups --confirm-preset-match` only as last resort when preset matches route
- `generate_mockups` without `--confirm-preset-match` **refuses** with hint

**Docs:** `reference/mockup-strategy.md`, updated `mockup-quality.md`, pipeline, SKILL v1.2.0.

## 2026-07-06 — Product-translator: no PNGs in skill package

**Context:** Skill should not ship sample PNGs or Pillow template drawers. Testing PNGs belong in hub eval tooling (`poe mockups`), not distributable skills.

**Decision:**
- Removed `generate_mockups.py` and `_layout_mockups.py` from `skills/heyeddi-intake/`
- Added `prepare_mockup_prompts.py` + `reference/ai-mockup-images.md` — agent generates PNGs with native image tool when needed
- Hub `scripts/generate-handoff-mockups.py` remains eval/fixture-only
- SKILL v1.3.0

**Verify:** `python3 scripts/test-skills.py` heyeddi-intake passes; no `.png` under `skills/`.

## 2026-07-06 — HeyEddi-design: project-specific ambition bar

**Context:** Designer on test projects only pushed harder when user explicitly asked for "artistic / top notch" design.

**Decision:** `reference/design-ambition.md` — impressive craft is **default** for flagship routes. Brief requires **Design signature** section; craft ends with ambition checklist; audience-fit adds **Visual distinction** dimension (≥4 when high fidelity). User saying "make it artistic" confirms the bar, does not replace `shape`/signature work.

**Verify:** shape → craft on flagship route; Decision log cites memorable detail per project.

## 2026-07-06 — Visual-auditor v2: WCAG contrast + motion-over-text

**Context:** Auditor only captured screenshots — missed green-on-green text and light gray copy over animated gradients.

**Decision:** `audit_contrast.py` + in-page `contrast_probe.js` — WCAG AA ratios, same-hue detection, motion/background-image behind text. Reports under `.heyeddi/audits/visual/`. `pre-merge-gate` runs contrast audit with `--check`. `capture_screenshots --check` chains contrast.

**Verify:** `pytest tests/test_contrast_audit.py`; fixture `contrast-violations.html` must report errors.

## 2026-07-06 — Visual-auditor paths under `.heyeddi/audits/visual/`

**Context:** Screenshots wrote to repo-root `.visual-audit/` while contrast reports used `.heyeddi/audits/visual/`.

**Decision:** All `@visual-auditor` artifacts under `.heyeddi/audits/visual/` — screenshots in `screenshots/` subdirectory. Eval harness mirrors to same path. Repo-root `.visual-audit/` is legacy read-only.

## 2026-07-06 — Visual-auditor v3: review, fix, document

**Context:** User wanted auditor to review screenshots against product + design spec, fix issues immediately, not only report them.

**Decision:** v3.0.0 — `load_visual_context`, `append_fix_log`, `finalize_visual_review`; `reference/visual-review.md` + `fix-loop.md`. Removed `disable-model-invocation`. Agent reads PNGs, edits Vue/CSS, logs each fix, re-verifies contrast.

## 2026-07-06 — Product-manager skill (holistic PM orchestrator)

**Context:** User wanted PM beyond backlog — verify product works, is useful, suggest better alternatives; delegate UX, design, engineering research in code.

**Decision:** New `@heyeddi-product` — `load_product_context`, `audit_product`, `write_feature_spec`, `check_features`, `write_review_plan`, `verify_product`. Artifacts under `.heyeddi/docs/product/`. Delegates to `@ux-flow-auditor`, `@heyeddi-design critique`, `@visual-auditor`, `@engineering-excellence` per `reference/delegation.md`.

**Chain:** `@heyeddi-intake` → `@heyeddi-product` audit + specs → design/engineering → PM review → `@pre-merge-gate`.

## 2026-07-07 — Cross-pillar workflow sync (product · UX · design)

**Context:** User wanted product, UX, and design flows connected — when one runs, others opine and maintain docs.

**Decision:** `@heyeddi-orchestrator` v1.2.0 — `init_workflow_sync`, `load_workflow_context`, `append_pillar_opinion`. Artifacts under `.heyeddi/docs/workflow/opinions/`. Mandatory bookends in `@heyeddi-product`, `@ux-flow-auditor`, `@heyeddi-design`. Hub `docs/cross-pillar-workflow.md`.

## 2026-07-07 — Two PR workflows (submission review vs respond)

**Context:** User needed distinct skills: (1) review submitted PR on committed diff only — product, docs, engineering, tests; (2) respond to human review comments with fix-vs-decline and re-gate.

**Decision:**
- **`@heyeddi-pr-review`** (new) — `fetch_pr_context`, `check_doc_drift`, `audit_pr_changes`, `write_pr_review`, `verify_pr_review` → `.heyeddi/docs/pr-<N>-review.md`
- **`@heyeddi-pr-respond`** (v1.1) — adds `verify_response`, `reference/workflow.md`, mandatory `pre_merge_gate` before summary

**Process:** See `docs/pr-workflows.md`. Evals: `uv run poe eval-pr-submission`, `uv run poe eval-pr`.

**Notes:** Submission review = reviewer/QA; responder = PR author after feedback. Default output is `.heyeddi/docs/` — post `gh pr review` only when user asks.

## 2026-07-07 — v2 skill naming plan (`heyeddi-*` spine)

**Context:** User asked whether to rename all skills to `heyeddi-*` or only main workflows.

**Decision:** **Spine only** (6–8 renames), not all 22. Canonical v2 names: `heyeddi-intake`, `heyeddi-product`, `heyeddi-orchestrator`, `heyeddi-handoff`, `heyeddi-pr-review`, `heyeddi-pr-respond` (+ optional `heyeddi-ship-gate`, `heyeddi-handoff-flutter`). Guardrails stay descriptive (`verify-build`, `engineering-excellence`, …).

**Migration:** v2.0.0 ships alias stub folders (symlink to canonical) + `skills-registry.json` `aliases` map + `migrate-skill-names-v2.py` for `.heyeddi/` routing JSON. Remove aliases in v3.0.0.

**Process:** Full plan in `docs/v2-skill-naming.md`. **Implemented in v2.0.0** (2026-07-07).

**Executed:** `git mv` + alias stubs (`bootstrap-skill-aliases.py`), bulk replace (`apply-v2-skill-names.py`), `migrate-skill-names-v2.py`, registry `aliases`, `_catalog.py` resolution. Smoke **386/386**; `tests/test_skill_aliases.py` **5/5**.

**Notes:** `@heyeddi-design` unchanged. Typing `@heyeddi` in Cursor surfaces the pipeline spine. v1 names remain as deprecated alias folders until v3.0.0.

## 2026-07-07 — Auto `.heyeddi/` migration on session start

**Context:** User expected reinstall to update `.heyeddi/` — skills should migrate project artifacts, not a separate manual script.

**Decision:** `@heyeddi-orchestrator` v2.0.0 — `migrate_heyeddi`, `sync_heyeddi_workspace`; `write_skills_index` and `load_catalog --refresh` run migration first. Writes `.heyeddi/sync-state.json` + `docs/skill-name-migration-2.0.0.json`.

**Process:** Session start → `sync_heyeddi_workspace`. After `npx skills add` → same. Hub `migrate-skill-names-v2.py` delegates to skill script.

## 2026-07-07 — Zero-command auto-sync; tool renamed to `sync`

**Context:** User should not need to run a manual orchestrator command — any HeyEddi skill invocation should keep `.heyeddi/` current.

**Decision:** `_auto_sync.ensure_heyeddi()` runs from every spine skill's `resolve_project_root()` (orchestrator, intake, product, handoff, design, pr-review, pr-respond). Renamed `sync_heyeddi_workspace` → `sync` (`sync.py`).

**Process:** Reinstall skills → use any `@heyeddi-*` skill normally; migration + index refresh happen automatically. Optional explicit full sync: `@heyeddi-orchestrator` `sync`.

## 2026-07-08 — Scanner hardening (Snyk/Socket) — v2.0.2

**Context:** skills.sh scanners flagged SSRF (urllib on caller URL) and subprocess-spawn capability on several skills.

**Decision:** No `# nosec`. Real mitigations only:
- `sync_openapi.py` (dart + backend type-bridgers): `validate_fetch_url()` sanitizer gate — http/https only, no embedded creds, host required; use explicit `urllib.request.Request(url, method="GET")`.
- `run_command()` (all `_skill_cli.py`) + direct `npm` call: resolve exe via `shutil.which()` to absolute path, `shell=False` explicit. Python spawns already use `sys.executable` (absolute) — left as-is.

**Also fixed:** `heyeddi-pr-respond` / `heyeddi-pr-review` `_skill_cli.py` had lost `run_command` when the auto-sync variant was copied over them — re-added (hardened). This restored 8 failing PR-fetch smoke tests → 392/392.

## 2026-07-08 — Orchestrator: remove in-skill subprocess spawn — v2.0.3

**Context:** `heyeddi-orchestrator` `sync.py` spawned its own `init_workflow_sync.py` via `subprocess.run([sys.executable, ...])` → Snyk Med Risk.

**Decision:** Extract `scaffold_workflow(root, force=)` in `init_workflow_sync.py`; `sync.py` imports and calls it in-process. Orchestrator now has **zero** subprocess/urllib/eval. Cross-*skill* spawns elsewhere keep `sys.executable` (needed for isolation).

**Note:** skills.sh scan lags releases — capability-only flags (Socket on handoff/intake, Gen on pre-merge-gate) are benign and irreducible without `# nosec`.

## 2026-07-08 — skills.sh page polish — v2.0.4

**Context:** skills.sh org page GitHub button points at `github.com/heyeddi-com` (not `/skills`); 28 skills listed due to v1 alias stubs.

**Decision:**
- Root `skills.sh.json` — Pipeline / Engineering / Design & QA groupings on [skills.sh/heyeddi-com/skills](https://www.skills.sh/heyeddi-com/skills).
- v1 alias folders (`design-handoff`, `product-translator`, …) → `metadata.internal: true` in SKILL.md (hidden from `npx skills add --list`).
- Canonical install command in docs: `npx skills add HeyEddi-com/skills --skill <name>` (hub, not per-skill standalone repos).

**Process:** Install counts = Vercel `npx skills add` only. Share repo page URL, not org page. Re-run `npx skills add` after release to refresh skills.sh cache. No custom HeyEddi usage telemetry in skills.

## 2026-07-08 — Next-skill handoff at task complete — v2.0.6

**Context:** User wants a copy-paste **prompt** for the next `@skill` when a pipeline task finishes (e.g. `@heyeddi-design craft /settings`), not `python scripts/...` paths.

**Decision:**
- `suggest_next_skill.py` returns `prompt` + `user_block` with **Prompt:** line for chat.
- `--mode` (shape, craft, audit, sync, …) refines chain (e.g. design shape → craft).
- 12 pipeline SKILL.md files — task complete only; utilities stripped.
- `reference/next-skill-handoff.md` — examples table.

## 2026-07-14 — Remove deprecated v1 skill alias folders

**Context:** User asked to remove all deprecated skill names (v1 aliases from v2 rename).

**Planned (awaiting approval):** Delete the 6 deprecated alias install folders (`product-translator`, `product-manager`, `skill-orchestrator`, `design-handoff`, `pr-submission-review`, `pr-review-responder`) from `skills/`, mirrored `.agents/skills/` and `plugins/heyeddi-skills/skills/`. Update `skills.sh.json`, `skills-lock.json`, README/docs counts. Keep `skill-name-aliases.json` + migrate path so consumer `.heyeddi/` artifacts still remap old names (unless user requests full alias-map removal). Leave `design-handoff-flutter` (not deprecated). Leave historical `evals/runs/` snapshots untouched.

## 2026-07-14 — v3.0.0 remove all v1 skill aliases

**Context:** User approved full removal — alias folders, alias map, migrate path, and bootstrap scripts. Only they use these skills.

**Decision / Executed:**
- Deleted 6 alias stub folders from `skills/` and `.agents/skills/` (`product-translator`, `product-manager`, `skill-orchestrator`, `design-handoff`, `pr-submission-review`, `pr-review-responder`). Kept `design-handoff-flutter`.
- Removed `scripts/skill-name-aliases.json`, `bootstrap-skill-aliases.py`, `apply-v2-skill-names.py`, `migrate-skill-names-v2.py`, `tests/test_skill_aliases.py`, orchestrator `_heyeddi_migrate.py` / `migrate_heyeddi.py`.
- Stripped alias resolution from `_catalog.py` / `_next_skill.py`; auto-sync + `sync` only refresh skills index.
- Bumped registry / README / plugin / orchestrator to **v3.0.0**; cleared deprecated grouping in `skills.sh.json` and lock entries.
- Regenerated fixture skills index; reinstalled `.agents/skills` from hub.
- Left historical `evals/runs/` and `learnings.md` history entries as-is.

## 2026-07-15 — Run tests before release (missed on v3.0.0)

**Context:** Shipped v3.0.0 without full pytest / `poe test` / agent evals; user asked afterward.

**Rule:** Before tagging a release, always run:
1. `uv run pytest tests/ -q`
2. `uv run poe test` (skill smoke)
3. At least `uv run poe eval-orchestrator` (or `eval-all` for major)

**Note:** `evals/prompts/design-handoff/` must match case paths (`heyeddi-handoff/`) — rename drift broke `eval-list` after v2 rename.

## 2026-07-15 — Full verification after v3.0.0

**Ran:** pytest 15/15; `poe test` 293/293; all 16 agent evals eventually PASS.

**Issues found:**
1. `evals/prompts/design-handoff/` vs cases expecting `heyeddi-handoff/` — fixed by rename (uncommitted at time of run).
2. `eval-all | tee` without `pipefail` reported exit 0 after judge `RuntimeError` timeout — suite aborted mid-run.
3. Default judge timeout 300s too low for some cases; `--judge-timeout 900` fixed retries.
4. `design-handoff-flutter-settings` flaked once (missing `verify_tokens` in evidence); passed on retry.

**Improvements to pursue:** release checklist script; `set -o pipefail` in eval docs/poe; raise default `EVAL_JUDGE_TIMEOUT`; structure test that prompt_file paths exist; continue-on-error for eval-all.

## 2026-07-15 — Release gate tooling (v3.0.1)

**Implemented:** `scripts/release-gate.sh`, default judge timeout 900s, `--all` continues on case errors, eval prompt-path pytest, `evals/runs/` gitignored, poe `eval-all` / `release-gate` tasks with `PYTHONUNBUFFERED=1`.

## 2026-07-15 — Snyk auto-sync / prompt-injection hardening

**Context:** skills.sh / Snyk flagged `_auto_sync.py` as high-risk (search home + env paths, `sys.path.insert`, dynamic import) and `load_context.py` for untrusted PRODUCT.md/DESIGN.md ingestion.

**Triage:**
- **Real:** auto-sync path search + `sys.path` mutation — supply-chain shaped.
- **Stale:** findings mentioning `_heyeddi_migrate.py` (removed in v3.0.0).
- **Mostly capability FP:** agent running `npm test` / skill scripts (expected for engineering skills).
- **Prompt injection:** legitimate risk surface; wrap project docs as data.

**Fix:** Allowlist-only orchestrator script roots (skill sibling + project `.agents`/`.cursor` only); load `_catalog.py` via `importlib.util.spec_from_file_location` (no `sys.path`); wrap product/design markdown in `UNTRUSTED_PROJECT_DOC` delimiters.

## 2026-07-15 — OpenAPI sync local-file only (Snyk third-party content)

**Context:** Snyk flagged `sync_openapi.py --url` as third-party content exposure (fetch → JSON → agent context).

**Decision:** Remove all network fetch from backend + dart type-bridgers. Sync only from a local file under project root (`openapi.json` or `--openapi <relpath>`). SKILL.md instructs agents to refresh with `curl … -o openapi.json` when needed. Stdout remains a summary (counts/names), never raw schema dump.

## 2026-07-15 — Handoff brief third-party content wrapping

**Context:** Snyk flagged `load_handoff.py` reading outsider-authored `mockup-brief.md` (and possibly wireframe/design) into agent JSON as third-party content exposure.

**Fix:** Shared `_untrusted_doc.wrap_untrusted_doc()` used by:
- `heyeddi-handoff` `load_handoff.py` / `describe_handoff.py`
- `design-handoff-flutter` `load_handoff.py`
- `heyeddi-design` `load_context.py` (same helper; product/design already wrapped)

Emitted `mockup_brief_text`, `wireframe_md_text`, and `design_md_excerpt` are delimited as `UNTRUSTED_PROJECT_DOC` with an explicit data-only note. Paths remain unwrapped.

## 2026-07-15 — PR review third-party content wrapping

**Context:** Snyk flagged `fetch_pr_context` (`gh pr view` / `gh pr diff`) ingesting outsider PR title/body/author/file list into JSON that `write_pr_review` embeds in `.heyeddi/docs/pr-<N>-review.md`.

**Decision:** Cannot remove `gh` fetch (core of the skill). Bound free text instead:
- `heyeddi-pr-review`: wrap title/body/author (+ `changed_files_text`) as `UNTRUSTED_EXTERNAL_CONTENT`; report H1 is only `PR #N` (title not in heading); metadata section is DATA-only.
- `heyeddi-pr-respond`: wrap comment/review `body` fields the same way in `fetch_pr_comments`.

## 2026-07-15 — Product skill: auto-sync tighten + prompt boundaries + verify allowlist

**Context:** Scanner flagged (1) `_auto_sync` loading catalog from project `.agents`/`.cursor`, (2) `load_product_context` / `audit_product` / `check_features` ingesting `product.md` + feature specs without boundaries, (3) `verify_product` subprocess as execution vector.

**Fixes:**
1. `_auto_sync` allowlist = skill-tree sibling `heyeddi-orchestrator/scripts` only (plus self when running as orchestrator). No project-root path search, no env, no `sys.path`, no migrate.
2. Product scripts emit `product_md_text` / `feature_spec_texts` / wrapped `purpose` with `UNTRUSTED_PROJECT_DOC`.
3. `verify_product` only execs allowlisted sibling basenames (`audit_product.py`, `check_features.py`) with fixed `--check` flag filtering.

## 2026-07-15 — PR respond comment fetch wrapping (reinforced)

**Context:** Snyk flagged `fetch_pr_comments.py` emitting outsider review/discussion/inline bodies into the agent “analyze vs PR goals” step.

**Status:** Wrapping was already applied earlier in this security batch; reinforced with:
- Also wrap `diff_hunk` free text
- Explicit DATA-only notes in SKILL.md / workflow.md / ANTI_PATTERNS
- `tests/test_fetch_pr_comments_untrusted.py`

## 2026-07-15 — Handoff SUSPICIOUS trust-chain (triage + docs)

**Context:** Scanner marked screenshot-to-code handoff SUSPICIOUS: untrusted design inputs + code/shell subagents + chained skills without stated provenance. No exfiltration/malware shown.

**Triage:** Accepted as **elevated agent-safety / trust-chain risk**, not malware. Core workflow is coherent and intentional.

**Mitigations documented/enforced:**
- Existing `UNTRUSTED_PROJECT_DOC` wraps on brief/wireframe/design excerpts
- New `heyeddi-handoff/reference/trust-boundaries.md` — DATA-only inputs, Pass 1/2 separation, same-install-tree skill provenance allowlist
- Subagent worker trust preamble; ANTI_PATTERNS against mockup-driven installs
- Flutter handoff SKILL.md points at the same policy

## 2026-07-15 — CI skill security: skill-trust (+ skills-check), not skills.sh CLI

**Context:** User asked to run skills.sh-adjacent security tools in CI. `npx skills` has no test/audit command.

**Decision (avoid duplication):**
- **Primary:** `@mnvsk97/skill-trust` `lint` on each `skills/*/`.
- **Secondary:** `skills-check audit --fail-on high` (injection/command). Do **not** also run `skills-check lint` (overlaps skill-trust; noisy `product-version` metadata).
- **Skip** `--include-registry-audits` in CI (local hub → skills.sh API 400; platform audits refresh after publish).

**Added:** `scripts/skill-security-scan.sh`, root `package.json` + lockfile, `.github/workflows/ci.yml` (pytest + smoke + scan), `poe skill-security`, release-gate step.

## 2026-07-15 — v3.0.2 security hardening + CI + release

**Shipped:** Untrusted-doc wraps (handoff, design, product, PR review/respond, orchestrator opinions), auto-sync skill-tree-only allowlist, OpenAPI local-only, verify_product allowlist, trust-boundaries docs, CI skill-security scans. Merge PR #1 → tag **v3.0.2**.

## 2026-07-16: v3.0.3 path-only emit (Snyk W011)

**Context:** skills.sh still showed Med/Critical-class badges on v3.0.2 installs for skills that emit project/PR free text (W011 third-party content exposure). Wrapping alone did not clear scanners.

**Change:** Loaders no longer put outsider free text on stdout.
- Handoff / flutter / design / product / orchestrator → paths + `agent_read_paths`; agent uses Read tool
- PR review/respond → wrapped payload written under `.heyeddi/docs/`; stdout is path + counts/structure
- Also: filesystem-only `_auto_sync` (no `exec_module`), no home/env catalog roots, bridger schema summaries, handoff_meta whitelist

**Ship:** bump hub to **v3.0.3**; platform rescans after tag/release.

## 2026-07-16: Prose anti-slop (no em dashes / AI filler)

**Context:** Skills had UI anti-slop (`modern-reference.md`) and Cursor `deslop` for code, but no shared ban on em dashes or AI prose filler. Skill docs themselves were full of `—`.

**Decision:**
- Canonical: `docs/prose-anti-slop.md`
- Copied to every skill as `context/PROSE_ANTI_SLOP.md` (+ template)
- Every `context/ANTI_PATTERNS.md` gets NEVER + pointer
- Scrubbed em/en dashes from skill docs and scripts
- Design craft checklist also gates UI copy via PROSE_ANTI_SLOP

**Note:** ASCII ` - ` is allowed; Unicode em/en dashes are not.

## 2026-07-16: Expanded AI prose slop ban list

**Context:** User demanded stronger prevention of obvious AI slop beyond em dashes.

**Expanded `docs/prose-anti-slop.md` / every `context/PROSE_ANTI_SLOP.md` with:**
- Soft-focus verbs/nouns/adjectives (delve, tapestry, realm, robust, seamless, …)
- Corporate sludge and chatbot residue
- Blog filler phrases and fake profundity patterns
- Structure bans (emoji theater, triad padding, hedge stacks)
- Replacement table + Slack smell test
- Stronger ANTI_PATTERNS NEVER line on all skills

## 2026-07-16: Automated GitHub releases on main

**Context:** Merge to main only ran CI; tagging was manual.

**Decision:** `.github/workflows/release.yml` on push to `main` reads `skills-registry.json` version and creates `vX.Y.Z` GitHub Release if the tag is missing. Version bumps stay in PRs. No full eval gate on release (PR CI is the gate).

**Maintainer:** bump version in PR → merge → auto-tag.

## 2026-07-18: Always post GitHub PR review after heyeddi-pr-review

**Context:** After `@heyeddi-pr-review`, default was report-only in `.heyeddi/docs/` unless the user asked to post.

**Decision:** Always post the review to GitHub via `gh pr review` when the submission review completes (Approve / Request changes / Block mapped to `--approve` / `--request-changes` / comment+block rationale). Keep the full report in `.heyeddi/docs/pr-<N>-review.md`.

**Exception:** GitHub forbids approving your own PR — post `--comment` with the same verdict text and note that a second reviewer must click Approve if branch rules require it.

**Process:** After `verify_pr_review --check` passes, run `gh pr review <N>` with the verdict; do not wait for a separate "post it" ask.

## 2026-07-24 — Prose hard gate (`verify_prose.py`)

**Context:** User still saw em dashes in website copy despite July 2026 advisory `PROSE_ANTI_SLOP` rules. Agents skipped optional checklist items.

**Decision:**
- New `@heyeddi-design` tool `verify_prose.py --check` scans `src/**/*.vue`, `src/**/*.json`, locale paths, `.heyeddi/product.md`, `.heyeddi/design.md` for em/en dashes (U+2014/U+2013) and high-signal AI filler words/phrases.
- `@pre-merge-gate` runs prose audit by default (`--skip-prose-audit` to omit).
- `@heyeddi-design` setup step **3g** + `craft.md` step 11 require `verify_prose --check` before done.
- `@heyeddi-handoff` Pass 2 step 10b requires same before route complete.

**Process:** Fix reported file:line; replace dash with period/comma/colon or ASCII ` - `; rewrite filler per `context/PROSE_ANTI_SLOP.md`.

**Verify:** `uv run pytest tests/test_verify_prose.py`; `python3 scripts/test-skills.py heyeddi-design`.

## 2026-07-24 — skills.sh official listing hygiene

**Context:** User wants HeyEddi skills listed as official on skills.sh (beyond telemetry indexing).

**Decision:**
- Playbook: `docs/skills-sh-official-listing.md` (installs → topics → frontmatter → security → vercel-labs/skills review).
- `scripts/sync-skill-frontmatter.py` sets `version` (manifest), `product-version` (hub registry), `author: HeyEddi-com` on all 22 `SKILL.md` files.
- GitHub topics on hub repo: `agent-skills`, `skills-sh`, `ai-agents` (+ existing `cursor`, `claude-code`).
- Template `templates/skill/SKILL.md` includes the three metadata fields for new skills.

**Process:** Run frontmatter sync on every hub version bump; drive installs via pinned `npx skills add` URLs; open vercel-labs/skills PR after traction.


## 2026-08-05 — PR respond: hard-gate individual thread replies

**Context:** `@heyeddi-pr-respond` (and the PR review handler rule) often posted a summary or marked tracking RESPONDED without posting a reply in each GitHub comment thread.

**Decision:**
- Replies draft must use `## Comment <id>` sections with `## Summary` last.
- New `post_thread_replies.py` posts every drafted reply and writes `pr-<N>-posted.json`.
- `verify_response --check` fails if any tracked ID lacks a draft or posted log; `--live` also checks GitHub `in_reply_to_id` for inline comments.
- Fixture/eval path still uses `--fixture` (drafts only; optional `--dry-run` for posted.json).

**Process:** draft replies → `post_thread_replies` → `verify_response --check [--live]` → summary last.

**Notes:** Skill version **1.2.0**. Parent `pr-review-handler.mdc` got a hard-gate callout pointing at this flow.

## 2026-08-05 — Skills update: detect and ask (no silent self-update)

**Context:** User asked whether skills should auto-self-update when newer versions exist, or ask first.

**Decision:** Detect + ask. Never silent install.
- Hub-wide check (max installed `product-version` vs GitHub latest release via `gh`)
- Runs on `@heyeddi-orchestrator` `sync` and `check_skills_update` (not every skill invoke)
- 24h throttle; kill switch via `--disable`, sync-state, or `HEYEDDI_SKILLS_UPDATE_CHECK=off`
- Agent must show `user_block` and wait for approval before `npx skills add`

**Process:** `check_skills_update` → ask → on yes install; on skip `--dismiss --latest`.

**Notes:** Orchestrator skill **3.1.0**. See `reference/skills-update.md`.

## 2026-08-05 — PR respond: ban top-level acknowledgement spam

**Context:** Agents posted Conversation-tab spam like "Acknowledged review attachment PRR_…" instead of replying in the reviewer's thread.

**Decision:**
- Individual replies MUST use `…/pulls/<N>/comments/<ID>/replies` only
- `gh pr comment` allowed at most once for final Summary
- Review submission bodies are not threads (skip top-level post)
- Ban acknowledgement body patterns in `post_thread_replies`

**Notes:** Skill **1.2.1**. Parent `pr-review-handler.mdc` updated.

## 2026-08-07 — PR respond: discussion quote-reply (no bare main-node)

**Context:** Agents still answered `@heyeddi-ci` Conversation comments as bare top-level `gh pr comment` posts (main Conversation node), not nested under the parent and without quoting it.

**Decision:**
- Inline / review-thread: `/pulls/<N>/comments/<ID>/replies` only
- Discussion IssueComments: no public nest API → **quote-reply** (`> parent snippet` + answer); refuse bare `@bot` posts
- If inline `/replies` fails → same quote-reply fallback
- Fix routing: tracking `type=discussion` wins even when the id is numeric (IssueComment databaseId)
- `post_thread_replies` injects the quote from `pr-<N>-comments.json` when the draft omits it
- Live verify only requires `in_reply_to_id` for explicit `inline` rows

**Process:** draft → `post_thread_replies` → `verify_response --check [--live]` → optional Summary last.

**Notes:** Skill **1.3.0**. Parent `pr-review-handler.mdc` hard gate updated.

## 2026-08-09 — Recreated HeyEddi CI skill pack (symlink-safe)

**Context:** `heyeddi-ci-guide`, `heyeddi-ci-respond`, `heyeddi-ci-fails`, `heyeddi-ci-runners` were wiped by a checkout. `plugins/heyeddi-skills/skills` is a symlink to `../../skills`.

**Process:** Write only under `skills/<name>/`. Copy into `plugins/heyeddi-ci-skills/skills/` with `cp -a` (real dirs). Never `rm -rf` via the heyeddi-skills symlink path. CI respond uses `pr-{n}-ci-*` artifact names; ephemeral PR scratch is gitignored via project-engineering scaffold snippet.


## 2026-08-09 — HeyEddi CI skill pack + ephemeral PR scratch

**Context:** CI-only agent skills for config, responding to HeyEddi findings, Check failures, runners placeholder, and guide. Orphan `.heyeddi/docs/pr-*` files after merge.

**Decision:**
- Ship `@heyeddi-ci-config|guide|respond|fails|runners` in hub + marketplace plugin `heyeddi-ci-skills`
- Runners skill is PLACEHOLDER (fail-closed; never claim jobs ran)
- Feedback: debate + support@ only (no FP API)
- PR artifacts (`pr-*-{tracking,replies,posted,comments,context,review,ci-*}`) are ephemeral — never commit; gitignore via project-engineering scaffold
- `plugins/heyeddi-skills/skills` is a symlink to `../../skills` — never `rm -rf` through it

**Process:** Author under `skills/<name>/`; `cp -a` into `plugins/heyeddi-ci-skills/skills/`. Living contract via `load_policy_contract`. Merge only with **authorize merge**.

**Notes:** Hub **v3.2.0**. Docs: `docs/ci-skills.md`.

## 2026-08-09 — Packs: heyeddi-skills + heyeddi-ci-skills from one hub

**Context:** Brand the hub as **heyeddi-skills**; ship CI as a separate pack/plugin without a second skill monorepo. Legacy `plugins/heyeddi-skills/skills → ../../skills` whole-dir symlink made `rm -rf` delete SSOT.

**Decision:**
- SSOT: `skills/<name>/` only
- Packs: `packs/heyeddi-skills.json` (full), `packs/heyeddi-ci-skills.json` (CI subset)
- Sync: `./scripts/sync-plugins.sh` → per-skill symlinks (default) or `--copy`
- Marketplace lists both plugins; landing `heyeddi-ci-skills/` is install docs only
- Optional later: rename GitHub repo `skills` → `heyeddi-skills`

**Process:** Edit pack JSON when adding skills → `sync-plugins.sh` → commit plugin link/copy updates as needed.

## 2026-08-09 — GitHub CI releases both packs (no repo rename)

**Context:** Keep GitHub repo `HeyEddi-com/skills`. Publish **heyeddi-skills** + **heyeddi-ci-skills** on each hub version tag.

**Decision:**
- `ci.yml`: sync-plugins + registry↔pack consistency before pytest
- `release.yml`: sync-plugins; require full pack version == registry; create `vX.Y.Z` with notes from `write-release-notes.py` and attach both pack JSON assets
- No GitHub rename

**Process:** Bump `skills-registry.json` + `packs/heyeddi-skills.json` (and CI pack version when needed) in PR → merge main → Release workflow.

## 2026-08-09 — Dual public repos for skills.sh (v3.3.0)

**Context:** skills.sh indexes GitHub repos 1:1. Branding packs as heyeddi-skills / heyeddi-ci-skills inside one `skills` repo left a single skills.sh page.

**Decision:**
- Rename GitHub `HeyEddi-com/skills` → `HeyEddi-com/heyeddi-skills` (redirects keep old URL)
- Publish CI pack mirror `HeyEddi-com/heyeddi-ci-skills` via `scripts/publish-ci-pack-repo.sh`
- SSOT remains the hub `skills/<name>/`; CI repo is mirror only
- App CTAs install `heyeddi-ci-skills`; orchestrator update checks hub `heyeddi-skills`
- `inspect_repo` accepts heyeddi-skills, heyeddi-ci-skills, and legacy `skills` lock pins
- Release workflow syncs CI mirror when `CI_PACK_PUSH_TOKEN` / cross-repo token available

**Process:** Bump hub + CI pack versions → sync-plugins → merge → Release tags hub → publish-ci-pack-repo pushes mirror.

**Install:**
```bash
npx skills add HeyEddi-com/heyeddi-skills -a cursor -y --skill '*'
npx skills add HeyEddi-com/heyeddi-ci-skills -a cursor -y --skill '*'
```

## 2026-08-09 — Monorepo only (no CI skills.sh mirror)

**Context:** Dual GitHub repos for skills.sh conflicted with the agreed monorepo model (one hub, two Marketplace packs).

**Decision:**
- Single public hub: `HeyEddi-com/heyeddi-skills` (local folder may stay `skills`)
- Packs `heyeddi-skills` + `heyeddi-ci-skills` are plugins/manifests inside the hub — **not** a second GitHub skill tree
- Remove `publish-ci-pack-repo.sh` / `CI_PACK_PUSH_TOKEN` / mirror sync
- Archive `HeyEddi-com/heyeddi-ci-skills` if it was created as a publish mirror
- CI install: selective `--skill heyeddi-ci-*` from the hub, or Marketplace plugin **heyeddi-ci-skills**

**Process:** Author under `skills/<name>/` → `sync-plugins.sh` → release attaches both pack JSON assets.
