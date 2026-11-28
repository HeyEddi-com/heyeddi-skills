"""heyeddi-video: designed voices, the asset inventory, and script to timeline."""
from __future__ import annotations

import json
import math
import struct
import wave
import zipfile

import pytest

from _skill_loader import load_skill_script

video = load_skill_script("heyeddi-video", "video")
say = load_skill_script("heyeddi-video", "say")
story = load_skill_script("heyeddi-video", "story")
assets = load_skill_script("heyeddi-video", "assets")


@pytest.mark.parametrize("engine", ["design", "clone"])
def test_designed_and_cloned_voices_run_in_the_qwen_environment_offline(tmp_path, engine):
    (tmp_path / "engines/qwen/bin").mkdir(parents=True)
    (tmp_path / "engines/qwen/bin/python").write_text("")
    command, env = video.say_command(tmp_path, engine, tmp_path / "jobs.json")
    assert command[0] == str(tmp_path / "engines/qwen/bin/python")
    assert env["HF_HUB_OFFLINE"] == "1"


def test_each_engine_loads_its_own_model():
    assert say.MODELS["design"] == ["Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"]
    assert say.MODELS["clone"] == ["Qwen/Qwen3-TTS-12Hz-1.7B-Base"]


def test_a_cloned_voice_cannot_take_a_direction():
    job = {"text": "Hi.", "voice": "maya.wav", "out": "a.wav", "direction": "excited"}
    with pytest.raises(ValueError, match="direction"):
        say.check_jobs("clone", [job])
    say.check_jobs("design", [{**job, "voice": "A young woman, warm."}])


SCRIPT = """\
# a comment
title: The Review
scene: office
MAYA (tired): It is two in the morning.
pause: 0.5
BUG: Ship it!
scene: desk
MAYA: Not tonight.
"""


def test_a_script_reads_into_lines_scenes_and_pauses():
    parsed = story.parse(SCRIPT)
    assert parsed["title"] == "The Review"
    assert parsed["lines"] == [
        {"speaker": "maya", "mood": "tired", "text": "It is two in the morning.", "scene": "office", "pause": 0.0},
        {"speaker": "bug", "mood": "", "text": "Ship it!", "scene": "office", "pause": 0.5},
        {"speaker": "maya", "mood": "", "text": "Not tonight.", "scene": "desk", "pause": 0.0},
    ]


def test_a_line_the_parser_does_not_understand_is_named():
    with pytest.raises(story.ScriptError, match="line 2"):
        story.parse("scene: a\nMAYA says hello\n")


def _cast(folder):
    (folder / "voices").mkdir(parents=True)
    (folder / "voices/maya.wav").write_bytes(b"one")
    (folder / "voices/maya-tired.wav").write_bytes(b"two")
    (folder / "maya.json").write_text(json.dumps(
        {"engine": "clone", "voice": "voices/maya.wav", "moods": {"tired": "voices/maya-tired.wav"}}))
    (folder / "bug.json").write_text(json.dumps(
        {"engine": "qwen", "voice": "Vivian", "direction": "a sneaky bug", "moods": {"scared": "now frightened"}}))
    return folder


def _line(speaker, mood="", text="Hello."):
    return {"speaker": speaker, "mood": mood, "text": text}


def test_a_mood_picks_the_reference_clip_or_extends_the_direction(tmp_path):
    cast = _cast(tmp_path)
    clone = story.job(_line("maya", "tired"), story.load_character(cast, "maya"), cast)
    assert clone["voice"] == str(cast / "voices/maya-tired.wav") and "direction" not in clone
    acted = story.job(_line("bug", "scared"), story.load_character(cast, "bug"), cast)
    assert acted["direction"] == "a sneaky bug, now frightened"


def test_a_mood_the_character_does_not_have_is_an_error_not_ignored(tmp_path):
    cast = _cast(tmp_path)
    with pytest.raises(story.ScriptError, match="maya.*furious"):
        story.job(_line("maya", "furious"), story.load_character(cast, "maya"), cast)


