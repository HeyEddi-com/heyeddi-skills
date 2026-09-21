
#!/usr/bin/env python3
"""Capture responsive screenshots with Playwright; optional contrast audit."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from _heyeddi_paths import screenshot_dir, visual_audit_dir
from _skill_cli import emit, resolve_project_root
from _widths import FAST_WIDTHS, resolve_widths


def main() -> None:
    parser = argparse.ArgumentParser(description="Visual audit screenshots + optional contrast check")
    parser.add_argument("--route", required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--widths", default=None, help=f"Comma-separated widths (default: {FAST_WIDTHS})")
    parser.add_argument(
        "--preset",
        default=None,
        choices=["fast", "done", "flagship"],
        help="fast=375,768,1440; done/flagship=375,430,768,1024,1440,1920",
    )
    parser.add_argument("--check", action="store_true", help="Run audit_contrast after capture; exit 1 on contrast errors")
    parser.add_argument("--strict", action="store_true", help="Pass --strict to contrast audit")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    try:
        widths_str = resolve_widths(args.widths, args.preset)
    except ValueError as exc:
        emit(str(exc))
        sys.exit(2)
    widths = [int(w) for w in widths_str.split(",") if w.strip()]
    base_url = os.environ.get(
        "DEV_SERVER_URL",
        os.environ.get("FLUTTER_WEB_URL", "http://localhost:5173"),
    )
    out_dir = screenshot_dir(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    visual_audit_dir(root).mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415
    except ImportError:
        emit(
            "[skip] Playwright not installed.\n"
            "Install: pip install playwright && playwright install chromium\n"
            "Fallback: python scripts/layout_tree.py --route "
            + args.route
            + " --project-root "
            + str(root)
        )
        return

    artifacts: list[str] = []
    url = base_url.rstrip("/") + args.route
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for w in widths:
            page = browser.new_page(viewport={"width": w, "height": 900})
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
            except Exception as exc:
                emit(f"[warn] navigation failed for {url}: {exc}")
                browser.close()
                return
            slug = args.route.strip("/").replace("/", "_") or "home"
            path = out_dir / f"{slug}_{w}px.png"
            page.screenshot(path=str(path), full_page=True)
            artifacts.append(str(path.relative_to(root)))
            page.close()
        browser.close()

    manifest_path = out_dir / "last-capture.json"
    manifest_path.write_text(
        json.dumps({"route": args.route, "artifacts": [str(Path(a)) for a in artifacts]}, indent=2) + "\n",
        encoding="utf-8",
    )

    emit(
        json.dumps(
            {
                "route": args.route,
                "artifacts": artifacts,
                "manifest": str(manifest_path.relative_to(root)),
                "screenshot_dir": str(out_dir.relative_to(root)),
            },
            indent=2,
        )
    )

    if args.check:
        contrast_script = Path(__file__).parent / "audit_contrast.py"
        cmd = [
            sys.executable,
            str(contrast_script),
            "--route",
            args.route,
            "--project-root",
            str(root),
            "--widths",
            widths_str,
            "--check",
        ]
        if args.strict:
            cmd.append("--strict")
        if args.preset:
            cmd.extend(["--preset", args.preset])
        result = subprocess.run(cmd, cwd=contrast_script.parent)
        if result.returncode != 0:
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
