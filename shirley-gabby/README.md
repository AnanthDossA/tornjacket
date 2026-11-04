# Shirley & Gabby engine

Separate from the Torn Jacket engine (which is untouched). Fictional cartoon series: elder sister Shirley + younger brother Gabby.

## Files
- `toon.py` - layer 1: Skia vector drawing, rigged human characters (FK skeleton, walk cycle, gestures, cartoon hands, springs for hair/pom-pom/strings, squash & stretch, smears, blinks, eye-look, cel shading), viseme lip-sync from audio, keyframe Tracks.
- `acting.py` - layer 2a: pose-to-pose acting (key poses, holds, anticipation/overshoot/settle curve, animation on twos, exaggeration, per-character personality), phrase-by-phrase TTS with comic pauses.
- `creature.py` - layer 2b: general creature parts (tentacles with curl/wave/follow-through, creature faces, crown, PoseTrack) + the Sock King.
- `chars.py` - Shirley and Gabby character specs.
- `sets.py` - laundromat + Sock Dimension sets (parallax layers), dryer glow, portal transition.
- `scene_ep.py` (laundromat -> portal -> Sock Dimension), `king_scene.py` (Sock King), `compare.py` (smooth vs pose-to-pose), `motion_test.py`, `scene_test.py` - test scenes. Run with `--preview` for a contact sheet.

## Requirements
`pip install skia-python numpy scipy pillow` + ffmpeg. Voices reuse Torn Jacket's `voices.py` (Kokoro) and fonts from `~/tj`.

## Status / next
Not yet a general engine: scenes are hand-scripted. Next: scene script format, set kit, action library (run/sit/jump), props, front/back views, creature templates.
