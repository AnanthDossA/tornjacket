"""Shirley & Gabby - FINAL teen characters in 3D (Blender 5.x), rendered with a 2D comic look.

Pipeline decision (owner, 2026-11-06): everything is built in 3D in Blender and rendered to look 2D
(comic) from any camera angle.

How the 3D matches the locked 2D sheet (concept/FINAL_characters.png):
  * heads, hair, hoodies are "lathed" from the sheet's front-silhouette widths (assets/profiles.json),
    so the front view has exactly the drawn outline; depth comes from a per-part ratio
  * face features are the sheet's own comic art (assets/decals/<who>_<expr>.png) wrapped on the face,
    one decal object per expression (switch = show/hide)
  * comic shader: flat colour + halftone dots only in the shadow side (screen-space dots), ink outline
    via inverted hull

Coordinates: sheet units (origin = face centre, y down) -> Blender: X = x*K, Z = (FEET - y)*K, Y = depth.
Usage (live Blender via the MCP add-on):
    ns = {}; exec(open(PATH).read(), ns); ns["demo_turnaround"]()
"""
import bpy, bmesh, math, os, json, time
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(os.path.expanduser("~"), "ShirleyGabby", "engine")
_sg = {"__name__": "sg3d"}
exec(compile(open(os.path.join(HERE, "sg3d.py"), encoding="utf-8").read(), "sg3d.py", "exec"), _sg)
lin, flat, new_scene, add_obj, mesh_obj, sun, camera = (_sg[k] for k in ("lin", "flat", "new_scene", "add_obj", "mesh_obj", "sun", "camera"))
ellipsoid, capsule, torus, xform, Rig, _mix = (_sg[k] for k in ("ellipsoid", "capsule", "torus", "xform", "Rig", "_mix"))
render_still, render_clip, on_screen, fcurves = (_sg[k] for k in ("render_still", "render_clip", "on_screen", "fcurves"))

ASSETS = os.path.join(HERE, "assets")
PROF = json.load(open(os.path.join(ASSETS, "profiles.json")))
K = 0.0035          # Blender units per sheet unit
FEET = 726.0        # sheet y of the ground
OUT = os.path.join(os.path.expanduser("~"), "ShirleyGabby", "renders")
os.makedirs(OUT, exist_ok=True)


