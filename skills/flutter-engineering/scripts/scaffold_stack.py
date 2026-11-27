#!/usr/bin/env python3
"""Scaffold HeyEddi Flutter stacks: flutter, fastapi, firebase, or full."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from _project_detect import detect, infer_backends
from _skill_cli import emit, resolve_project_root

SCRIPTS = Path(__file__).resolve().parent
PE_SCRIPTS = SCRIPTS.parent.parent / "project-engineering" / "scripts"


def run_script(script_path: Path, root: Path, *, dry_run: bool, force: bool) -> dict:
    cmd = [sys.executable, str(script_path), "--project-root", str(root)]
    if dry_run:
        cmd.append("--dry-run")
    if force:
        cmd.append("--force")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"script": script_path.name, "status": "fail", "output": proc.stderr or proc.stdout}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"script": script_path.name, "status": "ok", "output": proc.stdout}


def resolve_stacks(root: Path, stack: str) -> list[str]:
    if stack == "auto":
        detected = detect(root)
        stacks: list[str] = []
        if detected["flutter"] or (root / "pubspec.yaml").is_file():
            stacks.append("flutter")
        elif detected["vue"]:
            stacks.append("vue")
        else:
            stacks.append("flutter")
        for b in infer_backends(root):
            if b not in stacks:
                stacks.append(b)
        return stacks

    if stack == "full":
        return ["flutter", "fastapi", "firebase"]

    return [stack]


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold HeyEddi Flutter project stacks")
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--stack",
        choices=["auto", "flutter", "fastapi", "firebase", "full"],
        default="auto",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    stacks = resolve_stacks(root, args.stack)
    results: list[dict] = []

    local_mapping = {"flutter": SCRIPTS / "scaffold_flutter.py"}
    pe_mapping = {
        "fastapi": PE_SCRIPTS / "scaffold_fastapi.py",
        "firebase": PE_SCRIPTS / "scaffold_firebase.py",
    }

    for name in stacks:
        if name in local_mapping:
            results.append(run_script(local_mapping[name], root, dry_run=args.dry_run, force=args.force))
        elif name in pe_mapping and pe_mapping[name].is_file():
            results.append(run_script(pe_mapping[name], root, dry_run=args.dry_run, force=args.force))

    results.append(run_script(SCRIPTS / "scaffold_heyeddi.py", root, dry_run=args.dry_run, force=args.force))

    failed = any(result.get("status") == "fail" for result in results)
    emit(
        json.dumps(
            {
                "status": "fail" if failed else "ok",
                "stacks": stacks,
                "detected": detect(root),
                "dry_run": args.dry_run,
                "results": results,
                "next": "ensure_flutter / ensure_python → dev_server_info",
            },
            indent=2,
        )
    )
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
