#!/usr/bin/env python3
"""Add HeyEddi FastAPI backend under backend/."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from _project_detect import load_json
from _skill_cli import emit, resolve_project_root

SCAFFOLD = Path(__file__).resolve().parent.parent / "scaffold" / "fastapi"
BACKEND = "backend"


def _cors_origins(root: Path) -> list[str]:
    ports: set[int] = {5173}
    stack_path = root / ".heyeddi" / "stack.json"
    if stack_path.is_file():
        cfg = load_json(stack_path) or {}
        web_port = cfg.get("web_port")
        if cfg.get("frontend") == "flutter":
            ports = {web_port or 8085}
        elif web_port:
            ports.add(web_port)
    # The browser treats localhost and 127.0.0.1 as different origins.
    return sorted(f"http://{host}:{port}" for port in ports for host in ("localhost", "127.0.0.1"))


def _patch_cors(root: Path) -> None:
    main_py = root / BACKEND / "app" / "main.py"
    if not main_py.is_file():
        return
    origins_repr = json.dumps(_cors_origins(root))
    text = main_py.read_text(encoding="utf-8")
    text = re.sub(r"allow_origins=\[[^\]]*\]", f"allow_origins={origins_repr}", text, count=1)
    main_py.write_text(text, encoding="utf-8")


def _merge_stack_backends(root: Path) -> None:
    stack_path = root / ".heyeddi" / "stack.json"
    if not stack_path.is_file():
        return
    cfg = load_json(stack_path) or {}
    backends = list(cfg.get("backends") or [])
    if "fastapi" not in backends:
        backends.append("fastapi")
        cfg["backends"] = backends
        stack_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def copy_tree_files(src_root: Path, dest_root: Path, *, force: bool, dry_run: bool) -> tuple[list[str], list[str]]:
    created: list[str] = []
    skipped: list[str] = []
    for src in src_root.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(src_root)
        if rel.parts[0] == "openapi.json":
            continue
        dest = dest_root / rel
        if dest.exists() and not force:
            skipped.append(str(dest.relative_to(dest_root.parent.parent)) if dest_root.name == BACKEND else str(rel))
            continue
        if dry_run:
            created.append(f"{BACKEND}/{rel}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        created.append(f"{BACKEND}/{rel}")
    return created, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold FastAPI backend")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    backend = root / BACKEND

    created, skipped = copy_tree_files(SCAFFOLD, backend, force=args.force, dry_run=args.dry_run)

    openapi_dest = root / "openapi.json"
    openapi_src = SCAFFOLD / "openapi.json"
    if openapi_src.is_file():
        if not openapi_dest.exists() or args.force:
            if not args.dry_run:
                shutil.copy2(openapi_src, openapi_dest)
            created.append("openapi.json")
        else:
            skipped.append("openapi.json")

    if not args.dry_run:
        _merge_stack_backends(root)
        _patch_cors(root)

    stack_cfg = root / ".heyeddi" / "stack.json"
    if not stack_cfg.exists() and not args.dry_run:
        stack_cfg.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            Path(__file__).resolve().parent.parent / "scaffold" / "stack-fastapi.json",
            stack_cfg,
        )
        created.append(".heyeddi/stack.json")

    emit(
        json.dumps(
            {
                "status": "ok",
                "stack": "fastapi",
                "dry_run": args.dry_run,
                "created": created,
                "skipped": skipped,
                "next": "Run ensure_python then dev_server_info",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
