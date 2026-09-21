#!/usr/bin/env python3
"""WCAG contrast + motion-over-text audit via Playwright."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from _heyeddi_paths import visual_audit_dir
from _skill_cli import emit, fail, resolve_project_root
from _widths import FAST_WIDTHS, resolve_widths

PROBE_JS = (Path(__file__).parent / "contrast_probe.js").read_text(encoding="utf-8")


def _run_probe(page) -> dict:
    return page.evaluate(
        f"""() => {{
        {PROBE_JS}
        return runContrastProbe();
    }}"""
    )


def _audit_page(page, url: str, viewport_width: int) -> dict:
    page.set_viewport_size({"width": viewport_width, "height": 900})
    page.goto(url, wait_until="networkidle", timeout=20000)
    # Let CSS animations apply at least one frame
    page.wait_for_timeout(300)
    result = _run_probe(page)
    result["viewport"] = viewport_width
    result["url"] = url
    return result


def _render_report(route: str, results: list[dict]) -> str:
    lines = [
        f"# Visual contrast audit: {route}",
        "",
        f"**Date:** {date.today().isoformat()}",
        "",
    ]
    total_errors = sum(r.get("errorCount", 0) for r in results)
    total_warns = sum(r.get("warnCount", 0) for r in results)
    lines.append(f"**Errors:** {total_errors} · **Warnings:** {total_warns}")
    lines.append("")

    for block in results:
        lines.append(f"## Viewport {block.get('viewport')}px")
        lines.append("")
        lines.append(f"Scanned **{block.get('scanned', 0)}** text elements.")
        lines.append("")
        for v in block.get("violations", []):
            sev = v.get("severity", "error").upper()
            code = v.get("code", "issue")
            lines.append(f"### [{sev}] `{code}`: `{v.get('selector', '?')}`")
            lines.append("")
            lines.append(f"- **Text:** {v.get('text', '')[:100]}")
            if "ratio" in v:
                lines.append(f"- **Contrast:** {v['ratio']}:1 (needs {v.get('required', 4.5)}:1)")
            if "foreground" in v:
                lines.append(f"- **FG / BG:** {v['foreground']} on {v['background']}")
            if v.get("motion"):
                lines.append(f"- **Motion / busy BG:** {json.dumps(v['motion'][:3])}")
            if v.get("note"):
                lines.append(f"- **Note:** {v['note']}")
            lines.append("")

    if total_errors == 0 and total_warns == 0:
        lines.append("_No contrast or motion-over-text issues detected._")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit text contrast and motion-over-text risks")
    parser.add_argument("--route", default="/")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--widths", default=None, help=f"Comma-separated widths (default: {FAST_WIDTHS})")
    parser.add_argument(
        "--preset",
        default=None,
        choices=["fast", "done", "flagship"],
        help="fast=375,768,1440; done/flagship=375,430,768,1024,1440,1920",
    )
    parser.add_argument("--fixture", default=None, help="Local HTML file for offline probe (file://)")
    parser.add_argument("--check", action="store_true", help="Exit 1 when error-level violations exist")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures with --check")
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    try:
        widths_str = resolve_widths(args.widths, args.preset)
    except ValueError as exc:
        fail(str(exc))
    widths = [int(w) for w in widths_str.split(",") if w.strip()]

    try:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415
    except ImportError:
        emit(
            "[skip] Playwright not installed.\n"
            "Install: uv sync --group evals-quality && playwright install chromium"
        )
        return

    if args.fixture:
        fixture = Path(args.fixture).resolve()
        if not fixture.is_file():
            fail(f"fixture not found: {fixture}")
        url = fixture.as_uri()
    else:
        base_url = os.environ.get(
            "DEV_SERVER_URL",
            os.environ.get("FLUTTER_WEB_URL", "http://localhost:5173"),
        )
        url = base_url.rstrip("/") + args.route

    out_dir = visual_audit_dir(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.route.strip("/").replace("/", "_") or "home"

    results: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            for w in widths:
                results.append(_audit_page(page, url, w))
        except Exception as exc:
            browser.close()
            fail(f"contrast audit failed for {url}: {exc}")
        browser.close()

    report_path = out_dir / f"{slug}-contrast-{date.today().isoformat()}.md"
    json_path = out_dir / f"{slug}-contrast-{date.today().isoformat()}.json"
    report_path.write_text(_render_report(args.route, results), encoding="utf-8")
    payload = {"route": args.route, "url": url, "results": results, "report": str(report_path.relative_to(root))}
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    total_errors = sum(r.get("errorCount", 0) for r in results)
    total_warns = sum(r.get("warnCount", 0) for r in results)

    emit(
        json.dumps(
            {
                "status": "fail" if total_errors or (args.strict and total_warns) else "ok",
                "route": args.route,
                "errors": total_errors,
                "warnings": total_warns,
                "report": str(report_path.relative_to(root)),
                "json": str(json_path.relative_to(root)),
                "violations": [
                    v
                    for r in results
                    for v in r.get("violations", [])
                    if v.get("severity") == "error"
                ][:20],
            },
            indent=2,
        )
    )

    if args.check and (total_errors or (args.strict and total_warns)):
        sys.exit(1)


if __name__ == "__main__":
    main()
