"""Blender feasibility test for Shirley & Gabby (HANDOFF step 7.1).

Builds Gabby from primitives (colours from chars.py) and renders him two ways,
timing each:
  A) "flat2d"  - orthographic front camera, flat unlit colours, Grease Pencil
                 Line Art ink (falls back to inverted-hull outline)
  B) "toon3d"  - 3/4 perspective camera, two-tone cel shading, inverted-hull ink

Safe to run inside a live Blender session (through the Blender connector):
it never resets the file and never uses context-dependent operators. Each
mode lives in its own new scene "SG_<mode>"; the user's scene is untouched.

Each mode renders a 1920x1080 still and a 24-frame bounce/head-turn clip.
Usage inside Blender:  MODE = "flat2d"; exec(open(path).read())
Headless:              blender -b --python blender_test.py   (runs both)
Outputs: ~/ShirleyGabby/blender_test/
"""
import bpy, bmesh, math, os, time, json

# Not Documents: Windows "Controlled folder access" blocks Blender from writing there.
OUT = os.path.join(os.path.expanduser("~"), "ShirleyGabby", "blender_test")
os.makedirs(OUT, exist_ok=True)

def _lin(v):  # sRGB -> linear, so emission colours match chars.py exactly
    v /= 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


C = lambda r, g, b: (_lin(r), _lin(g), _lin(b), 1)
SKIN, HAIR = C(150, 98, 66), C(30, 24, 30)
HOODIE, JEANS = C(222, 82, 70), C(62, 84, 136)
SHOES, BEANIE = C(236, 236, 228), C(38, 150, 150)
WHITE, INK = C(250, 250, 245), C(14, 12, 16)
BG, FLOOR = C(244, 214, 120), C(110, 170, 140)
STUBBLE = C(104, 70, 52)


