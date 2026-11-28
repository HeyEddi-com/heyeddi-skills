"""heyeddi-video: renders stay local and the finished file is verified."""
from __future__ import annotations

import pytest

from _skill_loader import load_skill_script

video = load_skill_script("heyeddi-video", "video")


def test_env_turns_telemetry_off_even_when_the_caller_turned_it_on(tmp_path):
    env = video.hyperframes_env(tmp_path, base={"HYPERFRAMES_NO_TELEMETRY": "0"})
    assert env["HYPERFRAMES_NO_TELEMETRY"] == "1"
    assert env["DO_NOT_TRACK"] == "1"


def test_env_points_at_local_python_and_headless_chrome(tmp_path):
    python = tmp_path / "venv/bin/python"
    chrome = tmp_path / "chrome/chrome-headless-shell/linux-1/chrome-headless-shell-linux64/chrome-headless-shell"
    for path in (python, chrome):
        path.parent.mkdir(parents=True)
        path.write_text("")
    env = video.hyperframes_env(tmp_path, base={})
    assert env["HYPERFRAMES_PYTHON"] == str(python)
    assert env["HYPERFRAMES_BROWSER_PATH"] == str(chrome)


def test_env_leaves_tool_paths_unset_before_setup(tmp_path):
    env = video.hyperframes_env(tmp_path, base={})
    assert "HYPERFRAMES_PYTHON" not in env
    assert "HYPERFRAMES_BROWSER_PATH" not in env


@pytest.mark.parametrize("command", ["publish", "cloud", "lambda", "cloudrun", "auth", "events"])
def test_commands_that_leave_the_machine_are_refused(command):
    with pytest.raises(video.NotLocal):
        video.local_command([command])


def test_local_commands_use_the_pinned_cli():
    assert video.local_command(["lint"]) == ["npx", "--yes", f"hyperframes@{video.HYPERFRAMES}", "lint"]


def _probe(streams, duration="12.0"):
    return {"streams": streams, "format": {"duration": duration}}


def test_verify_accepts_a_video_with_sound_at_social_loudness():
    probe = _probe([{"codec_type": "video", "width": 1920, "height": 1080}, {"codec_type": "audio"}])
    assert video.problems(probe, loudness=-14.6, silent_ok=False) == []


def test_verify_reports_missing_audio_unless_silence_was_asked_for():
    probe = _probe([{"codec_type": "video", "width": 1920, "height": 1080}])
    assert video.problems(probe, loudness=None, silent_ok=False) == ["no audio track"]
    assert video.problems(probe, loudness=None, silent_ok=True) == []


def test_verify_reports_a_quiet_mix_and_a_missing_picture():
    probe = _probe([{"codec_type": "audio"}])
    assert video.problems(probe, loudness=-27.0, silent_ok=False) == [
        "no video stream",
        "loudness -27.0 LUFS is outside -18 to -12",
    ]


def test_loudness_is_read_from_the_summary_not_the_running_log():
    log = "t: 1  I: -30.0 LUFS\n  Integrated loudness:\n    I:         -14.8 LUFS\n"
    assert video.parse_loudness(log) == -14.8


@pytest.mark.parametrize("command", ["check", "snapshot", "render", "capture", "keyframes"])
def test_browser_commands_queue(command):
    assert video.is_heavy([command])


@pytest.mark.parametrize("command", ["lint", "init", "tts", "catalog", "add", "docs"])
def test_light_commands_do_not_wait_behind_a_render(command):
    assert not video.is_heavy([command])


def test_usage_reporting_is_refused_too():
    with pytest.raises(video.NotLocal):
        video.local_command(["usage", "--json"])


def test_a_queued_job_says_why_it_is_waiting(tmp_path, capsys):
    import fcntl

    lock = tmp_path / "lock"
    waits = []
    with lock.open("w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX)
        with lock.open("w") as second:
            video.take_lock(second, wait=lambda handle: waits.append(handle))
    assert waits and "waiting for another video job" in capsys.readouterr().err


def test_a_free_lock_is_taken_without_a_message(tmp_path, capsys):
    with (tmp_path / "lock").open("w") as handle:
        video.take_lock(handle)
    assert capsys.readouterr().err == ""


def test_word_timings_come_out_as_plain_rows():
    words = load_skill_script("heyeddi-video", "words")

    class Word:
        def __init__(self, word, start, end):
            self.word, self.start, self.end = word, start, end

    class Segment:
        words = [Word(" Ship", 0.0004, 0.4449), Word(" it.", 0.4449, 0.9)]

    assert words.rows([Segment()]) == [
        {"word": "Ship", "start": 0.0, "end": 0.445},
        {"word": "it.", "start": 0.445, "end": 0.9},
    ]


def test_word_timings_explain_how_to_install_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="setup --captions"):
        video.words_command(tmp_path, tmp_path / "a.wav")
