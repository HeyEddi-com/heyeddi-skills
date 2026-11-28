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


def test_the_queue_lock_lives_in_the_private_tool_folder(tmp_path):
    assert video.lock_path(tmp_path) == tmp_path / "heavy.lock"


def test_taking_the_queue_never_truncates_what_the_lock_path_points_at(tmp_path, monkeypatch):
    victim = tmp_path / "victim.txt"
    victim.write_text("keep me")
    home = tmp_path / "home"
    home.mkdir()
    (home / "heavy.lock").symlink_to(victim)
    monkeypatch.setenv("HEYEDDI_VIDEO_HOME", str(home))
    with video.one_heavy_job():
        pass
    assert victim.read_text() == "keep me"


def test_the_video_skill_installs_on_its_own():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    pack = json.loads((root / "packs" / "heyeddi-video-skills.json").read_text())
    assert pack["skills"] == ["heyeddi-video"]
    market = json.loads((root / ".cursor-plugin" / "marketplace.json").read_text())
    assert "heyeddi-video-skills" in [plugin["name"] for plugin in market["plugins"]]
    others = [s.name for s in (root / "skills").iterdir() if s.name != "heyeddi-video"]
    for doc in (root / "skills" / "heyeddi-video").rglob("*.md"):
        text = doc.read_text()
        assert "engineering-excellence" not in text, doc
        assert not [name for name in others if f"@{name}" in text], doc


def _installed(home, engine):
    (home / "engines" / engine / "bin").mkdir(parents=True)
    (home / "engines" / engine / "bin" / "python").write_text("")


def test_say_runs_inside_the_engine_environment_and_stays_offline(tmp_path):
    _installed(tmp_path, "qwen")
    command, env = video.say_command(tmp_path, "qwen", tmp_path / "jobs.json")
    assert command[0] == str(tmp_path / "engines/qwen/bin/python")
    assert command[1].endswith("say.py") and command[2:] == ["qwen", str(tmp_path / "jobs.json")]
    assert env == {"HF_HUB_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1"}


def test_say_names_the_install_command_for_a_missing_engine(tmp_path):
    with pytest.raises(FileNotFoundError, match="setup --voice pocket"):
        video.say_command(tmp_path, "pocket", tmp_path / "jobs.json")


def test_only_qwen_takes_acting_directions():
    say = load_skill_script("heyeddi-video", "say")
    job = {"text": "Ship it.", "voice": "alba", "out": "a.wav", "direction": "smug"}
    with pytest.raises(ValueError, match="direction"):
        say.check_jobs("pocket", [job])
    say.check_jobs("qwen", [{**job, "voice": "Aiden"}])


@pytest.mark.parametrize("missing", ["text", "voice", "out"])
def test_every_line_needs_text_voice_and_output(missing):
    say = load_skill_script("heyeddi-video", "say")
    job = {"text": "Ship it.", "voice": "Aiden", "out": "a.wav"}
    del job[missing]
    with pytest.raises(ValueError, match=missing):
        say.check_jobs("qwen", [job])


def test_setup_installs_one_at_a_time_across_agents(tmp_path, monkeypatch):
    import fcntl

    monkeypatch.setenv("HEYEDDI_VIDEO_HOME", str(tmp_path))
    held = []

    def probe(*_args):
        with video.lock_path(tmp_path).open("a") as second:
            try:
                fcntl.flock(second, fcntl.LOCK_EX | fcntl.LOCK_NB)
                held.append(False)
            except BlockingIOError:
                held.append(True)
        return 0

    monkeypatch.setattr(video, "install_voice", probe)
    monkeypatch.setattr(video, "setup", probe)
    assert video.main(["setup", "--voice", "pocket"]) == 0
    assert held == [True, True]
