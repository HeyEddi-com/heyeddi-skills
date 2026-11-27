# Examples: settings route visual pass

```bash
# Dev server running on :5173
python scripts/load_visual_context.py --project-root . --route /settings --write-review
python scripts/audit_ui.py --project-root . --route /settings
python scripts/audit_contrast.py --project-root . --route /settings

# Agent: read PNGs + product.md + design.md + mockup-brief
# Agent: fix Vue/CSS issues, then per fix:
python scripts/append_fix_log.py --project-root . --route /settings \
  --issue "Muted label below WCAG on card" \
  --fix "Set label color to var(--text-2)" \
  --files "src/views/SettingsView.vue" \
  --spec-ref "design.md semantic text + audit_contrast low-contrast"

python scripts/finalize_visual_review.py --project-root . --route /settings --check
```

Artifacts: `.heyeddi/audits/visual/reviews/settings-review-*.md`, `fix-log.md`
