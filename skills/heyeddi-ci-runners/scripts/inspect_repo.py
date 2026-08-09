#!/usr/bin/env python3
"""Read-only scan: HeyEddi product signals, languages, likely test commands."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "coverage",
    "__pycache__",
    ".turbo",
}

def _walk_files(root: Path, limit: int = 4000) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        out.append(path)
        if len(out) >= limit:
            break
    return out


def _text_mentions_heyeddi(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:20_000]
    except OSError:
        return False
    return bool(
        re.search(
            r"heyeddi|hey\s*eddi|ci\.heyeddi\.com|cihook\.heyeddi|@heyeddi|HeyEddi-com",
            text,
            re.I,
        )
    )


def detect_heyeddi_products(root: Path) -> dict:
    """Evidence that this repo already uses HeyEddi products → ok to add eddi-ci.yaml."""
    evidence: list[dict[str, str]] = []

    heyeddi_dir = root / ".heyeddi"
    if heyeddi_dir.is_dir():
        evidence.append({"signal": ".heyeddi/", "detail": "HeyEddi workspace folder present"})

    skills_dir = root / ".agents" / "skills"
    if skills_dir.is_dir():
        heyeddi_skills = sorted(
            p.name for p in skills_dir.iterdir() if p.is_dir() and p.name.startswith("heyeddi-")
        )
        if heyeddi_skills:
            evidence.append(
                {
                    "signal": ".agents/skills/heyeddi-*",
                    "detail": "installed: " + ", ".join(heyeddi_skills[:12]),
                }
            )

    lock = root / "skills-lock.json"
    if lock.is_file():
        try:
            raw = lock.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            raw = ""
        low = raw.lower()
        # Accept current packs + legacy hub slug (GitHub rename redirect).
        if any(
            needle in low
            for needle in (
                "heyeddi-com/heyeddi-skills",
                "heyeddi-com/heyeddi-ci-skills",
                "heyeddi-com/skills",  # legacy slug before rename
            )
        ):
            evidence.append(
                {
                    "signal": "skills-lock.json",
                    "detail": "pins HeyEddi-com/heyeddi-skills (or CI/legacy hub)",
                }
            )

    for rel in ("PRODUCT.md", ".heyeddi/product.md", "README.md"):
        path = root / rel
        if path.is_file() and _text_mentions_heyeddi(path):
            evidence.append({"signal": rel, "detail": "mentions HeyEddi product"})

    # Package / project name heuristics
    for name in ("package.json", "pyproject.toml"):
        path = root / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:8_000]
        except OSError:
            continue
        if re.search(r"heyeddi", text, re.I):
            evidence.append({"signal": name, "detail": "package/project identity mentions heyeddi"})

    # Deduplicate by signal
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in evidence:
        if item["signal"] in seen:
            continue
        seen.add(item["signal"])
        unique.append(item)

    return {
        "uses_heyeddi_product": bool(unique),
        "evidence": unique,
        "recommend_eddi_ci_yaml": bool(unique),
        "note": (
            "When uses_heyeddi_product is true and eddi-ci.yaml is missing, create a "
            "Reviewer-only safe file (billable knobs off, empty pipeline) unless the user declines."
            if unique
            else "No HeyEddi product markers found — do not create eddi-ci.yaml without explicit opt-in."
        ),
    }


def inspect(root: Path) -> dict:
    files = _walk_files(root)
    rel = [p.relative_to(root).as_posix() for p in files]
    suffixes = {Path(p).suffix for p in rel}

    languages: list[str] = []
    likely_commands: list[dict[str, str]] = []
    path_hints: list[str] = []

    if {".py"} & suffixes or any(p.endswith("pyproject.toml") or p.endswith("requirements.txt") for p in rel):
        languages.append("python")
        if any("pytest" in p or p.endswith("tests/") or "/tests/" in p for p in rel) or any(
            p.endswith("pyproject.toml") for p in rel
        ):
            likely_commands.append({"language": "python", "run": "pytest", "evidence": "python/tests or pyproject"})
        tops = sorted({p.split("/", 1)[0] for p in rel if p.endswith(".py") and "/" in p})[:4]
        path_hints.extend(f"{t}/**" for t in tops if t not in {"tests", "test"})

    if {".ts", ".tsx", ".js", ".jsx", ".vue"} & suffixes or "package.json" in rel:
        languages.append("node")
        pkg = root / "package.json"
        scripts: dict = {}
        if pkg.is_file():
            try:
                scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts") or {}
            except (OSError, json.JSONDecodeError):
                scripts = {}
        for name in ("test", "test:unit", "test:ci"):
            if name in scripts:
                likely_commands.append(
                    {
                        "language": "node",
                        "run": f"npm run {name}" if name != "test" else "npm test",
                        "evidence": f"package.json scripts.{name}",
                    }
                )
                break
        tops = sorted(
            {
                p.split("/", 1)[0]
                for p in rel
                if p.endswith((".ts", ".tsx", ".js", ".jsx", ".vue")) and "/" in p
            }
        )[:4]
        path_hints.extend(f"{t}/**" for t in tops if t not in {"node_modules"})

    if {".go"} & suffixes:
        languages.append("go")
        likely_commands.append({"language": "go", "run": "go test ./...", "evidence": ".go files"})
    if {".rs"} & suffixes or "Cargo.toml" in rel:
        languages.append("rust")
        likely_commands.append({"language": "rust", "run": "cargo test", "evidence": "Cargo.toml / .rs"})

    has_eddi = (root / "eddi-ci.yaml").is_file()
    heyeddi = detect_heyeddi_products(root)
    return {
        "project_root": str(root),
        "has_eddi_ci_yaml": has_eddi,
        "heyeddi_product": heyeddi,
        "languages": languages,
        "likely_commands": likely_commands,
        "suggested_path_filters": sorted(set(path_hints)),
        "notes": [
            "If heyeddi_product.uses_heyeddi_product and file missing → create Reviewer-only safe eddi-ci.yaml.",
            "Only add pipeline jobs when the user wants runners and a command is evidenced above.",
            "Keep ai_review.on_ci_failure false unless the user explicitly opts in.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"project_root not found: {root}"}))
        return 1
    print(json.dumps(inspect(root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