# ---------- scene / materials -------------------------------------------------
def new_scene(mode):
    name = f"SG_{mode}"
    if name in bpy.data.scenes:
        old = bpy.data.scenes[name]
        for o in list(old.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.scenes.remove(old)
    sc = bpy.data.scenes.new(name)
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    sc.frame_start, sc.frame_end = 1, 24
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new(f"W_{mode}")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    # camera sees the flat yellow; lighting gets only a dim ambient so cel bands survive
    lp = nt.nodes.new("ShaderNodeLightPath")
    seen = nt.nodes.new("ShaderNodeBackground"); seen.inputs[0].default_value = BG
    amb = nt.nodes.new("ShaderNodeBackground"); amb.inputs[0].default_value = BG; amb.inputs[1].default_value = 0.15
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(seen.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return sc


def mat(name, col, mode):
    m = bpy.data.materials.new(f"{name}_{mode}")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    if mode == "flat2d":
        em.inputs[0].default_value = col
    else:  # two-tone cel: diffuse -> ShaderToRGB -> constant ramp -> emission
        dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
        s2r = nt.nodes.new("ShaderNodeShaderToRGB")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        e0, e1 = ramp.color_ramp.elements
        e0.position, e1.position = 0.0, 0.3
        e0.color = tuple(c * 0.6 for c in col[:3]) + (1,)
        e1.color = col
        nt.links.new(dif.outputs[0], s2r.inputs[0])
        nt.links.new(s2r.outputs[0], ramp.inputs[0])
        nt.links.new(ramp.outputs[0], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def ink_mat(mode):
    m = mat("Ink", INK, "flat2d")
    m.name = f"Ink_{mode}"
    m.use_backface_culling = True
    return m


# ---------- ops-free primitives ----------------------------------------------
def mesh(kind, name):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    if kind == "sphere":
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
    else:
        bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=1.0, radius2=1.0, depth=2.0)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


class Builder:
    def __init__(self, sc, mode, outline):
        self.sc, self.mode, self.outline = sc, mode, outline
        self.ink = ink_mat(mode)
        self.M = {k: mat(k, v, mode) for k, v in dict(skin=SKIN, hair=HAIR, hoodie=HOODIE, jeans=JEANS,
                                                      shoes=SHOES, beanie=BEANIE, white=WHITE,
                                                      stubble=STUBBLE).items()}

    def obj(self, name, data=None, loc=(0, 0, 0), parent=None):
        o = bpy.data.objects.new(f"{name}_{self.mode}", data)
        self.sc.collection.objects.link(o)
        if parent:  # parents are built unrotated/unscaled, so local = world - parent
            o.parent = parent
            pl = parent.get("wloc", (0, 0, 0))
            loc = tuple(a - b for a, b in zip(loc, pl))
        o.location = loc
        o["wloc"] = tuple(a + b for a, b in zip(loc, parent.get("wloc", (0, 0, 0)))) if parent else loc
        return o

    def part(self, kind, name, loc, scale, m, parent, rot=(0, 0, 0), thick=0.025):
        o = self.obj(name, mesh(kind, name), loc, parent)
        o.scale = scale
        o.rotation_euler = rot
        o.data.materials.append(self.M[m])
        o.data.materials.append(self.ink)
        if self.outline and thick > 0:  # inverted-hull ink line
            sol = o.modifiers.new("outline", "SOLIDIFY")
            sol.thickness = thick / max(scale)  # roughly constant line width
            sol.offset = 1
            sol.use_flip_normals = True
            sol.material_offset = 1
            sol.use_rim = False
        return o


def build_gabby(b):
    root = b.obj("Gabby")
    S, Y = "sphere", "cyl"
    for s in (-1, 1):
        b.part(Y, f"leg{s}", (0.22 * s, 0, 0.55), (0.16, 0.16, 0.45), "jeans", root)
        b.part(S, f"shoe{s}", (0.24 * s, -0.1, 0.1), (0.21, 0.3, 0.12), "shoes", root)
        b.part(Y, f"arm{s}", (0.6 * s, 0, 1.42), (0.12, 0.12, 0.36), "hoodie", root, rot=(0, math.radians(10 * s), 0))
        b.part(S, f"hand{s}", (0.67 * s, 0, 1.02), (0.14, 0.14, 0.14), "skin", root)
        b.part(Y, f"string{s}", (0.1 * s, -0.42, 1.72), (0.018, 0.018, 0.16), "white", root, thick=0.008)
    b.part(S, "torso", (0, 0, 1.45), (0.55, 0.42, 0.62), "hoodie", root)
    b.part(S, "pocket", (0, -0.37, 1.18), (0.3, 0.08, 0.13), "hoodie", root, thick=0.012)
    head = b.part(S, "head", (0, 0, 2.55), (0.62, 0.58, 0.6), "skin", root)
    # head parts hang off an unscaled pivot so the head's own scale doesn't distort them
    pivot = b.obj("headpivot", None, (0, 0, 2.55), root)
    head.parent = pivot
    head.location = (0, 0, 0)
    # TODO: still reads as a full beard; real stubble wants a texture or dot pattern
    b.part(S, "stubble", (0, -0.03, 2.42), (0.58, 0.56, 0.45), "stubble", pivot, thick=0.0)
    b.part(S, "beanie", (0, 0, 2.85), (0.65, 0.61, 0.42), "beanie", pivot)
    b.part(S, "pompom", (0, 0, 3.32), (0.16, 0.16, 0.16), "beanie", pivot)
    for s in (-1, 1):  # big eyes
        b.part(S, f"eye{s}", (0.22 * s, -0.5, 2.64), (0.17, 0.09, 0.2), "white", pivot, thick=0.012)
        b.part(S, f"pupil{s}", (0.2 * s, -0.59, 2.62), (0.06, 0.03, 0.08), "hair", pivot, thick=0.0)
    b.part(S, "nose", (0, -0.6, 2.47), (0.1, 0.08, 0.09), "skin", pivot, thick=0.012)
    b.part(S, "mouth", (0, -0.555, 2.3), (0.16, 0.04, 0.04), "hair", pivot, thick=0.0)
    # bouncy squash-and-stretch + head turn
    for f, z, sq, turn in ((1, 0, 1.0, -20), (7, 0.25, 1.06, 0), (13, 0, 0.92, 20), (19, 0.25, 1.06, 0), (24, 0, 1.0, -20)):
        root.location.z = z
        root.scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)
        pivot.rotation_euler.z = math.radians(turn)
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("scale", frame=f)
        pivot.keyframe_insert("rotation_euler", frame=f)
    return root


def camera_and_light(b):
    sc, mode = b.sc, b.mode
    cd = bpy.data.cameras.new(f"cam_{mode}")
    if mode == "flat2d":
        cd.type = "ORTHO"
        cd.ortho_scale = 7.0
        cam = b.obj("cam", cd, (0, -10, 1.75))
        cam.rotation_euler = (math.radians(90), 0, 0)
    else:
        cd.lens = 45
        cam = b.obj("cam", cd, (4.2, -7.5, 3.0))
        cam.rotation_euler = (math.radians(82), 0, math.radians(29))
        ld = bpy.data.lights.new(f"sun_{mode}", "SUN")
        ld.energy = 4
        sun = b.obj("sun", ld)
        sun.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-35))
    sc.camera = cam
    if mode == "toon3d":
        me = bpy.data.meshes.new("floor")
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=15)
        bm.to_mesh(me); bm.free()
        me.materials.append(mat("floor", FLOOR, mode))
        b.obj("floor", me)


