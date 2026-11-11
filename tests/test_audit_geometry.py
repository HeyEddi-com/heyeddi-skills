"""Geometry gate: broken drawings fail, real settings captures pass."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from _skill_loader import REPO, load_skill_script

SCRIPT = REPO / "skills" / "visual-auditor" / "scripts" / "audit_geometry.py"
SETTINGS = REPO / "fixtures" / "sample-vue-app" / ".heyeddi" / "audits" / "visual" / "screenshots"


def _run(path: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--image", str(path), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, json.loads(result.stdout)


def _form(path: Path) -> None:
    image = Image.new("RGB", (390, 844), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((24, 80, 280, 108), fill=(17, 24, 39))
    for top in (160, 240, 320):
        draw.rectangle((24, top, 360, top + 48), outline=(17, 24, 39), width=2)
        draw.rectangle((32, top + 16, 180, top + 30), fill=(55, 65, 81))
    draw.rectangle((24, 420, 200, 468), fill=(17, 24, 39))
    image.save(path)


def _wall(path: Path) -> None:
    image = Image.new("RGB", (390, 844), (229, 231, 235))
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 400, 200, 416), fill=(156, 163, 175))
    image.save(path)


def _gray(path: Path) -> None:
    image = Image.new("RGB", (390, 844), (221, 221, 221))
    draw = ImageDraw.Draw(image)
    for top in range(80, 700, 48):
        draw.rectangle((32, top, 340, top + 22), fill=(176, 176, 176))
    image.save(path)


def _clip(path: Path) -> None:
    image = Image.new("RGB", (390, 700), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    x = 0
    while x < 390:
        width = 10 + (x % 28)
        draw.rectangle((x, 0, min(389, x + width // 2), 14), fill=(17, 24, 39))
        x += width
    draw.rectangle((24, 200, 300, 248), outline=(17, 24, 39), width=3)
    image.save(path)


def _gradient(path: Path) -> None:
    image = Image.new("RGB", (390, 844))
    pixels = image.load()
    for y in range(844):
        t = y / 843
        color = (int(80 + 140 * t), int(200 - 80 * t), int(120 + 60 * (1 - t)))
        for x in range(390):
            pixels[x, y] = color
    image.save(path)


def test_form_and_gradient_pass(tmp_path: Path) -> None:
    form = tmp_path / "form.png"
    gradient = tmp_path / "gradient.png"
    _form(form)
    _gradient(gradient)
    form_code, form_report = _run(form)
    gradient_code, gradient_report = _run(gradient)
    assert form_code == 0 and form_report["errors"] == []
    assert gradient_code == 0 and gradient_report["errors"] == []


def test_gray_type_and_blank_wall_fail(tmp_path: Path) -> None:
    wall = tmp_path / "wall.png"
    gray = tmp_path / "gray.png"
    _wall(wall)
    _gray(gray)
    _, wall_report = _run(wall)
    gray_code, gray_report = _run(gray)
    assert gray_code == 1
    assert {item["code"] for item in wall_report["errors"]} == {"low_contrast"}
    assert {item["code"] for item in gray_report["errors"]} == {"low_contrast"}


def test_clipped_top_fails(tmp_path: Path) -> None:
    image = tmp_path / "clip.png"
    _clip(image)
    code, report = _run(image)
    assert code == 1
    assert "clipped_content" in {item["code"] for item in report["errors"]}


def test_gate_captures_fails_closed(tmp_path: Path) -> None:
    gate = load_skill_script("visual-auditor", "audit_geometry")
    form = tmp_path / "form.png"
    gray = tmp_path / "gray.png"
    _form(form)
    _gray(gray)
    passed = gate.gate_captures([form])
    failed = gate.gate_captures([form, gray])
    assert passed["ok"] is True
    assert failed["ok"] is False
    assert failed["reports"][1]["errors"][0]["code"] == "low_contrast"


def test_finalize_stays_on_contrast() -> None:
    text = (REPO / "skills" / "visual-auditor" / "scripts" / "finalize_visual_review.py").read_text()
    assert "audit_geometry" not in text
    assert "audit_contrast.py" in text


def test_real_settings_captures_pass() -> None:
    for name in ("settings_375px.png", "settings_1440px.png"):
        code, report = _run(SETTINGS / name)
        assert code == 0, report
        assert report["errors"] == []
