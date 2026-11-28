# Video types

Read the matching type file in the official `/hyperframes` skill too. This table is what held up on a 12-core laptop with an integrated GPU.

| Type | Shape | How to build it | Needs from outside |
| --- | --- | --- | --- |
| Cartoon, character story | 20 to 40 s, 16:9 | Layered SVG rigs and GSAP (`cartoon.md`) | Nothing for flat 2D. A photo-real or felt-puppet look needs generated or pre-rendered footage |
| Launch, promo | 30 to 60 s, 16:9 | Real screens, camera moves, 3D backdrop | Screenshots or recordings at 2x |
| Explainer | 30 to 60 s, 16:9 | One diagram that grows; one worked example travels through it | The facts |
| Data story | 20 to 40 s, 16:9 or 1:1 | SVG charts drawn from a data file; count-ups; one number lands | The data and its source and dates |
| Vertical clip | 15 to 30 s, 1080x1920 | Large type, word-timed captions, inside the platform safe zone | Footage if there is a speaker |
| Kinetic type, music | 15 to 30 s | Cuts on a beat grid, type as the picture | A licensed track, or a synthesised one |

## Tools and files

- Voice: `video.py hf <project> -- tts "text" --voice am_michael --speed 1.08 --output assets/voice/01.wav`
- Python with numpy and soundfile: `~/.cache/heyeddi-video/venv/bin/python`
- Sound effects and their licence: `~/.claude/skills/media-use/audio/assets/sfx/`
- Fonts and libraries: `npm pack <package>` (for example `@fontsource/outfit`, `gsap`, `three`), then copy the files into the project
- Ready-made blocks: `video.py hf <project> -- catalog`, then `video.py hf <project> -- add <name>`

## Sound

- Voice: pick an engine in `voices.md`. Spell names the way they should sound.
- Effects: copy from the set above and keep `CREDITS.md` with them.
- Music: synthesise a bed with numpy, or use a track the user supplies. Duck it under the voice.

## Shader transitions

- The registry's transition blocks are showcase cards. They do not transition your scenes.
- Use `HyperShader.init()` from the npm package `@hyperframes/shader-transitions`, with `class="scene"` hosts that overlap across each cut.
- Vendor its ES module build and import it from `<script type="module">`, setting `window.HyperShader`. A classic script tag fails lint on `Date.now`, `performance.now`, and `requestAnimationFrame`.
- Snapshots do not show the blend. Render a draft and extract frames around each seam.
- Some shaders render far slower than others. `sdf-iris` was much cheaper than `cinematic-zoom`.

## Music-led pieces

No voice to follow: pick a tempo, compute every cut from the beat index (at 30 fps and 120 BPM a beat is 15 frames), and write the track with numpy on the same grid.

## Vertical clips

- `init` makes 1920x1080 unless told: add `--resolution portrait`.
- Platform safe zone: x 120 to 888, y 288 to 1248, and no further right than x 780 below y 840. Keep captions ending near y 1220, since entrance motion needs room.

## Data stories

- Decide and write down: do merges count, how are renames and repo-wide sweeps treated, which date puts a commit in a week.
- Use output formats that cannot print names or email addresses.
- Put the date range and the source on screen.

## Lessons from real renders

- Bundling Three.js into a scene file fails lint (`Math.random`, `requestAnimationFrame` inside the library). Vendor `three.module.js` and `three.core.js` into `lib/` and import them.
- Draw Three.js and canvas frames from `hf-seek` (`e.detail.time`) as a pure function of time.
- Word-timed captions need real timings: `video.py setup --captions` once, then `video.py words <file>.wav`. Match the words to your script by position and fix the odd zero-length one.
- Check every number and code line you rebuild against its source before rendering.
- Frames are drawn out of order: give tweens absolute end values, not `+=` ones.
- In the bundled effects, `riser` is long and builds toward its end, and `whoosh` and `whoosh-short` are the same file.
