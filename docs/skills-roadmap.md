# Skills Roadmap

**Date:** 2026-07-02  
**Status:** Phase 0 - 5 scaffolded (2026-07-02) - skills in `skills/`, install via `install-skills.sh` or `npx skills add`.  
**Audience:** HeyEddi team (Designer, QA, engineering) + Cloud Run agent (Pydantic AI / LangChain)

This document is the master plan to build, distribute, and operate the HeyEddi skill library. Every skill must work in **two runtimes**:

| Runtime | How skills load | How scripts run |
|---------|-----------------|-----------------|
| **Cursor** (consumer project) | Installed `.agents/skills/<name>/` or `~/.cursor/skills/<name>/` | Agent runs `scripts/*` in the app workspace |
| **Hub** (this repo) | `skills/<name>/` - authoring + subtree source | Same scripts; not auto-loaded until installed |
| **Cloud Run agent** (Pydantic AI + LangChain) | Skill registry loads `SKILL.md` + `context/` into agent context | `manifest.json` tools mapped to Pydantic AI / LangChain callables that invoke the same scripts |

---

## Design principles (all skills)

1. **Triad structure** - every skill ships `manifest.json`, `context/`, `scripts/` (see [skill-guides.md](./skill-guides.md)).
2. **Scripts return text** - never crash silently; stdout/stderr become agent feedback.
3. **Idempotent** - safe to re-run (especially in PR fix loops).
4. **Read vs write** - separate audit tools from mutating tools in `manifest.json`.
5. **Input adapters** - handoff and audit skills accept multiple input sources via a normalized brief (screenshots now, Penpot later).
6. **Explicit vs auto** - document invocation mode in each skill's frontmatter (`disable-model-invocation`).

### Standard skill directory

```
<skill-name>/
├── SKILL.md              # Cursor + cloud: instructions + YAML frontmatter
├── manifest.json         # Cloud agent: flat tool schemas
├── context/
│   ├── VOCABULARY.md     # Do this
│   ├── ANTI_PATTERNS.md  # Never do this
│   └── EXAMPLES.md       # Before/after
├── reference/            # Optional deep docs (modes, sub-commands)
└── scripts/
    ├── *.py              # Prefer Python for Cloud Run parity
    └── *.sh / *.mjs      # OK when wrapped or duplicated for cloud
```

### Cloud Run compatibility contract

Each `manifest.json` tool entry:

```json
{
  "name": "run_visual_audit",
  "description": "Capture responsive screenshots of a route and return paths or layout JSON.",
  "parameters": {
    "type": "object",
    "properties": {
      "route": { "type": "string", "description": "App route e.g. /settings" },
      "widths": { "type": "array", "items": { "type": "integer" }, "description": "Viewport widths" },
      "project_root": { "type": "string", "description": "Workspace root" }
    },
    "required": ["route", "project_root"]
  },
  "script": "scripts/audit_ui.py",
  "readonly": true
}
```

**Pydantic AI:** register each manifest tool as a `@agent.tool` that shells to the script (or calls shared Python module). Parse exit code; return combined stdout/stderr as `str`.

**LangChain:** wrap the same script invoker as `StructuredTool.from_function` with the manifest schema.

**Cloud Run constraints:**

| Concern | Approach |
|---------|----------|
| No local display | Playwright headless; artifacts to `/tmp` or GCS bucket via `ARTIFACT_BUCKET` env |
| Ephemeral filesystem | Clone repo or mount workspace volume; pass `project_root` on every tool call |
| Secrets | JWT/Firebase creds via Secret Manager - never in skill repos |
| Cold start | Keep scripts lean; heavy deps (Playwright) in container image, not per-invoke install |
| Skill discovery | Hub publishes `skills-registry.json`; cloud agent loads enabled skills at boot |

**Future (Phase 0 deliverable):** `scripts/cloud/register_tools.py` - reads all `manifest.json` files and emits Pydantic AI tool definitions (shared invoker).

---

## Skill inventory

