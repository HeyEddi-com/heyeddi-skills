#!/usr/bin/env python3
"""One entry point for local HyperFrames work: setup, hf, say, words, render, verify.

Everything stays on this machine. Heavy steps (Chrome, FFmpeg) take a lock, so
several agents on one machine run them one at a time.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HYPERFRAMES = "0.9.104"
CHROME = "158.0.8127.88"
LOUDNESS_RANGE = (-18.0, -12.0)
# Extra voice engines, each in its own environment. Kokoro needs none: `hf <project> -- tts`.
ENGINES = {"pocket": ["pocket-tts", "soundfile"], "qwen": ["qwen-tts", "soundfile"]}
CPU_WHEELS = "https://download.pytorch.org/whl/cpu"
# CLI commands that upload, bill, sign in or report usage.
LEAVES_MACHINE = {"publish", "cloud", "lambda", "cloudrun", "auth", "events", "feedback", "usage"}
# Commands that start a browser or encode video.
HEAVY = {"check", "snapshot", "render", "capture", "keyframes", "benchmark", "transcribe"}


class NotLocal(ValueError):
    pass


def tools_home() -> Path:
    default = Path.home() / ".cache" / "heyeddi-video"
    return Path(os.environ.get("HEYEDDI_VIDEO_HOME", default))


def hyperframes_env(home: Path, base: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base is None else base)
    env.update(HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1", HYPERFRAMES_SKIP_SKILLS="1")
    python = home / "venv" / "bin" / "python"
    if python.exists():
        env["HYPERFRAMES_PYTHON"] = str(python)
    shells = sorted(home.glob("chrome/chrome-headless-shell/*/*/chrome-headless-shell"))
    if shells:
        env["HYPERFRAMES_BROWSER_PATH"] = str(shells[-1])
    return env


def local_command(args: list[str]) -> list[str]:
    if args and args[0] in LEAVES_MACHINE:
        raise NotLocal(f"`hyperframes {args[0]}` sends data off this machine. The user runs that, not the agent.")
    return ["npx", "--yes", f"hyperframes@{HYPERFRAMES}", *args]


def is_heavy(args: list[str]) -> bool:
    return bool(args) and args[0] in HEAVY


def take_lock(handle, wait=lambda h: fcntl.flock(h, fcntl.LOCK_EX)) -> None:
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        # Without this a queued job looks hung.
        print("video.py: waiting for another video job to finish", file=sys.stderr, flush=True)
        wait(handle)


def lock_path(home: Path) -> Path:
    return home / "heavy.lock"


@contextlib.contextmanager
def one_heavy_job():
    # In the user's own folder, never shared /tmp, and opened without truncating.
    path = lock_path(tools_home())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        take_lock(handle)
        yield


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(command, env=hyperframes_env(tools_home()), **kwargs)


def parse_loudness(log: str) -> float | None:
    summary = log.rsplit("Integrated loudness:", 1)
    found = re.search(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", summary[-1])
    return float(found.group(1)) if len(summary) == 2 and found else None


def problems(probe: dict, loudness: float | None, silent_ok: bool) -> list[str]:
    kinds = {stream.get("codec_type") for stream in probe.get("streams", [])}
    found = []
    if "video" not in kinds:
        found.append("no video stream")
    if "audio" not in kinds:
        if not silent_ok:
            found.append("no audio track")
    elif loudness is None:
        found.append("loudness could not be measured")
    elif not LOUDNESS_RANGE[0] <= loudness <= LOUDNESS_RANGE[1]:
        found.append(f"loudness {loudness} LUFS is outside {LOUDNESS_RANGE[0]:.0f} to {LOUDNESS_RANGE[1]:.0f}")
    return found


def probe_file(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def measure_loudness(path: Path) -> float | None:
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-vn", "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    return parse_loudness(out.stderr)


def say_command(home: Path, engine: str, jobs: Path) -> tuple[list[str], dict[str, str]]:
    python = home / "engines" / engine / "bin" / "python"
    if not python.exists():
        raise FileNotFoundError(f"The {engine} voice is not installed. Run: video.py setup --voice {engine}")
    command = [str(python), str(Path(__file__).with_name("say.py")), engine, str(jobs)]
    env = {"HF_HUB_DISABLE_TELEMETRY": "1"}
    if engine == "qwen":
        env["HF_HUB_OFFLINE"] = "1"
    return command, env


def install_voice(home: Path, engine: str) -> None:
    folder = home / "engines" / engine
    python = folder / "bin" / "python"
    if not python.exists():
        subprocess.run(["uv", "venv", "-q", "-p", "3.12", str(folder)], check=True)
    pip = ["uv", "pip", "install", "-q", "-p", str(python)]
    # CPU builds of torch: the default Linux wheels pull gigabytes of CUDA.
    subprocess.run([*pip, "torch", "torchaudio", "--index-url", CPU_WHEELS], check=True)
    subprocess.run([*pip, *ENGINES[engine], "--extra-index-url", CPU_WHEELS, "--index-strategy", "unsafe-best-match"], check=True)
    if engine == "qwen":
        scripts = str(Path(__file__).parent)
        code = f"import sys; sys.path.insert(0, {scripts!r}); import say; say.qwen_path(download=True)"
        subprocess.run([str(python), "-c", code], env={**os.environ, "HF_HUB_DISABLE_TELEMETRY": "1"}, check=True)


def words_command(home: Path, audio: Path) -> list[str]:
    python = home / "venv" / "bin" / "python"
    if not any(home.glob("venv/lib/*/site-packages/faster_whisper")):
        raise FileNotFoundError("Word timings are not installed. Run: video.py setup --captions")
    return [str(python), str(Path(__file__).with_name("words.py")), str(audio)]


def setup(captions: bool = False) -> int:
    home = tools_home()
    home.mkdir(parents=True, exist_ok=True)
    python = home / "venv" / "bin" / "python"
    if not python.exists():
        subprocess.run(["uv", "venv", "-q", "-p", "3.12", str(home / "venv")], check=True)
    packages = ["kokoro-onnx", "soundfile", "numpy", *(["faster-whisper"] if captions else [])]
    subprocess.run(["uv", "pip", "install", "-q", "-p", str(python), *packages], check=True)
    if "HYPERFRAMES_BROWSER_PATH" not in hyperframes_env(home, base={}):
        subprocess.run(
            ["npx", "--yes", "@puppeteer/browsers", "install", f"chrome-headless-shell@{CHROME}",
             "--path", str(home / "chrome")],
            check=True,
        )
    run(local_command(["telemetry", "disable"]), check=True)
    return run(local_command(["doctor"])).returncode


def verify(path: Path, silent_ok: bool) -> int:
    probe = probe_file(path)
    loudness = measure_loudness(path)
    found = problems(probe, loudness, silent_ok)
    duration = float(probe["format"]["duration"])
    sheet = path.with_suffix(".frames.jpg")
    # Frames come from the finished file: a passing check does not show how it looks.
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf", f"fps=24/{duration},scale=480:-2,tile=4x6",
         "-frames:v", "1", str(sheet)],
        check=True,
    )
    print(json.dumps({"file": str(path), "seconds": duration, "lufs": loudness, "frames": str(sheet), "problems": found}))
    return 1 if found else 0


def render(project: Path, output: Path, quality: str, silent_ok: bool) -> int:
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with one_heavy_job():
        checked = run(local_command(["check"]), cwd=project)
        if checked.returncode:
            print("check failed: fix the errors before rendering", file=sys.stderr)
            return checked.returncode
        with tempfile.TemporaryDirectory(dir=output.parent) as work:
            raw = Path(work) / "raw.mp4"
            made = run(local_command(["render", "-w", "2", "-q", quality, "-o", str(raw)]), cwd=project)
            if made.returncode:
                return made.returncode
            if any(stream.get("codec_type") == "audio" for stream in probe_file(raw)["streams"]):
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af",
                     "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", str(output)],
                    check=True,
                )
            else:
                raw.replace(output)
    return verify(output, silent_ok)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    install = sub.add_parser("setup", help="install the local voice and headless Chrome, turn telemetry off")
    install.add_argument("--captions", action="store_true", help="also install local word timings")
    install.add_argument("--voice", choices=sorted(ENGINES), action="append", default=[], help="also install a voice engine")
    speak = sub.add_parser("say", help="speak a jobs file with a local voice engine")
    speak.add_argument("engine", choices=sorted(ENGINES))
    speak.add_argument("jobs", type=Path)
    timing = sub.add_parser("words", help="print word timings of a speech file as JSON")
    timing.add_argument("file", type=Path)
    run_cli = sub.add_parser("hf", help="run a local hyperframes command: video.py hf <project> -- check")
    run_cli.add_argument("project", type=Path)
    run_cli.add_argument("args", nargs=argparse.REMAINDER)
    make = sub.add_parser("render", help="check, render, normalise loudness and verify")
    make.add_argument("project", type=Path)
    make.add_argument("-o", "--output", type=Path, required=True)
    make.add_argument("-q", "--quality", default="high", choices=["draft", "standard", "high"])
    make.add_argument("--silent-ok", action="store_true")
    check = sub.add_parser("verify", help="verify a finished file")
    check.add_argument("file", type=Path)
    check.add_argument("--silent-ok", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "setup":
        # Two agents installing into one environment would corrupt it.
        with one_heavy_job():
            for engine in args.voice:
                install_voice(tools_home(), engine)
            return setup(args.captions)
    if args.command == "say":
        try:
            command, extra = say_command(tools_home(), args.engine, args.jobs.resolve())
        except FileNotFoundError as error:
            print(error, file=sys.stderr)
            return 2
        with one_heavy_job():
            return subprocess.run(command, env={**os.environ, **extra}).returncode
    if args.command == "words":
        try:
            command = words_command(tools_home(), args.file.resolve())
        except FileNotFoundError as error:
            print(error, file=sys.stderr)
            return 2
        with one_heavy_job():
            return run(command).returncode
    if args.command == "verify":
        return verify(args.file.resolve(), args.silent_ok)
    if args.command == "render":
        return render(args.project.resolve(), args.output, args.quality, args.silent_ok)
    rest = args.args[1:] if args.args[:1] == ["--"] else args.args
    try:
        command = local_command(rest)
    except NotLocal as error:
        print(error, file=sys.stderr)
        return 2
    with one_heavy_job() if is_heavy(rest) else contextlib.nullcontext():
        return run(command, cwd=args.project.resolve()).returncode


if __name__ == "__main__":
    sys.exit(main())
