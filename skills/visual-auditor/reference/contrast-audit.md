# Contrast & legibility audit

**Date:** 2026-07-06

Screenshots alone do **not** catch illegible UI. Always run **`audit_contrast`** (or `capture_screenshots --check`) after layout capture.

## What we detect

| Code | Severity | Example |
|------|----------|---------|
| `low-contrast` | error | Gray `#9ca3af` on white below WCAG AA (4.5:1) |
| `same-hue-low-contrast` | error | Green text on green panel: hue distance &lt; 18° |
| `motion-or-image-behind-text` | warn | Borderline contrast + animated gradient / video behind text |
| `text-over-dynamic-background` | warn | Text over `background-image` or animation with ratio &lt; 7:1 |
| `faded-text-over-busy-background` | warn | `opacity` &lt; 0.85 on text over motion/busy BG |

## WCAG thresholds (AA)

- Normal text: **4.5:1**
- Large text (≥18px or ≥14px bold): **3:1**

Use `--strict` to fail on warnings (recommended before merge on marketing routes).

## Pipeline

```
audit_contrast --route / --widths 375,768,1440 --check
# or: audit_contrast --route / --preset done --check

```

Reports: `.heyeddi/audits/visual/<route>-contrast-<date>.md` + `.json`  
Screenshots: `.heyeddi/audits/visual/screenshots/<route>_<width>px.png`

## Agent review

1. Read the markdown report: every **error** must be fixed before ship.
2. For **warnings** on `/` or hero routes: treat as errors unless `product.md` waives motion backgrounds.
3. Pair with screenshots from `capture_screenshots`: contrast audit is authoritative for legibility; screenshots for layout hierarchy.

## Offline / CI fixture

```bash
python scripts/audit_contrast.py --fixture fixtures/contrast-violations.html --check
```

Expect exit 1: proves probe catches green-on-green and motion cases.
