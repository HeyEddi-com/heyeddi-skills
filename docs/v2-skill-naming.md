# v2 skill naming — `heyeddi-*` spine + aliases

**Date:** 2026-07-07  
**Status:** Historical ADR — v2 implemented 2026-07-07; **aliases removed in v3.0.0** (2026-07-14)  
**Target release:** v2.0.0  
**Current release:** v3.0.0 (22 skills; no v1 alias folders or alias map)

## Goal

Brand the **main user-facing workflows** with a `heyeddi-*` prefix so they are easy to discover in `@` autocomplete and distinguish from generic marketplace skills. Keep **guardrails and stack adapters** on descriptive names.

**Non-goals for v2 naming:**

- Renaming all 22 skills
- Breaking v1 `@` invocations without a deprecation window
- Splitting the monorepo into 22 separate skills.sh repos (optional later)

## Naming policy (going forward)

| Category | Pattern | Examples | Auto-invoke? |
|----------|---------|----------|--------------|
| **Spine / orchestrator** | `heyeddi-*` | `heyeddi-intake`, `heyeddi-orchestrator` | No — explicit `@` |
| **Design craft** | `heyeddi-*` | `heyeddi-design`, `heyeddi-handoff` | No |
| **PR / ship** | `heyeddi-*` | `heyeddi-pr-review`, `heyeddi-ship-gate` | No |
| **Audit / delegate** | descriptive | `engineering-excellence`, `visual-auditor` | Sometimes |
| **Stack guardrail** | descriptive + stack | `verify-build`, `composable-patterns`, `primevue-openprops-architect` | Yes — file patterns |

**Rule:** New **pipeline entrypoints** and **multi-step orchestrators** get `heyeddi-*`. New **file-triggered guardrails** stay descriptive.

---

## v2 rename table (spine only — 8 skills)

| v1 name (current) | v2 canonical name | Rationale |
|-------------------|-------------------|-----------|
| `heyeddi-intake` | **`heyeddi-intake`** | Greenfield entry — prompt → product + routing |
| `heyeddi-product` | **`heyeddi-product`** | PM orchestrator — stories, AC, review plans |
| `heyeddi-orchestrator` | **`heyeddi-orchestrator`** | Catalog, suggest, cross-pillar sync |
| `heyeddi-design` | **`heyeddi-design`** | *(unchanged — already branded)* |
| `heyeddi-handoff` | **`heyeddi-handoff`** | Pairs with design; screenshot-first Vue |
| `design-handoff-flutter` | **`heyeddi-handoff-flutter`** | Optional — keeps Flutter variant obvious |
| `heyeddi-pr-review` | **`heyeddi-pr-review`** | Reviewer workflow — committed diff |
| `heyeddi-pr-respond` | **`heyeddi-pr-respond`** | Author workflow — reply to comments |
| `pre-merge-gate` | **`heyeddi-ship-gate`** | Optional rename — “ship” matches cheat sheet |

### Unchanged (14 skills)

```
backend-type-bridger      composable-patterns       dart-type-bridger
design-system-generalizer engineering-excellence    flutter-engineering
flutter-patterns          no-duplicate-ui           primevue-openprops-architect
project-engineering       ux-flow-auditor           verify-build
visual-auditor
```

*(Count: 8 renames if both handoff-flutter + ship-gate included; 6 if flutter handoff and ship-gate stay as-is.)*

### Recommended minimal spine (6 renames)

If you want the smallest breaking surface for v2.0.0:

1. `heyeddi-intake` → `heyeddi-intake`
2. `heyeddi-product` → `heyeddi-product`
3. `heyeddi-orchestrator` → `heyeddi-orchestrator`
4. `heyeddi-handoff` → `heyeddi-handoff`
5. `heyeddi-pr-review` → `heyeddi-pr-review`
6. `heyeddi-pr-respond` → `heyeddi-pr-respond`

Defer: `pre-merge-gate`, `design-handoff-flutter` (rename in v2.1 if needed).

---

## Alias strategy (one major release deprecation)

### Phase A — v2.0.0 (dual names, no user pain)

For each renamed skill, ship **two installable folders** in the hub:

```
skills/
├── heyeddi-intake/          # canonical — full triad
├── heyeddi-intake/      # alias stub — thin wrapper only
│   ├── SKILL.md             # frontmatter name: heyeddi-intake
│   │                        # body: "Deprecated — use @heyeddi-intake"
│   └── manifest.json        # re-exports same tools OR points to canonical scripts
```

