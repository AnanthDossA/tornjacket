"""Shirley & Gabby - toon-3D engine for Blender (5.x), first cut.

Runs inside a LIVE Blender session through the Blender Lab MCP add-on, so it:
  * never resets the file or uses context-dependent operators (data API + bmesh only)
  * builds everything in its own scenes, leaving the user's scene alone
  * keeps meshes unscaled (scale baked into vertices) so the inverted-hull ink
    line is the same width everywhere, like a hand-inked show

Pieces:
  materials  - cel shader (2 tones), flat shader, ink; colours given in sRGB 0-255
  meshes     - ellipsoid / capsule / torus / rounded box generators
  Rig        - a joint hierarchy (empties) with meshes hung on each joint (FK puppet rig)
  build_gabby- Gabby from chars.py: jowly head + stubble texture, beanie with cuff and
               pom-pom, red hoodie (hood, strings, pocket), bendable arms, 4-part cartoon
               hands, jeans, sneakers, face (eyes/pupils/brows/nose/mouth) with channels
  Acting3D   - pose-to-pose timing ported from acting.py (anticipation, overshoot,
               settle, moving holds, squash/stretch, on twos) driving rig channels
  build_laundromat - quick set: tiled floor, wall, washers, glowing dryer

Usage inside Blender (via the connector):
    ns = {}; exec(open(PATH).read(), ns); ns["demo_turnaround"](); ns["demo_line"]()
"""
import bpy, bmesh, math, os, time, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

OUT = os.path.join(os.path.expanduser("~"), "ShirleyGabby", "renders")
os.makedirs(OUT, exist_ok=True)
FPS = 24


# =============================================================== colour / materials
def lin(c):
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (f(c[0] / 255), f(c[1] / 255), f(c[2] / 255), 1.0)


def _mix(nt, fac, a, b):
    """RGBA mix node; a/b are sockets or colours, fac is socket or float"""
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    ins = [s for s in m.inputs if s.type == "RGBA"]
    fin = [s for s in m.inputs if s.name == "Factor" and s.type == "VALUE"][0]
    for sock, val in ((ins[0], a), (ins[1], b)):
        if isinstance(val, bpy.types.NodeSocket):
            nt.links.new(val, sock)
        else:
            sock.default_value = val
    if isinstance(fac, bpy.types.NodeSocket):
        nt.links.new(fac, fin)
    else:
        fin.default_value = fac
    return [s for s in m.outputs if s.type == "RGBA"][0]


def _new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(em.outputs[0], out.inputs[0])
    return m, nt, em


def flat(name, rgb):
    m, nt, em = _new_mat(name)
    em.inputs[0].default_value = lin(rgb)
    return m


def cel(name, rgb, shade=0.62, base_fn=None, cut=0.3):
    """two-tone cel: lit = colour, shadow = colour * shade. base_fn(nt) may return a colour socket."""
    m, nt, em = _new_mat(name)
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    e0, e1 = ramp.color_ramp.elements
    e0.position, e1.position = 0.0, cut
    e0.color = (shade, shade, shade, 1)
    e1.color = (1, 1, 1, 1)
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    nt.links.new(s2r.outputs[0], ramp.inputs[0])
    if base_fn:
        base = base_fn(nt)
    else:
        rgbn = nt.nodes.new("ShaderNodeRGB")
        rgbn.outputs[0].default_value = lin(rgb)
        base = rgbn.outputs[0]
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "MULTIPLY"
    nt.links.new(base, mul.inputs[0])
    nt.links.new(ramp.outputs[0], mul.inputs[1])
    nt.links.new(mul.outputs[0], em.inputs[0])
    return m


def ink(name="Ink", rgb=(16, 13, 18)):
    m = flat(name, rgb)
    m.use_backface_culling = True
    return m


def stubble_skin(name, skin, stub):
    """skin with a stubble zone on the lower face: tinted area + speckles (object coords, head-centred)"""
    def base(nt):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Object"], sep.inputs[0])
        zone = nt.nodes.new("ShaderNodeMapRange")  # z: -0.06 -> 0 ... -0.16 -> 1
        zone.inputs["From Min"].default_value = -0.06
        zone.inputs["From Max"].default_value = -0.16
        nt.links.new(sep.outputs["Z"], zone.inputs["Value"])
        front = nt.nodes.new("ShaderNodeMapRange")  # y: +0.12 (behind ears) -> 0 ... -0.12 -> 1
        front.inputs["From Min"].default_value = 0.12
        front.inputs["From Max"].default_value = -0.12
        nt.links.new(sep.outputs["Y"], front.inputs["Value"])
        jaw = nt.nodes.new("ShaderNodeMath")
        jaw.operation = "MULTIPLY"
        nt.links.new(zone.outputs[0], jaw.inputs[0])
        nt.links.new(front.outputs[0], jaw.inputs[1])
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 60.0
        noise.inputs["Detail"].default_value = 0.0
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        dots = nt.nodes.new("ShaderNodeMapRange")
        dots.inputs["From Min"].default_value = 0.58
        dots.inputs["From Max"].default_value = 0.62
        nt.links.new(noise.outputs["Fac"], dots.inputs["Value"])
        both = nt.nodes.new("ShaderNodeMath")
        both.operation = "MULTIPLY"
        nt.links.new(jaw.outputs[0], both.inputs[0])
        nt.links.new(dots.outputs[0], both.inputs[1])
        tint = nt.nodes.new("ShaderNodeMath")
        tint.operation = "MULTIPLY"
        tint.inputs[1].default_value = 0.35
        nt.links.new(jaw.outputs[0], tint.inputs[0])
        c1 = _mix(nt, tint.outputs[0], lin(skin), lin(stub))
        return _mix(nt, both.outputs[0], c1, lin(tuple(v * 0.55 for v in stub)))
    return cel(name, skin, base_fn=base)


