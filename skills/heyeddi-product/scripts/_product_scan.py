"""Parse product.md and scan implementation for PM checks."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


PLACEHOLDER_PATTERNS = re.compile(r"(lorem ipsum|todo:|coming soon|not implemented|fixme)", re.I)
# The word "placeholder" counts only as text the user reads, not as an input attribute or CSS.
PLACEHOLDER_ATTR = re.compile(r"""(?:v-bind:|:)?placeholder\s*=\s*(?:"[^"]*"|'[^']*')""", re.I)
NOT_VISIBLE = re.compile(
    r"""<(script|style)\b[\s\S]*?</\1>|<!--[\s\S]*?-->|\{\{[\s\S]*?\}\}|<(?:"[^"]*"|'[^']*'|[^'">])*>""",
    re.I,
)

ROUTE_IN_MD = re.compile(r"`(/[^`]+)`")
ROUTE_IN_ROUTER = re.compile(r"""path:\s*['"]([^'"]+)['"]""")


def parse_pages_from_product(text: str) -> list[dict[str, str]]:
    pages: list[dict[str, str]] = []
    in_pages = False
    for line in text.splitlines():
        if line.strip().lower().startswith("## pages"):
            in_pages = True
            continue
        if in_pages and line.startswith("## "):
            break
        if in_pages and line.startswith("|") and "`/" in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0].startswith("`"):
                route = cells[0].strip("`")
                pages.append(
                    {
                        "route": route,
                        "view": cells[1].strip("`") if "`" in cells[1] else cells[1],
                        "purpose": cells[2],
                    }
                )
    if pages:
        return pages
    routes = sorted(set(ROUTE_IN_MD.findall(text)))
    return [{"route": r, "view": "", "purpose": ""} for r in routes]


def product_sections_present(text: str) -> dict[str, bool]:
    lower = text.lower()
    return {
        "personas": "## personas" in lower,
        "route_intent": "per-route intent" in lower or "## per-route" in lower,
        "competitors": "## competitors" in lower,
        "voice": "voice" in lower and "tone" in lower,
        "pages": "## pages" in lower,
        "acceptance": "acceptance" in lower or "user stor" in lower,
    }


def vue_routes(root: Path) -> list[str]:
    routes: list[str] = []
    for rel in ("src/router/index.ts", "src/router/index.js", "src/router.ts"):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        routes.extend(ROUTE_IN_ROUTER.findall(text))
    return sorted(set(routes))


def vue_views(root: Path) -> dict[str, Path]:
    views_dir = root / "src" / "views"
    if not views_dir.is_dir():
        return {}
    return {p.stem: p for p in views_dir.glob("*.vue")}


def view_placeholder_flags(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    flags: list[str] = []
    if len(text.splitlines()) < 12:
        flags.append("very_short_view")
    for match in PLACEHOLDER_PATTERNS.finditer(PLACEHOLDER_ATTR.sub("", text)):
        flags.append(f"placeholder:{match.group(1).lower()}")
    if "placeholder" in NOT_VISIBLE.sub(" ", text).lower():
        flags.append("placeholder:placeholder")
    if "<router-view" in text and "views/" not in text and path.name == "App.vue":
        pass
    elif re.search(r"<template>\s*</template>", text, re.I):
        flags.append("empty_template")
    return flags


def feature_spec_paths(root: Path, features_dir: Path) -> list[Path]:
    if not features_dir.is_dir():
        return []
    return sorted(features_dir.glob("*.md"))


def ux_flow_tasks(root: Path) -> list[str]:
    flows = root / ".heyeddi" / "docs" / "ux-flows"
    if not flows.is_dir():
        return []
    return sorted(p.stem for p in flows.glob("*.flow.json"))


def build_feature_matrix(root: Path, pages: list[dict[str, str]]) -> list[dict[str, Any]]:
    code_routes = set(vue_routes(root))
    views = vue_views(root)
    rows: list[dict[str, Any]] = []
    for page in pages:
        route = page.get("route", "")
        view_name = page.get("view", "")
        view_path = views.get(view_name) if view_name else None
        status = "missing"
        flags: list[str] = []
        if route in code_routes or (route == "/" and "/" in code_routes):
            status = "routed"
        if view_path and view_path.is_file():
            status = "implemented" if status == "routed" else "view_only"
            flags = view_placeholder_flags(view_path)
            if flags:
                status = "placeholder"
        elif not code_routes:
            status = "unknown_no_router"
        rows.append(
            {
                "route": route,
                "view": view_name or page.get("view", ""),
                "purpose": page.get("purpose", ""),
                "status": status,
                "flags": flags,
            }
        )
    return rows
