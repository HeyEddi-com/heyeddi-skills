#!/usr/bin/env python3
"""Load the living eddi-ci.yaml policy contract for @heyeddi-ci-config.

Prefer the production (or override) JSON endpoint so skill packages never ship a
stale knob table. Fallbacks: local heyeddi-ci checkout, then public docs text.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_CONTRACT_URL = "https://cihook.heyeddi.com/api/public/eddi-ci-policy"
DEFAULT_DOCS_URL = "https://ci.heyeddi.com/docs#policy"


def _emit(data: Any) -> None:
    print(json.dumps(data, indent=2))


def _fetch_json(url: str, timeout: float = 12.0) -> dict[str, Any] | None:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "heyeddi-ci-config-skill/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 — fixed product URL
            body = resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"_error": f"fetch_failed: {exc}", "_url": url}
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"_error": "invalid_json", "_url": url, "_preview": body[:400]}
    if not isinstance(data, dict):
        return {"_error": "expected_object", "_url": url}
    return data


def _from_local_heyeddi_ci(root: Path) -> dict[str, Any] | None:
    """Import public_policy_contract from a heyeddi-ci checkout when available."""
    backend = root / "backend"
    if not (backend / "app" / "policy_insights.py").is_file():
        return None
    sys.path.insert(0, str(backend))
    try:
        from app.policy_insights import public_policy_contract  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001
        return {"_error": f"local_import_failed: {exc}", "_heyeddi_ci_root": str(root)}
    try:
        contract = public_policy_contract()
    except Exception as exc:  # noqa: BLE001
        return {"_error": f"local_contract_failed: {exc}", "_heyeddi_ci_root": str(root)}
    if isinstance(contract, dict):
        contract = {**contract, "source": "local_heyeddi_ci", "heyeddi_ci_root": str(root)}
    return contract


def _candidate_heyeddi_ci_roots(explicit: str | None, project_root: Path | None) -> list[Path]:
    roots: list[Path] = []
    if explicit:
        roots.append(Path(explicit).expanduser().resolve())
    env = os.environ.get("HEYEDDI_CI_ROOT")
    if env:
        roots.append(Path(env).expanduser().resolve())
    # Common monorepo layouts relative to the consumer project or CWD.
    anchors = [project_root] if project_root else []
    anchors.append(Path.cwd())
    for anchor in anchors:
        if anchor is None:
            continue
        for rel in (
            Path("heyeddi-ci"),
            Path("heyeddi-tool/heyeddi-ci"),
            Path("../heyeddi-ci"),
            Path("../../heyeddi-ci"),
            Path("../../../heyeddi-tool/heyeddi-ci"),
        ):
            roots.append((anchor / rel).resolve())
    # Dedupe while preserving order.
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in roots:
        if path in seen:
            continue
        seen.add(path)
        ordered.append(path)
    return ordered


def _docs_fallback() -> dict[str, Any]:
    """Last resort: point the agent at the human docs page."""
    return {
        "schema_version": "unknown",
        "source": "docs_fallback",
        "docs_url": DEFAULT_DOCS_URL,
        "contract_url": DEFAULT_CONTRACT_URL,
        "guide": (
            "Could not load the machine-readable contract. Open the docs URL and author "
            "eddi-ci.yaml only from documented keys. Keep on_ci_failure false and pipeline "
            "empty unless the user opts in."
        ),
        "knobs": [],
        "rules": [
            "Only documented keys are accepted.",
            "Safe defaults: runners off, on_ci_failure off, allow_external_prs off.",
        ],
        "minimal_example": (
            'version: "1.0"\n'
            "policy:\n"
            "  allow_external_prs: false\n"
            "ai_review:\n"
            "  validation_max_attempts: 5\n"
            "  on_ci_failure: false\n"
            "pipeline: {}\n"
        ),
        "safe_defaults": {
            "ai_review.on_ci_failure": False,
            "policy.allow_external_prs": False,
            "pipeline": {},
        },
        "warning": "Contract fetch failed — re-run after network access or pass --heyeddi-ci-root.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--heyeddi-ci-root", default=None)
    parser.add_argument("--url", default=None, help="Override contract URL")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve() if args.project_root else None

    for root in _candidate_heyeddi_ci_roots(args.heyeddi_ci_root, project_root):
        if not root.is_dir():
            continue
        local = _from_local_heyeddi_ci(root)
        if local and "knobs" in local and not local.get("_error"):
            _emit(local)
            return 0

    url = args.url or os.environ.get("HEYEDDI_CI_POLICY_URL") or DEFAULT_CONTRACT_URL
    remote = _fetch_json(url)
    if remote and "knobs" in remote and not remote.get("_error"):
        remote = {**remote, "source": "remote_api", "fetched_url": url}
        _emit(remote)
        return 0

    fallback = _docs_fallback()
    if remote and remote.get("_error"):
        fallback["fetch_error"] = remote
    _emit(fallback)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
