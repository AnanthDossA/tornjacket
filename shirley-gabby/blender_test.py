"""Blender feasibility test for Shirley & Gabby (HANDOFF step 7.1).

Builds Gabby from primitives (colours from chars.py) and renders him two ways,
timing each:
  A) "flat2d"  - orthographic camera, flat unlit colours, thick ink outline
                 (inverted hull) + Grease Pencil Line Art if available
  B) "toon3d"  - 3/4 perspective camera, two-tone cel shading, ink outline

Each mode renders one 1920x1080 still and a 24-frame bounce/head-turn clip.
Run inside Blender (connector) or headless:
    blender -b --python blender_test.py
Outputs: ~/Documents/ShirleyGabby/blender_test/
"""
import bpy, math, os, time, json

OUT = os.path.join(os.path.expanduser("~"), "Documents", "ShirleyGabby", "blender_test")
os.makedirs(OUT, exist_ok=True)

C = lambda r, g, b: (r / 255, g / 255, b / 255, 1)
SKIN, HAIR = C(150, 98, 66), C(30, 24, 30)
HOODIE, JEANS = C(222, 82, 70), C(62, 84, 136)
SHOES, BEANIE = C(236, 236, 228), C(38, 150, 150)
WHITE, INK = C(250, 250, 245), C(14, 12, 16)


def engine_id():
    ids = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        if e in ids:
            return e
    return ids[0]


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = engine_id()
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = 24
    sc.frame_start, sc.frame_end = 1, 24
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = C(244, 214, 120)
    return sc


def mat(name, col, mode):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if mode == "flat2d":
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs[0].default_value = col
        nt.links.new(em.outputs[0], out.inputs[0])
    else:  # two-tone cel: diffuse -> ShaderToRGB -> constant ramp -> emission
        dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
        s2r = nt.nodes.new("ShaderNodeShaderToRGB")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        e0, e1 = ramp.color_ramp.elements
        e0.position, e1.position = 0.0, 0.35
        e0.color = tuple(c * 0.62 for c in col[:3]) + (1,)
        e1.color = col
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(dif.outputs[0], s2r.inputs[0])
        nt.links.new(s2r.outputs[0], ramp.inputs[0])
        nt.links.new(ramp.outputs[0], em.inputs[0])
        nt.links.new(em.outputs[0], out.inputs[0])
    return m


def ink_mat():
    m = bpy.data.materials.new("Ink")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = INK
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs[0])
    m.use_backface_culling = True
    return m