**Option 1 (preferred): symlink scripts + shared context**

- Alias folder: `SKILL.md` + `manifest.json` only
- `scripts/` → symlink to `../heyeddi-intake/scripts/`
- `context/` → symlink or `DEPRECATED.md` + link

**Option 2: orchestrator-only alias**

- Alias folder: SKILL.md only (no manifest tools)
- Description: "Use @heyeddi-intake — this name is deprecated"
- Agent reads canonical SKILL.md when alias is invoked

**Option 3: git mv + symlink entire folder**

- `git mv skills/heyeddi-intake skills/heyeddi-intake`
- `ln -s heyeddi-intake skills/heyeddi-intake`

Option 3 is simplest for hub maintenance; `npx skills add --skill heyeddi-intake` still works.

### Phase B — v2.x catalog aliases (machine-readable)

Extend `skills-registry.json`:

```json
{
  "skills": [
    { "name": "heyeddi-intake", "description": "..." }
  ],
  "aliases": {
    "heyeddi-intake": "heyeddi-intake",
    "heyeddi-product": "heyeddi-product",
    "heyeddi-orchestrator": "heyeddi-orchestrator",
    "heyeddi-handoff": "heyeddi-handoff",
    "heyeddi-pr-review": "heyeddi-pr-review",
    "heyeddi-pr-respond": "heyeddi-pr-respond",
    "pre-merge-gate": "heyeddi-ship-gate"
  }
}
```

Update `@heyeddi-orchestrator`:

| File | Change |
|------|--------|
| `scripts/_catalog.py` | Resolve alias → canonical before scoring; emit `"alias_of"` in suggestions |
| `scripts/write_skills_index.py` | Index both names; mark aliases `deprecated: true` |
| `reference/triggers.md` | Duplicate triggers for alias tokens ("product translator" → both names) |

### Phase C — consumer project artifacts

Generated JSON in app repos must migrate or dual-read:

| Artifact | Field | Migration |
|----------|-------|-----------|
| `.heyeddi/docs/intake/skill-routing.json` | `"skill": "heyeddi-handoff"` | `build_routing.py` writes v2 names; add `migrate_routing.py` for brownfield |
| `.heyeddi/docs/intake/skill-routing.json` | `"post_intake": ["@heyeddi-orchestrator ..."]` | String replace in migration script |
| `.heyeddi/skills-index.json` | skill keys | Regenerate via `write_skills_index --refresh` |
| `learnings.md` / team docs | `@heyeddi-product` | Search-replace in hub; consumer docs manual |

**Migration (automatic):** Any HeyEddi skill tool call auto-syncs `.heyeddi/` (v1 → v2 names, skills index). Optional: `@heyeddi-orchestrator` `sync` for full sync + workflow scaffold. Hub CLI: `scripts/migrate-skill-names-v2.py` (delegates to skill).

### Phase D — v3.0.0 (remove aliases) — **DONE 2026-07-14**

- [x] Remove alias stub folders from hub (`product-translator`, `product-manager`, `skill-orchestrator`, `design-handoff`, `pr-submission-review`, `pr-review-responder`)
- [x] Remove alias keys / `skill-name-aliases.json` / migrate path / `bootstrap-skill-aliases.py`
- [x] Eval cases and docs use canonical names only
- Release note: "v1 skill names removed; use heyeddi-* spine"

---

## Implementation checklist

### Hub repo (`HeyEddi-com/heyeddi-skills`)

- [ ] Agree minimal vs full rename set (6 vs 8)
- [ ] `git mv` skill directories to canonical names
- [ ] Create symlink alias folders for v1 names
- [ ] Update every `SKILL.md` frontmatter `name:` to match folder
- [ ] Update `skills-registry.json` + new `aliases` block
- [ ] Update `_catalog.py`, `write_skills_index.py`, `suggest_skills`
- [ ] Update `heyeddi-intake/scripts/build_routing.py` default skill strings
- [ ] Update `reference/delegation.md` cross-skill `@` references
- [ ] Update all `docs/*.md`, `README.md`, cheat sheet, `pr-workflows.md`
- [ ] Update `plugins/heyeddi-skills` metadata (version 2.0.0)
- [ ] Update `pyproject.toml` `poe eval-*` task names (optional)
- [ ] Add `scripts/migrate-skill-names-v2.py`
- [ ] Add `tests/test_skill_aliases.py` — alias resolves to canonical, smoke both names

