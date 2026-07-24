#!/usr/bin/env python3
"""Sync skills/*/SKILL.md frontmatter from manifest.json + skills-registry.json."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
REGISTRY = REPO_ROOT / "skills-registry.json"
AUTHOR = "HeyEddi-com"

META_KEYS = ("version", "product-version", "author")


def load_hub_version() -> str:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return str(data["version"])


def load_skill_version(skill_dir: Path) -> str:
    manifest = skill_dir / "manifest.json"
    if not manifest.is_file():
        raise FileNotFoundError(f"missing manifest: {manifest}")
    return str(json.loads(manifest.read_text(encoding="utf-8"))["version"])


def split_skill_md(text: str) -> tuple[str, str, str]:
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md missing YAML frontmatter")
    return text[: match.start()], match.group(1), text[match.end() :]


def strip_meta_lines(frontmatter: str) -> str:
    lines = frontmatter.splitlines()
    kept = [line for line in lines if not any(line.startswith(f"{key}:") for key in META_KEYS)]
    return "\n".join(kept).rstrip()


def insert_meta_block(frontmatter: str, version: str, product_version: str) -> str:
    fm = strip_meta_lines(frontmatter)
    block = (
        f"version: {version}\n"
        f"product-version: {product_version}\n"
        f"author: {AUTHOR}"
    )
    lines = fm.splitlines()
    insert_at = len(lines)
    for idx, line in enumerate(lines):
        if line.startswith(("paths:", "disable-model-invocation:", "metadata:")):
            insert_at = idx
            break
    new_lines = lines[:insert_at] + block.splitlines() + lines[insert_at:]
    return "\n".join(new_lines)


def sync_skill(skill_dir: Path, product_version: str, *, dry_run: bool) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    version = load_skill_version(skill_dir)
    prefix, frontmatter, body = split_skill_md(skill_md.read_text(encoding="utf-8"))
    updated_fm = insert_meta_block(frontmatter, version, product_version)
    if updated_fm == frontmatter:
        return False
    new_text = f"---\n{updated_fm}\n---\n{body}"
    if dry_run:
        print(f"[dry-run] would update {skill_dir.name}")
        return True
    skill_md.write_text(new_text, encoding="utf-8")
    print(f"updated {skill_dir.name}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync SKILL.md frontmatter for skills.sh indexing")
    parser.add_argument("--skill", help="Single skill folder name under skills/")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    product_version = load_hub_version()
    targets = [SKILLS_DIR / args.skill] if args.skill else sorted(SKILLS_DIR.iterdir())
    changed = 0
    for skill_dir in targets:
        if not skill_dir.is_dir() or not (skill_dir / "manifest.json").is_file():
            continue
        if sync_skill(skill_dir, product_version, dry_run=args.dry_run):
            changed += 1
    print(f"done: {changed} skill(s) updated (hub product-version {product_version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
