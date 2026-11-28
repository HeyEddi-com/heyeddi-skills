---
name: backend-type-bridger
description: Syncs a local FastAPI OpenAPI file to TypeScript types and reads Firestore schema hints. Use when writing Vue composables against FastAPI or Firebase backends.
version: 1.0.1
product-version: 3.10.0
author: HeyEddi-com
paths:
  - "**/composables/**"
  - "**/api/**"
  - "openapi.json"
---

# Backend Type Bridger

## When to use

- Frontend agent needs accurate API payload shapes
- Local `openapi.json` (or another OpenAPI file under the project root)
- Firestore rules or schema file exists for Firebase projects

## Instructions

1. **Ensure a local OpenAPI file** at `openapi.json` (project root). Prefer the scaffolded file. If the API is running and the file is missing/stale, export to disk first (do **not** pass a URL into this skill):

   ```bash
   curl -fsS http://127.0.0.1:8090/openapi.json -o openapi.json
   ```

2. FastAPI types: `python .agents/skills/backend-type-bridger/scripts/sync_openapi.py --project-root .`: writes `src/types/api.ts` from local `openapi.json` only (optional `--openapi path/rel.json`).

3. Firebase: `python .agents/skills/backend-type-bridger/scripts/fetch_firestore_schema.py --project-root .`

4. Import generated types in composables: never guess field names. Each run overwrites `src/types/api.ts`, so put narrower or derived types in another file. The script exits 1 on a missing or invalid file: fix the input and rerun.