def test_a_speaker_without_a_character_file_is_named(tmp_path):
    with pytest.raises(story.ScriptError, match="nobody"):
        story.load_character(_cast(tmp_path), "nobody")


def test_a_line_is_spoken_again_only_when_something_that_changes_it_changes(tmp_path):
    cast = _cast(tmp_path)
    maya = story.load_character(cast, "maya")
    first = story.job(_line("maya"), maya, cast)["out"]
    assert story.job(_line("maya"), maya, cast)["out"] == first
    assert story.job(_line("maya", text="Bye."), maya, cast)["out"] != first
    (cast / "voices/maya.wav").write_bytes(b"redesigned")
    assert story.job(_line("maya"), maya, cast)["out"] != first


def _tone(path, seconds, rate=24000):
    samples = [int(9000 * math.sin(i / 9)) for i in range(int(seconds * rate))]
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def test_the_timeline_follows_the_measured_voices(tmp_path):
    lines = story.parse(SCRIPT)["lines"]
    files = []
    for number, seconds in enumerate([2.0, 1.0, 1.5]):
        files.append(tmp_path / f"{number}.wav")
        _tone(files[-1], seconds)
    timeline = story.build_timeline(lines, files, tmp_path / "dialogue.wav")
    starts = [row["start"] for row in timeline["lines"]]
    assert starts[0] == story.LEAD
    assert starts[1] == pytest.approx(story.LEAD + 2.0 + story.GAP + 0.5)
    assert starts[2] == pytest.approx(starts[1] + 1.0 + story.SCENE_GAP)
    assert timeline["duration"] == pytest.approx(starts[2] + 1.5 + story.TAIL)
    assert [scene["name"] for scene in timeline["scenes"]] == ["office", "desk"]
    assert timeline["scenes"][0]["end"] == timeline["scenes"][1]["start"]
    assert len(timeline["lines"][0]["mouth"]) == 24 and max(timeline["lines"][0]["mouth"]) == 1.0
    with wave.open(str(tmp_path / "dialogue.wav")) as mixed:
        assert mixed.getnframes() / mixed.getframerate() == pytest.approx(timeline["duration"], abs=0.01)


@pytest.mark.parametrize("licence", ["Royalty-free", "CC-BY-NC-4.0", ""])
def test_only_licences_that_allow_reuse_enter_the_inventory(licence):
    with pytest.raises(assets.AssetError, match="licence"):
        assets.check_licence(licence, author="someone")


def test_attribution_licences_need_an_author():
    with pytest.raises(assets.AssetError, match="author"):
        assets.check_licence("CC-BY-4.0", author="")
    assets.check_licence("CC0", author="")


def test_only_https_downloads(tmp_path):
    with pytest.raises(assets.AssetError, match="https"):
        assets.download("http://example.com/a.glb", tmp_path / "a.glb")


@pytest.mark.parametrize("name", ["../escape.txt", "/etc/escape.txt", "a/../../escape.txt"])
def test_a_zip_cannot_write_outside_its_folder(tmp_path, name):
    archive = tmp_path / "a.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr(name, "x")
    with pytest.raises(assets.AssetError, match="outside"):
        assets.unpack(archive, tmp_path / "into")


def test_getting_an_asset_records_its_licence_and_reuses_the_copy(tmp_path):
    calls = []

    def fetch(url, target):
        calls.append(url)
        target.write_bytes(b"model")

    item = {"id": "hero", "licence": "CC0", "source": "https://example.com/pack", "repo": "o/r",
            "commit": "abc", "files": ["gltf/Hero.glb"]}
    home, project = tmp_path / "inventory", tmp_path / "project"
    assets.get(item, home, project, fetch=fetch)
    assets.get(item, home, project, fetch=fetch)
    assert calls == ["https://raw.githubusercontent.com/o/r/abc/gltf/Hero.glb"]
    assert (project / "hero/Hero.glb").read_bytes() == b"model"
    credits = json.loads((project / "CREDITS.json").read_text())
    assert credits == {"hero": {"licence": "CC0", "source": "https://example.com/pack", "author": ""}}


