#!/usr/bin/env python3
"""A script and a cast in, speech files and a timeline out.

Run through `video.py story` and `video.py character`.
"""
from __future__ import annotations

import array
import hashlib
import json
import math
import re
import subprocess
import sys
import wave
from pathlib import Path

RATE = 24000
LEAD, GAP, SCENE_GAP, TAIL = 0.5, 0.35, 0.8, 1.0
MOUTH_STEP = 1 / 12
SPOKEN = re.compile(r"^([A-Z][A-Z0-9_ -]*?)\s*(?:\(([^)]*)\))?:\s*(.+)$")
# Neutral enough to be said in any mood.
SAMPLE_TEXT = "All right, listen. I have looked at this twice now, and I know exactly what happens next."


class ScriptError(ValueError):
    pass


def parse(text: str) -> dict:
    title, scene, pause, lines = "", "main", 0.0, []
    for number, raw in enumerate(text.splitlines(), 1):
        row = raw.strip()
        if not row or row.startswith("#"):
            continue
        key, _, value = row.partition(":")
        if key == "title":
            title = value.strip()
        elif key == "scene":
            scene = value.strip()
        elif key == "pause":
            pause += float(value)
        elif found := SPOKEN.match(row):
            speaker, mood, said = found.groups()
            lines.append({"speaker": speaker.lower().replace(" ", "-"), "mood": (mood or "").strip(),
                          "text": said, "scene": scene, "pause": pause})
            pause = 0.0
        else:
            raise ScriptError(f"line {number} is not `NAME (mood): text`, `scene:`, `pause:` or `title:`: {row}")
    if not lines:
        raise ScriptError("the script has no spoken lines")
    return {"title": title, "lines": lines}


def load_character(cast: Path, name: str) -> dict:
    path = cast / f"{name}.json"
    if not path.exists():
        raise ScriptError(f"no character file for {name}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def job(line: dict, character: dict, cast: Path) -> dict:
    """The say.py job for one line. `engine` picks the batch it goes in."""
    engine, voice, mood = character["engine"], character["voice"], line["mood"]
    moods = character.get("moods", {})
    if mood and mood not in moods:
        raise ScriptError(f"{line['speaker']} has no mood {mood!r}; it has: {', '.join(sorted(moods)) or 'none'}")
    made = {"engine": engine, "text": line["text"]}
    changes = b""
    if engine == "clone":
        # A cloned voice acts through its reference clip, one clip per mood.
        reference = cast / (moods[mood] if mood else voice)
        voice = str(reference)
        changes = reference.read_bytes()
    elif engine == "qwen":
        direction = ", ".join(part for part in (character.get("direction"), moods.get(mood)) if part)
        if direction:
            made["direction"] = direction
    made["voice"] = voice
    key = json.dumps(made, sort_keys=True).encode() + changes
    made["out"] = f"{hashlib.sha256(key).hexdigest()[:16]}.wav"
    return made


def samples_of(path: Path) -> array.array:
    with wave.open(str(path)) as source:
        if (source.getframerate(), source.getnchannels(), source.getsampwidth()) != (RATE, 1, 2):
            raise ScriptError(f"{path} is not mono 16-bit {RATE} Hz")
        data = array.array("h")
        data.frombytes(source.readframes(source.getnframes()))
    return data


def mouth_levels(samples: array.array) -> list[float]:
    step = round(RATE * MOUTH_STEP)
    levels = [
        math.sqrt(sum(value * value for value in chunk) / len(chunk))
        for chunk in (samples[at:at + step] for at in range(0, len(samples), step))
    ]
    loudest = max(levels, default=0) or 1
    return [round(level / loudest, 2) for level in levels]


def build_timeline(lines: list[dict], files: list[Path], mix: Path) -> dict:
    rows, scenes, voices, clock = [], [], [], LEAD
    for line, path in zip(lines, files, strict=True):
        samples = samples_of(path)
        if rows:
            changed = line["scene"] != rows[-1]["scene"]
            clock += (SCENE_GAP if changed else GAP) + line["pause"]
        else:
            clock += line["pause"]
        if not scenes or scenes[-1]["name"] != line["scene"]:
            # A scene starts at the cut, in the middle of the gap before its first line.
            cut = round(clock - SCENE_GAP / 2, 3) if scenes else 0.0
            if scenes:
                scenes[-1]["end"] = cut
            scenes.append({"name": line["scene"], "start": cut})
        duration = len(samples) / RATE
        rows.append({**{key: line[key] for key in ("speaker", "mood", "text", "scene")},
                     "start": round(clock, 3), "duration": round(duration, 3), "mouth": mouth_levels(samples)})
        voices.append((round(clock * RATE), samples))
        clock += duration
    total = round(clock + TAIL, 3)
    scenes[-1]["end"] = total
    track = array.array("h", bytes(2 * round(total * RATE)))
    for at, samples in voices:
        track[at:at + len(samples)] = samples
    with wave.open(str(mix), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(track.tobytes())
    return {"duration": total, "mouth_step": MOUTH_STEP, "scenes": scenes, "lines": rows}


def trim(source: Path, target: Path) -> None:
    """Drop the silence engines leave at both ends, in the one format the timeline reads."""
    edge = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(source), "-af", f"{edge},areverse,{edge},areverse",
         "-ar", str(RATE), "-ac", "1", "-c:a", "pcm_s16le", str(target)],
        check=True,
    )


