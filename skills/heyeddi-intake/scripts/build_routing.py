#!/usr/bin/env python3
"""Build skill-routing.json from product-translation.json + design folders."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _heyeddi_paths import designs_dir, intake_dir
from _product_schema import load_json, product_json_path, validate_product_json
from _skill_cli import emit, fail, resolve_project_root


def infer_stack(data: dict) -> tuple[str, list[str]]:
    note = (data.get("stack_note") or "").lower()
    frontend = "flutter" if "flutter" in note else "vue"
    backends: list[str] = []
    if "fastapi" in note:
        backends.append("fastapi")
    if "firebase" in note:
        backends.append("firebase")
    if not backends:
        backends = ["fastapi"]
    return frontend, backends


def feature_slug(route: str, view: str) -> str:
    slug = route.strip("/").replace("/", "-") or "home"
    if slug == "":
        slug = "home"
    if route == "/":
        return "taskflow-marketing"
    if "login" in route:
        return "taskflow-login"
    if "dashboard" in route:
        return "taskflow-dashboard"
    if "settings" in route:
        return "settings"
    return slug or view.replace("View", "").lower()


def has_handoff_artifacts(root: Path, feature: str) -> bool:
    folder = designs_dir(root) / feature
    if not folder.is_dir():
        return False
    if (folder / "wireframe.md").is_file():
        return True
    return (folder / "desktop.png").is_file()


def build_routing(root: Path, data: dict) -> dict:
    frontend, backends = infer_stack(data)
    product_name = data.get("product_name", "Product")
    routes_out: list[dict] = []

    for page in data.get("pages") or []:
        if not isinstance(page, dict):
            continue
        route = page.get("route", "/")
        view = page.get("view", "View")
        feature = feature_slug(route, view)
        register = "brand" if route in ("/", "/login") else "product"

        if route == "/settings" or has_handoff_artifacts(root, feature):
            feat = "settings" if "settings" in route else feature
            routes_out.append(
                {
                    "route": route,
                    "register": register,
                    "skill": "heyeddi-handoff",
                    "feature": feat,
                    "mockups": f".heyeddi/designs/{feat}/",
                    "brief": f".heyeddi/designs/{feat}/mockup-brief.md",
                    "notes": page.get("purpose", ""),
                }
            )
        else:
            routes_out.append(
                {
                    "route": route,
                    "register": register,
                    "skill": "heyeddi-design",
                    "mode": "craft",
                    "feature": feature,
                    "notes": page.get("purpose", ""),
                }
            )

    scaffold_skill = "flutter-engineering" if frontend == "flutter" else "project-engineering"
    return {
        "frontend": frontend,
        "backends": backends,
        "product_name": product_name,
        "routes": routes_out,
        "scaffold": [scaffold_skill, "scaffold_stack --stack full"],
        "post_intake": [
            "@heyeddi write_skills_index",
            "@heyeddi-design document",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build skill-routing manifest from product JSON")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--json", default=None, help="Defaults to .heyeddi/docs/intake/product-translation.json")
    parser.add_argument("--write", action="store_true", help="Write skill-routing.json")
    parser.add_argument("--save-input", action="store_true", help="Also save skill-routing-input.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    json_path = Path(args.json) if args.json else product_json_path(root)
    if not json_path.is_file():
        fail(f"product JSON not found: {json_path}: run write_product first")

    data = load_json(json_path)
    ok, errors = validate_product_json(data)
    if not ok:
        fail("invalid product JSON:\n- " + "\n- ".join(errors))

    routing = build_routing(root, data)

    if args.dry_run:
        emit({"dry_run": True, "routing": routing})
        return

    if args.save_input:
        intake_dir(root).mkdir(parents=True, exist_ok=True)
        routing_input_path = intake_dir(root) / "skill-routing-input.json"
        routing_input_path.write_text(json.dumps(routing, indent=2) + "\n")

    if args.write:
        dest = intake_dir(root) / "skill-routing.json"
        intake_dir(root).mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(routing, indent=2) + "\n")
        emit({"status": "ok", "path": str(dest), "route_count": len(routing["routes"])})
    else:
        emit(routing)


if __name__ == "__main__":
    main()