| Skill | Phase | Invocation | Primary user | Replaces / complements |
|-------|-------|------------|--------------|------------------------|
| `project-engineering` | 1 | Auto | Everyone | npm/Vite/Vitest scaffold + tests |
| `primevue-openprops-architect` | 1 | Auto | Everyone | Guardrails during any Vue work |
| `verify-build` | 1 | Auto / explicit | QA, CI loop | Vite static build gate |
| `visual-auditor` | 2 | Explicit | Designer, QA | Impeccable `audit`; Cursor preview pane |
| `heyeddi-handoff` | 2 | Explicit | Designer | Figma MCP (deferred); screenshot-first |
| `heyeddi-design` | 5 | Explicit | Designer | **Replaces impeccable** |
| `pre-merge-gate` | 3 | Pipeline | Agent, QA | Manual merge checklist |
| `heyeddi-pr-respond` | 3 | Pipeline | Agent, QA | Built-in `/babysit` (stricter, team rules) |
| `design-system-generalizer` | 4 | Explicit | Designer, architect | Spread golden pages app-wide |
| `no-duplicate-ui` | 4 | Auto (narrow) | Engineering | DRY / architecture enforcement |
| `backend-type-bridger` | 4 | Auto (narrow) | AI during FE work | Guessed API shapes |
| `composable-patterns` | 4 | Auto (narrow) | AI | FastAPI JWT + Firebase client consistency |
| `heyeddi-intake` | 0 | Explicit | PM, architect | Upstream intake - personas, routing, mockups |
| `heyeddi-orchestrator` | 0 | Auto | Everyone | Discover and suggest @skills from catalog |
| `engineering-excellence` | 4 | Explicit | Engineering | KISS/YAGNI/DRY/SOLID audits + ADRs |
| `ux-flow-auditor` | 4 | Explicit | Designer, QA | Task flow traces - click depth, friction |
| `flutter-engineering` | 1 | Auto | Mobile | Flutter + FastAPI/Firebase scaffold |
| `flutter-patterns` | 4 | Auto (narrow) | Mobile AI | Riverpod repository patterns |
| `dart-type-bridger` | 4 | Auto (narrow) | Mobile AI | OpenAPI / Firestore → Dart models |
| `design-handoff-flutter` | 2 | Explicit | Mobile designer | Screenshot-first Material 3 Flutter |

---

## Phase 0 - Foundation (week 1)

**Goal:** One skill template and cloud wiring so every later skill is born compatible.

### Tasks

- [ ] **(Software Architect)** Extend `templates/skill/` with `manifest.json`, `context/` stubs, `scripts/` README.
- [ ] **(JAMStack Developer)** Add `docs/cloud-agent-integration.md` - env vars, tool registration pattern, artifact storage.
- [ ] **(JAMStack Developer)** `scripts/cloud/register_tools.py` - manifest → tool list prototype.
- [ ] **(JAMStack Developer)** Define normalized handoff brief schema (`reference/handoff-brief.schema.json`).
- [ ] **(Product Manager)** Require `DESIGN.md` + `PRODUCT.md` in app repos (consumed by design skills).
- [ ] **(Technical Writer)** Designer + QA cheat sheet (which `@skill` for which task).

### Acceptance criteria

- Scaffold one skill with `./scripts/new-skill.sh` and get triad layout.
- Cloud agent can register and invoke a no-op test tool from `manifest.json`.
- Handoff brief schema validates screenshot-based input.

---

## Phase 1 - Guardrails (weeks 2 - 3)

**Goal:** Stop bad frontend code before it reaches PR.

### 1. `primevue-openprops-architect`

**Purpose:** Enforce PrimeVue + OpenProps + centralized design system. Block hallucinated props and raw CSS.

| Layer | Contents |
|-------|----------|
| `context/VOCABULARY.md` | Approved OpenProps tokens, PrimeVue components in use |
| `context/ANTI_PATTERNS.md` | Inline styles, hex colors, duplicate Button wrappers |
| `context/EXAMPLES.md` | Good vs bad Vue SFC snippets |
| `scripts/validate_vue.py` | `vue-tsc --noEmit` + stylelint; return warnings as text |
| `manifest.json` | `validate_vue` (readonly) |

**Cursor:** `disable-model-invocation` omitted - auto when editing `**/*.vue`, `**/*.css`.

**Cloud:** Run validator against cloned workspace; same script.

### 2. `verify-build`

**Purpose:** Catch Vite/Rollup failures before merge.

| Layer | Contents |
|-------|----------|
| `scripts/verify_build.sh` | `npm run build`; pipe errors to stdout |
| `manifest.json` | `verify_build` (readonly) |

