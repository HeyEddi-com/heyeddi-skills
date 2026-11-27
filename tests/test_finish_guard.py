"""The Stop hook that refuses a turn ending on "waiting for your go"."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "heyeddi" / "scripts"))

import finish_guard  # noqa: E402
import worktree_guard  # noqa: E402


@pytest.mark.parametrize(
    "ending",
    [
        'Nothing was running: I was waiting for your "go" on RR-2.',
        "If you say go, I'll finish the PR.",
        "Should I start phase 2?",
        "Want me to commit and push this?",
        "Can I commit and push the Telegram change?",
        "Let me know if you want me to continue.",
    ],
)
def test_waiting_for_a_go_is_blocked_once(ending: str) -> None:
    event = {"last_assistant_message": ending, "stop_hook_active": False}
    assert finish_guard.decide(event)
    assert not finish_guard.decide({**event, "stop_hook_active": True})


@pytest.mark.parametrize(
    "ending",
    [
        "Done: the three features are merged into staging.",
        "The production merge waits for you: reply authorize merge.",
    ],
)
def test_finished_work_and_production_merges_pass(ending: str) -> None:
    assert not finish_guard.decide({"last_assistant_message": ending})


def test_reads_the_transcript_when_the_event_has_no_message(tmp_path: Path) -> None:
    transcript = tmp_path / "t.jsonl"
    row = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Waiting for your go."}]}}
    transcript.write_text(json.dumps(row) + "\n", encoding="utf-8")
    assert finish_guard.decide({"transcript_path": str(transcript)})


def test_install_registers_the_stop_hook(tmp_path: Path) -> None:
    worktree_guard.install(tmp_path)
    worktree_guard.install(tmp_path)
    data = json.loads((tmp_path / "settings.json").read_text())
    assert len(data["hooks"]["Stop"]) == 1
    assert (tmp_path / "hooks" / "finish_guard.py").is_file()
