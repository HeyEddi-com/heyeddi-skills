---
name: dart-type-bridger
description: Syncs a local FastAPI OpenAPI file to Dart model stubs and reads Firestore schema hints for Flutter projects. Use when writing Flutter repositories against FastAPI or Firebase backends.
version: 1.0.0
product-version: 3.4.2
author: HeyEddi-com
paths:
  - "lib/models/**"
  - "lib/repositories/**"
  - "openapi.json"
---

# Dart Type Bridger

## When to use

- Flutter agent needs accurate API payload shapes
- Local `openapi.json` (or another OpenAPI file under the project root)
- Firestore rules or schema file exists for Firebase projects

## Instructions

1. **Ensure a local OpenAPI file** at `openapi.json`. Prefer the scaffolded file. If the API is running and the file is missing/stale, export to disk first (do **not** pass a URL into this skill):

   ```bash
   curl -fsS http://127.0.0.1:8090/openapi.json -o openapi.json
   ```

2. FastAPI models: `python scripts/sync_openapi.py --project-root <root>`: writes `lib/models/api_models.dart` from local `openapi.json` only (optional `--openapi path/rel.json`).

3. Firebase: `python scripts/fetch_firestore_schema.py --project-root <root>`

4. Import generated models in repositories: never guess field names.
