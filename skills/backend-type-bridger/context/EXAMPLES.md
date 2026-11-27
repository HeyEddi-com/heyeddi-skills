# Examples

## Sync types from local OpenAPI

```bash
# Prefer existing scaffold file. Refresh from a running API only by writing a file:
curl -fsS http://127.0.0.1:8090/openapi.json -o openapi.json

python .agents/skills/backend-type-bridger/scripts/sync_openapi.py --project-root .
# optional: python .agents/skills/backend-type-bridger/scripts/sync_openapi.py --project-root . --openapi docs/openapi.json
```

## Firestore hints

```bash
python .agents/skills/backend-type-bridger/scripts/fetch_firestore_schema.py --project-root .
```
