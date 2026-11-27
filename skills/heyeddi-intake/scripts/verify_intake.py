#!/usr/bin/env python3
"""Verify complete @heyeddi-intake intake artifacts."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from _heyeddi_paths import canonical_product_path, designs_dir, intake_dir, product_md
from _product_schema import (
    handoff_features,
    load_json,
    product_json_path,
    validate_product_json,
    validate_product_md,
)
from _skill_cli import emit, resolve_project_root

# Baseline Vue shell files allowed on scaffolded repos: intake must not add feature UI.
ALLOWED_VUE_REL = frozenset(
    {
        Path("src/App.vue"),
    }
)


def _disallowed_vue(root: Path) -> list[str]:
    disallowed: list[str] = []
    src = root / "src"
    if not src.is_dir():
        return disallowed
    for path in src.rglob("*.vue"):
        rel = path.relative_to(root)
        if rel not in ALLOWED_VUE_REL:
            disallowed.append(str(rel))
    changed = _changed_in_git(root)
    if changed is not None:
        # Views already committed belong to the app, not to this intake run.
        disallowed = [rel for rel in disallowed if rel in changed]
    return sorted(disallowed)


def _changed_in_git(root: Path) -> set[str] | None:
    """Untracked, modified, or staged files under src/. None outside a git repo."""
    git = shutil.which("git")
    if git is None:
        return None
    changed: set[str] = set()
    for args in (
        ["ls-files", "--others", "--modified", "--exclude-standard", "--", "src"],
        ["diff", "--cached", "--name-only", "--relative", "--", "src"],
    ):
        proc = subprocess.run([git, "-C", str(root), *args], capture_output=True, text=True, shell=False)
        if proc.returncode != 0:
            return None
        changed.update(proc.stdout.splitlines())
    return changed


def _check_repo_buildable(root: Path) -> tuple[bool, str]:
    if not (root / "package.json").is_file():
        return True, "no package.json: skip build gate"
    if not (root / "node_modules").is_dir():
        return True, "node_modules missing: skip build gate"
    npm = shutil.which("npm")
    if npm is None:
        return True, "npm not found: skip build gate"
    try:
        proc = subprocess.run(
            [npm, "run", "build"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=180,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"npm run build failed: {exc}"
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-600:]
        return False, tail or f"exit {proc.returncode}"
    return True, "npm run build exit 0"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify heyeddi-intake intake")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--check", action="store_true", help="Exit 1 if any check fails")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    issues: list[str] = []
    checks: list[dict] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            issues.append(f"{name}: {detail}")

    p_path = product_md(root) or canonical_product_path(root)
    if not p_path.is_file():
        record("product-md", False, "missing .heyeddi/product.md")
    else:
        text = p_path.read_text(errors="replace")
        ok, errs = validate_product_md(text)
        record("product-md-sections", ok, "; ".join(errs) if errs else "all required sections present")

    json_path = product_json_path(root)
    if not json_path.is_file():
        record("product-translation-json", False, f"missing {json_path.relative_to(root)}")
    else:
        data = load_json(json_path)
        ok, errs = validate_product_json(data)
        record("product-translation-json", ok, "; ".join(errs) if errs else "schema valid")

    intake = intake_dir(root)
    translations = list(intake.glob("translation-*.md"))
    record("translation-log", bool(translations), f"found {len(translations)} translation-*.md")

    routing_path = intake / "skill-routing.json"
    if not routing_path.is_file():
        record("skill-routing", False, "missing skill-routing.json")
    else:
        routing = load_json(routing_path)
        routes = routing.get("routes") or []
        record("skill-routing", len(routes) >= 1, f"{len(routes)} routes")
        if json_path.is_file():
            data = load_json(json_path)
            page_routes = {p["route"] for p in data.get("pages", []) if isinstance(p, dict) and p.get("route")}
            routed = {r["route"] for r in routes if isinstance(r, dict) and r.get("route")}
            missing = sorted(page_routes - routed)
            record("routing-coverage", not missing, f"missing routes: {missing}" if missing else "all pages routed")

    for feature in handoff_features(load_json(routing_path) if routing_path.is_file() else {}):
        folder = designs_dir(root) / feature
        has_wireframe = (folder / "wireframe.md").is_file()
        has_png_pair = (folder / "desktop.png").is_file() and (folder / "mobile.png").is_file()
        record(
            f"{feature}-handoff-visual",
            has_wireframe or has_png_pair,
            "wireframe.md or desktop.png+mobile.png required",
        )
        for artifact, label in (
            (folder / "mockup-brief.md", f"{feature}-brief"),
            (folder / "handoff.json", f"{feature}-handoff-json"),
        ):
            record(label, artifact.is_file(), str(artifact.relative_to(root)))

        brief = folder / "mockup-brief.md"
        if brief.is_file():
            btext = brief.read_text(errors="replace")
            record(f"{feature}-brief-implementation-spec", "Implementation spec" in btext, "section present")
            record(
                f"{feature}-brief-audience",
                "## Audience" in btext and "Primary persona:" in btext and "_(missing" not in btext,
                "audience block filled from product.md",
            )

    disallowed_vue = _disallowed_vue(root)
    if disallowed_vue:
        record(
            "no-vue-implementation",
            False,
            f"feature Vue not allowed during intake: {', '.join(disallowed_vue)} "
            "(baseline src/App.vue shell only)",
        )
    else:
        record(
            "no-vue-implementation",
            True,
            "no feature views: baseline App.vue shell OK" if (root / "src/App.vue").is_file() else "no src/**/*.vue",
        )

    build_ok, build_detail = _check_repo_buildable(root)
    record("repo-buildable", build_ok, build_detail)

    result = {
        "ok": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
        "checks": checks,
    }
    emit(json.dumps(result, indent=2))

    if args.check and issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
