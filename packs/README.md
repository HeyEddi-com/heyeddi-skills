# Skill packs

**Brand:** this hub is **HeyEddi Skills** (`heyeddi-skills`). **Monorepo:** packs are curated subsets from one SSOT tree `skills/<name>/` — not separate GitHub repos.

| Pack | Plugin | Who |
|------|--------|-----|
| [`heyeddi-skills.json`](heyeddi-skills.json) | `plugins/heyeddi-skills/` | Full product + CI + QA |
| [`heyeddi-ci-skills.json`](heyeddi-ci-skills.json) | `plugins/heyeddi-ci-skills/` | CI-only (Marketplace / selective `npx` install) |

## Sync

```bash
./scripts/sync-plugins.sh           # link mode (default) — per-skill symlinks
./scripts/sync-plugins.sh --copy    # copy mode — for release archives / CI
./scripts/sync-plugins.sh --pack heyeddi-ci-skills
```

**Never** point `plugins/*/skills` at the whole `skills/` directory as one symlink — `rm -rf` through that path deletes the SSOT. Pack sync uses a **real** `skills/` directory containing **per-skill** links or copies.

Author skills only under `skills/<name>/`, then re-run sync before publishing marketplace plugins.