**Depends on:** Node in cloud container image.

### Acceptance criteria

- AI-generated Vue with hardcoded `#fff` fails validation with readable output.
- Broken import fails `verify_build` with Rollup stack trace.
- Both tools callable from Cursor and Cloud Run agent.

---

## Phase 2 - Design loop (weeks 4 - 6)

**Goal:** Unblock Designer with screenshots; prove UI visually.

### 3. `visual-auditor`

**Purpose:** Headless responsive screenshots + optional compare to reference image.

| Layer | Contents |
|-------|----------|
| `context/VISUAL_HIERARCHY.md` | Spacing, alignment, density expectations |
| `scripts/audit_ui.py` | Playwright: load dev URL, widths 375/768/1440, save artifacts |
| `scripts/layout_tree.py` | Fallback: computed dimensions JSON when no vision model |
| `manifest.json` | `capture_screenshots`, `extract_layout` (readonly) |

**Env:** `DEV_SERVER_URL` (default `http://localhost:5173`), `ARTIFACT_BUCKET` (cloud).

**Cursor:** `disable-model-invocation: true` - Designer calls `@visual-auditor`.

**Cloud:** Upload screenshots to GCS; return signed URLs in tool response.

### 4. `heyeddi-handoff` (v1 - screenshot mode)

**Purpose:** Implement screens from designer screenshots without Figma MCP.

| Layer | Contents |
|-------|----------|
| `SKILL.md` | Input-agnostic workflow |
| `reference/screenshot-mode.md` | v1: attachments + `designs/<feature>/` folder |
| `reference/penpot-mode.md` | Stub for Phase 6 |
| `scripts/load_handoff.py` | Resolve inputs → normalized handoff brief |
| `manifest.json` | `load_handoff` (readonly) |

**Workflow:**

1. Load `DESIGN.md` + component catalog.
2. `load_handoff` - screenshots + optional `handoff.json` → brief.
3. Map regions → existing PrimeVue components.
4. Implement (agent code gen).
5. Chain `primevue-openprops-architect` → `visual-auditor` → compare to reference.

**Designer input:**

```
@heyeddi-handoff
Route: /settings
Attachments: desktop.png, mobile.png
Notes: reuse SettingsSection; empty state on mobile
```

### Acceptance criteria

- Designer completes handoff without writing code.
- Implemented route passes visual-auditor compare against reference PNG.
- `load_handoff` output identical whether run in Cursor or Cloud Run.

---

## Phase 3 - Team workflow (weeks 7 - 8)

**Goal:** QA and PR loop skills for non-coders.

### 5. `pre-merge-gate`

**Purpose:** Single green/red report before PR approval.

| Check | Script |
|-------|--------|
| Unit/integration tests | project test command |
| Build | `verify-build` |
| Types | `vue-tsc` |
| UI changed? | optional `visual-auditor` on changed routes |
| Duplicates | optional `no-duplicate-ui` scan |

| Layer | Contents |
|-------|----------|
| `scripts/pre_merge_gate.py` | Orchestrate checks; markdown report |
| `manifest.json` | `run_pre_merge_gate` (readonly) |

**Cursor / Cloud:** the agent runs `@pre-merge-gate` itself as part of the ship pipeline; QA can run it too.

### 6. `heyeddi-pr-respond`

**Purpose:** Team PR review loop (stricter than built-in `/babysit`).

| Layer | Contents |
|-------|----------|
| `context/RESPONSE_TEMPLATES.md` | Fix / decline / partial / out-of-scope |
| `reference/workflow.md` | Fetch all comment types, thread replies, tracking table |
| `scripts/fetch_pr_comments.py` | `gh api` wrapper; flat JSON for agent |
| `manifest.json` | `fetch_pr_comments` (readonly); fix steps remain agent-driven |

**Note:** `/babysit` is a built-in Cursor shortcut for merge-ready loops. This skill encodes **your** rules: reply to every comment, fix-vs-decline matrix, summary comment.

**Cloud:** Requires `GH_TOKEN` in Secret Manager; same `gh` CLI or GitHub API client.

### Acceptance criteria

- QA gets pass/fail markdown from `pre-merge-gate` without reading raw logs.
- PR skill fetches inline + review + discussion comments in one call.
- Documented when to use `@heyeddi-pr-respond` vs Cursor `/babysit`.