def speak(jobs: list[dict], folder: Path) -> None:
    """Speak what is not already there, one engine (one model load) at a time."""
    import video

    folder.mkdir(parents=True, exist_ok=True)
    missing = {made["out"]: made for made in jobs if not (folder / made["out"]).exists()}
    for engine in sorted({made["engine"] for made in missing.values()}):
        batch = [made for made in missing.values() if made["engine"] == engine]
        plan = folder / f"jobs-{engine}.json"
        plan.write_text(json.dumps(
            [{**{k: v for k, v in made.items() if k != "engine"}, "out": f"raw/{made['out']}"} for made in batch], indent=1))
        code = video.main(["say", engine, str(plan)])
        if code:
            raise ScriptError(f"the {engine} voice failed with exit {code}")
        for made in batch:
            trim(folder / "raw" / made["out"], folder / made["out"])


def run_story(args) -> int:
    try:
        parsed = parse(args.script.read_text(encoding="utf-8"))
        cast = args.cast.resolve()
        characters = {line["speaker"]: load_character(cast, line["speaker"]) for line in parsed["lines"]}
        jobs = [job(line, characters[line["speaker"]], cast) for line in parsed["lines"]]
        out = args.out.resolve()
        speak(jobs, out / "voices")
        timeline = build_timeline(parsed["lines"], [out / "voices" / made["out"] for made in jobs], out / "dialogue.wav")
    except ScriptError as error:
        print(error, file=sys.stderr)
        return 2
    timeline = {"title": parsed["title"], "cast": {name: c.get("look", {}) for name, c in characters.items()}, **timeline}
    (out / "timeline.json").write_text(json.dumps(timeline, indent=1))
    # A composition reads this with a script tag: no fetch while frames are seeked.
    (out / "timeline.js").write_text(f"window.STORY = {json.dumps(timeline)};\n")
    print(json.dumps({"timeline": str(out / "timeline.json"), "seconds": timeline["duration"], "lines": len(jobs)}))
    return 0


def run_character(args) -> int:
    name = args.name.lower()
    cast = args.cast.resolve()
    folder = cast / "voices"
    folder.mkdir(parents=True, exist_ok=True)
    try:
        moods = dict(entry.split("=", 1) for entry in args.mood)
    except ValueError:
        print("--mood is NAME=DIRECTION", file=sys.stderr)
        return 2
    clips = {"": name, **{mood: f"{name}-{mood}" for mood in moods}}
    jobs = []
    for mood, stem in clips.items():
        made = {"engine": "design", "text": SAMPLE_TEXT, "voice": args.voice_design, "out": f"{stem}.wav"}
        if mood:
            made["direction"] = moods[mood]
        # A new description replaces the old clip.
        (folder / made["out"]).unlink(missing_ok=True)
        jobs.append(made)
        (folder / f"{stem}.txt").write_text(SAMPLE_TEXT + "\n")
    try:
        speak(jobs, folder)
    except ScriptError as error:
        print(error, file=sys.stderr)
        return 2
    path = cast / f"{name}.json"
    previous = json.loads(path.read_text()) if path.exists() else {}
    character = {**previous, "engine": "clone", "voice": f"voices/{name}.wav", "description": args.voice_design,
                 "moods": {mood: f"voices/{stem}.wav" for mood, stem in clips.items() if mood}}
    path.write_text(json.dumps(character, indent=1) + "\n")
    print(json.dumps({"character": str(path), "listen": str(folder / f"{name}.wav")}))
    return 0
