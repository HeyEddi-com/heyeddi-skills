"""Tests for SKILL.md frontmatter sync script."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_sync_skill_frontmatter_adds_required_fields(tmp_path: Path) -> None:
    skill = tmp_path / "demo-skill"
    scripts = skill / "scripts"
    scripts.mkdir(parents=True)
    (skill / "manifest.json").write_text(json.dumps({"version": "1.2.3"}), encoding="utf-8")
    (skill / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo skill for tests.\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    registry = tmp_path / "skills-registry.json"
    registry.write_text(json.dumps({"version": "9.9.9"}), encoding="utf-8")

    script = REPO / "scripts" / "sync-skill-frontmatter.py"
    env = {**dict(**__import__("os").environ)}
    # Point script at temp registry by copying layout
    hub = tmp_path / "hub"
    hub.mkdir()
    (hub / "skills-registry.json").write_text(registry.read_text(), encoding="utf-8")
    (hub / "skills").mkdir()
    (hub / "skills" / "demo-skill").mkdir()
    for name in ("manifest.json", "SKILL.md"):
        (hub / "skills" / "demo-skill" / name).write_text((skill / name).read_text(), encoding="utf-8")
    (hub / "scripts").mkdir()
    (hub / "scripts" / "sync-skill-frontmatter.py").write_text(script.read_text(), encoding="utf-8")

    subprocess.run(
        [sys.executable, str(hub / "scripts" / "sync-skill-frontmatter.py"), "--skill", "demo-skill"],
        cwd=hub,
        check=True,
    )
    text = (hub / "skills" / "demo-skill" / "SKILL.md").read_text(encoding="utf-8")
    assert "version: 1.2.3" in text
    assert "product-version: 9.9.9" in text
    assert "author: HeyEddi-com" in text