---

## Phase 4 - Architecture (weeks 9 - 11)

**Goal:** Scale quality across the app; tighten backend ↔ frontend contract.

### 7. `design-system-generalizer`

**Purpose:** Extract patterns from a “golden” page; migrate violations elsewhere.

| Layer | Contents |
|-------|----------|
| `scripts/scan_patterns.py` | Token/component usage scan |
| `scripts/diff_violations.py` | Compare routes against golden reference |
| `manifest.json` | `scan_patterns`, `diff_violations` (readonly) |

**Rule:** Propose PR-sized chunks - never whole-app rewrite in one shot.

### 8. `no-duplicate-ui`

**Purpose:** Detect forked components and copy-pasted templates.

| Layer | Contents |
|-------|----------|
| `scripts/find_duplicate_ui.py` | Similar filenames, template overlap |
| `manifest.json` | `find_duplicate_ui` (readonly) |

**Cursor:** narrow auto on `**/*.vue` in PR context.

### 9. `backend-type-bridger`

**Purpose:** Stop frontend from guessing API shapes.

| Layer | Contents |
|-------|----------|
| `scripts/sync_openapi.py` | FastAPI `openapi.json` → `types.ts` |
| `scripts/fetch_firestore_schema.py` | Rules / schema file → TS types |
| `manifest.json` | `sync_openapi`, `fetch_firestore_schema` |

**Detection:** `openapi.json` vs `firebase.json` in project root.

### 10. `composable-patterns`

**Purpose:** Consistent auth/data layer for FastAPI JWT vs Firebase.

| Layer | Contents |
|-------|----------|
| `context/fastapi-jwt.md` | Composables, interceptors, error handling |
| `context/firebase-client.md` | Rules-aware reads, security patterns |
| No heavy scripts - context-only skill; optional `validate_composable.py` later |

### Acceptance criteria

- Generalizer produces a violation report for ≥1 golden vs non-golden route pair.
- `sync_openapi` updates types consumed by Vue composables.
- Duplicate scan flags known test fixtures in a sample repo.

---

## Phase 5 - Replace impeccable (weeks 12 - 14)

**Goal:** Retire `~/.cursor/skills/impeccable` with stack-specific craft skill.

### 11. `heyeddi-design`

**Purpose:** Design from scratch within OpenProps + PrimeVue + `DESIGN.md`.

| Sub-command | Reference file | Replaces impeccable |
|-------------|----------------|---------------------|
| `craft` | `reference/craft.md` | New screen from brief |
| `shape` | `reference/shape.md` | IA / layout exploration |
| `polish` | `reference/polish.md` | Refine existing screen |
| `audit` | Delegates to `visual-auditor` | Visual proof |

| Layer | Contents |
|-------|----------|
| `scripts/load_context.py` | `PRODUCT.md` + `DESIGN.md` loader (like impeccable `context.mjs`) |
| `manifest.json` | `load_design_context` (readonly) |

**Cursor:** `disable-model-invocation: true` - explicit `@heyeddi-design craft`.

**Migration:** Remove impeccable after Designer signs off on craft + handoff + audit flows.

### Acceptance criteria

- Designer produces new screen from brief without impeccable installed.
- All new UI passes `primevue-openprops-architect` validation.
- Cloud agent can run `load_design_context` against repo in GCS/workspace mount.

---

## Future plans

### Phase 6 - Penpot integration (Q3 2026+)

| Version | Input | Work |
|---------|-------|------|
| **v2** | Penpot PNG/SVG export | `load_handoff.py` accepts `designs/*.svg` + `handoff.json` |
| **v3** | Penpot REST API | Fetch frames/export without MCP |
| **v4** | **Penpot MCP** (custom) | New skill or `heyeddi-handoff` adapter: live tokens, components, spacing |

**Do not rebuild Figma MCP.** Penpot is open-source - MCP can live in a separate repo (`heyeddi/penpot-mcp`) and plug into `heyeddi-handoff` via `reference/penpot-mode.md` + manifest tool `fetch_penpot_frame`.

### Phase 7 - Cloud agent skill orchestration

