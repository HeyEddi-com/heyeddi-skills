"""Extract product + design context for a route: visual auditor."""
from __future__ import annotations

import json
import re
from pathlib import Path


def _read(path: Path | None) -> str:
    if path and path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def parse_route_intent(product_text: str, route: str) -> dict[str, str]:
    row: dict[str, str] = {}
    in_table = False
    for line in product_text.splitlines():
        if "per-route intent" in line.lower():
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if in_table and route in line and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 5:
                row = {
                    "route": cells[0].strip("`"),
                    "register": cells[1],
                    "primary_persona": cells[2],
                    "mindset": cells[3],
                    "success_feeling": cells[4],
                }
                break
    return row


def parse_page_purpose(product_text: str, route: str) -> str:
    in_pages = False
    for line in product_text.splitlines():
        if line.strip().lower().startswith("## pages"):
            in_pages = True
            continue
        if in_pages and line.startswith("## "):
            break
        if in_pages and route in line and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3:
                return cells[2]
    return ""


def feature_slug(route: str) -> str:
    return route.strip("/").replace("/", "-") or "home"


def latest_contrast_report(visual_dir: Path, slug: str) -> Path | None:
    if not visual_dir.is_dir():
        return None
    matches = sorted(visual_dir.glob(f"{slug}-contrast-*.json"), reverse=True)
    return matches[0] if matches else None


def list_screenshots(screenshot_dir: Path, slug: str) -> list[str]:
    if not screenshot_dir.is_dir():
        return []
    return sorted(str(p) for p in screenshot_dir.glob(f"{slug}_*px*.png"))


def design_excerpt(design_text: str, limit: int = 2500) -> str:
    if len(design_text) <= limit:
        return design_text
    return design_text[:limit] + "\n\n…(truncated: read full design.md for tokens)"


def load_route_context(
    root: Path,
    route: str,
    *,
    product_path: Path | None,
    design_path: Path | None,
    designs_root: Path,
    visual_dir: Path,
    screenshot_dir: Path,
) -> dict:
    slug = feature_slug(route)
    feature_dir = designs_root / slug
    product_text = _read(product_path)
    design_text = _read(design_path)

    contrast_path = latest_contrast_report(visual_dir, slug)
    contrast_summary: dict = {}
    if contrast_path and contrast_path.is_file():
        try:
            data = json.loads(contrast_path.read_text())
            results = data.get("results") or []
            contrast_summary = {
                "path": str(contrast_path.relative_to(root)),
                "errors": sum(r.get("errorCount", 0) for r in results),
                "warnings": sum(r.get("warnCount", 0) for r in results),
            }
        except json.JSONDecodeError:
            contrast_summary = {"path": str(contrast_path.relative_to(root)), "parse_error": True}

    refs: list[str] = []
    if feature_dir.is_dir():
        for ext in ("*.png", "*.jpg", "*.webp"):
            refs.extend(str(p.relative_to(root)) for p in feature_dir.glob(ext))

    mockup_brief = feature_dir / "mockup-brief.md"
    wireframe = feature_dir / "wireframe.md"

    return {
        "route": route,
        "feature": slug,
        "product_md": str(product_path.relative_to(root)) if product_path else None,
        "design_md": str(design_path.relative_to(root)) if design_path else None,
        "route_intent": parse_route_intent(product_text, route),
        "page_purpose": parse_page_purpose(product_text, route),
        "mockup_brief": str(mockup_brief.relative_to(root)) if mockup_brief.is_file() else None,
        "wireframe_md": str(wireframe.relative_to(root)) if wireframe.is_file() else None,
        "reference_mockups": refs,
        "captures": [str(Path(p).relative_to(root)) for p in list_screenshots(screenshot_dir, slug)],
        "contrast": contrast_summary,
        "review_checklist": [
            "Screenshot matches page purpose and route_intent success_feeling",
            "Hierarchy matches mockup-brief or wireframe regions",
            "Colors follow design.md semantic tokens: not mockup PNG pixels",
            "Contrast errors from audit_contrast are fixed in code",
            "375px capture has no horizontal scroll or clipped CTAs",
            "430px and 1024px captures checked on flagship done preset",
            "Edges/links read on the plane (not washed out)",
            "Logo-off brand test: still reads as this product",
        ],
    }
