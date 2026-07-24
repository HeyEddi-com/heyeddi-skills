"""Unit tests for UI copy prose verification in heyeddi-design."""
from __future__ import annotations

from _skill_loader import load_skill_script

_vp = load_skill_script("heyeddi-design", "verify_prose")
scan_text = _vp.scan_text
verify_project = _vp.verify_project

GOOD_COPY = '<p>Update your profile and save changes.</p>'
BAD_EM_DASH = "<p>Update your profile — then save.</p>"
BAD_EN_DASH = "<p>Update your profile – then save.</p>"
BAD_FILLER = "<p>Delve into settings for a seamless experience.</p>"


def test_scan_text_accepts_plain_copy() -> None:
    assert scan_text(GOOD_COPY, "SettingsView.vue") == []


def test_scan_text_flags_em_dash() -> None:
    issues = scan_text(BAD_EM_DASH, "SettingsView.vue")
    assert any(issue["type"] == "dash" for issue in issues)


def test_scan_text_flags_en_dash() -> None:
    issues = scan_text(BAD_EN_DASH, "SettingsView.vue")
    assert any(issue["type"] == "dash" for issue in issues)


def test_scan_text_flags_banned_filler() -> None:
    issues = scan_text(BAD_FILLER, "SettingsView.vue")
    types = {issue["type"] for issue in issues}
    assert "word" in types


def test_verify_project_on_empty_fixture(tmp_path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "HomeView.vue").write_text(GOOD_COPY, encoding="utf-8")
    result = verify_project(tmp_path)
    assert result["ok"] is True
    assert result["files_scanned"] == 1