- [ ] `delegate_to_skill()` - child runs per `reference/subagents.md` (see [subagent-delegation.md](./subagent-delegation.md))
- [ ] Skill router in Pydantic AI: match user intent → skill `description` fields (same as Cursor Agent Decides).
- [ ] LangChain fallback chain for tool-heavy steps.
- [ ] Skill enablement per tenant/project in Cloud Run config.
- [ ] Telemetry: which skills invoked, pass/fail rates on gates.

### Phase 8 - Distribution

- [ ] Each skill → standalone GitHub repo via subtree push.
- [ ] `npx skills add heyeddi/<skill-name>` for external teams.
- [ ] Optional Cursor plugin bundle (`heyeddi-team-kit`) for marketplace - skills + rules, no MCP required initially.

### Deferred / use builtins

| Item | Decision |
|------|----------|
| Figma MCP | Skip - screenshots + Penpot path instead |
| `/babysit` | Use for quick PR loops; `heyeddi-pr-respond` for team rules |
| `/review-security` | Use builtin unless stack-specific rules needed |
| Generic impeccable | Retire after Phase 5 |

---

## Trigger strategy summary

| Skill | Cursor mode | Cloud agent |
|-------|-------------|-------------|
| `primevue-openprops-architect` | Auto | Router auto on Vue/CSS paths |
| `verify-build` | Auto in CI context | Explicit or CI webhook |
| `visual-auditor` | Explicit | Explicit |
| `heyeddi-handoff` | Explicit | Explicit |
| `heyeddi-design` | Explicit | Explicit |
| `pre-merge-gate` | Pipeline (agent runs it) | Pipeline (QA webhook too) |
| `heyeddi-pr-respond` | Pipeline (agent runs it) | Pipeline |
| `design-system-generalizer` | Explicit | Explicit |
| `no-duplicate-ui` | Auto (narrow) | Auto on PR diff |
| `backend-type-bridger` | Auto (narrow) | Auto when API files touched |
| `composable-patterns` | Auto (narrow) | Auto when composables touched |

**Installing all skills does not run them all.** Metadata is discovered; full skill loads on relevance or explicit `@` / `/` invoke. Keep descriptions **narrow** to avoid wrong-skill collisions.

---

## Build order (single timeline)

```
Phase 0  Foundation + cloud contract
    ↓
Phase 1  primevue-openprops-architect, verify-build
    ↓
Phase 2  visual-auditor, heyeddi-handoff (screenshot v1)
    ↓
Phase 3  pre-merge-gate, heyeddi-pr-respond
    ↓
Phase 4  design-system-generalizer, no-duplicate-ui, backend-type-bridger, composable-patterns
    ↓
Phase 5  heyeddi-design → retire impeccable
    ↓
Phase 6+ Penpot export → API → MCP
```

---

## Per-skill publish checklist

When a skill exits a phase:

1. [ ] `SKILL.md` frontmatter: `name`, `description`, invocation mode
2. [ ] `manifest.json` with flat schemas + `readonly` flags
3. [ ] Scripts runnable CLI: `python scripts/foo.py --help`
4. [ ] Tested in Cursor (`@skill-name`)
5. [ ] Tested in Cloud Run agent via `register_tools.py`
6. [ ] `README.md` in standalone repo (install: `npx skills add heyeddi/<name>`)
7. [ ] Entry in `skills-registry.json`
8. [ ] `./scripts/push-skill-subtree.sh <name> <remote>`

---

## Team cheat sheet (target)

| I want to… | Skill |
|------------|-------|
| Implement from screenshots | `@heyeddi-handoff` |
| Design a new screen from scratch | `@heyeddi-design craft` |
| Explore vague UI intent (research + wireframes) | `@heyeddi-design shape` or plain language |
| Check mobile/desktop looks right | `@visual-auditor` |
| Approve a PR | `@pre-merge-gate` |
| Fix AI PR review comments | `@heyeddi-pr-respond` |
| Spread a good page across the app | `@design-system-generalizer` |

Guardrails (`primevue-openprops-architect`, etc.) run automatically - no action needed.

---

## Related docs

- [skill-guides.md](./skill-guides.md) - triad architecture and stack blueprints
- [distribution.md](./distribution.md) - git subtree publish workflow
- [cloud-agent-integration.md](./cloud-agent-integration.md) - Pydantic AI / LangChain wiring (Phase 0)
