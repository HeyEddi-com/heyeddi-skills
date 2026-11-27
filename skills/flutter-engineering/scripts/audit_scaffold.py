#!/usr/bin/env python3
"""Audit Flutter, FastAPI, and Firebase layers for HeyEddi Flutter apps."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _project_detect import BACKEND_DIR, detect, fastapi_root, has_fastapi, has_firebase, has_flutter, is_existing_app
from _skill_cli import emit, resolve_project_root

FLUTTER_REQUIRED = (
    "pubspec.yaml",
    "analysis_options.yaml",
    "lib/main.dart",
    "lib/app.dart",
    "lib/router/app_router.dart",
    "lib/theme/app_theme.dart",
    "test/widget_test.dart",
)

FLUTTER_RECOMMENDED = (
    "lib/config/env.dart",
    "lib/services/api_client.dart",
    "lib/widgets/app_shell.dart",
    "lib/screens/settings_screen.dart",
)

FASTAPI_REQUIRED = (
    f"{BACKEND_DIR}/pyproject.toml",
    f"{BACKEND_DIR}/app/main.py",
    f"{BACKEND_DIR}/tests/test_health.py",
)

FASTAPI_RECOMMENDED = ("openapi.json",)

FIREBASE_REQUIRED = ("firebase.json", "firestore.rules")

FIREBASE_RECOMMENDED = (".firebaserc", "firestore.indexes.json", ".env.firebase.example")


def _audit_flutter(root: Path) -> dict:
    missing_required: list[str] = []
    missing_recommended: list[str] = []
    warnings: list[str] = []

    existing = is_existing_app(root)
    required = ("pubspec.yaml", "lib/main.dart") if existing else FLUTTER_REQUIRED
    for rel in required:
        if not (root / rel).is_file():
            missing_required.append(rel)
    for rel in () if existing else FLUTTER_RECOMMENDED:
        if not (root / rel).is_file():
            missing_recommended.append(rel)

    if not (root / ".dart_tool").is_dir() and not (root / "pubspec.lock").is_file():
        warnings.append("Flutter deps may be missing: run ensure_flutter")

    status = "ok" if not missing_required else "incomplete"
    if status == "ok" and (warnings or missing_recommended):
        status = "needs_attention"

    return {
        "status": status,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "warnings": warnings,
    }


def _audit_fastapi(root: Path) -> dict:
    missing_required: list[str] = []
    missing_recommended: list[str] = []
    warnings: list[str] = []

    for rel in FASTAPI_REQUIRED:
        if not (root / rel).is_file():
            missing_required.append(rel)
    for rel in FASTAPI_RECOMMENDED:
        if not (root / rel).is_file():
            missing_recommended.append(rel)

    api = fastapi_root(root)
    if not (api / ".venv").is_dir():
        warnings.append("Python venv/deps may be missing: run ensure_python via @project-engineering")

    status = "ok" if not missing_required else "incomplete"
    return {
        "status": status,
        "backend_root": str(api),
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "warnings": warnings,
    }


def _audit_firebase(root: Path) -> dict:
    missing_required: list[str] = []
    missing_recommended: list[str] = []

    for rel in FIREBASE_REQUIRED:
        if not (root / rel).is_file():
            missing_required.append(rel)
    for rel in FIREBASE_RECOMMENDED:
        if not (root / rel).is_file():
            missing_recommended.append(rel)

    status = "ok" if not missing_required else "incomplete"
    return {
        "status": status,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "warnings": [],
    }


def audit(root: Path) -> dict:
    stacks = detect(root)
    layers: dict = {"detected": stacks}
    next_steps: list[str] = []

    if stacks["flutter"] or has_flutter(root) or (root / "pubspec.yaml").is_file():
        layers["flutter"] = _audit_flutter(root)
        if layers["flutter"]["status"] != "ok":
            next_steps.append("scaffold_stack --stack flutter")

    if stacks["fastapi"] or has_fastapi(root):
        layers["fastapi"] = _audit_fastapi(root)
        if layers["fastapi"]["status"] != "ok":
            next_steps.append("scaffold_stack --stack fastapi")

    if stacks["firebase"] or has_firebase(root):
        layers["firebase"] = _audit_firebase(root)
        if layers["firebase"]["status"] != "ok":
            next_steps.append("scaffold_stack --stack firebase")

    statuses = [v["status"] for k, v in layers.items() if k != "detected" and isinstance(v, dict)]
    overall = "ok"
    if any(s == "incomplete" for s in statuses):
        overall = "incomplete"
    elif any(s == "needs_attention" for s in statuses):
        overall = "needs_attention"

    return {
        "project_root": str(root),
        "status": overall,
        "layers": layers,
        "next_steps": next_steps or ["dev_server_info for local URLs"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit HeyEddi Flutter project scaffold")
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    emit(json.dumps(audit(root), indent=2))


if __name__ == "__main__":
    main()
