# Geometry gate

Reads one screenshot. No model. Each 24px block keeps its median color as the background, so thin type does not paint the background and a gradient still counts as a gradient.

```bash
python skills/visual-auditor/scripts/audit_geometry.py --image screen.png --check
```

## Hard errors

| Code | Meaning |
|------|---------|
| `text_wall` | Almost no marks, and the background is one flat color. |
| `low_contrast` | Marks exist, and under 4% of them reach 4.5:1. |
| `clipped_content` | Ink alternates along the top or bottom edge, as cut-off type does. |

`--check` exits 1 only for those.

## What does not fail

- A smooth gradient with no type. That is a background, not a text wall.
- A page whose median mark is under 3:1 because icons and soft edges are mixed in, while real type still reaches 4.5:1.
- Overlap and tap-target size. Those need element boxes.

`capture_screenshots` runs this gate on each PNG it writes and exits 1 on a hard error. Fix the layout, then capture again. If the capture JSON says `skipped: pillow missing`, the gate did not run. Install Pillow and capture again.

`finalize_visual_review --check` still ships on `audit_contrast`, which sees real text nodes.

Width is capped at 480. Height is kept, so a tall capture does not turn type into gray mush.
