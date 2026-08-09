#!/usr/bin/env python3
"""Write ephemeral CI fails report under .heyeddi/docs/pr-<N>-ci-fails.md."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _skill_cli import emit, resolve_project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Write CI fails markdown report")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--input",
        default=None,
        help="Raw JSON from fetch_failing_checks (default pr-<N>-ci-fails-raw.json)",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    docs = root / ".heyeddi" / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    raw_path = Path(args.input) if args.input else docs / f"pr-{args.pr}-ci-fails-raw.json"
    if not raw_path.is_absolute():
        raw_path = root / raw_path
    report_path = docs / f"pr-{args.pr}-ci-fails.md"
    if report_path.exists() and not args.force:
        emit(
            json.dumps(
                {
                    "status": "exists",
                    "path": str(report_path.relative_to(root)),
                    "hint": "Pass --force to overwrite",
                },
                indent=2,
            )
        )
        return

    data: dict[str, Any] = {}
    if raw_path.is_file():
        data = json.loads(raw_path.read_text(encoding="utf-8"))

    failing = data.get("failing") or []
    lines = [
        f"# PR #{args.pr} CI fails",
        "",
        "**Ephemeral:** do not commit this file. GitHub Checks are the SSOT.",
        "",
        f"- Head: `{data.get('head_sha') or 'unknown'}`",
        f"- Ref: `{data.get('head_ref') or 'unknown'}`",
        f"- URL: {data.get('url') or '(none)'}",
        "",
        "## Failing checks",
        "",
    ]
    if not failing:
        lines.append("_No failing checks in raw payload. Re-run `fetch_failing_checks` or inspect GitHub._")
        lines.append("")
    else:
        for item in failing:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or "(unnamed)"
            state = item.get("state") or "?"
            url = item.get("detailsUrl") or ""
            desc = item.get("description") or ""
            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"- State: `{state}`")
            if desc:
                lines.append(f"- Detail: {desc}")
            if url:
                lines.append(f"- Link: {url}")
            lines.append("- Likely cause: _(fill from logs)_")
            lines.append("- Proposed fix: _(fill after reading evidence)_")
            lines.append("")

    lines.extend(
        [
            "## Hosted App option",
            "",
            "Comment `/heyeddi fails` on the PR for HeyEddi App analysis of failed Checks "
            "(billable when `on_ci_failure` / command path applies).",
            "",
            "## Merge lock",
            "",
            "Never `gh pr merge` without **authorize merge** in the current turn.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    emit(
        json.dumps(
            {
                "status": "ok",
                "path": str(report_path.relative_to(root)),
                "failing_count": len(failing),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