def test_a_changed_inventory_file_is_refused(tmp_path):
    item = {"id": "hero", "licence": "CC0", "source": "s", "repo": "o/r", "commit": "abc", "files": ["Hero.glb"]}
    fetch = lambda url, target: target.write_bytes(b"model")
    assets.get(item, tmp_path / "inv", tmp_path / "p", fetch=fetch)
    (tmp_path / "inv/hero/Hero.glb").write_bytes(b"tampered")
    with pytest.raises(assets.AssetError, match="changed"):
        assets.get(item, tmp_path / "inv", tmp_path / "p", fetch=fetch)


def test_every_catalog_entry_is_pinned_and_licensed():
    for item in assets.catalog()["items"]:
        assets.check_licence(item["licence"], item.get("author", ""))
        assert len(item["commit"]) == 40 and item["files"] and item["source"].startswith("https://")


def _locked(path):
    import fcntl

    with path.open("a") as second:
        try:
            fcntl.flock(second, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
    return False


def test_story_speech_runs_inside_the_heavy_queue(tmp_path, monkeypatch):
    import subprocess
    import sys

    monkeypatch.setenv("HEYEDDI_VIDEO_HOME", str(tmp_path))
    (tmp_path / "engines/pocket/bin").mkdir(parents=True)
    (tmp_path / "engines/pocket/bin/python").write_text("")
    # speak() imports the script by name, as it does when run from its folder.
    monkeypatch.setitem(sys.modules, "video", video)
    held = []

    def engine(command, **_kwargs):
        held.append(_locked(video.lock_path(tmp_path)))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(video.subprocess, "run", engine)
    monkeypatch.setattr(story, "trim", lambda source, target: None)
    story.speak([{"engine": "pocket", "text": "Hi.", "voice": "alba", "out": "a.wav"}], tmp_path / "voices")
    assert held == [True]


def test_the_inventory_is_locked_while_an_asset_is_fetched_and_recorded(tmp_path):
    held = []

    def fetch(url, target):
        held.append(_locked(tmp_path / "inv/inventory.lock"))
        target.write_bytes(b"model")

    item = {"id": "hero", "licence": "CC0", "source": "s", "repo": "o/r", "commit": "abc", "files": ["Hero.glb"]}
    assets.get(item, tmp_path / "inv", tmp_path / "p", fetch=fetch)
    assert held == [True]
    assert not _locked(tmp_path / "inv/inventory.lock")


def test_redesigning_a_character_keeps_the_old_voice_when_it_fails(tmp_path, monkeypatch):
    import argparse

    cast = _cast(tmp_path)

    def broken(jobs, folder):
        raise story.ScriptError("the design voice failed with exit 1")

    monkeypatch.setattr(story, "speak", broken)
    args = argparse.Namespace(name="maya", cast=cast, voice_design="Someone new.", mood=[])
    assert story.run_character(args) == 2
    assert (cast / "voices/maya.wav").read_bytes() == b"one"


def test_a_missing_reference_clip_is_named(tmp_path):
    cast = _cast(tmp_path)
    (cast / "voices/maya.wav").unlink()
    with pytest.raises(story.ScriptError, match="maya.wav"):
        story.job(_line("maya"), story.load_character(cast, "maya"), cast)


def test_a_redesigned_character_gets_the_new_clips(tmp_path, monkeypatch):
    import argparse

    cast = _cast(tmp_path)

    def spoken(jobs, folder):
        for made in jobs:
            (folder / made["out"]).write_bytes(b"new")

    monkeypatch.setattr(story, "speak", spoken)
    args = argparse.Namespace(name="maya", cast=cast, voice_design="Someone new.", mood=["calm=Calm."])
    assert story.run_character(args) == 0
    assert (cast / "voices/maya.wav").read_bytes() == b"new"
    assert (cast / "voices/maya-calm.wav").read_bytes() == b"new"
    assert (cast / "voices/maya-calm.txt").read_text().strip() == story.SAMPLE_TEXT
