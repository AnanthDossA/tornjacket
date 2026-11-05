# Shirley & Gabby — handoff notes (read this first in a new chat)

Written at the end of the first build session (2026-11-04) so a new conversation can continue without the old chat history.

## 0. LOCKED: FINAL CHARACTER DESIGNS (owner-approved 2026-11-06), read before touching any character
**Shirley and Gabby are final. Never drift from these details, and never change them without the owner's explicit OK.**
Full spec with exact colours: `concept/characters_final.json`. Reference image: `concept/FINAL_characters.png` (drawn by `concept/teens_sheet.py`, default styles). Style: 2D comic, bold ink, flat colour, halftone shadows.
- **Shirley (~16, elder sister, sensible, modern Indian teen):**
  - Face and hair: oval face tapering to a small soft chin, kept short, small nose-to-mouth gap, almond eyes with big dark irises, soft thin brows, small closed smile. Black jaw-length bob with a wispy fringe and a **green flower clip**.
  - Outfit: **fitted lilac zip hoodie** (hood down, half-zipped over a white tee with a little planet print), slim blue jeans, white sneakers, gold bangle. Slim.
  - Never: **no bindi**, no makeup look, not an adult, not a long face.
- **Gabby (~14, younger brother, gymnastics/fitness freak):**
  - Face and hair: **round but lean face (NOT chubby)**, widest at the eyes, clean taper to the chin, narrow-ish, short, prominent ears, smiling squinty almond eyes, wide upper-teeth grin with dimples. Skin a little fairer than Shirley's (not too fair). Thick short wavy black hair.
  - Outfit: **red hoodie, hood down** (strings, pocket, sleeves pushed up), frayed denim shorts with chalk handprints, white wrist tape, chalky hands, knee plaster, white sneakers with red soles. Lean, athletic.
  - Signature poses: the "ta-da" salute and a handstand.
- Earlier designs (the adult Gabby and Shirley sheets, the chubby or long faces, kurti outfits, `blender/sg3d.py` 3D Gabby) are **superseded** and kept only as reusable code (drawing kit, organic hands, rig and engine).
- The repo is public: never commit the owner's reference photos.

