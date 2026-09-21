#!/usr/bin/env python3
"""Finalize visual review after fixes: re-capture, contrast check, close review doc."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from _heyeddi_paths import screenshot_dir, visual_audit_dir
from _skill_cli import emit, fail, resolve_project_root
from _spec_context import feature_slug, latest_contrast_report
from _widths import DONE_WIDTHS, resolve_widths


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-verify route and finalize visual review")
    parser.add_argument("--route", required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--widths",
        default=None,
        help=f"Comma-separated widths (finalize default: done = {DONE_WIDTHS})",
    )
    parser.add_argument(
        "--preset",
        default="done",
        choices=["fast", "done", "flagship"],
        help="Default done (6 widths). Use fast for quick re-check.",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-recapture", action="store_true")
    parser.add_argument("--check", action="store_true", help="Exit 1 if contrast still fails")
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    slug = feature_slug(args.route)
    scripts = Path(__file__).parent
    try:
        widths_str = resolve_widths(args.widths, args.preset, default=DONE_WIDTHS)
    except ValueError as exc:
        fail(str(exc))

    if not args.skip_recapture:
        for script, extra in (
            ("audit_ui.py", ["--route", args.route, "--widths", widths_str]),
            ("audit_contrast.py", ["--route", args.route, "--widths", widths_str, "--check"]),
        ):
            cmd = [sys.executable, str(scripts / script), "--project-root", str(root), *extra]
            if script == "audit_contrast.py" and args.strict:
                cmd.append("--strict")
            result = subprocess.run(cmd, cwd=scripts)
            if script == "audit_contrast.py" and result.returncode != 0:
                if args.check:
                    fail("contrast check failed after fixes: review fix-log.md")
                emit(json.dumps({"status": "contrast_fail", "route": args.route}, indent=2))
                return

    contrast = latest_contrast_report(visual_audit_dir(root), slug)
    contrast_errors = 0
    if contrast and contrast.is_file():
        try:
            data = json.loads(contrast.read_text())
            contrast_errors = sum(r.get("errorCount", 0) for r in data.get("results", []))
        except json.JSONDecodeError:
            pass

    reviews = visual_audit_dir(root) / "reviews"
    review_path = None
    if reviews.is_dir():
        matches = sorted(reviews.glob(f"{slug}-review-*.md"), reverse=True)
        review_path = matches[0] if matches else None

    if review_path and review_path.is_file():
        text = review_path.read_text(encoding="utf-8")
        shots = list(screenshot_dir(root).glob(f"{slug}_*px*.png"))
        verify = [
            "",
            "## Re-verify (finalized)",
            "",
            f"**Date:** {date.today().isoformat()}",
            f"**Contrast errors:** {contrast_errors}",
            f"**Widths:** {widths_str}",
            "",
            "### Post-fix captures",
            "",
        ]
        for p in sorted(shots):
            verify.append(f"- `{p.relative_to(root)}`")
        verify.append("")
        verify.append(f"- [{'x' if contrast_errors else ' '}] `audit_contrast --check`")
        if "## Re-verify (finalized)" not in text:
            text = text.rstrip() + "\n" + "\n".join(verify) + "\n"
            review_path.write_text(text, encoding="utf-8")

    payload = {
        "status": "ok" if contrast_errors == 0 else "contrast_remaining",
        "route": args.route,
        "widths": widths_str,
        "contrast_errors": contrast_errors,
        "review_doc": str(review_path.relative_to(root)) if review_path else None,
        "fix_log": str((visual_audit_dir(root) / "fix-log.md").relative_to(root)),
    }
    emit(json.dumps(payload, indent=2))
    if args.check and contrast_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
