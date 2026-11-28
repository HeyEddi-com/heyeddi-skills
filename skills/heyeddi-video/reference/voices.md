# Voices

All three run on this machine on the CPU. Pick one engine per video. Timings are from a 12-thread laptop.

| Engine | Use it for | Speed | Directions | Licence |
| --- | --- | --- | --- | --- |
| Qwen3-TTS 1.7B | Characters and anything that needs acting | 7 to 9 times slower than real time | Yes, plain English | Apache-2.0 code; check the model card |
| Pocket TTS | Fast natural narration, many takes | About 4 times faster than real time | No | MIT code, CC-BY-4.0 weights: credit Kyutai |
| Kokoro | Default, nothing extra to install | A few seconds a line | No | Apache-2.0 weights |

## Voices

- Qwen3-TTS, native English: `Aiden`, `Ryan`. Others (`Vivian`, `Serena`, `Dylan`, `Eric`, `Uncle_Fu`, `Ono_Anna`, `Sohee`) are native to other languages; they can still read English, in character.
- Pocket TTS: `alba`, `anna`, `george`, `marius`, `michael`, `eve`, and more.
- Kokoro: prefer the higher-graded `af_heart`, `af_bella`, `bf_emma`, `am_fenrir`, `am_puck` over `am_michael`.

## Use

```bash
python3 scripts/video.py setup --voice qwen            # once; downloads about 4.5 GB
python3 scripts/video.py say qwen <project>/lines.json
python3 scripts/video.py hf <project> -- tts "text" --voice af_heart --output assets/a.wav   # Kokoro
```

`lines.json`, with `out` relative to that file:

```json
[{"text": "Not tonight, little bug.", "voice": "Aiden", "direction": "wide awake, determined, a little smug", "out": "assets/l5.wav"}]
```

## Practice

- Put all lines in one jobs file: the model loads once.
- Write the direction as who is speaking and how they feel.
- Trim the silence at both ends, then time the scenes to the files.
- Check a take with `video.py words <file>.wav` against the script. It does not judge acting: say that nobody has heard it.
- Voice cloning is not offered here. Cloning a real person needs their consent.
