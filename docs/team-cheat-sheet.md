# Team Cheat Sheet — HeyEddi Skills

**Date:** 2026-07-02  
**Audience:** Designer, QA, engineering

Quick reference for which `@skill` to use. Guardrails run automatically — no action needed.

---

## Designer + frontend developer

`@heyeddi-handoff` is not paint-by-numbers. The agent resolves **layout** and **component architecture**:

- Reuse existing `design.md` / `@/components/` catalog?
- PrimeVue primitive sufficient (`Card`, `InputText`, …)?
- Thin wrapper for repeated patterns?
- Custom Vue component when PrimeVue doesn't fit?

Document **Component strategy** in the Decision log for each handoff.

| I want to… | Skill | How to invoke |
|------------|-------|---------------|
| Explore a vague idea ("enterprise view", new screen) | `heyeddi-design` | Plain language or `@heyeddi-design shape` |
| Set up product + design context | `heyeddi-design` | `@heyeddi-design init` |
| Plan before pixels (Q&A, research, wireframes) | `heyeddi-design` | `@heyeddi-design shape` + brief |
| Design a new screen from confirmed brief | `heyeddi-design` | `@heyeddi-design craft` + feature/route |
| Create or refresh DESIGN.md | `heyeddi-design` | `@heyeddi-design document` |
| Implement from screenshots | `heyeddi-handoff` | `@heyeddi-handoff` + route, attachments, notes |
| Refine spacing and hierarchy on existing UI | `heyeddi-design` | `@heyeddi-design polish` + route |
| Check mobile/desktop looks right | `visual-auditor` | `@visual-auditor` + route |
| Spread a golden page across the app | `design-system-generalizer` | `@design-system-generalizer` + golden route |

**Vague brief example (no design jargon):**

```
I want an enterprise view for our admin settings
```

Agent should discover → research trends → show concept directions → wireframes → brief → craft after you confirm.

**Designer inputs for handoff (mockups already exist):**

```
@heyeddi-handoff
Route: /settings
Attachments: desktop.png, mobile.png
Notes: reuse SettingsSection; empty state on mobile
```

Place reference images in `designs/<feature>/` or attach in chat.

---

## QA

| I want to… | Skill | How to invoke |
|------------|-------|---------------|
| **Review a submitted PR** (inline findings on the committed diff) | `heyeddi-pr-review` | `@heyeddi-pr-review` + PR number |
| Approve a PR (CI pass/fail report) | `pre-merge-gate` | `@pre-merge-gate` |
| **Respond to PR review comments** (fix vs decline, re-gate) | `heyeddi-pr-respond` | `@heyeddi-pr-respond` + PR number |
| Verify production build | `verify-build` | `@verify-build` or automatic in CI context |
| Visual regression on a route | `visual-auditor` | `@visual-auditor` + route |
| Find duplicate UI components | `no-duplicate-ui` | `@no-duplicate-ui` |

**Two PR workflows:** See [pr-workflows.md](./pr-workflows.md) — `@heyeddi-pr-review` (reviewer) vs `@heyeddi-pr-respond` (author responding).

**PR review vs `/babysit`:** Use built-in `/babysit` for quick merge-ready loops. Use `@heyeddi-pr-respond` when you need team rules: reply to every comment, fix-vs-decline matrix, threaded inline replies.

---

## Engineering (automatic guardrails)

These skills auto-invoke when editing matching files — no `@` needed:

| Skill | Triggers on |
|-------|-------------|
| `primevue-openprops-architect` | `**/*.vue`, `**/*.css`, `**/*.scss` |
| `verify-build` | `package.json`, Vue/TS changes in CI context |
| `no-duplicate-ui` | `**/*.vue` (PR context) |
| `backend-type-bridger` | composables, API files, `openapi.json` |
| `composable-patterns` | `**/composables/**`, `use*.ts` |

---

## Cloud Run agent

Same skills and `manifest.json` tools work in the Cloud Run agent (Pydantic AI / LangChain). Register with:

```bash
python3 scripts/cloud/register_tools.py .
```

Requires `GH_TOKEN` for `heyeddi-pr-respond`, `ARTIFACT_BUCKET` for `visual-auditor` screenshots in cloud.

---

## Related docs

- [skills-roadmap.md](./skills-roadmap.md) — full build plan
- [cloud-agent-integration.md](./cloud-agent-integration.md) — tool wiring
- [skill-guides.md](./skill-guides.md) — triad architecture
