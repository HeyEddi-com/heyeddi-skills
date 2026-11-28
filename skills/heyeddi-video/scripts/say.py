#!/usr/bin/env python3
"""Speak a batch of lines with a local engine, loading the model once.

Run through `video.py say`, which uses the engine's own environment.
Jobs file: [{"text": ..., "voice": ..., "out": ..., "direction": ...}]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

QWEN_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"


def check_jobs(engine: str, jobs: list[dict]) -> None:
    for number, job in enumerate(jobs, 1):
        for key in ("text", "voice", "out"):
            if not job.get(key):
                raise ValueError(f"line {number} needs {key!r}")
        if job.get("direction") and engine != "qwen":
            raise ValueError(f"line {number}: only qwen follows a direction, {engine} would ignore it")


def qwen_path(download: bool = False) -> str:
    from huggingface_hub import snapshot_download

    # A local folder: given a model name, the library asks the network on every load.
    return snapshot_download(QWEN_MODEL, local_files_only=not download)


def qwen_speaker():
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel

    torch.manual_seed(7)
    model = Qwen3TTSModel.from_pretrained(qwen_path(), device_map="cpu", dtype=torch.float32)

    def speak(job: dict) -> float:
        wavs, rate = model.generate_custom_voice(
            text=job["text"], language="English", speaker=job["voice"], instruct=job.get("direction", "")
        )
        sf.write(job["out"], wavs[0], rate)
        return len(wavs[0]) / rate

    return speak


def pocket_speaker():
    import soundfile as sf
    from pocket_tts import TTSModel

    model = TTSModel.load_model()
    states: dict = {}

    def speak(job: dict) -> float:
        voice = job["voice"]
        states[voice] = states.get(voice) or model.get_state_for_audio_prompt(voice)
        audio = model.generate_audio(states[voice], job["text"]).numpy()
        sf.write(job["out"], audio, model.sample_rate)
        return len(audio) / model.sample_rate

    return speak


def main(engine: str, jobs_file: str) -> int:
    jobs = json.loads(Path(jobs_file).read_text(encoding="utf-8"))
    check_jobs(engine, jobs)
    # Output paths are relative to the jobs file.
    for job in jobs:
        job["out"] = str(Path(jobs_file).resolve().parent / job["out"])
        Path(job["out"]).parent.mkdir(parents=True, exist_ok=True)
    speak = {"qwen": qwen_speaker, "pocket": pocket_speaker}[engine]()
    for job in jobs:
        start = time.time()
        seconds = speak(job)
        print(json.dumps({"out": job["out"], "seconds": round(seconds, 2), "took": round(time.time() - start, 1)}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
