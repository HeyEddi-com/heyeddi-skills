#!/usr/bin/env python3
"""Speak a batch of lines with a local engine, loading the model once.

Run through `video.py say`, which uses the engine's own environment.
Jobs file: [{"text": ..., "voice": ..., "out": ..., "direction": ...}]
`voice` is a speaker name (qwen, pocket), a description of the voice to invent
(design), or a reference .wav with its transcript in a .txt beside it (clone).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

MODELS = {
    "qwen": ["Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"],
    "design": ["Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"],
    "clone": ["Qwen/Qwen3-TTS-12Hz-1.7B-Base"],
}
DIRECTED = {"qwen", "design"}


def check_jobs(engine: str, jobs: list[dict]) -> None:
    for number, job in enumerate(jobs, 1):
        for key in ("text", "voice", "out"):
            if not job.get(key):
                raise ValueError(f"line {number} needs {key!r}")
        if job.get("direction") and engine not in DIRECTED:
            raise ValueError(f"line {number}: {engine} cannot follow a direction and would ignore it")


def model_path(engine: str, download: bool = False) -> str:
    from huggingface_hub import snapshot_download

    # A local folder: given a model name, the library asks the network on every load.
    return snapshot_download(MODELS[engine][0], local_files_only=not download)


def load_model(engine: str):
    import torch
    from qwen_tts import Qwen3TTSModel

    return Qwen3TTSModel.from_pretrained(model_path(engine), device_map="cpu", dtype=torch.float32)


def writer(generate):
    import soundfile as sf

    def speak(job: dict) -> float:
        import torch

        # The same seed per line: a line sounds the same whatever else is in the batch.
        torch.manual_seed(7)
        wavs, rate = generate(job)
        sf.write(job["out"], wavs[0], rate)
        return len(wavs[0]) / rate

    return speak


def qwen_speaker():
    model = load_model("qwen")
    return writer(lambda job: model.generate_custom_voice(
        text=job["text"], language="English", speaker=job["voice"], instruct=job.get("direction", "")
    ))


def design_speaker():
    model = load_model("design")
    return writer(lambda job: model.generate_voice_design(
        text=job["text"], language="English",
        instruct=" ".join(part for part in (job["voice"], job.get("direction")) if part),
    ))


def clone_speaker():
    model = load_model("clone")
    prompts: dict = {}

    def generate(job: dict):
        reference = Path(job["voice"])
        if job["voice"] not in prompts:
            prompts[job["voice"]] = model.create_voice_clone_prompt(
                ref_audio=str(reference), ref_text=reference.with_suffix(".txt").read_text(encoding="utf-8").strip()
            )
        return model.generate_voice_clone(
            text=job["text"], language="English", voice_clone_prompt=prompts[job["voice"]]
        )

    return writer(generate)


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
        if engine == "clone":
            job["voice"] = str(Path(jobs_file).resolve().parent / job["voice"])
        Path(job["out"]).parent.mkdir(parents=True, exist_ok=True)
    speakers = {"qwen": qwen_speaker, "design": design_speaker, "clone": clone_speaker, "pocket": pocket_speaker}
    speak = speakers[engine]()
    for job in jobs:
        start = time.time()
        seconds = speak(job)
        print(json.dumps({"out": job["out"], "seconds": round(seconds, 2), "took": round(time.time() - start, 1)}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
