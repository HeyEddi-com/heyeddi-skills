"""Released content must not change under the same version number.

The Release workflow publishes only when `skills-registry.json` has a version with no tag.
A merge that changes skills without bumping it ships nothing, silently.
Needs the git tags: CI checks out with `fetch-depth: 0`.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ("skills", "packs")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, env=ENV, check=True, capture_output=True, text=True).stdout


def _number(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version))


def _version(text: str) -> str:
    return json.loads(text)["version"]


def _at(root: Path, ref: str, path: str) -> str | None:
    try:
        return _git(root, "show", f"{ref}:{path}")
    except subprocess.CalledProcessError:
        return None


def _changed(root: Path, ref: str) -> list[str]:
    """Shipped files that differ from `ref`, ignoring the stamped product-version line."""
    names = _git(root, "diff", "--name-only", "--no-renames", ref, "--", *SHIPPED).splitlines()
    names += _git(root, "ls-files", "--others", "--exclude-standard", "--", *SHIPPED).splitlines()

    def strip(text: str | None) -> str | None:
        return None if text is None else re.sub(r"(?m)^product-version:.*\n", "", text)

    changed = []
    for name in sorted(set(names)):
        now = (root / name).read_text(encoding="utf-8", errors="replace") if (root / name).is_file() else None
        if name.endswith("/SKILL.md") and strip(_at(root, ref, name)) == strip(now):
            continue
        changed.append(name)
    return changed


def version_problems(root: Path) -> list[str]:
    tags = [t for t in _git(root, "tag", "--list", "v*").split() if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
    if not tags:
        return ["no release tags found: fetch them (`git fetch --tags`, or `fetch-depth: 0` in CI)"]
    version = _version((root / "skills-registry.json").read_text(encoding="utf-8"))
    latest = max(tags, key=_number)

    if f"v{version}" in tags:
        changed = _changed(root, f"v{version}")
        if changed:
            return [f"hub {version} is already released but {changed[0]} changed ({len(changed)} files): bump skills-registry.json"]
        return []
    if _number(version) <= _number(latest):
        return [f"hub {version} is not above the latest release {latest}"]

    changed = _changed(root, latest)
    versioned = {f"skills/{p.parent.name}/manifest.json": f"skills/{p.parent.name}/" for p in root.glob("skills/*/manifest.json")}
    for pack in root.glob("packs/*.json"):
        data = json.loads(pack.read_text(encoding="utf-8"))
        if pack.stem != "heyeddi-skills":
            versioned[f"packs/{pack.name}"] = tuple(f"skills/{s}/" for s in data["skills"]) + (f"packs/{pack.name}",)

    problems = []
    for version_file, prefixes in sorted(versioned.items()):
        before = _at(root, latest, version_file)
        touched = [name for name in changed if name.startswith(prefixes)]
        if before and touched and _number(_version((root / version_file).read_text(encoding="utf-8"))) <= _number(_version(before)):
            problems.append(f"{touched[0]} changed since {latest}: bump the version in {version_file}")
    return problems


def test_changed_content_has_a_new_version() -> None:
    problems = version_problems(ROOT)
    assert not problems, "Bump the version, then run scripts/sync-skill-frontmatter.py:\n" + "\n".join(problems)


def _write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _versions(root: Path, hub: str, skill: str, pack: str) -> None:
    _write(root, "skills-registry.json", json.dumps({"version": hub}))
    _write(root, "skills/demo/manifest.json", json.dumps({"version": skill}))
    _write(root, "packs/heyeddi-ci-skills.json", json.dumps({"version": pack, "skills": ["demo"]}))
    _write(root, "skills/demo/SKILL.md", f"---\nproduct-version: {hub}\n---\nbody\n")


@pytest.fixture()
def released(tmp_path: Path) -> Path:
    _versions(tmp_path, "1.0.0", "1.0.0", "1.0.0")
    _write(tmp_path, "skills/demo/reference/rule.md", "old\n")
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qm", "r"], ["tag", "v1.0.0"]):
        _git(tmp_path, *args)
    return tmp_path


def test_unchanged_release_passes(released: Path) -> None:
    assert version_problems(released) == []


@pytest.mark.parametrize("path", ["skills/demo/reference/rule.md", "skills/demo/reference/added.md"])
def test_change_without_bump_fails(released: Path, path: str) -> None:
    _write(released, path, "new\n")
    assert "bump skills-registry.json" in version_problems(released)[0]


def test_hub_bump_alone_still_needs_skill_and_pack_bumps(released: Path) -> None:
    _write(released, "skills/demo/reference/rule.md", "new\n")
    _versions(released, "1.0.1", "1.0.0", "1.0.0")
    problems = "\n".join(version_problems(released))
    assert "skills/demo/manifest.json" in problems and "packs/heyeddi-ci-skills.json" in problems


def test_full_bump_passes(released: Path) -> None:
    _write(released, "skills/demo/reference/rule.md", "new\n")
    _versions(released, "1.0.1", "1.0.1", "1.0.1")
    assert version_problems(released) == []


def test_missing_tags_fail_instead_of_passing(released: Path) -> None:
    _git(released, "tag", "-d", "v1.0.0")
    assert "no release tags" in version_problems(released)[0]
