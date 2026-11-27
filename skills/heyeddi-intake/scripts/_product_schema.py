"""Product translation JSON schema, validation, and product.md parsing."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PRODUCT_JSON_NAME = "product-translation.json"
ROUTING_JSON_NAME = "skill-routing-input.json"

REQUIRED_PERSONA_KEYS = ("name", "role", "primary_job", "design_implication")
REQUIRED_ROUTE_INTENT_KEYS = ("route", "register", "primary_persona", "mindset", "success_feeling")


def intake_dir(root: Path) -> Path:
    return root / ".heyeddi" / "docs" / "intake"


def product_json_path(root: Path) -> Path:
    return intake_dir(root) / PRODUCT_JSON_NAME


def routing_input_path(root: Path) -> Path:
    return intake_dir(root) / ROUTING_JSON_NAME


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def handoff_features(routing: dict[str, Any]) -> list[str]:
    """Design folders that skill-routing.json sends to @heyeddi-handoff."""
    return [
        str(row["feature"])
        for row in routing.get("routes") or []
        if isinstance(row, dict) and row.get("skill") == "heyeddi-handoff" and row.get("feature")
    ]


def validate_product_json(data: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not data.get("product_name"):
        errors.append("product_name is required")

    if not (data.get("audience_summary") or data.get("audience")):
        errors.append("audience_summary (or audience) is required")

    if not data.get("stack_note"):
        errors.append("stack_note is required")

    if not data.get("voice_tone") and not data.get("brand_personality"):
        errors.append("voice_tone is required")

    competitors = data.get("competitors") or []
    if not competitors:
        errors.append("competitors must list at least one product users compare against")

    if not data.get("competitive_edge"):
        errors.append("competitive_edge is required (one line differentiation)")

    if not data.get("anti_audience"):
        errors.append("anti_audience is required")

    pages = data.get("pages") or []
    if not pages:
        errors.append("pages must include at least one route")

    personas = data.get("personas") or []
    if len(personas) < 2:
        errors.append("personas must include at least 2 entries (e.g. buyer + daily user)")
    for index, persona in enumerate(personas):
        if not isinstance(persona, dict):
            errors.append(f"personas[{index}] must be an object")
            continue
        for key in REQUIRED_PERSONA_KEYS:
            if not persona.get(key):
                errors.append(f"personas[{index}].{key} is required")

    route_intent = data.get("route_intent") or []
    page_routes = {p.get("route") for p in pages if isinstance(p, dict) and p.get("route")}
    intent_routes = {r.get("route") for r in route_intent if isinstance(r, dict) and r.get("route")}
    missing_intent = sorted(page_routes - intent_routes)
    if missing_intent:
        errors.append(f"route_intent missing entries for page routes: {missing_intent}")
    for index, row in enumerate(route_intent):
        if not isinstance(row, dict):
            errors.append(f"route_intent[{index}] must be an object")
            continue
        for key in REQUIRED_ROUTE_INTENT_KEYS:
            if not row.get(key):
                errors.append(f"route_intent[{index}].{key} is required")

    refs = data.get("design_references") or []
    if len(refs) < 2:
        errors.append("design_references must include at least 2 named anchors")

    return len(errors) == 0, errors


def validate_product_md(text: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    lower = text.lower()
    for header in ("## personas", "## per-route intent", "## voice & tone", "## competitors"):
        if header not in lower:
            errors.append(f"product.md missing {header.replace('## ', '## ')} section")
    if "## anti-audience" not in lower:
        errors.append("product.md missing ## Anti-audience section")
    return len(errors) == 0, errors


def parse_route_intent_row(product_text: str, route: str) -> dict[str, str] | None:
    """Parse one row from Per-route intent table in product.md."""
    match = re.search(r"##\s*Per-route intent\s*\n([\s\S]*?)(?:\n## |\Z)", product_text, re.IGNORECASE)
    if not match:
        return None
    block = match.group(1)
    target = route.strip()
    for line in block.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip().strip("`") for c in line.split("|")[1:-1]]
        if len(cells) < 5:
            continue
        if cells[0] == target:
            return {
                "route": cells[0],
                "register": cells[1],
                "primary_persona": cells[2],
                "mindset": cells[3],
                "success_feeling": cells[4],
            }
    return None


def format_audience_block(product_text: str | None, route: str) -> str:
    row = parse_route_intent_row(product_text or "", route) if product_text else None
    if not row:
        return (
            f"- **Primary persona:** _(missing in product.md for `{route}`: run write_product)_\n"
            f"- **Mindset / success:** _\n"
            f"- **Direction:** See `heyeddi-design/reference/audience-design.md`"
        )
    return (
        f"- **Primary persona:** {row['primary_persona']}\n"
        f"- **Mindset:** {row['mindset']}\n"
        f"- **Success feeling:** {row['success_feeling']}\n"
        f"- **Register:** {row['register']} · Direction: `heyeddi-design/reference/audience-design.md`"
    )
