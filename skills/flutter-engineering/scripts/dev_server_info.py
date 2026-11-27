#!/usr/bin/env python3
"""Return how to run Flutter web, FastAPI, and Firebase emulators."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _project_detect import detect, fastapi_root, has_fastapi, has_firebase, has_flutter, parse_api_port, parse_web_port
from _skill_cli import emit, resolve_project_root


def flutter_server(root: Path, route: str | None) -> dict | None:
    if not has_flutter(root) and not (root / "pubspec.yaml").is_file():
        return None
    if not (root / "pubspec.yaml").is_file():
        return {"name": "flutter", "status": "incomplete", "reason": "no pubspec.yaml"}

    port = parse_web_port(root)
    base = f"http://127.0.0.1:{port}"
    info = {
        "name": "flutter",
        "status": "ok",
        "command": f"flutter run -d web-server --web-port={port} --web-hostname=127.0.0.1",
        "cwd": str(root),
        "url": base,
        "port": port,
        "platforms": ["web", "android", "ios"],
        "mobile_command": "flutter run",
        "has_pub_get": (root / "pubspec.lock").is_file() or (root / ".dart_tool").is_dir(),
        "note": "Web preview for @visual-auditor; set DEV_SERVER_URL or FLUTTER_WEB_URL to url below",
    }
    if route:
        r = route if route.startswith("/") else f"/{route}"
        info["example_url"] = base.rstrip("/") + f"#{r}" if r != "/" else base
        info["go_router_note"] = "Flutter web uses path URLs when configured; default scaffold uses path routes"
        info["example_url"] = base.rstrip("/") + r
    return info


def fastapi_server(root: Path) -> dict | None:
    if not has_fastapi(root) and not (fastapi_root(root) / "app" / "main.py").is_file():
        return None
    api = fastapi_root(root)
    port = parse_api_port(root)
    base = f"http://127.0.0.1:{port}"
    return {
        "name": "fastapi",
        "status": "ok",
        "command": f"poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port {port}",
        "cwd": str(api),
        "url": base,
        "port": port,
        "docs_url": f"{base}/docs",
        "health_url": f"{base}/health",
        "note": "Mobile/web clients use kApiBaseUrl in lib/config/env.dart (default :8090)",
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
        "note": "Add firebase_core + cloud_firestore to pubspec when using Firebase backend",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Local dev server instructions for Flutter stacks")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--route", default=None, help="GoRouter path e.g. /settings")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    servers = []
    for builder in (
        lambda: flutter_server(root, args.route),
        lambda: fastapi_server(root),
        lambda: firebase_server(root),
    ):
        info = builder()
        if info:
            servers.append(info)

    steps = []
    if any(s["name"] == "flutter" and not s.get("has_pub_get") for s in servers):
        steps.append("ensure_flutter")
    if any(s["name"] == "fastapi" for s in servers):
        steps.append("ensure_python (via @project-engineering)")
    steps.append("Start each server in its own terminal")

    emit(
        json.dumps(
            {
                "status": "ok" if servers else "skip",
                "detected": detect(root),
                "prerequisites": steps,
                "servers": servers,
                "visual_audit_env": "FLUTTER_WEB_URL=http://127.0.0.1:<web_port>",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
