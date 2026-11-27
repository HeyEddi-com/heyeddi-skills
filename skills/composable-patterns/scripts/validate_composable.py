#!/usr/bin/env python3
"""Validate Vue composable conventions for FastAPI JWT and Firebase client patterns."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _skill_cli import emit, fail, resolve_project_root

USE_EXPORT = re.compile(r"export\s+(?:async\s+)?function\s+(use[A-Z]\w+)|export\s+const\s+(use[A-Z]\w+)")
REF_OR_REACTIVE = re.compile(r"\b(ref|reactive|computed|shallowRef)\s*(<[^()]*>)?\s*\(")
LOADING_STATE = re.compile(r"\b(loading|isLoading|pending)\b")
ERROR_STATE = re.compile(r"\b(error|lastError|fetchError)\b")
LOCAL_STORAGE_REFRESH = re.compile(r"localStorage\.(setItem|getItem)\s*\([^)]*refresh", re.I)
ADMIN_SDK = re.compile(r"firebase-admin|from\s+['\"]firebase-admin")
MIXED_AUTH = re.compile(r"Bearer|Authorization|getAuth|signInWith")
FETCH_INLINE = re.compile(r"\bfetch\s*\(")


def validate_composable_text(text: str, *, path_label: str) -> dict:
    name_match = USE_EXPORT.search(text)
    composable_name = (name_match.group(1) or name_match.group(2)) if name_match else None

    checks: dict[str, bool | str] = {
        "exports_use_composable": bool(composable_name),
        "composable_name": composable_name or "missing",
        "no_admin_sdk": not ADMIN_SDK.search(text),
        "no_refresh_token_in_local_storage": not LOCAL_STORAGE_REFRESH.search(text),
        "has_error_handling": bool(re.search(r"\bcatch\b", text) or re.search(r"\bthrow\b", text)),
    }

    if composable_name:
        checks["uses_vue_reactivity"] = bool(REF_OR_REACTIVE.search(text))
        # Data-fetch composables should expose loading + error refs
        if FETCH_INLINE.search(text) or "fetchApi" in text or "/api" in text:
            checks["exposes_loading_state"] = bool(LOADING_STATE.search(text))
            checks["exposes_error_state"] = bool(ERROR_STATE.search(text))

    # Flag mixing JWT headers and Firebase auth in one file
    has_jwt = bool(re.search(r"Authorization|Bearer|accessToken", text))
    has_firebase = bool(re.search(r"getAuth|signInWith|firebase/auth", text))
    checks["single_auth_pattern"] = not (has_jwt and has_firebase)

    failed = [
        key
        for key, value in checks.items()
        if key not in ("composable_name",) and value is False
    ]
    return {
        "path": path_label,
        "checks": checks,
        "ok": not failed,
        "failed": failed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate composable conventions")
    parser.add_argument("--path", required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--check", action="store_true", help="Exit 1 if validation fails")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    target = (root / args.path).resolve()
    if not target.is_file():
        emit(json.dumps({"status": "SKIP", "reason": f"file not found: {target}"}, indent=2))
        return

    result = validate_composable_text(
        target.read_text(encoding="utf-8", errors="replace"),
        path_label=str(target.relative_to(root)),
    )
    emit(json.dumps(result, indent=2))

    if args.check and not result.get("ok"):
        fail(
            "Composable validation failed: "
            + ", ".join(result.get("failed") or [])
            + ". See context/ANTI_PATTERNS.md and fastapi-jwt.md."
        )


if __name__ == "__main__":
    main()
