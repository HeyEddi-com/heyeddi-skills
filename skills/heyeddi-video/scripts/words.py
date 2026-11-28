#!/usr/bin/env python3
"""Print word timings of a speech file as JSON. Runs locally with faster-whisper.

Run through `video.py words <file>`, which uses the tool venv.
"""
from __future__ import annotations

import json
import subprocess
import sys

MODEL = "base.en"


def rows(segments) -> list[dict]:
    return [
        {"word": word.word.strip(), "start": round(word.start, 3), "end": round(word.end, 3)}
        for segment in segments
        for word in segment.words
    ]


def main(path: str) -> int:
    import numpy as np
    from faster_whisper import WhisperModel

    # A decoded array, not a path: the library's own file reader breaks on current PyAV.
    pcm = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(np.frombuffer(pcm, dtype=np.float32).copy(), word_timestamps=True)
    print(json.dumps(rows(segments)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
