# Token strategy: follow the project

**New HeyEddi scaffolds use PrimeVue Aura tokens bridged in `src/styles/tokens.css`, without OpenProps.** Follow whatever token system an existing **project** already uses.

## Detect before styling

1. `package.json`: `"open-props"` in dependencies?
2. `src/styles/tokens.css` (or project equivalent): `@import "open-props/style"`?
3. `.heyeddi/design.md`: **Token source** or **Colors** section naming OpenProps vs custom vars?
4. `.heyeddi/stack.json` / `product.md`: explicit waiver or client stack constraints?

If none of the above mention OpenProps, **do not add** `open-props` unless the user asks.

## When OpenProps fits

| Signal | Use OpenProps |
|--------|----------------|
| An existing app that already imports `open-props` | Yes: keep it |
| Need fluid type/spacing scales without maintaining tables | Yes |
| Want `light-dark()` / gray ramps from a shared palette | Yes |
| `design.md` says token source is OpenProps | Yes |

Pattern: `@import "open-props/style"` then **semantic aliases** in `:root` (`--surface-1`, `--text-1`, `--brand`) so Vue/CSS never reference raw OpenProps names directly unless documented.

**Never** alias a custom property to itself (`--size-6: var(--size-6)`): that is circular and breaks computed padding/gap in the browser. Use OpenProps `--size-*` directly in components, or map to a **different** semantic name (`--space-6: var(--size-6)`).

## When to skip OpenProps

| Signal | Approach |
|--------|----------|
| Client repo has no `open-props` dependency | Custom CSS variables in `tokens.css` only |
| Small app; PrimeVue Aura preset + a few vars is enough | Wire preset `primary` to `--brand` in `:root`; minimal `tokens.css` |
| Existing system (Tailwind, Vuetify, corporate token JSON) | Follow that system; document in `design.md` + `product.md` waiver |
| `design.md` lists custom hex/CSS vars with no OpenProps mention | Use those vars: do not introduce OpenProps mid-project |

## Always (any token strategy)

- **Semantic tokens** in components: `var(--surface-1)`, `var(--text-1)`, `var(--brand)` from project `tokens.css` / `design.md`: not scattered `#hex` in `.vue` files.
- **PrimeVue**: map Aura (or project preset) `primary` to the project's brand token when buttons/toggles matter. Use `definePreset` in `main.ts` (see `@primevue-openprops-architect` VOCABULARY); CSS `--p-primary-color` alone is insufficient on PrimeVue v4.
- **design.md**: name the token source once; new tokens get added there before use in code.
- **Exceptions**: raw hex or third-party CSS only with a line in `design.md` **Decision log** or **Do's and Don'ts**.

## Decision log snippet

```markdown
**Token source:** Aura tokens via `tokens.css` aliases (project scaffold).

**We rejected:** Adding Tailwind: stack is PrimeVue + semantic CSS vars per design.md.
```

Or:

```markdown
**Token source:** Custom `:root` vars only: client repo has no open-props; `--brand` defined in tokens.css.
```

## Skills

| Skill | Behavior |
|-------|----------|
| `@heyeddi-design` | Aura tokens on **new** HeyEddi scaffolds; respect existing project token source on brownfield |
| `@heyeddi-handoff` | Match project token strategy; mockups never dictate hex |
| `@primevue-openprops-architect` | Enforce PrimeVue + **project** semantic tokens; OpenProps rules apply only when package is present |
