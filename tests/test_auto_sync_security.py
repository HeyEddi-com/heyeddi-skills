"""Unit tests for filesystem-only auto-sync (no dynamic code loading)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "heyeddi" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _auto_sync import (  # noqa: E402
    _install_skills_root,
    _write_minimal_index,
    ensure_heyeddi,
)


def test_auto_sync_source_has_no_dynamic_loaders() -> None:
    text = (SCRIPTS / "_auto_sync.py").read_text(encoding="utf-8")
    assert "import importlib" not in text
    assert "exec_module(" not in text
    assert "sys.path.insert" not in text
    assert "_heyeddi_migrate" not in text
    assert "HEYEDDI_SKILLS_ROOT" not in text
    assert not re.search(r"Path\.home\s*\(", text)


def test_install_skills_root_from_scripts_dir() -> None:
    root = _install_skills_root(SCRIPTS)
    assert root == (REPO_ROOT / "skills").resolve()


def test_ensure_heyeddi_writes_minimal_index(tmp_path: Path) -> None:
    result = ensure_heyeddi(tmp_path, once_per_process=False)
    assert result is not None
    assert result.get("status") == "ok"
    index = tmp_path / ".heyeddi" / "skills-index.json"
    assert index.is_file()
    data = json.loads(index.read_text(encoding="utf-8"))
    assert data["generator"] == "heyeddi-auto-sync-minimal"
    assert data["skill_count"] >= 1
    names = {s["name"] for s in data["skills"]}
    assert "heyeddi" in names


def test_ensure_heyeddi_skips_write_when_index_exists(tmp_path: Path) -> None:
    heyeddi = tmp_path / ".heyeddi"
    heyeddi.mkdir()
    (heyeddi / "skills-index.json").write_text('{"skills":[],"skill_count":0}\n', encoding="utf-8")
    result = ensure_heyeddi(tmp_path, once_per_process=False)
    assert result == {"status": "ok"}
    data = json.loads((heyeddi / "skills-index.json").read_text(encoding="utf-8"))
    assert data["skill_count"] == 0


def test_write_minimal_index_scans_siblings(tmp_path: Path) -> None:
    skills_root = tmp_path / "skills"
    sample = skills_root / "sample-skill"
    sample.mkdir(parents=True)
    (sample / "SKILL.md").write_text(
        "---\nname: sample-skill\ndescription: A test skill for scanning\nversion: 1.0.0\n---\n\n# Sample\n",
        encoding="utf-8",
    )
    project = tmp_path / "app"
    project.mkdir()
    out = _write_minimal_index(project, skills_root)
    assert out["ok"] is True
    assert out["skill_count"] == 1
    data = json.loads((project / ".heyeddi" / "skills-index.json").read_text(encoding="utf-8"))
    assert data["skills"][0]["name"] == "sample-skill"


def test_catalog_no_home_or_env_search() -> None:
    text = (SCRIPTS / "_catalog.py").read_text(encoding="utf-8")
    assert not re.search(r"Path\.home\s*\(", text)
    assert "HEYEDDI_SKILLS_ROOT" not in text