## 1. The project
- **Owner:** the Torn Jacket channel owner (India). Wants a premium animated series, aiming toward **Rick and Morty / Inside Job quality**, for YouTube now and possibly longer-form (Netflix-style, 11–22 min) later.
- **Show:** *Shirley & Gabby* (working title, the owner's own invention). **Pure fiction: no real-world news or facts.** Absurd adventures in weird worlds.
- **Formula:** Gabby jumps into trouble, Shirley gets dragged along complaining, the world is absurd, and it ends on a sting.
- **Completely separate from Torn Jacket.** The Torn Jacket news-Shorts pipeline (scheduled task + studio artifact, engine.py) must stay untouched. This engine reuses Torn Jacket's `voices.py` (Kokoro TTS) and fonts only by reading them.

## 2. Characters
**Current design (2026-11-06): comic-style TEENS**, see `concept/teens_sheet.png` (drawn by `concept/teens_sheet.py`; halftone comic shading via `gabby_sheet.HALFTONE`). The owner dropped the earlier trait lists; the only brief is that both look like Indian teens, and Gabby is a gymnastics freak. The older adult/teen sheets (`gabby_sheet.png`, `shirley_sheet.png`) are superseded but keep the reusable drawing kit and organic hands.
- **Shirley (~16, elder sister):** the sensible one; a modern Indian girl who likes fitted clothes; **no bindi**. Oval face tapering to a small soft chin (kept short top-to-bottom, small nose-to-mouth gap), almond eyes with big dark irises, soft thin brows, small nose, small closed smile. Short bob with a wispy fringe, green flower hair clip. Fitted lilac zip hoodie (hood down, half-zipped over a white tee with a little planet print, ribbed cuffs and hem), slim blue jeans, white sneakers, gold bangle. (Alt outfit kept in code history: fitted teal kurti.) Hair: current bob + wispy fringe (owner kept it; alternatives in `concept/hair_options.png`). Slim build. Voice `bf_emma` (speed ~0.92) until real voices exist.
- **Gabby (~14, younger brother):** gymnastics freak, can't pass a wall without a handstand; loud and bouncy; lean, slim build. Round but lean face (fitness freak, NOT chubby): widest at the eyes, clean taper to the chin, no puffy cheeks; short top-to-bottom, small nose-to-mouth gap; skin a little fairer than Shirley's; prominent ears, almond eyes that squint up when he grins, small broad nose, thick short wavy black hair, wide smile showing the upper teeth. Red hoodie with the hood down (drawstrings, kangaroo pocket, ribbed hem, sleeves pushed up), frayed light-denim shorts with chalk handprints, white wrist tape, chalky hands, plaster on one knee, white sneakers with red soles. Signature poses: the gymnast "ta-da" salute and a handstand. Voice `am_puck` (speed ~1.05–1.1).
- Note for future sessions: this repo is **public**, so never add the owner's personal reference photos to it.
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

## 7a. Blender feasibility test: DONE (2026-11-05)
- **Setup that works:** Blender 5.2.3 LTS + the official **Blender Lab MCP add-on** (v1.0.3, Edit > Preferences > Add-ons > MCP; localhost:9876, Auto Start on). The connector talks to the *open* Blender window. Headless mode (`execute_blender_code_for_cli`) still can't find `blender.exe`: the connector ignores the Windows `BLENDER_PATH` user variable, even after a restart. Live Blender is enough, so this was left alone.
- **Outputs go to `C:\Users\USER\ShirleyGabby\blender_test`.** Windows Controlled Folder Access blocks Blender from writing into Documents. Claude has folder access to `C:\Users\USER\ShirleyGabby`.
- **Live-session rules (`blender_test.py`):** never `read_factory_settings` (it would switch off the MCP add-on and cut the connection). Build in new scenes (`SG_flat2d`, `SG_toon3d`) with the data API and bmesh, not context operators. Render with `bpy.ops.render.render(..., scene=name)`. Calls over ~60 s time out on the bridge but keep running, so poll for the output file. `run()` is stashed in `bpy.app.driver_namespace["sg_run"]` so later calls are one line. Blender 5.x video needs `image_settings.media_type = "VIDEO"` before `file_format = "FFMPEG"`. Colours must be converted sRGB to linear.
- **Results (Gabby from primitives, 1920x1080 EEVEE):**
  - Flat 2D: ortho camera, emission colours, Grease Pencil **Line Art** ink (works via `bpy.data.grease_pencils` + LINEART modifier). Still about 3–4 s; 24-frame clip 33 s (**1.4 s/frame**).
  - Toon 3D: 3/4 camera, two-tone cel shading (Diffuse > Shader to RGB > constant ramp), inverted-hull ink, sun shadow. Still about 2–8 s; 24-frame clip 35 s (**1.5 s/frame**).
  - The very first render took 64 s (one-time shader compile).
- **Verdict so far:** Blender is viable and fast enough (11-min episode ≈ 15.8k frames ≈ 6–7 h per pass on this PC). Both looks work; toon 3D gives free camera angles, shadows and props. Gabby's model is crude primitives: stubble reads as a beard; arms and hands have no rig yet.
- **Next:** owner picks flat 2D vs toon 3D (or 3D with the Line Art ink). Then a proper Gabby model with an armature (rig), Shirley, and a port of the pose-to-pose `acting.py` timing onto Blender keyframes (constant interpolation on twos).

## 7b. DECISION: toon 3D in Blender (2026-11-05)
The owner chose **toon 3D** (after seeing both tests and asking how Rick and Morty looks: R&M is flat 2D, which a 3D character can also imitate later with Line Art, flat colour and an ortho camera).
- **Engine:** `blender/sg3d.py` (on the PC at `C:\Users\USER\ShirleyGabby\engine\sg3d.py`, renders go to `...\ShirleyGabby\renders`). Load it in live Blender:
  `ns={}; exec(open(p).read(), ns); bpy.app.driver_namespace["sg3d"]=ns`, then `ns["demo_turnaround"]()`, `ns["demo_line"]()`, `ns["demo_line_clip"]()`.
- **What's in it:**
  - Cel shader (two tones; base colour can be a texture) and an inverted-hull ink line. Mesh scale is baked into the vertices so the line is the same width everywhere.
  - Mesh generators: ellipsoid, capsule, torus, box.
  - `Rig`: an FK puppet rig of empties with meshes hung on joints.
  - `build_gabby`: jowly head, stubble texture (front of the jaw only), cuffed beanie and pom-pom, hoodie with hood, strings, pocket and hem, 2-part arms, cartoon hands (3 fingers + thumb, shapes relax/open/fist/point/tuck), jeans and sneakers. Face channels: brows (raise and angle), blink, pupils look, mouth open/smile.
  - `POSES3` + `Acting3D`: acting.py's pose-to-pose ported (anticipation, overshoot, settle, moving holds, squash and stretch, on twos, constant keys), plus placeholder mouth flaps and blinks.
  - `build_laundromat`: tiled floor, wall, washers, glowing-green dryer.
- **Gotchas found:**
  - Blender only evaluates animation for the scene shown in the window. `render_still`/`render_clip` switch the window to the scene and back (`on_screen`).
  - Python keyframe inserts ignore the interpolation preference, so keys are set to CONSTANT on the fcurves (Blender 5 channelbags, see `fcurves()`).
  - Two scenes building "Gabby" get `.001` names.
  - `device_commit_files` silently doesn't overwrite an existing file on the PC: commit under a new name and `cp` it over with device_bash, then check the md5.
  - Clips longer than ~60 s of rendering time out on the bridge but keep going, so poll the output file.
- **Speed:** about 1.3–2.3 s per 1080p still once shaders are compiled (the first render of a session takes 10–60 s).
- **Next:**
  - Shirley (tall head, bun with pencil, round glasses, earrings, mustard blouse, plum trousers, half-lidded eyes).
  - Real voices plus lip-sync from audio (the visemes from toon.py / Rhubarb drive the `mouth` channel).
  - Secondary motion (pom-pom, strings, bun and pencil springs).
  - Walk cycle.
  - Shot/reverse-shot camera.
  - The scene-script format (step 7.2).
  - Shoes render greyish (cel shadow on white): lift the shoe colour or lower its shade.

## 7c. PIPELINE DECISION (owner, 2026-11-06): all production in 3D Blender, rendered to a 2D comic look
- `blender/teen3d.py` builds the FINAL teens in 3D.
  - Heads, hair and hoodies are lathed from the sheet's front-silhouette widths (`concept/assets3d/profiles.json`, made by `concept/export_3d_assets.py`).
  - Faces are the sheet's own comic art as decals, one per expression.
  - The halftone comic shader puts dots only on the shadow side (light from the upper left). The ink hull must not cast shadows (Light Path "Is Shadow Ray" goes to transparent), and hair has `visible_shadow` off.
  - `demo_turnaround()` and `demo_shots()` (wide, low-angle and over-the-shoulder cameras) work. Renders take about 1.5–3 s per 1080p frame.
- **Owner feedback on that build:** it looks like a toy (stiff puppet parts, flat painted eyes).
- **Agreed next:**
  - A real skeleton (recommended: Rigify, free and built into Blender; the owner must enable it under Preferences > Add-ons).
  - One continuous, higher-poly body mesh per character with edge loops at the joints, auto-weighted, with clothes as separate fitted meshes.
  - Real 3D eyeballs with moving irises, eyelids for blinks and squints, movable brows.
  - Mouth shapes swapped from the approved drawn mouths, for lip-sync.
  - Proper finger bones.
  - Do Gabby first, then Shirley. The locked designs must not change.
- **2026-11-06 progress: Gabby is rigged** (`blender/rig3d.py`, `build_rigged("gabby")`, about 107 s).
  - Skeleton: the Rigify human metarig with face bones removed, fitted to the sheet joints with chains kept connected, then generated (69 DEF bones). FK posing via `fk(R)` + `rot(R, "upper_arm_fk.L", x, y, z)` (z = raise the arm sideways).
  - Meshes: one fused skin (about 76k polys, voxel remesh 0.0075) plus fused hoodie and shorts, all auto-weighted. `keep_torso_off_arms()` stops the hoodie sides following the arms.
  - Face: 3D almond eyes (iris drawn in the shader, steered by object props `look_x`/`look_z`; shape keys blink, squint, wide), 3D brows, mouth decal layers per expression plus a static nose/blush decal. `set_face(R, expr, look=, blink=)`.
  - To do: finger/hand quality (still small mitts), slight hoodie stretch at the armpits, Shirley's rigged build (her bob, jeans, full sleeves), lip-sync mouth set, an animation clip.
- PC file transfer: `device_commit_files` will not overwrite an existing file, so commit to a new name and `cp` it over (check the md5).

## 8. Ideas parked for later
Recurring extras: the landlord in disguises, a sentient router that knows too much, Mum on video call. Alternate dynamics considered: an Inside Job flip (Shirley works inside a tech giant) or Shirley as a reckless genius inventor. The chosen dynamic is gullible Gabby causing trouble and Shirley the reluctant brave one, in pure-fiction weird worlds.
