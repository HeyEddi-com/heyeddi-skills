#!/usr/bin/env python3
"""Load intake state: user prompt, product, designs, gaps for translation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _heyeddi_paths import design_md, designs_dir, intake_dir, product_md
from _product_schema import handoff_features, product_json_path, validate_product_json, validate_product_md
from _skill_cli import emit, resolve_project_root


def list_features(root: Path) -> list[dict]:
    base = designs_dir(root)
    out: list[dict] = []
    if not base.is_dir():
        return out
    for d in sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")):
        pngs = sorted(str(p.name) for p in d.glob("*.png"))
        has_brief = (d / "mockup-brief.md").is_file()
        has_wireframe = (d / "wireframe.md").is_file()
        handoff = d / "handoff.json"
        route = None
        if handoff.is_file():
            try:
                route = json.loads(handoff.read_text()).get("route")
            except json.JSONDecodeError:
                pass
        out.append(
            {
                "feature": d.name,
                "route": route,
                "mockups": pngs,
                "has_mockup_brief": has_brief,
                "has_wireframe": has_wireframe,
            }
        )
    return out


def read_prompt(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    text = path.read_text(errors="replace").strip()
    return text or None


def main() -> None:
    parser = argparse.ArgumentParser(description="Load product translation intake state")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--user-prompt", default=None, help="Inline user request")
    parser.add_argument("--prompt-file", default=None, help="Path to user prompt text file")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    prompt = args.user_prompt
    if args.prompt_file:
        prompt = read_prompt(Path(args.prompt_file)) or prompt

    p_path = product_md(root)
    d_path = design_md(root)
    features = list_features(root)
    intake = intake_dir(root)
    json_path = product_json_path(root)

    gaps: list[str] = []
    if not p_path:
        gaps.append("missing .heyeddi/product.md: run write_product (never hand-write)")
    elif p_path.is_file():
        ok, errs = validate_product_md(p_path.read_text(errors="replace"))
        if not ok:
            gaps.extend(errs)

    if not json_path.is_file():
        gaps.append(f"missing {json_path.relative_to(root)}: write_product saves this automatically")
    else:
        try:
            data = json.loads(json_path.read_text())
            ok, errs = validate_product_json(data)
            if not ok:
                gaps.extend([f"product-translation.json: {e}" for e in errs])
        except json.JSONDecodeError:
            gaps.append("product-translation.json is invalid JSON")

    if not d_path:
        gaps.append("missing .heyeddi/design.md: chain @heyeddi-design document after translate")
    if not (intake / "skill-routing.json").is_file():
        gaps.append("missing skill-routing.json: run build_routing --write")
    if not list(intake.glob("translation-*.md")):
        gaps.append("missing translation-*.md: run write_translation")
    routing_path = intake / "skill-routing.json"
    routing = json.loads(routing_path.read_text()) if routing_path.is_file() else {}
    for feature in handoff_features(routing):
        folder = designs_dir(root) / feature
        has_png_pair = (folder / "desktop.png").is_file() and (folder / "mobile.png").is_file()
        if not (folder / "wireframe.md").is_file() and not has_png_pair:
            gaps.append(
                f"missing designs/{feature} handoff: run generate_wireframe, ingest_mockups, "
                "or prepare_mockup_prompts + AI PNGs"
            )

    emit(
        json.dumps(
            {
                "project_root": str(root),
                "user_prompt": prompt,
                "product_md": str(p_path) if p_path else str(root / ".heyeddi" / "product.md"),
                "product_json": str(json_path.relative_to(root)),
                "product_exists": p_path is not None,
                "design_md": str(d_path) if d_path else None,
                "design_features": features,
                "intake_dir": str(intake),
                "gaps": gaps,
                "ready_for_downstream": len(gaps) == 0,
                "workflow": [
                    "1. Draft product-translation.json (see reference/audience-intake.md)",
                    "2. write_product --json .heyeddi/docs/intake/product-translation.json --force",
                    "3. write_translation",
                    "4. generate_wireframe or ingest_mockups + seed_brief per handoff feature",
                    "5. build_routing --write",
                    "6. verify_intake --check",
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