def W(x, y, d=0.0):
    """sheet (x, y) + depth (sheet units, + = back) -> Blender world"""
    return Vector((x * K, d * K, (FEET - y) * K))


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ comic shader
def comic(name, lit, dark, cut=0.36, dots=12.0, dot_r=0.32):
    """flat colour; on the shadow side, halftone dots of the dark colour (screen-space, round)"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    sh = nt.nodes.new("ShaderNodeMath"); sh.operation = "LESS_THAN"; sh.inputs[1].default_value = cut
    nt.links.new(dif.outputs[0], s2r.inputs[0]); nt.links.new(s2r.outputs[0], bw.inputs[0]); nt.links.new(bw.outputs[0], sh.inputs[0])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sc = nt.nodes.new("ShaderNodeVectorMath"); sc.operation = "MULTIPLY"; sc.inputs[1].default_value = (16 * dots, 9 * dots, 0)
    nt.links.new(tc.outputs["Window"], sc.inputs[0])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.voronoi_dimensions = "2D"
    vor.inputs["Scale"].default_value = 1.0
    vor.inputs["Randomness"].default_value = 0.0
    nt.links.new(sc.outputs[0], vor.inputs["Vector"])
    dot = nt.nodes.new("ShaderNodeMath"); dot.operation = "LESS_THAN"; dot.inputs[1].default_value = dot_r
    nt.links.new(vor.outputs["Distance"], dot.inputs[0])
    mk = nt.nodes.new("ShaderNodeMath"); mk.operation = "MULTIPLY"
    nt.links.new(sh.outputs[0], mk.inputs[0]); nt.links.new(dot.outputs[0], mk.inputs[1])
    col = _mix(nt, mk.outputs[0], lin(lit), lin(dark))
    nt.links.new(col, em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def ink(name="Ink", rgb=(16, 13, 18)):
    """inverted-hull ink that does NOT cast shadows (otherwise the hull shadows the whole part)"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = lin(rgb)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lp = nt.nodes.new("ShaderNodeLightPath")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0])
    nt.links.new(em.outputs[0], mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.use_backface_culling = True
    if hasattr(m, "use_transparent_shadow"):
        m.use_transparent_shadow = True
    if hasattr(m, "shadow_method"):
        m.shadow_method = "NONE"
    return m


def decal_mat(name, path):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path, check_existing=True)
    tex.extension = "CLIP"
    tex.interpolation = "Cubic"
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Color"], em.inputs[0])
    nt.links.new(tex.outputs["Alpha"], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    return m


# ------------------------------------------------------------------ geometry from the sheet
def rows_of(key, y0=None, y1=None, grow=0.0):
    r = [row for row in PROF["shapes"][key] if (y0 is None or row[0] >= y0) and (y1 is None or row[0] <= y1)]
    return [[y, xa - grow, xb + grow] for y, xa, xb in r]


def lathe(rows, depth, seg=56, d_off=0.0, step=1):
    """rings through each silhouette row: x from the sheet, depth = half-width * ratio (ellipse); capped"""
    bm = bmesh.new()
    rings = []
    rows = rows[::step] if step > 1 else rows
    for y, xa, xb in rows:
        cx, rx = (xa + xb) / 2, max(0.5, (xb - xa) / 2)
        ry = rx * depth
        ring = [bm.verts.new(W(cx + rx * math.cos(2 * math.pi * k / seg), y, d_off + ry * math.sin(2 * math.pi * k / seg))) for k in range(seg)]
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    for ring, rev in ((rings[0], True), (rings[-1], False)):
        c = bm.verts.new(sum((v.co for v in ring), Vector()) / len(ring))
        for k in range(seg):
            f = (ring[(k + 1) % seg], ring[k], c) if not rev else (ring[k], ring[(k + 1) % seg], c)
            bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    return bm


def to_sheet(co):
    return co.x / K, FEET - co.z / K


def inside(pt, poly):
    x, y = pt
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1:
            c = not c
    return c


def cut_opening(bm, poly):
    """delete the front faces of a hair shell where the face shows through"""
    kill = [f for f in bm.faces if f.calc_center_median().y < 0 and inside(to_sheet(f.calc_center_median()), poly)]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    return bm


def keep_back(bm, frac=0.15):
    kill = [f for f in bm.faces if f.calc_center_median().y < frac]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    return bm


def front_depth(key, x, y, depth):
    """sheet-unit depth (negative = toward camera) of a lathe surface at sheet (x, y)"""
    best = min(PROF["shapes"][key], key=lambda r: abs(r[0] - y))
    _, xa, xb = best
    cx, rx = (xa + xb) / 2, (xb - xa) / 2
    u = max(-1, min(1, (x - cx) / rx))
    return -rx * depth * math.sqrt(1 - u * u)


def decal_from(head_bm, img_path, push=1.6):
    """copy the front of the head, push it out a little, UV it with the sheet's decal view box"""
    vb = PROF["decal_viewbox"]
    bm = head_bm.copy()
    kill = [f for f in bm.faces if f.calc_center_median().y > -0.02]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * push * K
    me = bpy.data.meshes.new("decal")
    bm.to_mesh(me)
    bm.free()
    uv = me.uv_layers.new(name="UV")
    for loop in me.loops:
        co = me.vertices[loop.vertex_index].co
        sx, sy = to_sheet(co)
        uv.data[loop.index].uv = ((sx - vb[0]) / vb[2], 1 - (sy - vb[1]) / vb[3])
    for p in me.polygons:
        p.use_smooth = True
    return me


# ------------------------------------------------------------------ character builder
LINE = 0.013


def _hand(R, s, sx, skin_m, K_, wrist):
    """simple organic-ish cartoon hand on a wrist joint: palm + 3 fingers + thumb (finger joints for poses)"""
    R.part(f"palm{s}", ellipsoid(0.06, 0.11, 0.11), skin_m, f"wr{s}", R.W[f"wr{s}"] + Vector((0, 0, -0.09)), 0.009, K_)
    for i, fyo in enumerate((-0.07, 0.0, 0.07)):
        fk = f"f{s}{i}"
        kn = R.W[f"wr{s}"] + Vector((0, fyo, -0.18))
        R.joint(fk, kn, f"wr{s}")
        R.part(f"finger{s}{i}", capsule(0.032, 0.085 - 0.012 * (i == 2), 0.028), skin_m, fk, kn, 0.007, K_)
        R.anim(R.J[fk], "rotation_euler")
    tk = R.W[f"wr{s}"] + Vector((-0.02 * sx, -0.09, -0.07))
    R.joint(f"th{s}", tk, f"wr{s}")
    R.part(f"thumb{s}", capsule(0.034, 0.065, 0.029), skin_m, f"th{s}", tk, 0.007, K_)
    R.anim(R.J[f"th{s}"], "rotation_euler")


def build_teen(sc, who, x_off=0.0):
    G = who == "gabby"
    pal = {
        "skin": ("#a46f4b", "#774d31") if G else ("#8c5b3d", "#5f3c27"),
        "hair": ("#17121a", "#0b080d"),
        "top": ("#e5483b", "#ad2f28") if G else ("#b583c9", "#83579a"),
        "top_dk": ("#c23a31", "#8f2620") if G else ("#9b6bb0", "#6e4683"),
        "low": ("#9fb1c6", "#6f8299") if G else ("#4d6ea6", "#344d7d"),
        "shoe": ("#f2f1ea", "#c3c1b8"), "sole": ("#d84a3c", "#a8352a") if G else ("#d9d6cc", "#b2afa6"),
        "white": ("#fbfaf4", "#d7d5cc"), "gold": ("#ecc65e", "#b48c2c"), "clip": ("#3fae5a", "#24803c"),
    }
    Kk = ink(f"ink_{who}")
    M = {k: comic(f"{k}_{who}", hx(a), hx(b)) for k, (a, b) in pal.items()}
    R = Rig(sc, who.capitalize())
    J = R.joint
    J("root", W(0, FEET) + Vector((x_off, 0, 0)))
    J("hips", W(0, 380) + Vector((x_off, 0, 0)), "root")
    J("chest", W(0, 250) + Vector((x_off, 0, 0)), "hips")
    J("head", W(0, 118) + Vector((x_off, 0, 0)), "chest")
    off = Vector((x_off, 0, 0))
    at0 = off  # parts are built in world coords (character at x_off), parented with location = at - joint
    shx, hipx = (100, 40) if G else (92, 38)
    for s, sx in (("L", 1), ("R", -1)):
        J(f"sh{s}", W(shx * sx, 170) + off, "chest")
        J(f"el{s}", W((shx + 8) * sx, 292) + off, f"sh{s}")
        J(f"wr{s}", W((shx + 12) * sx, 404) + off, f"el{s}")
        J(f"hip{s}", W(hipx * sx, 380) + off, "hips")
        J(f"kn{s}", W(hipx * sx, 560) + off, f"hip{s}")
        J(f"an{s}", W(hipx * sx, 680) + off, f"kn{s}")

    def part(key, bm, mat, joint, line=LINE):
        bmesh.ops.translate(bm, verts=bm.verts, vec=off)
        return R.part(key, bm, mat, joint, Vector((0, 0, 0)), line, Kk)

    # ---------------- head + face decals + hair
    face_key = "face_gabby" if G else "face_shirley"
    hb = lathe(rows_of(face_key), 1.0, 64)
    decals = {}
    for e in PROF["decals"][who]:
        img = os.path.join(ASSETS, "decals", f"{who}_{e}.png")
        me = decal_from(hb, img)
        me.transform(Matrix.Translation(off))
        me.materials.append(decal_mat(f"dec_{who}_{e}", img))
        o = add_obj(sc, f"{who}_face_{e}", me)
        o.parent = R.J["head"]
        o.location = -R.W["head"]
        decals[e] = o
    part("head", hb, M["skin"], "head")
    for sx in (-1, 1):  # ears
        ex, ey = (95, -6) if G else (86, 0)
        part(f"ear{sx}", xform(ellipsoid(18 * K, 9 * K, (28 if G else 19) * K), loc=W(ex * sx, ey, 6) - Vector((0, 0, 0))), M["skin"], "head", 0.01)
    if G:
        hair = cut_opening(lathe(rows_of("hair_gabby", grow=3), 1.08, 160), PROF["openings"]["gabby"])
        part("hair", hair, M["hair"], "head")
        nape = keep_back(lathe(rows_of("face_gabby", -110, 40, grow=3), 1.04, 64), 0.12)
        part("nape", nape, M["hair"], "head")
    else:
        bob = cut_opening(lathe(rows_of("bob_shirley"), 1.1, 160), PROF["openings"]["shirley"])
        part("bob", bob, M["hair"], "head")
        fx, fy = -60, -124
        d = front_depth("bob_shirley", fx, fy, 1.1)
        for k in range(5):  # green flower clip
            a = math.radians(-90 + 72 * k)
            part(f"petal{k}", xform(ellipsoid(12 * K, 5 * K, 12 * K), loc=W(fx + 13 * math.cos(a), fy + 13 * math.sin(a), d - 4)), M["clip"], "head", 0.007)
        part("flowerc", xform(ellipsoid(7 * K, 5 * K, 7 * K), loc=W(fx, fy, d - 8)), M["gold"], "head", 0.006)
    part("neck", xform(capsule(24 * K, 60 * K), loc=W(0, 92, 8)), M["skin"], "head", 0.01)

    # ---------------- hoodie
    hood_key = "hoodie_gabby" if G else "hoodie_shirley"
    part("torso", lathe(rows_of(hood_key), 0.62, 56), M["top"], "chest")
    hem_y = (340, 368) if G else (404, 428)
    hem = [[y, xa - 3, xb + 3] for y, xa, xb in rows_of(hood_key) if hem_y[0] - 4 <= y]
    hem = hem + [[hem_y[1], hem[-1][1], hem[-1][2]]]
    part("hem", lathe([r for r in hem if r[0] <= hem_y[1]], 0.64, 56), M["top_dk"], "hips", 0.01)
    part("hood", xform(ellipsoid(76 * K, 46 * K, 30 * K), loc=W(0, 136, 46)), M["top_dk"], "chest")
    dz = front_depth(hood_key, 0, 200, 0.62)
    for sx in (-1, 1):  # drawstrings
        part(f"string{sx}", xform(capsule(3.5 * K, 80 * K), loc=W(17 * sx, 152, dz - 3)), M["white"], "chest", 0.006)
    if G:
        dp = front_depth(hood_key, 0, 300, 0.62)
        part("pocket", xform(ellipsoid(72 * K, 8 * K, 38 * K), loc=W(0, 298, dp - 2)), M["top"], "chest", 0.009)
    else:
        dv = front_depth(hood_key, 0, 180, 0.62)
        tee = bmesh.new()
        a_, b_, c_ = [tee.verts.new(W(x, y, dv - 3)) for x, y in ((-26, 150), (26, 150), (0, 236))]
        tee.faces.new((a_, b_, c_))
        part("tee", tee, M["white"], "chest", 0.008)
        part("zip", xform(capsule(2.5 * K, 178 * K), loc=W(0, 236, front_depth(hood_key, 0, 320, 0.62) - 3)), M["hair"], "chest", 0)
    # ---------------- arms (sleeves), hands
    for s, sx in (("L", 1), ("R", -1)):
        up = (R.W[f"el{s}"] - R.W[f"sh{s}"]).length
        lo = (R.W[f"wr{s}"] - R.W[f"el{s}"]).length
        R.part(f"upper{s}", capsule(30 * K, up, 27 * K), M["top"], f"sh{s}", None, LINE, Kk)
        if G:  # sleeves pushed up: bunched cuff at the elbow, bare forearm, wrist tape
            R.part(f"cuff{s}", torus(29 * K, 9 * K), M["top_dk"], f"el{s}", R.W[f"el{s}"] + Vector((0, 0, 0.01)), 0.008, Kk)
            R.part(f"fore{s}", capsule(17 * K, lo, 15 * K), M["skin"], f"el{s}", None, LINE, Kk)
            R.part(f"tape{s}", xform(capsule(17.5 * K, 16 * K), loc=Vector((0, 0, -lo + 0.06))), M["white"], f"el{s}", R.W[f"el{s}"], 0.007, Kk)
        else:  # full sleeve with a ribbed cuff, gold bangle on one wrist
            R.part(f"fore{s}", capsule(27 * K, lo - 0.05, 23 * K), M["top"], f"el{s}", None, LINE, Kk)
            R.part(f"cuff{s}", torus(22 * K, 8 * K), M["top_dk"], f"el{s}", R.W[f"el{s}"] + Vector((0, 0, -lo + 0.06)), 0.008, Kk)
            if s == "R":
                R.part("bangle", torus(19 * K, 4 * K), M["gold"], f"wr{s}", R.W[f"wr{s}"] + Vector((0, 0, 0.02)), 0.006, Kk)
        _hand(R, s, sx, M["skin"], Kk, f"wr{s}")
        R.anim(R.J[f"sh{s}"], "rotation_euler"); R.anim(R.J[f"el{s}"], "rotation_euler"); R.anim(R.J[f"wr{s}"], "rotation_euler")
    # ---------------- legs, shorts / jeans, sneakers
    if G:
        R.part("pelvis", xform(ellipsoid(86 * K, 52 * K, 44 * K), loc=Vector(W(0, 380)) + off), M["low"], "hips", Vector((0, 0, 0)), LINE, Kk)
    else:
        R.part("pelvis", xform(ellipsoid(78 * K, 50 * K, 40 * K), loc=Vector(W(0, 420)) + off), M["low"], "hips", Vector((0, 0, 0)), LINE, Kk)
    for s, sx in (("L", 1), ("R", -1)):
        th = (R.W[f"kn{s}"] - R.W[f"hip{s}"]).length
        sh_ = (R.W[f"an{s}"] - R.W[f"kn{s}"]).length
        if G:
            R.part(f"short{s}", capsule(44 * K, 70 * K, 40 * K), M["low"], f"hip{s}", None, LINE, Kk)
            R.part(f"thigh{s}", capsule(19 * K, th, 17 * K), M["skin"], f"hip{s}", None, LINE, Kk)
            R.part(f"shin{s}", capsule(17 * K, sh_, 15 * K), M["skin"], f"kn{s}", None, LINE, Kk)
            R.part(f"sock{s}", capsule(19 * K, 14 * K), M["white"], f"an{s}", None, 0.008, Kk)
            if s == "R":
                R.part("plaster", ellipsoid(12 * K, 3 * K, 9 * K), M["gold"], f"kn{s}", R.W[f"kn{s}"] + Vector((0, -17 * K, -0.04)), 0.005, Kk)
        else:
            R.part(f"thigh{s}", capsule(32 * K, th, 25 * K), M["low"], f"hip{s}", None, LINE, Kk)
            R.part(f"shin{s}", capsule(25 * K, sh_, 18 * K), M["low"], f"kn{s}", None, LINE, Kk)
        a_ = R.W[f"an{s}"]
        R.part(f"shoe{s}", ellipsoid(30 * K, 52 * K, 20 * K), M["shoe"], f"an{s}", a_ + Vector((0, -26 * K, -20 * K)), LINE, Kk)
        R.part(f"sole{s}", ellipsoid(32 * K, 54 * K, 8 * K), M["sole"], f"an{s}", a_ + Vector((0, -26 * K, -36 * K)), 0.009, Kk)
        for j in ("hip", "kn", "an"):
            R.anim(R.J[f"{j}{s}"], "rotation_euler")
    R.anim(R.J["root"], "location", "scale"); R.anim(R.J["chest"], "rotation_euler"); R.anim(R.J["head"], "rotation_euler")
    R.anim(R.J["hips"], "rotation_euler")
    for o in sc.objects:  # hair and small accessories don't throw blotchy shadows on the face
        if any(t in o.name for t in ("_hair", "_nape", "_bob", "_petal", "_flowerc", "_hood", "_string")):
            o.visible_shadow = False
    R.decals = decals
    set_expr(R, list(decals)[0])
    return R


def set_expr(R, name, frame=None):
    for e, o in R.decals.items():
        o.hide_render = o.hide_viewport = (e != name)
        if frame is not None:
            o.keyframe_insert("hide_render", frame=frame)
            o.keyframe_insert("hide_viewport", frame=frame)


def pose_rest(R, G):
    """arms relaxed slightly out from the body, as on the sheet"""
    r = math.radians
    for s, sx in (("L", 1), ("R", -1)):
        R.J[f"sh{s}"].rotation_euler = (0, r(-sx * 8), 0)
        R.J[f"el{s}"].rotation_euler = (r(-8), 0, 0)
        for i in range(3):
            R.J[f"f{s}{i}"].rotation_euler = (0, r(sx * 22), 0)


# ------------------------------------------------------------------ demos
def demo_turnaround(who="both"):
    sc = new_scene("SG_TEENS_turn", bg=(244, 238, 226), ambient=0.2)
    t0 = time.time()
    chars = []
    if who in ("both", "shirley"):
        chars.append(build_teen(sc, "shirley", -0.75 if who == "both" else 0))
    if who in ("both", "gabby"):
        chars.append(build_teen(sc, "gabby", 0.75 if who == "both" else 0))
    for R in chars:
        pose_rest(R, R.name == "Gabby")
    build_s = round(time.time() - t0, 2)
    sun(sc, rot=(56, 0, -34), energy=4)  # light from the upper left, like the sheet
    cam = camera(sc, (0, -16, 1.75), (0, 0, 1.75), lens=50)
    files, times = [], []
    for ang in (0, -35, -90):
        for R in chars:
            R.J["root"].rotation_euler.z = math.radians(ang)
        f = os.path.join(OUT, f"teens_turn_{abs(ang)}.png")
        times.append(render_still(sc, f))
        files.append(f)
    return dict(build_s=build_s, still_s=times, files=files)


def pose(R, **p):
    """quick pose: sh{L,R}=(flex, abduct, twist), el{L,R}=(bend, twist), turn, tilt, lean (degrees); hands 'open'/'relax'/'fist'"""
    r = math.radians
    for s, sx in (("L", 1), ("R", -1)):
        f, a, t = p.get(f"sh{s}", (0, 8, 0))
        R.J[f"sh{s}"].rotation_euler = (r(-f), r(-sx * a), r(sx * t))
        b, bt = p.get(f"el{s}", (8, 0))
        R.J[f"el{s}"].rotation_euler = (r(-b), 0, r(-sx * bt))
        curl = {"open": -4, "relax": 22, "fist": 100}[p.get(f"hand{s}", "relax")]
        for i in range(3):
            R.J[f"f{s}{i}"].rotation_euler = (r(10 * (1 - i)) if curl < 0 else 0, r(sx * curl), 0)
    R.J["head"].rotation_euler = (r(p.get("nod", 0)), r(p.get("tilt", 0)), r(p.get("turn", 0)))
    R.J["chest"].rotation_euler = (r(p.get("lean", 0)), 0, r(p.get("twist", 0)))


def backdrop(sc, rgb=(255, 214, 92), dark=(242, 169, 59)):
    floor = bmesh.new()
    bmesh.ops.create_circle(floor, cap_ends=True, segments=64, radius=9)
    mesh_obj(sc, "floor", floor, comic("floor", (236, 226, 204), (196, 182, 156)), 0)
    wall = bmesh.new()
    bmesh.ops.create_grid(wall, x_segments=1, y_segments=1, size=12)
    xform(wall, loc=(0, 4, 6), rot=(math.radians(90), 0, 0))
    mesh_obj(sc, "wall", wall, comic("wall", rgb, dark), 0)


def demo_shots():
    """same 3D scene, three camera angles, all rendered with the 2D comic look"""
    sc = new_scene("SG_TEENS_shots", bg=(255, 214, 92), ambient=0.22)
    backdrop(sc)
    S = build_teen(sc, "shirley", -0.75)
    G = build_teen(sc, "gabby", 0.75)
    sun(sc, rot=(56, 0, -34), energy=4)
    out = {}
    # A: wide two-shot, Gabby in his gymnast 'ta-da' salute, Shirley hand on hip
    pose(G, shL=(10, 150, 0), shR=(10, 150, 0), elL=(15, 0), elR=(15, 0), handL="open", handR="open", tilt=-6)
    pose(S, shL=(-12, 34, 0), elL=(105, 80), handL="fist", tilt=4)
    set_expr(G, "grin"); set_expr(S, "calm")
    camera(sc, (0.6, -9.5, 2.3), (0, 0, 1.55), lens=38, name="camA")
    out["A_wide"] = render_still(sc, os.path.join(OUT, "shot_A_wide.png"))
    # B: low-angle hero shot on Gabby
    camera(sc, (1.9, -3.4, 0.7), (0.8, 0, 2.05), lens=30, name="camB")
    out["B_low"] = render_still(sc, os.path.join(OUT, "shot_B_low.png"))
    # C: over Gabby's shoulder onto an unimpressed Shirley (they face each other)
    S.J["root"].rotation_euler.z = math.radians(62)
    G.J["root"].rotation_euler.z = math.radians(-62)
    pose(G, shL=(20, 20, 0), shR=(0, 10, 0), elL=(40, 0), handL="open", turn=-8)
    set_expr(S, "unimpressed")
    camera(sc, (2.9, 1.9, 2.7), (-0.7, -0.1, 2.2), lens=55, name="camC")
    out["C_ots"] = render_still(sc, os.path.join(OUT, "shot_C_ots.png"))
    return out
