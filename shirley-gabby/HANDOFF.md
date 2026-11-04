# Shirley & Gabby — handoff notes (read this first in a new chat)

Written at the end of the first build session (2026-11-04) so a new conversation can continue without the old chat history.

## 1. The project
- **Owner:** the Torn Jacket channel owner (India). Wants a premium animated series, aiming toward **Rick and Morty / Inside Job quality**, for YouTube now and possibly longer-form (Netflix-style, 11–22 min) later.
- **Show:** *Shirley & Gabby* (working title, the owner's own invention). **Pure fiction: no real-world news or facts.** Absurd adventures in weird worlds.
- **Formula:** Gabby jumps into trouble, Shirley gets dragged along complaining, the world is absurd, and it ends on a sting.
- **Completely separate from Torn Jacket.** The Torn Jacket news-Shorts pipeline (scheduled task + studio artifact, engine.py) must stay untouched. This engine reuses Torn Jacket's `voices.py` (Kokoro TTS) and fonts only by reading them.

## 2. Characters (adults, never kids)
- **Shirley (elder sister, ~29):** sharp, deadpan, permanently tired, secretly the bravest. Tall head, black hair in a bun with a pencil stuck through it, round glasses, gold earrings, mustard blouse with collar and buttons, plum trousers, half-lidded eyes. Voice `bf_emma` (speed ~0.92). Moves minimally and slowly; barely gestures; rolls her eyes.
- **Gabby (younger brother, ~22):** loud, optimistic, gullible, causes every adventure, occasionally accidentally right. Round head, stubble, teal beanie with a pom-pom, red hoodie with strings and a pocket, jeans, white sneakers, big eyes. Voice `am_puck` (speed ~1.05–1.1). Fast, bouncy, exaggerated, overacts.
- **Sock King:** first creature. A giant pink-and-gold-striped sock with bendy sock-arms (tentacles), a ribbed cuff and a crown. Deep echoey voice (`am_onyx`, pitched down). Poses: regal, loom, point, swoon, flex. Sits on a royal-blue throne in the Sock Dimension.
- Specs live in `chars.py`.

## 3. Sample episode used for tests: "The Lost Sock Dimension"
Laundromat at night: Gabby: "Shirl, the dryer ate my lucky sock." Shirley: "You've never been lucky." Gabby: "Because it keeps getting eaten!" The dryer glows green, a portal swirls, they fall into the **Sock Dimension** (purple swirl sky, sock mountains, floating socks). Gabby: "It's beautiful, every sock I ever lost." Shirley: "Why do they all smell like you?" Sock King: "Who dares enter with a matching pair?" Shirley (looks at her matching socks): "Gabby. Run." King: "Wait… She's perfect." (heart eyes). Planned ending: Shirley is engaged to a sock; Gabby: "Lucky." End card: "(next week: the fridge light. where does it go?)"

## 4. What is built (files in this folder)
- `toon.py`: Skia vector renderer, human rig (FK skeleton, 3/4 view, walk cycle with heel-toe, gestures), cartoon hands (relax/point/open/fist/tuck), springs for secondary motion (hair strands, bun, pencil, pom-pom, hoodie strings, earrings, inertia lean, head lag), expression pop, squash & stretch, smear streaks, blinks, eye-look, cel shading, fold lines, viseme lip-sync from audio (amplitude + spectral centroid).
- `acting.py`: **pose-to-pose acting** (the owner liked this a lot): key poses → holds with a small drift → snappy anticipation/overshoot/settle, animation on twos, exaggeration, personalities (gabby / shirley), ~13 poses. `say_phrases()` voices each phrase separately with comic pauses, which gives exact timings for pose changes.
- `creature.py`: general creature parts (Tentacle chains with curl/wave/springs, creature_face, crown, PoseTrack) + `SockKing`.
- `sets.py`: laundromat (parallax wall/floor/foreground, washers with tumbling clothes, the glowing dryer, flickering lights, neon "SPIN CYCLE", "LOST SOCKS?" poster) and the Sock Dimension (sky/far/mid/ground/fg layers, throne), plus a green swirl `portal()` transition.
- Scenes: `scene_ep.py` (21 s laundromat → portal → Sock Dimension, 1920x1080), `king_scene.py` (15 s Sock King scene), `compare.py` (smooth vs pose-to-pose side by side), `motion_test.py`, `scene_test.py`. Run any with `--preview` for a contact sheet. Outputs go to `/root/sg/out` (paths are hardcoded: adjust `OUT`, `/root/tj/...` voices and fonts).
- Requirements: `pip install skia-python numpy scipy pillow kokoro-onnx misaki onnxruntime` + ffmpeg; Kokoro model files + Torn Jacket `voices.py` + fonts (Bangers, Catamaran) as in the Torn Jacket runbook.

## 5. Owner feedback and preferences so far
- **Show intermediate results**: send every still and clip as it's generated, not only the final.
- Liked: pose-to-pose acting ("looks better, continue"). Asked to fix Shirley's crossed-arm hands (done: tucked).
- Rick and Morty / Inside Job motion is **stylized, not realistic**: no motion capture. Strong poses, holds, snappy timing, exaggeration. Creatures and aliens must be supported (general rig).
- Wants it to become a **general engine** that can make any scene, not hand-coded test scenes.
- Asked about Unity (not suitable: GUI-driven, breaks automation) and then **Blender** (suitable: fully scriptable headless with `blender -b --python script.py`). The owner installed Blender and a **Blender connector/extension** in the Claude desktop app. It only works in a desktop chat linked to their computer (not in the scheduled cloud chat).
- Voices are the weakest part. The engine supports recorded audio (4th item of a LINES entry = wav path); lip-sync works from any audio.

## 6. Honest status
Today it's a **toolkit, not a general engine**: every scene is a hand-timed script. Missing: a scene script format, a set kit, an action library (run/sit/jump/trip/hold/throw, walking paths, walking toward or away from camera), props attached to hands, character interaction, front/back views and turning, creature templates (blob / multi-arm / quadruped / robot / floating), Rhubarb Lip Sync, a bigger pose library.

## 7. Next steps (agreed direction)
1. **Blender feasibility test on the owner's PC** (through the Blender connector and/or headless `blender -b`): render Gabby two ways, flat 2D Grease Pencil and cartoon-shaded 3D, with timings. Decide whether to move rendering to Blender (better lines, lighting, any camera angle, props and interaction for free in 3D toon style) or keep improving the Skia engine.
2. Build a **scene script format** (screenplay-like: location, characters, lines with emotion, actions) that compiles to animation automatically: auto poses from emotions, auto shot/reverse-shot camera, timing from phrases.
3. Set kit, action library, props, more views, creature templates, Rhubarb lip-sync.
4. Optional: owner/friends record real voice lines.

## 8. Ideas parked for later
Recurring extras: the landlord in disguises, a sentient router that knows too much, Mum on video call. Alternate dynamics considered: an Inside Job flip (Shirley works inside a tech giant) or Shirley as a reckless genius inventor. The chosen dynamic is gullible Gabby causing trouble and Shirley the reluctant brave one, in pure-fiction weird worlds.