def checker_cel(name, a, b, scale=1.0):
    def base(nt):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        ck = nt.nodes.new("ShaderNodeTexChecker")
        ck.inputs["Scale"].default_value = scale
        ck.inputs["Color1"].default_value = lin(a)
        ck.inputs["Color2"].default_value = lin(b)
        nt.links.new(tc.outputs["Object"], ck.inputs["Vector"])
        return ck.outputs["Color"]
    return cel(name, a, base_fn=base, shade=0.7)


# =============================================================== mesh generators (bmesh)
def ellipsoid(rx, ry, rz, seg=32, rings=16, deform=None, cut_below=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * rx, v.co.y * ry, v.co.z * rz))
        if deform:
            v.co = Vector(deform(v.co))
    if cut_below is not None:
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < cut_below - 1e-6], context="VERTS")
    return bm


def capsule(r, length, r_end=None, seg=24, rings=12):
    """capsule hanging DOWN from the origin (joint) to z=-length; optional taper"""
    r_end = r if r_end is None else r_end
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        if z >= -1e-6:
            v.co = Vector((x * r, y * r, z * r))
        else:
            v.co = Vector((x * r_end, y * r_end, z * r_end - length))
    return bm


def torus(R, r, seg=48, rseg=14):
    bm = bmesh.new()
    vs = [[bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
           for b in (2 * math.pi * j / rseg for j in range(rseg))] for a in (2 * math.pi * i / seg for i in range(seg))]
    for i in range(seg):
        for j in range(rseg):
            bm.faces.new((vs[i][j], vs[(i + 1) % seg][j], vs[(i + 1) % seg][(j + 1) % rseg], vs[i][(j + 1) % rseg]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def box(sx, sy, sz):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    return bm


def xform(bm, loc=(0, 0, 0), rot=(0, 0, 0)):
    m = Matrix.Translation(loc) @ (Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y") @ Matrix.Rotation(rot[0], 4, "X"))
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return bm


def front_y(bm, x, z):
    """y of the front (-y) surface of a bmesh at (x, z), local coords"""
    bvh = BVHTree.FromBMesh(bm)
    hit = bvh.ray_cast(Vector((x, -10, z)), Vector((0, 1, 0)))
    return hit[0].y if hit[0] else 0.0


# =============================================================== scene helpers
def new_scene(name, bg=(244, 214, 120), ambient=0.18):
    if name in bpy.data.scenes:
        old = bpy.data.scenes[name]
        for o in list(old.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.scenes.remove(old)
    sc = bpy.data.scenes.new(name)
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.view_settings.view_transform = "Standard"
    sc.render.film_transparent = False
    w = bpy.data.worlds.new(f"W_{name}")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    lp = nt.nodes.new("ShaderNodeLightPath")
    seen = nt.nodes.new("ShaderNodeBackground"); seen.inputs[0].default_value = lin(bg)
    amb = nt.nodes.new("ShaderNodeBackground"); amb.inputs[0].default_value = (1, 1, 1, 1); amb.inputs[1].default_value = ambient
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(seen.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return sc


def add_obj(sc, name, data=None):
    o = bpy.data.objects.new(name, data)
    sc.collection.objects.link(o)
    return o


def mesh_obj(sc, name, bm, mat, line=0.02, inkmat=None, smooth=True, bevel=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    me.materials.append(mat)
    o = add_obj(sc, name, me)
    if bevel:
        bv = o.modifiers.new("bevel", "BEVEL")
        bv.width, bv.segments = bevel, 4
    if line and inkmat:
        me.materials.append(inkmat)
        sol = o.modifiers.new("ink", "SOLIDIFY")
        sol.thickness = line
        sol.offset = 1
        sol.use_flip_normals = True
        sol.use_rim = False
        sol.material_offset = 1
    return o


def sun(sc, rot=(50, 0, 30), energy=4.0):
    ld = bpy.data.lights.new(f"sun_{sc.name}", "SUN")
    ld.energy = energy
    ld.angle = math.radians(3)
    o = add_obj(sc, f"sun_{sc.name}", ld)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    return o


def camera(sc, loc, target, lens=40, name="cam"):
    cd = bpy.data.cameras.new(f"{name}_{sc.name}")
    cd.lens = lens
    o = add_obj(sc, f"{name}_{sc.name}", cd)
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = o
    return o


# =============================================================== rig
class Rig:
    """joint empties in a hierarchy; meshes hang on joints. All rest rotations are zero,
    so a child's local offset is simply world_pos - parent_world_pos."""

    def __init__(self, sc, name):
        self.sc, self.name = sc, name
        self.J, self.W = {}, {}      # joints, their world rest positions
        self.parts = {}
        self.base = {}               # rest location / rotation / scale per animated object
        self.keyed = []              # (object, data_path) to keyframe

    def joint(self, key, world, parent=None):
        o = add_obj(self.sc, f"{self.name}_{key}")
        o.empty_display_size = 0.08
        if parent:
            o.parent = self.J[parent]
            o.location = Vector(world) - Vector(self.W[parent])
        else:
            o.location = world
        self.J[key], self.W[key] = o, Vector(world)
        self.base[o.name] = (o.location.copy(), Vector((0, 0, 0)), Vector((1, 1, 1)))
        return o

    def part(self, key, bm, mat, joint, at=None, line=0.02, inkmat=None):
        """mesh built around its own origin, placed at world position `at` (default: the joint)"""
        o = mesh_obj(self.sc, f"{self.name}_{key}", bm, mat, line, inkmat=inkmat)
        o.parent = self.J[joint]
        o.location = (Vector(at) - self.W[joint]) if at is not None else Vector((0, 0, 0))
        self.parts[key] = o
        self.base[o.name] = (o.location.copy(), Vector((0, 0, 0)), Vector((1, 1, 1)))
        return o

    def anim(self, obj, *paths):
        for p in paths:
            self.keyed.append((obj, p))

    def key_all(self, frame):
        for o, p in self.keyed:
            o.keyframe_insert(p, frame=frame)


# =============================================================== Gabby
GABBY_COL = dict(skin=(150, 98, 66), stub=(70, 45, 34), hoodie=(222, 82, 70), hoodie_dk=(170, 52, 48),
                 jeans=(62, 84, 136), shoe=(240, 240, 232), sole=(196, 196, 190), beanie=(38, 150, 150),
                 beanie_dk=(28, 118, 118), white=(250, 250, 245), dark=(26, 20, 24), string=(245, 245, 238))

HAND_SHAPES = {  # curl per finger [front(index), mid, back], thumb curl, spread
    "relax": ([18, 24, 30], 15, 0.4), "open": ([-4, -4, -4], -12, 1.0), "fist": ([105, 110, 110], 70, 0.0),
    "point": ([-2, 110, 110], 70, 0.2), "tuck": ([60, 65, 70], 40, 0.0),
}


def build_gabby(sc, name="Gabby"):
    c = GABBY_COL
    K = ink(f"ink_{name}")
    M = {k: cel(f"{k}_{name}", v) for k, v in c.items() if k not in ("white", "dark", "skin")}
    M["skin"] = cel(f"skin_{name}", c["skin"])
    M["face"] = stubble_skin(f"face_{name}", c["skin"], c["stub"])
    M["white"] = flat(f"white_{name}", c["white"])
    M["dark"] = flat(f"dark_{name}", c["dark"])
    R = Rig(sc, name)
    J = R.joint
    # ---------------- skeleton (character faces -Y; his left = +X)
    J("root", (0, 0, 0))
    J("hips", (0, 0, 1.0), "root")
    J("chest", (0, 0, 1.35), "hips")
    J("head", (0, 0, 2.15), "chest")
    for s, sx in (("L", 1), ("R", -1)):
        J(f"sh{s}", (0.47 * sx, 0, 1.86), "chest")
        J(f"el{s}", (0.47 * sx, 0, 1.46), f"sh{s}")
        J(f"wr{s}", (0.47 * sx, 0, 1.09), f"el{s}")
        J(f"hip{s}", (0.2 * sx, 0, 0.98), "hips")
        J(f"kn{s}", (0.2 * sx, 0, 0.54), f"hip{s}")
        J(f"an{s}", (0.2 * sx, 0, 0.15), f"kn{s}")
    # ---------------- head (centre z=2.62) - jowly, stubble zone
    HC = Vector((0, 0, 2.62))
    jowl = lambda v: (v.x * (1 + 0.2 * max(0, -v.z / 0.6)), v.y * (1 + 0.14 * max(0, -v.z / 0.6)), v.z * (0.94 if v.z < 0 else 1))
    hb = ellipsoid(0.62, 0.58, 0.6, 40, 20, deform=jowl)
    fy = lambda x, z: front_y(hb, x, z)
    spots = {k: fy(*xz) for k, xz in dict(eye=(0.2, 0.02), nose=(0, -0.1), mouth=(0, -0.3), brow=(0.2, 0.26)).items()}
    R.part("head", hb, M["face"], "head", HC, 0.022, K)
    R.part("neck", capsule(0.16, 0.25), M["skin"], "head", HC + Vector((0, 0.05, -0.38)), 0, K)
    # beanie: dome + cuff + pom-pom
    R.part("beanie", ellipsoid(0.665, 0.635, 0.56, 40, 20, cut_below=0.0), M["beanie"], "head", HC + Vector((0, 0.01, 0.22)), 0.022, K)
    cuff = xform(torus(0.6, 0.11), rot=(0, 0, 0))
    for v in cuff.verts:
        v.co.y *= 0.95
    R.part("cuff", cuff, M["beanie_dk"], "head", HC + Vector((0, 0.01, 0.3)), 0.02, K)
    R.part("pompom", ellipsoid(0.17, 0.17, 0.16), M["beanie"], "head", HC + Vector((0, 0.02, 0.84)), 0.02, K)
    # eyes: group joint per eye (blink = scale z), pupils + highlight children (look)
    for s, sx in (("L", 1), ("R", -1)):
        ec = HC + Vector((0.2 * sx, spots["eye"] + 0.035, 0.02))
        e = J(f"eye{s}", ec, "head")
        R.part(f"eyeball{s}", ellipsoid(0.165, 0.085, 0.2), M["white"], f"eye{s}", ec, 0.013, K)
        pj = J(f"pup{s}", ec + Vector((-0.012 * sx, -0.075, -0.01)), f"eye{s}")
        R.part(f"pupil{s}", ellipsoid(0.062, 0.025, 0.078), M["dark"], f"pup{s}", ec + Vector((-0.012 * sx, -0.075, -0.01)), 0, K)
        R.part(f"glint{s}", ellipsoid(0.02, 0.01, 0.022), M["white"], f"pup{s}", ec + Vector((0.02 - 0.03 * (sx < 0), -0.098, 0.03)), 0, K)
        R.anim(e, "scale")
        R.anim(pj, "location")
        bj = J(f"brow{s}", HC + Vector((0.21 * sx, min(spots["brow"], -0.6) - 0.06, 0.27)), "head")
        R.part(f"browm{s}", xform(capsule(0.032, 0.2), rot=(0, math.radians(90), 0), loc=(0.1, 0, 0)), M["dark"], f"brow{s}",
               HC + Vector((0.21 * sx, min(spots["brow"], -0.6) - 0.06, 0.27)), 0, K)
        R.anim(bj, "location", "rotation_euler")
    R.part("nose", ellipsoid(0.1, 0.08, 0.09), M["skin"], "head", HC + Vector((0, spots["nose"] + 0.01, -0.1)), 0.013, K)
    mj = J("mouth", HC + Vector((0, spots["mouth"] + 0.012, -0.3)), "head")
    R.part("mouthm", ellipsoid(0.15, 0.045, 0.035), M["dark"], "mouth", HC + Vector((0, spots["mouth"] + 0.012, -0.3)), 0.0, K)
    R.anim(mj, "scale")
    # ---------------- hoodie torso (pear), hood, strings, pocket
    TC = Vector((0, 0, 1.5))
    pear = lambda v: (v.x * (1 + 0.16 * max(0, -v.z / 0.62)), v.y * (1 + 0.1 * max(0, -v.z / 0.62)), v.z)
    tb = ellipsoid(0.55, 0.43, 0.62, 40, 20, deform=pear)
    ty_str, ty_pk = front_y(tb, 0.1, 0.3), front_y(tb, 0, -0.3)
    R.part("torso", tb, M["hoodie"], "chest", TC, 0.022, K)
    R.part("hood", ellipsoid(0.44, 0.22, 0.17), M["hoodie_dk"], "chest", Vector((0, 0.3, 2.02)), 0.02, K)
    for s, sx in (("L", 1), ("R", -1)):
        top = TC + Vector((0.1 * sx, ty_str - 0.035, 0.3))
        R.part(f"string{s}", capsule(0.022, 0.3), M["string"], "chest", top, 0.009, K)
        R.part(f"aglet{s}", ellipsoid(0.03, 0.03, 0.04), M["white"], "chest", top + Vector((0, -0.01, -0.34)), 0.009, K)
    R.part("pocket", ellipsoid(0.32, 0.07, 0.15), M["hoodie"], "chest", TC + Vector((0, ty_pk + 0.035, -0.3)), 0.016, K)
    R.part("hem", ellipsoid(0.5, 0.42, 0.12), M["hoodie_dk"], "hips", Vector((0, 0, 1.0)), 0.018, K)
    # ---------------- arms + hands
    for s, sx in (("L", 1), ("R", -1)):
        R.part(f"upper{s}", capsule(0.13, 0.4, 0.122), M["hoodie"], f"sh{s}", None, 0.02, K)
        R.part(f"fore{s}", capsule(0.122, 0.34, 0.112), M["hoodie"], f"el{s}", None, 0.02, K)
        R.part(f"cuff{s}", torus(0.105, 0.04), M["hoodie_dk"], f"el{s}", R.W[f"el{s}"] + Vector((0, 0, -0.35)), 0.012, K)
        R.part(f"palm{s}", ellipsoid(0.065, 0.12, 0.12), M["skin"], f"wr{s}", R.W[f"wr{s}"] + Vector((0, 0, -0.1)), 0.014, K)
        for i, fyo in enumerate((-0.075, 0.0, 0.075)):
            fk = f"f{s}{i}"
            kn = R.W[f"wr{s}"] + Vector((0, fyo, -0.2))
            J(fk, kn, f"wr{s}")
            R.part(f"finger{s}{i}", capsule(0.036, 0.09 - 0.012 * (i == 2)), M["skin"], fk, kn, 0.01, K)
            R.anim(R.J[fk], "rotation_euler")
        tk = R.W[f"wr{s}"] + Vector((-0.02 * sx, -0.1, -0.08))
        J(f"th{s}", tk, f"wr{s}")
        R.part(f"thumb{s}", capsule(0.038, 0.07), M["skin"], f"th{s}", tk, 0.01, K)
        R.anim(R.J[f"th{s}"], "rotation_euler")
        R.anim(R.J[f"sh{s}"], "rotation_euler")
        R.anim(R.J[f"el{s}"], "rotation_euler")
        R.anim(R.J[f"wr{s}"], "rotation_euler")
    # ---------------- jeans + sneakers
    R.part("pelvis", ellipsoid(0.42, 0.33, 0.24), M["jeans"], "hips", Vector((0, 0, 0.98)), 0.02, K)
    for s, sx in (("L", 1), ("R", -1)):
        R.part(f"thigh{s}", capsule(0.165, 0.44, 0.15), M["jeans"], f"hip{s}", None, 0.02, K)
        R.part(f"shin{s}", capsule(0.15, 0.36, 0.135), M["jeans"], f"kn{s}", None, 0.02, K)
        R.part(f"shoe{s}", ellipsoid(0.17, 0.29, 0.12), M["shoe"], f"an{s}", R.W[f"an{s}"] + Vector((0, -0.08, -0.04)), 0.02, K)
        R.part(f"sole{s}", ellipsoid(0.18, 0.305, 0.05), M["sole"], f"an{s}", R.W[f"an{s}"] + Vector((0, -0.08, -0.1)), 0.016, K)
        R.part(f"stripe{s}", ellipsoid(0.175, 0.12, 0.035), M["beanie"], f"an{s}", R.W[f"an{s}"] + Vector((0, -0.02, -0.02)), 0.0, K)
        for j in ("hip", "kn", "an"):
            R.anim(R.J[f"{j}{s}"], "rotation_euler")
    R.anim(R.J["root"], "location", "scale")
    R.anim(R.J["chest"], "rotation_euler")
    R.anim(R.J["head"], "rotation_euler")
    R.anim(R.J["hips"], "rotation_euler")
    apply_pose(R, dict(NEUTRAL3), {"L": "relax", "R": "relax"})
    return R


# =============================================================== poses (degrees; L = his left, +X)
NEUTRAL3 = dict(root_z=0.0, sq=1.0, lean=0, twist=0, hip_twist=0, tilt=0, turn=0, nod=0,
                shL_f=0, shL_a=9, shL_t=0, elL=12, elL_t=0, wrL=0,
                shR_f=0, shR_a=9, shR_t=0, elR=12, elR_t=0, wrR=0,
                hipL_f=0, hipL_a=2, knL=0, hipR_f=0, hipR_a=2, knR=0,
                brow=0.0, brow_ang=0.0, mouth=0.0, smile=0.0, look_x=0.0, look_z=0.0, blink=0.0)
BODY = [k for k in NEUTRAL3 if k not in ("brow", "brow_ang", "mouth", "smile", "look_x", "look_z", "blink", "sq")]

POSES3 = {
    "stand": {},
    "call_out": dict(shL_a=150, shL_f=20, elL=35, wrL=10, shR_a=14, elR=20, lean=-5, tilt=8, turn=28, root_z=0.04,
                     brow=1, mouth=0.4, look_x=1, hands={"L": "open"}),  # near-camera arm waves
    "point": dict(shR_f=80, shR_a=10, shR_t=40, elR=4, shL_a=20, shL_f=10, elL=40, lean=8, twist=-6, turn=-12, tilt=6,
                  brow=0.6, brow_ang=-0.3, look_x=-1, hands={"R": "point", "L": "fist"}),
    "whine": dict(shL_f=34, shL_a=6, elL=70, shR_f=34, shR_a=6, elR=70, wrL=20, wrR=20, lean=16, tilt=12, nod=10, root_z=-0.08,
                  hipL_f=24, knL=46, hipR_f=24, knR=46, brow=0.8, brow_ang=-1, mouth=0.3, look_z=0.5, hands={"L": "fist", "R": "fist"}),
    "shrug_big": dict(shL_a=55, shL_f=10, elL=100, shR_a=55, shR_f=10, elR=100, lean=-4, tilt=-10, root_z=-0.03,
                      brow=1, smile=0.4, hands={"L": "open", "R": "open"}),
    "deadpan": dict(shL_f=22, shL_a=4, elL=118, elL_t=60, shR_f=24, shR_a=4, elR=112, elR_t=60, lean=-2, tilt=-3,
                    brow=-0.3, hands={"L": "tuck", "R": "tuck"}),
    "hands_hips": dict(shL_a=38, elL=95, elL_t=-70, shR_a=38, elR=95, elR_t=-70, lean=-3, brow=0.2, smile=0.3,
                       hands={"L": "fist", "R": "fist"}),
}

PERSONALITY = {
    "gabby": dict(frames=4, antic=0.18, over=0.16, exag=1.2, drift=1.0, twos=True, stretch=0.07),
    "shirley": dict(frames=6, antic=0.06, over=0.05, exag=0.85, drift=0.25, twos=True, stretch=0.02),
}


def toon_curve(u, antic, over):
    """acting.py: anticipation -> fast travel -> overshoot -> settle"""
    if u <= 0:
        return 0.0
    if u >= 1:
        return 1.0
    a = 0.22
    if u < a:
        return -antic * math.sin(math.pi * u / a)
    v = (u - a) / (1 - a)
    if v < 0.45:
        w = v / 0.45
        return (1 + over) * (1 - (1 - w) ** 3)
    w = (v - 0.45) / 0.55
    return 1 + over * math.exp(-5 * w) * math.cos(math.pi * 1.5 * w)


def _full(name, exag):
    src = POSES3[name] if isinstance(name, str) else name
    p = dict(NEUTRAL3)
    for k, v in src.items():
        if k == "hands":
            continue
        base = NEUTRAL3[k]
        p[k] = base + (v - base) * (exag if k in BODY else 1.0)
    return p, dict(src.get("hands", {}))


class Acting3D:
    """keys: [(t_seconds, pose)], talk: [(t0, t1)] mouth-flap windows, blinks: [t]"""

    def __init__(self, keys, personality="gabby", talk=(), blinks=(), seed=0):
        self.P = PERSONALITY[personality] if isinstance(personality, str) else personality
        self.keys = sorted(keys, key=lambda k: k[0])
        self.full = [_full(p, self.P["exag"]) for _, p in self.keys]
        self.talk, self.blinks, self.seed = list(talk), list(blinks), seed

    def __call__(self, t):
        P, s = self.P, self.seed
        if P["twos"]:
            t = math.floor(t * FPS / 2) * 2 / FPS
        i = 0
        while i + 1 < len(self.keys) and self.keys[i + 1][0] <= t:
            i += 1
        (cur, ch), (prev, ph) = self.full[i], self.full[i - 1] if i > 0 else self.full[i]
        dur = P["frames"] / FPS * 1.6
        u = (t - self.keys[i][0]) / dur if i > 0 else 1.0
        m = toon_curve(u, P["antic"], P["over"])
        out = {k: prev[k] + (cur[k] - prev[k]) * (m if k in BODY else min(1, max(0, u * 2.5))) for k in NEUTRAL3}
        hands = {"L": "relax", "R": "relax"}
        hands.update(ph if u <= 0.35 else ch)
        d = P["drift"]  # moving hold
        out["tilt"] += d * 1.6 * math.sin(t * 1.3 + s)
        out["lean"] += d * 0.8 * math.sin(t * 0.9 + s)
        out["shL_a"] += d * 1.5 * math.sin(t * 1.1 + s + 1)
        out["shR_a"] += d * 1.5 * math.sin(t * 1.2 + s + 2)
        out["root_z"] += d * 0.012 * math.sin(t * 1.7 + s)
        if 0 < u < 1:  # stretch on the move, squash on the settle
            if u < 0.55:
                out["sq"] = 1 + P["stretch"] * math.sin(math.pi * min(1, max(0, (u - 0.2) / 0.35)))
            else:
                out["sq"] = 1 - P["stretch"] * 0.7 * math.sin(math.pi * min(1, (u - 0.55) / 0.45))
        for t0, t1 in self.talk:  # mouth flaps (placeholder until lip-sync from audio)
            if t0 <= t <= t1:
                out["mouth"] = 0.15 + 0.75 * abs(math.sin(t * 17.3 + 2.1 * math.sin(t * 5.3 + s)))
        for tb in self.blinks:
            if 0 <= t - tb < 0.17:
                out["blink"] = 1.0
        return out, hands


def apply_pose(R, p, hands):
    r = math.radians
    J = R.J
    J["root"].location.z = p["root_z"]
    sq = p.get("sq", 1.0)
    J["root"].scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)
    J["chest"].rotation_euler = (r(p["lean"]), 0, r(p["twist"]))
    J["hips"].rotation_euler = (0, 0, r(p["hip_twist"]))
    J["head"].rotation_euler = (r(p["nod"]), r(p["tilt"]), r(p["turn"]))
    for s, sx in (("L", 1), ("R", -1)):
        J[f"sh{s}"].rotation_euler = (r(-p[f"sh{s}_f"]), r(-sx * p[f"sh{s}_a"]), r(sx * p[f"sh{s}_t"]))
        J[f"el{s}"].rotation_euler = (r(-p[f"el{s}"]), 0, r(-sx * p[f"el{s}_t"]))
        J[f"wr{s}"].rotation_euler = (r(-p[f"wr{s}"]), 0, 0)
        J[f"hip{s}"].rotation_euler = (r(-p[f"hip{s}_f"]), r(-sx * p[f"hip{s}_a"]), 0)
        J[f"kn{s}"].rotation_euler = (r(p[f"kn{s}"]), 0, 0)
        J[f"an{s}"].rotation_euler = (r(p[f"hip{s}_f"] - p[f"kn{s}"]), r(sx * p[f"hip{s}_a"]), 0)
        curls, thumb, spread = HAND_SHAPES[hands.get(s, "relax")]
        for i in range(3):  # palms face the body: curl around Y toward the body
            J[f"f{s}{i}"].rotation_euler = (r(spread * 12 * (1 - i)), r(sx * curls[i]), 0)
        J[f"th{s}"].rotation_euler = (r(-35), r(sx * thumb * 0.6), r(-sx * 20))
        # face
        b = R.base[J[f"brow{s}"].name][0]
        J[f"brow{s}"].location = (b.x, b.y, b.z + 0.06 * p["brow"])
        J[f"brow{s}"].rotation_euler = (0, r(-sx * 14 * p["brow_ang"]), 0)
        J[f"eye{s}"].scale = (1, 1, max(0.08, 1 - 0.92 * p["blink"]))
        pb = R.base[J[f"pup{s}"].name][0]
        J[f"pup{s}"].location = (pb.x + 0.06 * p["look_x"], pb.y, pb.z + 0.07 * p["look_z"])
    J["mouth"].scale = (1 + 0.25 * p["smile"] - 0.18 * p["mouth"], 1, 1 + 4.2 * p["mouth"])


def fcurves(o):
    ad = o.animation_data
    if not (ad and ad.action):
        return []
    if hasattr(ad.action, "fcurves"):  # Blender < 5
        return list(ad.action.fcurves)
    from bpy_extras import anim_utils
    cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
    return list(cb.fcurves) if cb else []


def bake(R, acting, t_end, start_frame=1):
    """sample the acting on twos and keyframe every animated channel, held (constant) like drawings"""
    n = int(round(t_end * FPS))
    for f in range(0, n + 1, 2):
        p, h = acting(f / FPS)
        apply_pose(R, p, h)
        R.key_all(start_frame + f)
    for o in {o for o, _ in R.keyed}:
        for fc in fcurves(o):
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"
    return n


# =============================================================== sets
def build_laundromat(sc):
    K = ink(f"ink_set_{sc.name}")
    floor = mesh_obj(sc, f"floor_{sc.name}", xform(box(30, 30, 0.02), loc=(0, 0, -0.01)),
                     checker_cel(f"tiles_{sc.name}", (226, 220, 196), (170, 196, 178), scale=0.7), 0, K)
    wall = mesh_obj(sc, f"wall_{sc.name}", xform(box(30, 0.2, 9), loc=(0, 3.2, 4.5)), cel(f"wallc_{sc.name}", (86, 140, 146), shade=0.75), 0, K)
    mesh_obj(sc, f"skirt_{sc.name}", xform(box(30, 0.3, 0.35), loc=(0, 3.05, 0.17)), cel(f"skirtc_{sc.name}", (56, 92, 98)), 0.02, K)
    white = cel(f"machine_{sc.name}", (236, 236, 230), shade=0.7)
    panel = cel(f"panel_{sc.name}", (190, 196, 200))
    glow = flat(f"glow_{sc.name}", (120, 255, 140))
    glass = flat(f"glass_{sc.name}", (40, 70, 80))
    chrome = cel(f"chrome_{sc.name}", (170, 176, 186))
    for i, x in enumerate((-4.4, -2.9, 2.6, 4.1, 5.6)):
        y, z = 2.25, 0.85
        mesh_obj(sc, f"mach{i}_{sc.name}", xform(box(1.36, 1.3, 1.7), loc=(x, y, z)), white, 0.022, K, bevel=0.12)
        mesh_obj(sc, f"panel{i}_{sc.name}", xform(box(1.3, 0.3, 0.28), loc=(x, y + 0.48, z + 0.95)), panel, 0.016, K, bevel=0.05)
        ring = xform(torus(0.4, 0.07), loc=(x, y - 0.66, z + 0.05), rot=(math.radians(90), 0, 0))
        mesh_obj(sc, f"ring{i}_{sc.name}", ring, chrome, 0.016, K)
        disc = xform(ellipsoid(0.38, 0.04, 0.38), loc=(x, y - 0.64, z + 0.05))
        mesh_obj(sc, f"door{i}_{sc.name}", disc, glow if i == 1 else glass, 0, K)
    return floor, wall


# =============================================================== render helpers
class on_screen:
    """temporarily show `sc` in the main window (animation is only evaluated for it), then restore"""
    def __init__(self, sc):
        self.sc = sc

    def __enter__(self):
        wins = bpy.context.window_manager.windows
        self.win = wins[0] if len(wins) else None
        if self.win:
            self.prev = self.win.scene
            self.win.scene = self.sc

    def __exit__(self, *a):
        if self.win:
            self.win.scene = self.prev


def render_still(sc, path, frame=1):
    with on_screen(sc):
        return _render_still(sc, path, frame)


def render_clip(sc, path, f0, f1):
    with on_screen(sc):
        return _render_clip(sc, path, f0, f1)


def _render_still(sc, path, frame=1):
    sc.frame_set(frame)
    s = sc.render.image_settings
    s.media_type = "IMAGE"
    s.file_format = "PNG"
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    return round(time.time() - t, 2)


def _render_clip(sc, path, f0, f1):
    sc.frame_start, sc.frame_end = f0, f1
    s = sc.render.image_settings
    s.media_type = "VIDEO"
    s.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(animation=True, scene=sc.name)
    return round(time.time() - t, 2)


# =============================================================== demos
def demo_turnaround():
    """front / 3-4 / side / back stills of Gabby in the neutral pose"""
    sc = new_scene("SG3D_turn", bg=(244, 214, 120))
    t0 = time.time()
    R = build_gabby(sc)
    build_s = round(time.time() - t0, 2)
    sun(sc, rot=(55, 0, 25))
    camera(sc, (0, -11, 1.9), (0, 0, 1.75), lens=50)
    times, files = [], []
    for ang in (0, -35, -90, 180):
        R.J["root"].rotation_euler.z = math.radians(ang)
        f = os.path.join(OUT, f"gabby_turn_{ang if ang >= 0 else 'm' + str(-ang)}.png")
        times.append(render_still(sc, f))
        files.append(f)
    R.J["root"].rotation_euler.z = 0
    return dict(build_s=build_s, still_s=times, files=files)


def demo_line():
    """Gabby: 'Shirl! ... the dryer ate my lucky sock.' pose-to-pose, in the laundromat"""
    sc = new_scene("SG3D_line", bg=(86, 140, 146))
    t0 = time.time()
    build_laundromat(sc)
    R = build_gabby(sc)
    R.J["root"].location.x = 0.4
    R.J["root"].rotation_euler.z = math.radians(18)  # cheat him toward camera (unkeyed staging)
    sun(sc, rot=(52, 0, 28))
    camera(sc, (3.3, -7.4, 2.45), (0.15, 0.6, 1.7), lens=36)
    acting = Acting3D([(0.0, "stand"), (0.35, "call_out"), (1.15, "point"), (2.15, "whine"), (3.45, "whine")],
                      "gabby", talk=[(0.42, 0.78), (1.25, 1.95), (2.25, 3.05)], blinks=[1.05, 3.2])
    n = bake(R, acting, 3.6)  # root x stays 0.4 (apply_pose only drives z)
    build_s = round(time.time() - t0, 2)
    still = os.path.join(OUT, "gabby_line_still.png")
    st = render_still(sc, still, frame=int(1.6 * FPS))
    return dict(build_s=build_s, still_s=st, still=still, frames=n + 1, scene=sc.name)


def demo_line_clip():
    sc = bpy.data.scenes["SG3D_line"]
    path = os.path.join(OUT, "gabby_line.mp4")
    n = int(round(3.6 * FPS)) + 1
    t = render_clip(sc, path, 1, n)
    return dict(clip=path, clip_s=t, sec_per_frame=round(t / n, 3))
