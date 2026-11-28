# Cartoon and character work

Flat 2D characters can be drawn and acted entirely in code.

## Rig

- One inline SVG per character. Each moving part is its own `<g>` with an id: body, head, eyes, pupils, eyelids, brows, mouth shapes, each arm, each leg, held props.
- Set pivots with GSAP `svgOrigin` at the joint, never CSS `transform-origin`.
- Draw several mouth shapes and switch their opacity with `tl.set` on syllable beats while that character speaks.
- A character is a function that returns SVG, so two shots share one design.

## Camera

- Draw the whole set in one SVG and move an HTML wrapper around it (`x`, `y`, `scale`, `transformOrigin: "0 0"`). Give the SVG `overflow: visible` and paint the backdrop past the frame.
- Do not tween an SVG group with `svgOrigin` across several zoom levels: the framing drifts a little more at every change.
- Shake the child, not the camera, so the two never fight over one property.

## Acting

- Anticipate before a move, overshoot, settle. Squash on landing, stretch in flight, keeping volume.
- Blink every few seconds. Eyes move before the head; the head before the body.
- Hold a pose long enough to read it, with a small breathing move on the body only.
- No `repeat: -1`: compute the repeat count from the scene length.

## Staging

- Background, middle, and foreground layers that move at different speeds.
- Change shot size for the joke: wide to set up, close for the reaction, then the payoff.
- Words on screen in speech bubbles or captions, so it reads muted.
- Squash, smear frames, and a sound effect make a hit land.

## Limits

Say them before building: felt, fur, realistic lighting, and film-like acting are not drawn by this method. Those need a 3D pipeline (Blender renders, or rigged glTF characters) or a video generator.
