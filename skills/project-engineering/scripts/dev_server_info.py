#!/usr/bin/env python3
"""Return how to run local dev servers (Vue, FastAPI, Firebase emulators)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _project_detect import detect, fastapi_root, has_fastapi, has_firebase, has_vue
from _skill_cli import emit, resolve_project_root

DEFAULT_VITE_PORT = 5173
DEFAULT_API_PORT = 8090


def parse_api_port(root: Path) -> int:
    stack = root / ".heyeddi" / "stack.json"
    if stack.is_file():
        try:
            data = json.loads(stack.read_text())
            if data.get("api_port") is not None:
                return int(data["api_port"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    return DEFAULT_API_PORT


def parse_vite_port(root: Path) -> int:
    cfg = root / "vite.config.ts"
    if not cfg.is_file():
        return DEFAULT_VITE_PORT
    match = re.search(r"port\s*:\s*(\d+)", cfg.read_text())
    return int(match.group(1)) if match else DEFAULT_VITE_PORT


def vue_server(root: Path, route: str | None) -> dict | None:
    if not has_vue(root) and not (root / "package.json").is_file():
        return None
    pkg_path = root / "package.json"
    if not pkg_path.is_file():
        return {"name": "vue", "status": "incomplete", "reason": "no package.json"}
    pkg = json.loads(pkg_path.read_text())
    if "dev" not in pkg.get("scripts", {}):
        return {"name": "vue", "status": "incomplete", "reason": "no npm run dev"}

    port = parse_vite_port(root)
    url = f"http://localhost:{port}"
    info = {
        "name": "vue",
        "status": "ok",
        "command": "npm run dev",
        "cwd": str(root),
        "url": url,
        "port": port,
        "has_node_modules": (root / "node_modules").is_dir(),
    }
    if route:
        r = route if route.startswith("/") else f"/{route}"
        info["example_url"] = url.rstrip("/") + r
    return info


def fastapi_server(root: Path) -> dict | None:
    if not has_fastapi(root) and not (fastapi_root(root) / "app" / "main.py").is_file():
        return None
    api = fastapi_root(root)
    port = parse_api_port(root)
    base = f"http://localhost:{port}"
    return {
        "name": "fastapi",
        "status": "ok",
        "command": f"poetry run uvicorn app.main:app --reload --port {port}",
        "cwd": str(api),
        "url": base,
        "port": port,
        "docs_url": f"{base}/docs",
        "health_url": f"{base}/health",
        "note": "Run from backend/ after ensure_python; port from .heyeddi/stack.json api_port (default 8090)",
    }


def firebase_server(root: Path) -> dict | None:
    if not has_firebase(root):
        return None
    return {
        "name": "firebase",
        "status": "ok",
        "command": "firebase emulators:start",
        "cwd": str(root),
        "emulator_ui": "http://localhost:4000",
        "firestore_port": 8080,
        "auth_port": 9099,
        "note": "Requires Firebase CLI (npm i -g firebase-tools) and firebase login",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Local dev server instructions")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--route", default=None, help="Vue route e.g. /settings")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    servers = []
    for builder in (lambda: vue_server(root, args.route), lambda: fastapi_server(root), lambda: firebase_server(root)):
        info = builder()
        if info:
            servers.append(info)

    steps = []
    if any(s["name"] == "vue" and not s.get("has_node_modules") for s in servers):
        steps.append("ensure_npm")
    if any(s["name"] == "fastapi" for s in servers):
        steps.append("ensure_python")
    steps.append("Start each server in its own terminal (see servers[].command)")

    emit(
        json.dumps(
            {
                "status": "ok" if servers else "skip",
                "detected": detect(root),
                "prerequisites": steps,
                "servers": servers,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
