# Agent instructions

<!-- heyeddi-always-on:start -->
## HeyEddi always-on

Thin gates for **every Agent chat** in this project. Full playbooks and scripts stay in skills — load them when a gate says so (or via `/skill`).

### Checklist

1. **Router / `.heyeddi/`** — Session start or ambiguous task: `@heyeddi`. Keep `.heyeddi/skills-index` current; follow `.heyeddi/docs/intake/skill-routing.json` when present. Do not freestyle the pipeline. Do not re-scaffold workflow every message.
2. **Setup** — Before git / CI / commit / push / agent autonomy: `@heyeddi-setup` → `verify_setup --check`. Incomplete prefs **fail** those actions.
3. **Local-first** — Before apply or other live cloud writes: `@heyeddi-local-first` → `classify_command.py --check`. Exit 1 → do not run. `terraform plan` is allowed and must be summarized.
4. **Engineering** — Before feature code: `@engineering-excellence` plan gate. After edits: `audit_engineering --check` (errors fail; warns advisory).
5. **Prose** — Any prose you author (chat, books, docs, UI, PRs): follow skill `PROSE_ANTI_SLOP`. Run `verify_prose --check` on touched surfaces; add `--glob` for non-default paths. No "not for books" carve-out.
6. **Ship** — Before merge-ready claims: `@pre-merge-gate --signoff` (exit 0 required).

### On demand (not every chat)

`@heyeddi-intake`, `@heyeddi-product`, `@taste-penpot`, `@heyeddi-design`, visual/UX auditors, `@heyeddi-pr-review`, `@heyeddi-pr-respond`, scaffolders / handoff.

Managed by `@heyeddi` sync / auto-sync. Edit outside this block freely; content between the markers is replaced on sync.
<!-- heyeddi-always-on:end -->
