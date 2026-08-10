"""publish-ci-pack-repo materializes a skills.sh-ready tree."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "publish-ci-pack-repo.sh"


def test_publish_ci_pack_materialize(tmp_path: Path) -> None:
    out = tmp_path / "ci-pack"
    subprocess.run([str(SCRIPT), "--out", str(out)], check=True, cwd=ROOT)
    pack = json.loads((ROOT / "packs" / "heyeddi-ci-skills.json").read_text(encoding="utf-8"))
    for name in pack["skills"]:
        assert (out / "skills" / name / "SKILL.md").is_file(), name
    assert (out / "LICENSE").is_file()
    assert (out / "README.md").is_file()
    assert (out / "skills.sh.json").is_file()
    reg = json.loads((out / "skills-registry.json").read_text(encoding="utf-8"))
    assert reg["version"] == pack["version"]
    assert "HeyEddi-com/heyeddi-ci-skills" in (out / "README.md").read_text(encoding="utf-8")
