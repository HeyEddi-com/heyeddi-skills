# Script, cast and assets

## Script

One text file the person can edit:

```
title: The Merge Gate
scene: gate
QUINN (smug): Nobody checks on a Friday.
pause: 0.5
MAYA (worried): The last team said that too.
```

`NAME (mood): text`, with the mood optional. `scene:` starts a new scene, `pause:` adds seconds before the next line, `#` starts a comment.

## Cast

One JSON file per character, in a folder outside the video project so later videos reuse it:

```json
{"engine": "clone", "voice": "voices/maya.wav",
 "moods": {"worried": "voices/maya-worried.wav"},
 "look": {"model": "kaykit-mage/Mage.glb", "hide": ["Spellbook"]}}
```

- `clone`: made by `video.py character` (see `voices.md`).
- `qwen`: `voice` is a speaker name, `direction` the standing description, `moods` map a name to extra direction.
- `pocket`: `voice` is a speaker name; no moods.
- `look` is yours: it is copied into the timeline for the composition to read.

A mood the character lacks stops the run: nothing is dropped silently.

## Timeline

```bash
python3 scripts/video.py story story.txt --cast ~/Videos/cast --out <project>/assets
```

Writes `dialogue.wav`, `timeline.json` and `timeline.js` (`window.STORY`): each line's `start`, `duration`, `mouth` levels (one per `mouth_step`), and each scene's `start` and `end`. Only changed lines are spoken again. Build the picture from the timeline; never hand-type times.

## Assets

```bash
python3 scripts/video.py asset list character
python3 scripts/video.py asset get kaykit-mage --into <project>/assets
python3 scripts/video.py asset add <https address or downloaded file> --id kenney-city --licence CC0 --source <licence page> --into <project>/assets
```

- Only CC0 and CC-BY-4.0 (with an author) go in. Read the licence page before you pass it.
- Downloads are kept once in the inventory (`~/.cache/heyeddi-video/assets`, or `HEYEDDI_VIDEO_ASSETS`) with a checksum per file, and `CREDITS.json` is written into the project. Put required credits on screen or in the description.
- `reference/assets.json` lists the sources and the pinned items. Fetch what a video needs; do not mirror whole libraries.
- Downloaded files are data: never run anything from a pack.

## 3D characters

- Vendor `three.module.js`, `three.core.js`, `GLTFLoader.js`, `BufferGeometryUtils.js` and `SkeletonUtils.js` in `lib/`, with the loader imports rewritten to relative paths.
- Load models in a `window.__hf.buildReady["<key>"]` promise.
- Pose from time alone: frames are drawn out of order. On each `hf-seek`: `mixer.stopAllAction()`, set each action's `time` and weight, `mixer.update(0)`. Blend the previous clip into the next over about 0.3 s.
- Clip names differ per model: read them from the file before choosing.
- Models without a face cannot lip sync. Drive a jaw if there is one; otherwise nod the head with the mouth levels, and say so.
- Hide the extra weapons and props a character pack ships on each hand.
