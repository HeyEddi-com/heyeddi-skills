#!/usr/bin/env python3
"""Add or repair HeyEddi standard Flutter scaffold files."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from _project_detect import is_existing_app, merge_stack
from _skill_cli import emit, resolve_project_root, run_command

SCAFFOLD_ROOT = Path(__file__).resolve().parent.parent / "scaffold" / "flutter"

# The only files added to an app the scaffold did not create.
SUPPORT_FILES = ("analysis_options.yaml", "lib/config/env.dart", "lib/services/api_client.dart")
DEPENDENCIES = {"flutter_riverpod": "^2.6.1", "go_router": "^14.6.2", "dio": "^5.7.0"}
LINTS = ("flutter_lints", "^5.0.0")


def copy_tree(src_root: Path, dest_root: Path, *, force: bool, dry_run: bool) -> tuple[list[str], list[str]]:
    created: list[str] = []
    skipped: list[str] = []
    for src in src_root.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(src_root)
        dest = dest_root / rel
        if dest.exists() and not force:
            skipped.append(str(rel))
            continue
        if dry_run:
            created.append(str(rel))
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        created.append(str(rel))
    return created, skipped


def add_support_files(root: Path, *, dry_run: bool) -> tuple[list[str], list[str]]:
    created: list[str] = []
    skipped: list[str] = []
    env = root / "lib" / "config" / "env.dart"
    foreign_env = env.is_file() and "kApiBaseUrl" not in env.read_text(encoding="utf-8", errors="replace")
    for rel in SUPPORT_FILES:
        dest = root / rel
        if dest.exists() or (rel.endswith("api_client.dart") and foreign_env):
            skipped.append(rel)
            continue
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SCAFFOLD_ROOT / rel, dest)
        created.append(rel)
    return created, skipped


def missing_dependencies(root: Path, *, lints: bool) -> list[str]:
    pubspec = (root / "pubspec.yaml").read_text(encoding="utf-8", errors="replace")

    def absent(name: str) -> bool:
        return not re.search(rf"(?m)^\s+{name}:", pubspec)

    specs = [f"{name}:{version}" for name, version in DEPENDENCIES.items() if absent(name)]
    if lints and absent(LINTS[0]):
        specs.append(f"dev:{LINTS[0]}:{LINTS[1]}")
    return specs


def add_dependencies(root: Path, specs: list[str]) -> str | None:
    """Run `flutter pub add`. Returns an error message, or None on success."""
    if not shutil.which("flutter"):
        return "flutter CLI not found: install the Flutter SDK, then rerun"
    output = run_command(["flutter", "pub", "add", *specs], root, timeout=300)
    if output.startswith("[exit") or output.startswith("[error]"):
        return output[:4000]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold Flutter engineering baseline")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    result: dict = {"status": "ok", "stack": "flutter", "dry_run": args.dry_run}
    if is_existing_app(root):
        created, skipped = add_support_files(root, dry_run=args.dry_run)
        specs = missing_dependencies(root, lints="analysis_options.yaml" in created)
        result["existing_app"] = True
        result["dependencies"] = specs
        if specs and not args.dry_run:
            error = add_dependencies(root, specs)
            if error:
                result.update(status="fail", error=error)
    else:
        created, skipped = copy_tree(SCAFFOLD_ROOT, root, force=args.force, dry_run=args.dry_run)

    stack_src = Path(__file__).resolve().parent.parent / "scaffold" / "stack-flutter.json"
    if merge_stack(root / ".heyeddi" / "stack.json", stack_src, dry_run=args.dry_run):
        created.append(".heyeddi/stack.json")
    else:
        skipped.append(".heyeddi/stack.json")

    result.update(created=created, skipped=skipped, next="ensure_flutter \u2192 dev_server_info")
    emit(json.dumps(result, indent=2))
    if result["status"] == "fail":
        sys.exit(1)


if __name__ == "__main__":
    main()
