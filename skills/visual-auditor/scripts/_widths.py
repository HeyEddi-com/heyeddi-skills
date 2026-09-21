"""Viewport width presets for visual capture and contrast audit."""
from __future__ import annotations

# Fast iteration during craft/polish
FAST_WIDTHS = "375,768,1440"

# Flagship / marketing done gate (catches large-phone, hinge, wide stretch)
DONE_WIDTHS = "375,430,768,1024,1440,1920"

PRESETS = {
    "fast": FAST_WIDTHS,
    "done": DONE_WIDTHS,
    "flagship": DONE_WIDTHS,
}


def resolve_widths(widths: str | None, preset: str | None, *, default: str = FAST_WIDTHS) -> str:
    """Explicit --widths wins; else --preset; else default (fast unless caller overrides)."""
    if widths and widths.strip():
        return widths.strip()
    if preset:
        key = preset.strip().lower()
        if key not in PRESETS:
            raise ValueError(f"Unknown preset {preset!r}; use: {', '.join(sorted(PRESETS))}")
        return PRESETS[key]
    return default
