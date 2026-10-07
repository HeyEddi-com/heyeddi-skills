#!/usr/bin/env python3
"""Record a pillar opinion and request sibling product/UX/design responses."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime

from _skill_cli import emit, fail, resolve_project_root
from _workflow_paths import (
    VALID_PILLARS,
    active_context_path,
    opinion_path,
    sync_log_path,
    workflow_dir,
)

SIBLING_PROMPTS = {
    "product": ("ux", "design"),
    "ux": ("product", "design"),
    "design": ("product", "ux"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Append cross-pillar opinion")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--pillar", required=True, choices=sorted(VALID_PILLARS))
    parser.add_argument("--route", required=True)
    parser.add_argument("--opinion", required=True, help="What this pillar concludes for this route")
    parser.add_argument("--docs-updated", default="", help="Comma-separated paths maintained")
    parser.add_argument("--request-pillars", default="", help="Comma-separated siblings that must respond")
    parser.add_argument("--feature", default=None)
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    if not workflow_dir(root).is_dir():
        fail("missing .heyeddi/docs/workflow/: run init_workflow_sync first")

    docs = [d.strip() for d in args.docs_updated.split(",") if d.strip()]
    requested = [p.strip() for p in args.request_pillars.split(",") if p.strip()]
    if not requested:
        requested = [p for p in SIBLING_PROMPTS[args.pillar]]

    ts = datetime.now().isoformat(timespec="seconds")
    feature = args.feature or args.route.strip("/").replace("/", "-") or "home"

    block = [
        f"### {ts}: `{args.route}` ({args.pillar})",
        "",
        f"**Opinion:** {args.opinion}",
        "",
        f"**Docs updated:** {', '.join(f'`{d}`' for d in docs) if docs else ' - '}",
        "",
        f"**Requests:** {', '.join(f'`@{p}`' for p in requested)} must append opinion for this route",
        "",
    ]

    path = opinion_path(root, args.pillar)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        path.write_text(f"# {args.pillar.title()} opinions\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(block))

    log = sync_log_path(root)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"- `{ts}` **{args.pillar}** `{args.route}` → requests {', '.join(requested)}\n")

    active_context_path(root).write_text(
        json.dumps(
            {
                "route": args.route,
                "feature": feature,
                "last_pillar": args.pillar,
                "updated": date.today().isoformat(),
                "pending_pillars": requested,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    emit(
        json.dumps(
            {
                "status": "ok",
                "pillar": args.pillar,
                "route": args.route,
                "opinion_file": str(path.relative_to(root)),
                "request_pillars": requested,
                "next": [
                    f"Invoke sibling skills so each runs load_workflow_context + append_pillar_opinion for {args.route}",
                    "Do not mark route done until all requested pillars have entries in opinions/",
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
