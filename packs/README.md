# Skill packs

**Brand:** this hub is **HeyEddi Skills** (`heyeddi-skills`). Packs are curated subsets from one SSOT tree: `skills/<name>/`.

| Pack | Plugin | Public GitHub (skills.sh) | Who |
|------|--------|---------------------------|-----|
| [`heyeddi-skills.json`](heyeddi-skills.json) | `plugins/heyeddi-skills/` | [`HeyEddi-com/heyeddi-skills`](https://github.com/HeyEddi-com/heyeddi-skills) | Full product + CI + QA |
| [`heyeddi-ci-skills.json`](heyeddi-ci-skills.json) | `plugins/heyeddi-ci-skills/` | [`HeyEddi-com/heyeddi-ci-skills`](https://github.com/HeyEddi-com/heyeddi-ci-skills) (published mirror) | CI-only |

## Sync

```bash
./scripts/sync-plugins.sh           # link mode (default) — per-skill symlinks
./scripts/sync-plugins.sh --copy    # copy mode — for release archives / CI
./scripts/sync-plugins.sh --pack heyeddi-ci-skills
./scripts/publish-ci-pack-repo.sh --out ../heyeddi-ci-skills --push
```

**Never** point `plugins/*/skills` at the whole `skills/` directory as one symlink — `rm -rf` through that path deletes the SSOT. Pack sync uses a **real** `skills/` directory containing **per-skill** links or copies.

Author skills only under `skills/<name>/`, then re-run sync before publishing marketplace plugins / CI mirror.
