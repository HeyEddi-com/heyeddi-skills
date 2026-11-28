---
name: heyeddi-video
description: "Makes finished videos locally with HyperFrames: cartoons and character stories, product launches, explainers, data stories, vertical social clips with captions, and kinetic type. Use when asked to make, animate, or render a video, promo, reel, story, or cartoon. Rides on the official HyperFrames skills for craft and adds local-only rendering, truth rules, and a verified finished file. Not for UI motion inside an app (motion-physics) or for posting to social networks."
version: 1.0.0
product-version: 3.10.0
author: HeyEddi-com
---

# HeyEddi video

The finished MP4 on this machine is the output. Posting is not part of this skill.

## Before the first video

1. Official craft skills (once per machine). If `hyperframes` is not in the skill list:
   `DISABLE_TELEMETRY=1 npx skills add heygen-com/hyperframes -g -a claude-code cursor -y --skill hyperframes hyperframes-cli hyperframes-registry media-use remotion-to-hyperframes figma slideshow`
2. Local tools (once per machine): `python3 scripts/video.py setup`. It installs the Kokoro voice and headless Chrome under `~/.cache/heyeddi-video` and turns telemetry off. Needs Node 22+, FFmpeg, and `uv`.
3. Load `/hyperframes` and the reference it names for this kind of video. Then read `reference/video-types.md` and `reference/voices.md`; for a character, also `reference/cartoon.md`.

Paths below that start with `scripts/` are relative to this skill's folder: use the absolute path when your shell is elsewhere. The `CLAUDE.md` that `init` writes says to call `npx hyperframes` directly: use `video.py` instead.

## Where this skill overrides theirs

- **Local wins.** Skip their usage note, `usage`, `auth status`, sign-in prompts, and Google Fonts. Vendor every font and library.
- **Synthesised music is fine** when the user supplied no track, though their sound guide advises against synthesised music, tones, and chimes. Say it was synthesised.
- **No Studio preview** unless the user wants to edit there. Render when your check and frame review pass.
- **A single `index.html` is fine**, with one continuous scene or several. The lint warnings about file size and sub-compositions are then expected.

## Local only

Their skills mention hosted features. Here:

- Do not send the usage note (`hyperframes events`), `usage`, `feedback`, `publish`, `cloud`, `lambda`, `cloudrun`, or `auth`. `video.py` refuses them.
- No HeyGen voices, avatars, or music, and no image or video generator, unless the user asked for it and was told it costs money or leaves the machine.
- Run every command through the script so telemetry stays off and heavy jobs queue: `python3 scripts/video.py hf <project> -- lint`.
  Browser and encoding commands run one at a time on the machine. `check`, `snapshot`, and `render` can take many minutes: run them in the background and wait to be told they finished. If the machine refuses another background job, run it in the foreground.

## Pipeline

1. **Story.** One viewer, one thing to remember. A build request takes your recommended storyline: write it and the two others to `STORYLINES.md` and keep going. For a film over 15 s, also write the `SPEC.md` and `REVIEW.md` their skill asks for.
2. **Sources.** Every claim on screen traces to the person's words, the repo, or their site. Real screens come from captures or files they gave you. Anything you invent is marked as an illustration on screen.
3. **Assets.** Copy fonts, libraries, and media into the project. Search the registry before hand-building a named effect. Added items often load GSAP from a CDN or fonts from Google: rewrite those to vendored files. Record the licence of anything you did not make.
4. **Build.** `python3 scripts/video.py hf <parent-dir> -- init <name> --non-interactive --skip-skills` creates `<parent-dir>/<name>`. In the new `index.html`, replace the CDN script tag with a vendored file, and ignore the `publish` script in its `package.json`. Times follow the voice: generate speech first, measure each file (they carry silent padding), then lay out scenes.
5. **Look.** `hf <project> -- snapshot --at ...` while you build, and open every frame (they land in `<project>/.hyperframes/artifacts/snapshots/<id>/`). A passing check does not show how it looks.
6. **Render.** `python3 scripts/video.py render <project> -o <file>.mp4`. It runs `check` first, so do not run a separate check just before it. Exit 1 means the file has a listed problem: fix it and render again. Open the `.frames.jpg` it writes, then extract more frames with FFmpeg around each transition.
7. **Report.** The file path, length, render time, what was only looked at, and what nobody checked. You cannot hear audio: say so.

## Notes

- Videos and project folders are build output. Keep them out of git unless asked.
- Say which parts code drew and which came from somewhere else.
