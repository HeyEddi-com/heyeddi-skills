#!/usr/bin/env python3
"""Install the local-first gate as a user Cursor hook (~/.cursor)."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HOOK_FILES = ("classify_command.py", "hook_before_shell.py", "hook_before_mcp.py")


def _python() -> str:
    system = Path("/usr/bin/python3")
    if system.is_file():
        return str(system)
    found = shutil.which("python3")
    if not found:
        raise SystemExit("python3 is required to install the local-first hook")
    return found


def _cursor_dir() -> Path:
    return Path.home() / ".cursor"


def _load(path: Path) -> dict:
    if not path.is_file():
        return {"version": 1, "hooks": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {"version": 1, "hooks": {}}
    data.setdefault("version", 1)
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        data["hooks"] = {}
    return data


def _upsert(hooks: dict, event: str, command: str) -> None:
    entries = hooks.get(event)
    if not isinstance(entries, list):
        entries = []
    kept = [entry for entry in entries if not (isinstance(entry, dict) and entry.get("command") == command)]
    kept.append({"command": command, "failClosed": True, "timeout": 15})
    hooks[event] = kept


def install(cursor_dir: Path | None = None) -> Path:
    source = Path(__file__).resolve().parent
    root = cursor_dir or _cursor_dir()
    hooks_dir = root / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    for name in HOOK_FILES:
        shutil.copy2(source / name, hooks_dir / name)
    config_path = root / "hooks.json"
    config = _load(config_path)
    python = _python()
    _upsert(config["hooks"], "beforeShellExecution", f"{python} ./hooks/hook_before_shell.py")
    _upsert(config["hooks"], "beforeMCPExecution", f"{python} ./hooks/hook_before_mcp.py")
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return config_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install the local-first Cursor user hook")
    parser.add_argument("--cursor-dir", default="", help="Override ~/.cursor (tests)")
    args = parser.parse_args(argv)
    target = Path(args.cursor_dir) if args.cursor_dir else None
    path = install(target)
    print(f"Installed local-first gate in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
