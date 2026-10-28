@heyeddi-intake @heyeddi

Run the **mandatory translator pipeline** (`reference/pipeline.md`):

1. `load_intake` — enrich or validate TaskFlow product context
2. Ensure `.heyeddi/docs/intake/product-translation.json` meets schema (use template if needed)
3. **`write_product --json .heyeddi/docs/intake/product-translation.json --force`**
4. `write_translation` if missing
5. **`build_routing --write`** if routing stale
6. **`verify_intake --check`**
7. `@heyeddi` → **`write_skills_index --project-root .`**

No Vue implementation. Read `.heyeddi/product.md`, `skills-index.md`, `skill-routing.json`.

**Never delete baseline scaffold files** (`src/App.vue`, `src/main.ts`). Intake is docs-only — feature views under `src/views/` are forbidden. `verify_intake --check` includes a `repo-buildable` gate when `node_modules` exists.