def add(prim, name, loc, scale, material, ink, parent=None, rot=(0, 0, 0), thick=0.025):
    getattr(bpy.ops.mesh, prim)(location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.shade_smooth()
    o.data.materials.append(material)
    o.data.materials.append(ink)
    sol = o.modifiers.new("outline", "SOLIDIFY")  # inverted-hull ink line
    sol.thickness = thick
    sol.offset = 1
    sol.use_flip_normals = True
    sol.material_offset = 1
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


def build_gabby(mode):
    ink = ink_mat()
    M = {k: mat(k, v, mode) for k, v in dict(skin=SKIN, hair=HAIR, hoodie=HOODIE, jeans=JEANS,
                                              shoes=SHOES, beanie=BEANIE, white=WHITE).items()}
    bpy.ops.object.empty_add(location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "Gabby"
    S = "primitive_uv_sphere_add"
    Y = "primitive_cylinder_add"
    for side in (-1, 1):
        add(Y, f"leg{side}", (0.22 * side, 0, 0.55), (0.16, 0.16, 0.45), M["jeans"], ink, root)
        add(S, f"shoe{side}", (0.22 * side, -0.08, 0.1), (0.2, 0.3, 0.12), M["shoes"], ink, root)
        add(Y, f"arm{side}", (0.62 * side, 0, 1.45), (0.12, 0.12, 0.38), M["hoodie"], ink, root,
            rot=(0, math.radians(18 * side), 0))
        add(S, f"hand{side}", (0.75 * side, 0, 1.0), (0.14, 0.14, 0.14), M["skin"], ink, root)
    body = add(S, "torso", (0, 0, 1.45), (0.55, 0.42, 0.62), M["hoodie"], ink, root)
    add(S, "pocket", (0, -0.36, 1.2), (0.3, 0.08, 0.14), M["hoodie"], ink, root, thick=0.015)
    head = add(S, "head", (0, 0, 2.55), (0.62, 0.58, 0.6), M["skin"], ink, root)
    add(S, "stubble", (0, -0.12, 2.3), (0.5, 0.46, 0.32), M["hair"], ink, head, thick=0.0)
    add(S, "beanie", (0, 0, 2.85), (0.64, 0.6, 0.42), M["beanie"], ink, head)
    add(S, "pompom", (0, 0, 3.32), (0.16, 0.16, 0.16), M["beanie"], ink, head)
    for side in (-1, 1):  # big eyes
        add(S, f"eye{side}", (0.22 * side, -0.5, 2.6), (0.17, 0.08, 0.2), M["white"], ink, head, thick=0.015)
        add(S, f"pupil{side}", (0.22 * side, -0.58, 2.58), (0.06, 0.03, 0.08), M["hair"], ink, head, thick=0.0)
        add(Y, f"string{side}", (0.12 * side, -0.4, 1.75), (0.02, 0.02, 0.18), M["white"], ink, root, thick=0.008)
    add(S, "nose", (0, -0.6, 2.45), (0.1, 0.08, 0.09), M["skin"], ink, head, thick=0.015)
    # Animation: bouncy squash-and-stretch + head turn (on twos, like acting.py)
    for f, z, sq, turn in ((1, 0, 1.0, -20), (7, 0.25, 1.06, 0), (13, 0, 0.92, 20), (19, 0.25, 1.06, 0), (24, 0, 1.0, -20)):
        root.location.z = z
        root.scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)
        head.rotation_euler.z = math.radians(turn)
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("scale", frame=f)
        head.keyframe_insert("rotation_euler", frame=f)
    return root


def camera_and_light(mode):
    sc = bpy.context.scene
    if mode == "flat2d":
        bpy.ops.object.camera_add(location=(0, -10, 1.7), rotation=(math.radians(90), 0, 0))
        cam = bpy.context.active_object
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = 5.2
    else:
        bpy.ops.object.camera_add(location=(4.2, -7.5, 3.0), rotation=(math.radians(82), 0, math.radians(29)))
        cam = bpy.context.active_object
        cam.data.lens = 45
        bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), math.radians(-20), math.radians(-35)))
        bpy.context.active_object.data.energy = 4
    sc.camera = cam
    # simple ground
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(mat("floor", C(110, 170, 140), mode))


def try_lineart():
    """Grease Pencil Line Art over the scene (API changed in 4.3, so try both)."""
    for op, kw in (("grease_pencil_add", dict(type="LINEART_SCENE")),
                   ("gpencil_add", dict(type="LINEART_SCENE"))):
        try:
            getattr(bpy.ops.object, op)(**kw)
            return op
        except Exception:
            continue
    return None


def run(mode):
    t0 = time.time()
    sc = reset()
    build_gabby(mode)
    camera_and_light(mode)
    lineart = try_lineart() if mode == "flat2d" else None
    t_build = time.time() - t0
    t1 = time.time()
    sc.frame_set(1)
    sc.render.filepath = os.path.join(OUT, f"gabby_{mode}_still.png")
    bpy.ops.render.render(write_still=True)
    t_still = time.time() - t1
    t2 = time.time()
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.filepath = os.path.join(OUT, f"gabby_{mode}_clip.mp4")
    try:
        bpy.ops.render.render(animation=True)
        clip = sc.render.filepath
    except Exception as e:  # FFMPEG option removed in some versions -> PNG frames
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = os.path.join(OUT, f"{mode}_frames", "f_")
        bpy.ops.render.render(animation=True)
        clip = sc.render.filepath + f" (png frames; {e})"
    t_clip = time.time() - t2
    return dict(mode=mode, engine=sc.render.engine, lineart=lineart, build_s=round(t_build, 2),
                still_s=round(t_still, 2), clip24_s=round(t_clip, 2),
                sec_per_frame=round(t_clip / 24, 3), still=os.path.join(OUT, f"gabby_{mode}_still.png"), clip=clip)


report = dict(blender=bpy.app.version_string, out=OUT, runs=[run("flat2d"), run("toon3d")])
with open(os.path.join(OUT, "timings.json"), "w") as fh:
    json.dump(report, fh, indent=2)
result = report
print(json.dumps(report, indent=2))
