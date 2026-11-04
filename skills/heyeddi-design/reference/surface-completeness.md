# Surface completeness: design the full screen

**When:** Any `discover`, `shape`, `craft`, or `critique` for a route or feature.

Agents often ship the **happy-path minimum** (two fields + button, a table with no empty state, settings with no save affordance). Users expect a **complete surface at the scope you're working on**: spacing, related actions, edge states, and a clear backlog for unwired backend work.

## Scope: what “complete” means

**Complete the unit of work, not the entire product every time.**

| You were asked to… | Completeness means… |
|--------------------|---------------------|
| **One view / route** (e.g. `/login`) | That screen is production-complete: all regions, affordances, states, spacing for *that* archetype |
| **One feature** (e.g. settings, onboarding flow) | Every screen in the feature brief: or document which routes are in/out of scope |
| **Whole product** (`init` → multiple `shape`/`craft`) | `product.md` + `design.md` north star; each feature still gets its own complete brief before craft |

**In scope:** everything a user would expect **on the screen(s) you're designing now**.  
**Out of scope:** other routes: unless the brief explicitly includes them (e.g. settings inside app shell).

Unwired backend is fine; **missing UI** for in-scope affordances is not. Record gaps in **`## Deferred wiring`**, not by omitting controls.

## Core rule

> **Design everything the user would expect on this screen. Wire what you can. Document the rest.**

| Do | Don't |
|----|--------|
| Ship UI for standard affordances (links, secondary actions, empty states) | Drop UI because "API isn't ready" |
| Stub behavior (`router-link` to placeholder, toast, disabled + tooltip) | Use "deferred" to mean "omitted" |
| Record unwired work in brief **`## Deferred wiring`** | Leave completeness implicit |
| Apply generous spacing and clear hierarchy | Ship cramped MVP layouts |

Optional backlog file: `.heyeddi/docs/<feature>-backlog.md` for engineering follow-ups.

---

## Completeness audit (every surface)

Before brief sign-off or craft, walk this list. Skip only what **product.md** explicitly waives.

### 1. Context & hierarchy
- **Page title + subtitle**: what is this screen, who is it for?
- **Primary action**: one obvious CTA; secondary actions visually subordinate
- **Wayfinding**: breadcrumbs, back, or nav context when not a standalone auth/marketing page

### 2. Content regions
- Map **every visible block** (ASCII or region table): not just the main form/table
- **Related actions** users expect on this *type* of screen (see archetypes below)
- **Help / learn more** when the task is non-obvious

### 3. States (design all in brief; implement in scope)
| State | Design for |
|-------|------------|
| Default | Typical content |
| Empty | First-time, no data |
| Loading | Skeleton or spinner; disable destructive actions |
| Error | Inline + page-level; recovery path |
| Success | Confirmation, toast, or next step |
| Validation | Field-level before submit |
| Permission denied | When roles matter |

### 4. Spacing & layout
Use project semantic scale (`--size-*` / design.md spacing tokens):

- **Container padding**: cards and panels need room to breathe (`--size-5`-`--size-6` internal)
- **Section gaps**: between title block and content, between cards (`--size-4`-`--size-6`)
- **Field stacks**: labels, inputs, helpers; verify components don't visually merge
- **CTA separation**: primary button not glued to last field (`--size-4`+ above)
- **Max-width**: constrain line length and form width on large viewports

### 5. Affordances & escape hatches
Ask: *"What else would a user look for here?"*

- Links to **recovery** (forgot password, undo, cancel)
- **Persistence** options (remember me, save draft, auto-save indicator)
- **Alternate paths** (sign up, import, skip, use demo)
- **Destructive actions**: confirm pattern, not surprise

### 6. Deferred wiring (required in brief)

```markdown
## Deferred wiring

| UI element | Shipped as | Wire later |
|------------|------------|------------|
| Forgot password link | `/forgot-password` placeholder view | Reset API + email |
| Save button | Toast "Saved" stub | PATCH `/api/settings` |
| Export CSV | Disabled button + tooltip | Export job + download URL |
```

Craft implements the **Shipped as** column. Engineering picks up **Wire later**.

---

## Surface archetypes (apply the audit)

Use these as **completeness prompts**: not separate skill files. Combine with discover Q&A.

| Archetype | Users also expect… |
|-----------|-------------------|
| **Sign-in / sign-up** | Forgot password, remember me, sign-up or invite copy, SSO row for team apps, legal footer if public |
| **Settings / profile** | Section cards, **one control per row** (label + field + helper + trailing action), 8px grid rhythm, save/discard, validation, danger zone separated. **Reject** a card that is only a multiline text dump ("text-wall"). |
| **List / index** | Search/filter, empty state, pagination or load more, row actions, create button |
| **Detail / view** | Edit, back, status badge, related links, delete with confirm |
| **Dashboard** | Shell (nav), page header, card grid, empty widgets, date range or refresh |
| **Onboarding / empty** | Clear next step, illustration or icon, single CTA, skip if optional |
| **Form (create/edit)** | Required markers, field help, cancel, submit loading, unsaved warning if long; separate nodes per field on 8px grid (same text-wall reject) |
| **Suite / multi-panel** | Each panel is real UI chrome (tabs/nav + field rows), not pasted copy blocks; hi-fi via `@taste-penpot` `hifi.html` when Penpot MCP cannot Flex |

If the surface doesn't match one row, **invent a checklist** in the brief using the audit sections above.

---

## Brief requirements (`designs/<feature>/brief.md`)

Every shape brief should include:

1. **Feature summary** + primary user action  
2. **Layout regions**: all blocks, not just core fields  
3. **Component map**: PrimeVue / catalog per region  
4. **Key states**: from audit §3  
5. **Copy**: labels, buttons, errors, helper text  
6. **`## Deferred wiring`**: table (audit §6)  
7. **Open questions**: only genuinely unresolved  

---

## Craft & critique

**Craft:** Implement every region and affordance in the brief. Add placeholder routes/views when needed. Append **Decision log** citing deferred items.

**Critique:** Flag **missing archetype affordances**, **missing states**, and **spacing violations** as P0/P1 before polish.

**Polish:** Addresses critique findings: does not invent missing regions; if IA is incomplete, recommend `shape` + brief update.

---

## Routing

| User / task | Load this file when… |
|-------------|----------------------|
| `shape`, `craft` for any route | Always (with mode-specific reference) |
| `critique` sparse existing UI | Compare against audit + archetype |
| `discover` vague "build X page" | Use archetypes to drive questions |

Auth, settings, and dashboards are **examples** of completeness thinking: not separate rule files.