def add_lineart(sc, mode):
    """Grease Pencil (v3, Blender 4.3+) Line Art over the whole scene."""
    gp = bpy.data.grease_pencils.new(f"LA_{mode}")
    layer = gp.layers.new("Lines")
    m = bpy.data.materials.new(f"LAink_{mode}")
    bpy.data.materials.create_gpencil_data(m)
    m.grease_pencil.color = INK
    gp.materials.append(m)
    o = bpy.data.objects.new(f"LineArt_{mode}", gp)
    sc.collection.objects.link(o)
    md = o.modifiers.new("lineart", "LINEART")
    md.source_type = "SCENE"
    md.target_layer = layer.name
    md.target_material = m
    for attr, val in (("thickness", 6), ("radius", 0.012)):
        if hasattr(md, attr):
            setattr(md, attr, val)
    return o.name


# ---------- run ---------------------------------------------------------------
def run(mode, clip=True):
    t0 = time.time()
    sc = new_scene(mode)
    lineart, outline = None, True
    if mode == "flat2d":
        try:
            lineart = add_lineart(sc, mode)
            outline = False
        except Exception as e:
            lineart = f"failed: {e}"
    b = Builder(sc, mode, outline)
    build_gabby(b)
    camera_and_light(b)
    t_build = time.time() - t0

    sc.frame_set(1)
    still = os.path.join(OUT, f"gabby_{mode}_still.png")
    sc.render.image_settings.media_type = "IMAGE"
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = still
    t1 = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    t_still = time.time() - t1

    rep = dict(mode=mode, scene=sc.name, engine=sc.render.engine, lineart=lineart,
               build_s=round(t_build, 2), still_s=round(t_still, 2), still=still)
    if clip:
        sc.render.image_settings.media_type = "VIDEO"
        sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"
        sc.render.ffmpeg.codec = "H264"
        sc.render.ffmpeg.constant_rate_factor = "HIGH"
        sc.render.filepath = os.path.join(OUT, f"gabby_{mode}_clip.mp4")
        t2 = time.time()
        bpy.ops.render.render(animation=True, scene=sc.name)
        t_clip = time.time() - t2
        rep.update(clip24_s=round(t_clip, 2), sec_per_frame=round(t_clip / 24, 3), clip=sc.render.filepath)
    with open(os.path.join(OUT, f"timings_{mode}.json"), "w") as fh:
        json.dump(dict(blender=bpy.app.version_string, **rep), fh, indent=2)
    return rep


bpy.app.driver_namespace["sg_run"] = run  # later calls: bpy.app.driver_namespace["sg_run"]("toon3d")

if "MODE" in globals():
    result = run(MODE, clip=globals().get("CLIP", True))
else:
    result = dict(blender=bpy.app.version_string, runs=[run("flat2d"), run("toon3d")])
    print(json.dumps(result, indent=2))
