# Subagent delegation: visual-auditor v3

| Phase | Who | Tool |
|-------|-----|------|
| Load spec context | `shell` | `load_visual_context --write-review` |
| Capture + geometry + contrast | `shell` | `capture_screenshots` (runs `audit_geometry`), `audit_contrast` |
| **Review screenshots** | **main agent** | Read PNGs vs product.md + design.md |
| **Fix code** | **main agent** | Edit views/CSS: same turn |
| Log each fix | `shell` | `append_fix_log` |
| Re-verify | `shell` | `finalize_visual_review --check` |

Parent skills (`heyeddi-design`, `heyeddi-handoff`, `heyeddi-product`) may invoke the full loop inline or delegate capture/contrast to Task `shell` then fix in main chat.

**Anti-pattern:** Task subagent that only returns issue bullets without code changes.
