"""Pack manifests and sync-plugins safety."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
REGISTRY = ROOT / "skills-registry.json"


def test_packs_skills_exist_in_ssot() -> None:
    for pack_file in PACKS.glob("*.json"):
        data = json.loads(pack_file.read_text(encoding="utf-8"))
        for name in data["skills"]:
            assert (ROOT / "skills" / name / "SKILL.md").is_file(), f"{pack_file.name}: missing {name}"


def test_full_pack_matches_registry() -> None:
    registry = {s["name"] for s in json.loads(REGISTRY.read_text(encoding="utf-8"))["skills"]}
    pack = set(json.loads((PACKS / "heyeddi-skills.json").read_text(encoding="utf-8"))["skills"])
    assert pack == registry


def test_ci_pack_is_subset() -> None:
    full = set(json.loads((PACKS / "heyeddi-skills.json").read_text(encoding="utf-8"))["skills"])
    ci = set(json.loads((PACKS / "heyeddi-ci-skills.json").read_text(encoding="utf-8"))["skills"])
    assert ci <= full
    assert "heyeddi-pr-respond" in ci
    assert all(n.startswith("heyeddi-ci-") or n == "heyeddi-pr-respond" for n in ci)


def test_write_release_notes(tmp_path: Path) -> None:
    out = tmp_path / "notes.md"
    proc = subprocess.run(
        [
            "python3",
            str(ROOT / "scripts" / "write-release-notes.py"),
            "--tag",
            "v3.2.0",
            "--version",
            "3.2.0",
            "-o",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    text = out.read_text(encoding="utf-8")
    assert "heyeddi-skills" in text
    assert "heyeddi-ci-skills" in text
    assert "heyeddi-pr-respond" in text


def test_sync_plugins_link_mode() -> None:
    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "sync-plugins.sh"), "--link"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    full_skills = ROOT / "plugins" / "heyeddi-skills" / "skills"
    assert full_skills.is_dir()
    assert not full_skills.is_symlink(), "whole-dir skills symlink is forbidden"
    sample = full_skills / "heyeddi-ci-config"
    assert sample.is_symlink()
    assert sample.resolve() == (ROOT / "skills" / "heyeddi-ci-config").resolve()
    ci_sample = ROOT / "plugins" / "heyeddi-ci-skills" / "skills" / "heyeddi-pr-respond"
    assert ci_sample.exists()