### Evals (16 cases)

| Case ID | Skills to update |
|---------|------------------|
| `heyeddi-intake-intake` | → `heyeddi-intake` (keep case id or rename) |
| `heyeddi-orchestrator-suggest` | → `heyeddi-orchestrator` |
| `heyeddi-handoff-only` | → `heyeddi-handoff` |
| `design-handoff-flutter-settings` | → `heyeddi-handoff-flutter` (if renamed) |
| `heyeddi-pr-review-workflow` | → `heyeddi-pr-review` |
| `heyeddi-pr-respond-workflow` | → `heyeddi-pr-respond` |
| `full-product-integration` | all spine references in prompts/judges |

Run after rename: `uv run poe eval-all` (full suite).

### Subtrees / standalone repos

Each renamed skill with a standalone GitHub repo needs:

```bash
./scripts/push-skill-subtree.sh heyeddi-intake git@github.com:HeyEddi-com/heyeddi-intake.git
```

**Decision:** Retire standalone repos for alias-only names; keep canonical repo names aligned with v2 folders.

### Cloud Run / manifest registration

- `register_tools.py` registers by folder name — aliases with symlinked scripts register duplicate tool names unless deduped
- **Recommendation:** alias stubs have **no manifest.json** (SKILL-only redirect); cloud registers canonical tools once

### Consumer install

Pinned v2 install:

```bash
npx skills add https://github.com/HeyEddi-com/heyeddi-skills/tree/v2.0.0 -a cursor -y --skill '*'
```

Both `@heyeddi-intake` and `@heyeddi-intake` work during v2.x if alias stubs ship.

---

## User-facing before / after

### Greenfield pipeline (v2)

```
@heyeddi-intake          → product.md, routing, mockups
@heyeddi-product         → specs, review plan
@heyeddi-design shape    → brief
@heyeddi-handoff         → implement from mockups
@heyeddi-ship-gate       → merge checklist
```

### PR workflows (v2)

```
@heyeddi-pr-review       → review submitted PR (reviewer)
@heyeddi-pr-respond      → address review comments (author)
```

### Autocomplete benefit

Typing `@heyeddi` surfaces the **entire spine** in one group — intake, product, orchestrator, design, handoff, PR, ship.

---

## Risk matrix

| Risk | Mitigation |
|------|------------|
| Broken `@` habits in chats / rules | Alias stubs + orchestrator maps old names |
| Eval sandboxes pin old paths | Regenerate cases; `--refresh` skills index in harness |
| `skill-routing.json` in customer repos | `migrate-skill-names-v2.py` |
| Duplicate tools in cloud agent | Alias = SKILL-only, no manifest |
| skills.sh leaderboard split | Canonical name only in analytics; document alias in README |
| Subtree push confusion | One canonical remote per skill; archive old repo with README redirect |

---

## Recommended rollout sequence

1. **v2.0.0-alpha** — rename in hub + alias symlinks + registry; docs updated; smoke tests pass both names
2. **v2.0.0-beta** — agent evals green on canonical names; migration script tested on `fixtures/sample-vue-app`
3. **v2.0.0** — GitHub release; README promotes `@heyeddi-*`; cheat sheet shows deprecated v1 names in small print
4. **v2.1–v2.x** — telemetry: log alias invocations (if harness supports); nag in alias SKILL.md
5. **v3.0.0** — remove alias folders

---

## Open decisions (need product call)

1. **Minimal (6) vs full (8) renames** — include `heyeddi-ship-gate` and `heyeddi-handoff-flutter`?
2. **Case-sensitive `@` names** — keep kebab-case (`heyeddi-pr-respond`) vs shorter (`heyeddi-pr`)?
3. **Subtree repos** — rename GitHub repos to match or keep legacy repo URLs with README redirects?
4. **Eval case IDs** — rename YAML ids (breaks CI history) or keep ids, update `skills:` list only?

**Recommendation:** Minimal 6 renames; defer ship-gate and flutter-handoff; keep eval case **ids** stable, update `skills:` arrays only.

---

## Related docs

- [pr-workflows.md](./pr-workflows.md) — will reference `heyeddi-pr-review` / `heyeddi-pr-respond` after migration
- [distribution.md](./distribution.md) — pin install tag `v2.0.0`
- [skills-roadmap.md](./skills-roadmap.md) — update inventory when implemented
- [team-cheat-sheet.md](./team-cheat-sheet.md) — spine table with v2 names + deprecated column
