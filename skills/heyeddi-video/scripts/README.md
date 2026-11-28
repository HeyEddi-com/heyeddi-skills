# Skill scripts

`video.py` runs from any directory.

- `setup`: local voice, headless Chrome, telemetry off.
- `hf <project> -- <hyperframes args>`: one local CLI command, queued behind other heavy jobs.
- `setup --captions` once, then `words <file>.wav`: word timings as JSON, computed locally.
- `render <project> -o <file>.mp4`: check, render, normalise loudness, verify.
- `verify <file>.mp4`: streams, loudness, and a frame sheet.

`HEYEDDI_VIDEO_HOME` moves the tool cache (default `~/.cache/heyeddi-video`).
