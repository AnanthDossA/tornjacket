"""Rigged FINAL characters (Rigify skeleton + one smooth deforming body + 3D eyes/brows + mouth swaps).

Owner feedback on the first 3D build: "looks like a toy, stiff eyes". This rebuild:
  * Rigify human metarig, face bones removed (face is done our own way), fitted to the character's
    sheet proportions (spine/neck/head, arms, hands + 4 fingers + thumb, legs, feet), then generated
  * ONE continuous skin mesh (parts fused with voxel remesh, ~tens of k polys), auto-weighted;
    hoodie and shorts/jeans are separate fused meshes, auto-weighted; rigid bits ride on bones
  * eyes: almond 3D eye meshes; iris/pupil/glint drawn in the shader and steered by the eye object's
    custom props look_x/look_z; shape keys blink / squint / wide
  * brows: 3D brow meshes (from the sheet's brow shape) that move/rotate per expression
  * mouth: the sheet's drawn mouths as swappable decal layers (for expressions and later lip-sync);
    nose/blush as a static decal
Everything still renders with teen3d's halftone comic shader + ink outline.

Usage (live Blender via MCP):
    ns = {}; exec(open(PATH).read(), ns); R = ns["build_rigged"]("gabby"); ns["demo_rig"]()
"""
import bpy, bmesh, math, os, json, time
from mathutils import Vector, Matrix

HERE = os.path.join(os.path.expanduser("~"), "ShirleyGabby", "engine")
_t = {"__name__": "teen3d"}
exec(compile(open(os.path.join(HERE, "teen3d.py"), encoding="utf-8").read(), "teen3d.py", "exec"), _t)
for _k in ("comic", "ink", "decal_mat", "lathe", "rows_of", "cut_opening", "keep_back", "front_depth", "decal_from", "W", "K",
           "FEET", "PROF", "ASSETS", "OUT", "new_scene", "add_obj", "mesh_obj", "sun", "camera", "render_still", "render_clip",
           "ellipsoid", "capsule", "torus", "xform", "hx", "lin", "backdrop", "to_sheet", "LINE"):
    globals()[_k] = _t[_k]

SPEC = {
    "gabby": dict(
        skin=("#a46f4b", "#774d31"), hair=("#17121a", "#0b080d"), top=("#e5483b", "#ad2f28"), top_dk=("#c23a31", "#8f2620"),
        low=("#9fb1c6", "#6f8299"), shoe=("#f2f1ea", "#c3c1b8"), sole=("#d84a3c", "#a8352a"), white=("#fbfaf4", "#d7d5cc"),
        gold=("#ecc65e", "#b48c2c"), iris="#3e2416",
        face="face_gabby", hood="hoodie_gabby", hem=(340, 368),
        joints=dict(sh=(100, 170), el=(108, 292), wr=(112, 404), hip=(40, 380), kn=(40, 560), an=(40, 680), neck=150, chin=112, pelvis=380),
        eye=dict(cx=36, cy=-12, rx=29, ry=22), brow=dict(y0=-54, xo=62, thick=9),
        arm_r=(19, 16), leg_r=(19, 15), shorts=True, exprs=["grin", "focus", "whoa", "dizzy"],
        face_expr={"grin": dict(raise_=-6, ang=-4, look=(2, 0), squint=0.35), "focus": dict(raise_=6, ang=12, look=(0, -1), lid=0.32),
                   "dizzy": dict(raise_=-10, ang=-8, lid=0.2), "whoa": dict(raise_=-16, ang=-6, look=(0, 0), wide=1.0)}),
}


# ------------------------------------------------------------------ context helpers (ops need the scene on screen)
class OnScreen:
    def __init__(self, sc):
        self.sc = sc

    def __enter__(self):
        self.win = bpy.context.window_manager.windows[0]
        self.prev = self.win.scene
        self.win.scene = self.sc
        area = [a for a in self.win.screen.areas if a.type == "VIEW_3D"][0]
        region = [r for r in area.regions if r.type == "WINDOW"][0]
        self.ov = bpy.context.temp_override(window=self.win, area=area, region=region, scene=self.sc)
        self.ov.__enter__()
        return self

    def __exit__(self, *a):
        self.ov.__exit__(*a)
        self.win.scene = self.prev


def activate(sc, obj, mode="OBJECT"):
    vl = sc.view_layers[0]
    for o in sc.objects:
        o.select_set(False)
    vl.objects.active = obj
    obj.select_set(True)
    if bpy.context.object and bpy.context.object.mode != mode:
        bpy.ops.object.mode_set(mode=mode)


# ------------------------------------------------------------------ geometry helpers
def seg_capsule(a, b, r0, r1=None):
    """capsule from world point a to b"""
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    bm = capsule(r0, L, r1 if r1 is not None else r0)
    rot = Vector((0, 0, -1)).rotation_difference((b - a).normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(a) @ rot, verts=bm.verts)
    return bm


def sphere_at(c, r, sy=1.0, sz=1.0):
    return xform(ellipsoid(r, r * sy, r * sz), loc=Vector(c))


def merge(bms):
    out = bmesh.new()
    me = bpy.data.meshes.new("tmp")
    for bm in bms:
        bm.to_mesh(me)
        out.from_mesh(me)
        bm.free()
    bpy.data.meshes.remove(me)
    return out


def fused_object(sc, name, bms, mat, inkm, voxel=0.008, line=LINE):
    """join parts, voxel-remesh them into one continuous smooth mesh (scene must be on screen)"""
    bm = merge(bms)
    me = bpy.data.meshes.new(name + "_src")
    bm.to_mesh(me); bm.free()
    tmp = add_obj(sc, name + "_src", me)
    rm = tmp.modifiers.new("remesh", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = voxel
    rm.adaptivity = 0.0
    sm = tmp.modifiers.new("smooth", "SMOOTH")
    sm.factor, sm.iterations = 0.5, 4
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    out = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.meshes.remove(me)
    out.name = name
    for p in out.polygons:
        p.use_smooth = True
    out.materials.append(mat)
    o = add_obj(sc, name, out)
    if inkm and line:
        out.materials.append(inkm)
        so = o.modifiers.new("ink", "SOLIDIFY")
        so.thickness, so.offset, so.use_flip_normals, so.use_rim, so.material_offset = line, 1, True, False, 1
    return o


def simple_object(sc, name, bm, mat, inkm, line=0.009):
    return mesh_obj(sc, name, bm, mat, line, inkmat=inkm)


# ------------------------------------------------------------------ Rigify metarig fitting
def _descendants(eb):
    out = []
    for c in eb.children:
        out.append(c)
        out += _descendants(c)
    return out


def fit_metarig(meta, S, off):
    """move the Rigify human metarig's bones onto the character's sheet joints (edit mode)"""
    J = S["joints"]
    arm = meta.data
    E = arm.edit_bones
    face = E.get("face")
    if face:
        for b in _descendants(face) + [face]:
            E.remove(b)
    for n in ("breast.L", "breast.R", "pelvis.L", "pelvis.R"):
        if n in E:
            E.remove(E[n])
    w = lambda x, y, d=0.0: W(x, y, d) + off

    def put(name, head, tail, keep_children=True):
        eb = E[name]
        old_dir = (eb.tail - eb.head).normalized()
        old_z = eb.z_axis.copy()
        if not eb.use_connect:  # connected bones keep their head on the parent's tail (Rigify needs the chains)
            eb.head = head
        eb.tail = tail
        q = old_dir.rotation_difference((eb.tail - eb.head).normalized())
        eb.align_roll(q @ old_z)

    def put_group(root, head, tail, length_scale):
        """move a bone + all its descendants rigidly (hands, feet): map the old bone frame to the new one"""
        eb = E[root]
        old = eb.matrix.copy()
        kids = _descendants(eb)
        put(root, head, tail)
        new = eb.matrix.copy()
        M = new @ Matrix.Scale(length_scale, 4) @ old.inverted()
        for k in kids:
            k.transform(M, scale=True, roll=True)

    # spine (pelvis -> chest -> neck -> head)
    sp = [w(0, J["pelvis"], 4), w(0, 330, 4), w(0, 270, 2), w(0, 210, 0), w(0, J["neck"], 4), w(0, 132, 6), w(0, J["chin"], 6), w(0, -190, 6)]
    for i, n in enumerate(["spine", "spine.001", "spine.002", "spine.003", "spine.004", "spine.005", "spine.006"]):
        put(n, sp[i], sp[i + 1])
    for s, sx in (("L", 1), ("R", -1)):
        shx, shy = J["sh"]; elx, ely = J["el"]; wrx, wry = J["wr"]
        put(f"shoulder.{s}", w(14 * sx, J["neck"] + 4, 2), w((shx - 10) * sx, shy - 2, 2))
        put(f"upper_arm.{s}", w(shx * sx, shy, 0), w(elx * sx, ely, 7))      # elbow slightly back: bends forward
        put(f"forearm.{s}", w(elx * sx, ely, 7), w(wrx * sx, wry, 0))
        old_len = E[f"hand.{s}"].length
        new_len = 40 * K
        put_group(f"hand.{s}", w(wrx * sx, wry, 0), w((wrx + 1) * sx, wry + 40, -2), new_len / old_len)
        hpx, hpy = J["hip"]; knx, kny = J["kn"]; anx, any_ = J["an"]
        put(f"thigh.{s}", w(hpx * sx, hpy, 0), w(knx * sx, kny, -6))          # knee slightly forward
        put(f"shin.{s}", w(knx * sx, kny, -6), w(anx * sx, any_, 2))
        old_len = E[f"foot.{s}"].length
        put_group(f"foot.{s}", w(anx * sx, any_, 2), w(anx * sx, any_ + 30, -42), (52 * K) / old_len)


def build_rig(sc, name, S, off):
    with OnScreen(sc):
        bpy.ops.object.mode_set(mode="OBJECT") if bpy.context.object and bpy.context.object.mode != "OBJECT" else None
        bpy.ops.object.armature_human_metarig_add()
        meta = bpy.context.active_object
        meta.name = f"{name}_metarig"
        meta.location, meta.rotation_euler, meta.scale = (0, 0, 0), (0, 0, 0), (1, 1, 1)
        activate(sc, meta, "EDIT")
        fit_metarig(meta, S, off)
        bpy.ops.object.mode_set(mode="OBJECT")
        t = time.time()
        bpy.ops.pose.rigify_generate()
        rig = bpy.context.active_object if bpy.context.active_object.name != meta.name else None
        rig = rig or [o for o in sc.objects if o.type == "ARMATURE" and o is not meta][0]
        rig.name = f"{name}_rig"
        meta.hide_render = meta.hide_viewport = True
        return rig, round(time.time() - t, 1)


def bone_world(rig, name, end="head"):
    b = rig.data.bones[name]
    return rig.matrix_world @ (b.head_local if end == "head" else b.tail_local)


def parent_to_bone(obj, rig, bone):
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    b = rig.data.bones[bone]
    obj.matrix_parent_inverse = (rig.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted()


ARM_GROUPS = ("upper_arm", "forearm", "hand", "shoulder", "f_", "thumb", "palm")


def keep_torso_off_arms(obj, x_off, x_in, x_out, z_top):
    """auto-weights glue the sides of the torso to the arms; make torso verts follow the spine only
    (|x| < x_in fully, blended out to x_out), below shoulder height z_top"""
    vg = obj.vertex_groups
    names = {g.index: g.name for g in vg}
    arm_idx = {i for i, n in names.items() if any(t in n for t in ARM_GROUPS)}
    spine = vg.get("DEF-spine.003") or vg.get("DEF-spine.002")
    changed = 0
    for v in obj.data.vertices:
        x = abs(v.co.x - x_off)
        if v.co.z > z_top or x > x_out:
            continue
        t = 1.0 if x <= x_in else (x_out - x) / (x_out - x_in)
        moved = 0.0
        for g in v.groups:
            if g.group in arm_idx and g.weight > 0:
                d = g.weight * t
                vg[names[g.group]].add([v.index], g.weight - d, "REPLACE")
                moved += d
        if moved > 0 and spine:
            cur = next((g.weight for g in v.groups if g.group == spine.index), 0.0)
            spine.add([v.index], cur + moved, "REPLACE")
            changed += 1
    return changed


def auto_weights(sc, rig, objs):
    with OnScreen(sc):
        vl = sc.view_layers[0]
        for o in sc.objects:
            o.select_set(False)
        for o in objs:
            o.select_set(True)
        rig.select_set(True)
        vl.objects.active = rig
        with bpy.context.temp_override(selected_editable_objects=objs + [rig], selected_objects=objs + [rig], active_object=rig, object=rig):
            bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        return [len(o.vertex_groups) for o in objs]


# ------------------------------------------------------------------ face: 3D eyes, brows, decal layers
def eye_mat(name, iris_hex, r_iris, r_pupil):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])

    def attr(n):
        a = nt.nodes.new("ShaderNodeAttribute")
        a.attribute_type = "OBJECT"
        a.attribute_name = f'["{n}"]'
        return a.outputs["Fac"]

    def math_(op, a, b):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, bpy.types.NodeSocket):
                nt.links.new(v, n.inputs[i])
            else:
                n.inputs[i].default_value = v
        return n.outputs[0]

    dx = math_("SUBTRACT", sep.outputs["X"], attr("look_x"))
    dz = math_("SUBTRACT", sep.outputs["Z"], attr("look_z"))
    d = math_("SQRT", math_("ADD", math_("MULTIPLY", dx, dx), math_("MULTIPLY", dz, dz)), 0)
    iris = math_("LESS_THAN", d, r_iris)
    pupil = math_("LESS_THAN", d, r_pupil)
    gx = math_("ADD", dx, r_iris * 0.35)
    gz = math_("SUBTRACT", dz, r_iris * 0.4)
    glint = math_("LESS_THAN", math_("SQRT", math_("ADD", math_("MULTIPLY", gx, gx), math_("MULTIPLY", gz, gz)), 0), r_iris * 0.28)
    c = _t["_mix"](nt, iris, lin((251, 250, 244)), lin(hx(iris_hex)))
    c = _t["_mix"](nt, pupil, c, lin((27, 20, 24)))
    c = _t["_mix"](nt, glint, c, lin((255, 255, 255)))
    nt.links.new(c, em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def almond_pts(cx, cy, rx, ry, u):
    """top and bottom y of the sheet's almond eye at fraction u (0..1 across) - same curve family as teens_sheet.almond"""
    def bez(p0, p1, p2, p3, t):
        return tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))
    top = bez((cx - rx, cy + 2), (cx - rx * 0.6, cy - ry * 1.25), (cx + rx * 0.55, cy - ry * 1.3), (cx + rx, cy - 2), u)
    bot = bez((cx - rx, cy + 2), (cx - rx * 0.6, cy + ry * 0.9), (cx + rx * 0.6, cy + ry * 0.9), (cx + rx, cy - 2), u)
    return top, bot


def eye_object(sc, name, S, side, mat, inkm, off):
    e = S["eye"]
    cx, cy, rx, ry = e["cx"] * side, e["cy"], e["rx"], e["ry"]
    nu, nv = 24, 10
    bm = bmesh.new()
    grid, base, keys = [], [], {"blink": [], "squint": [], "wide": []}
    for i in range(nu + 1):
        u = i / nu
        (tx, ty), (bx, by) = almond_pts(cx, cy, rx, ry, u)
        col = []
        for j in range(nv + 1):
            v = j / nv
            x = bx + (tx - bx) * v
            y = by + (ty - by) * v
            bulge = 4 * math.sin(math.pi * u) * math.sin(math.pi * max(0.0, min(1.0, v)))
            d = front_depth(S["face"], x, y, 1.0) - 1.5 - bulge
            co = W(x, y, d) + off
            col.append(bm.verts.new(co))
            yb = by + (ty - by) * 0.18
            keys["blink"].append(W(x, yb, front_depth(S["face"], x, yb, 1.0) - 2.0) + off)
            ys = by + (ty - by) * (0.38 + 0.62 * v)
            keys["squint"].append(W(x, ys, front_depth(S["face"], x, ys, 1.0) - 1.5 - bulge) + off)
            yw = by + (ty - by) * v * 1.0 - (ty - by) * 0.22 * v
            keys["wide"].append(W(x, yw, front_depth(S["face"], x, yw, 1.0) - 1.5 - bulge) + off)
        grid.append(col)
    for i in range(nu):
        for j in range(nv):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    o = add_obj(sc, name, me)
    me.materials.append(inkm)
    so = o.modifiers.new("ink", "SOLIDIFY")
    so.thickness, so.offset, so.use_flip_normals, so.use_rim, so.material_offset = 0.008, 1, True, False, 1
    # keep the origin at the eye centre so look_x/look_z are in object space
    centre = W(cx, cy, front_depth(S["face"], cx, cy, 1.0)) + off
    me.transform(Matrix.Translation(-centre))
    o.location = centre
    o["look_x"], o["look_z"] = 0.0, 0.0
    # shape keys (positions were built in world space; convert to local)
    o.shape_key_add(name="Basis")
    n_unique = len(me.vertices)
    for kname, pts in keys.items():
        sk = o.shape_key_add(name=kname)
        # match by nearest basis vertex (grid duplicates at the corners were merged)
        basis = [v.co.copy() for v in me.vertices]
        src = [Vector(p) - centre for p in pts]
        flat_basis = []
        for i in range(nu + 1):
            for j in range(nv + 1):
                flat_basis.append(i * (nv + 1) + j)
        grid_world = []
        for i in range(nu + 1):
            (tx, ty), (bx, by) = almond_pts(cx, cy, rx, ry, i / nu)
            for j in range(nv + 1):
                v = j / nv
                x = bx + (tx - bx) * v; y = by + (ty - by) * v
                grid_world.append(Vector((x * K, 0, (FEET - y) * K)) + off - centre)
        for vi, v in enumerate(me.vertices):
            k = min(range(len(grid_world)), key=lambda q: (grid_world[q].x - v.co.x) ** 2 + (grid_world[q].z - v.co.z) ** 2)
            sk.data[vi].co = src[k]
    return o


def brow_object(sc, name, S, side, mat, inkm, off):
    b = S["brow"]
    sx = side
    xi, xe = 12 * sx, b["xo"] * sx
    yi, ye = b["y0"], b["y0"] + 4
    th = b["thick"]

    def q(p0, p1, p2, t):
        return tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * c + t * t * d for a, c, d in zip(p0, p1, p2))
    top = [q((xi, yi - th / 2), ((xi + xe) / 2, min(yi, ye) - 12), (xe, ye - 1), t / 12) for t in range(13)]
    bot = [q((xe + 2 * sx, ye + 2), ((xi + xe) / 2, min(yi, ye) - 4), (xi, yi + th / 2), t / 12) for t in range(13)]
    pts = top + bot
    bm = bmesh.new()
    vs = [bm.verts.new(W(x, y, front_depth(S["face"], x, y, 1.0) - 3.0) + off) for x, y in pts]
    bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    o = add_obj(sc, name, me)
    me.materials.append(inkm)
    so = o.modifiers.new("ink", "SOLIDIFY")
    so.thickness, so.offset, so.use_flip_normals, so.use_rim, so.material_offset = 0.006, 1, True, False, 1
    c = sum((v.co for v in me.vertices), Vector()) / len(me.vertices)
    me.transform(Matrix.Translation(-c))
    o.location = c
    o["rest"] = list(c)
    return o


# ------------------------------------------------------------------ build
def build_rigged(who="gabby", sc=None, x_off=0.0):
    S = SPEC[who]
    sc = sc or new_scene(f"SG_RIG_{who}", bg=(244, 238, 226), ambient=0.2)
    off = Vector((x_off, 0, 0))
    t0 = time.time()
    info = {}
    Kk = ink(f"rink_{who}")
    M = {k: comic(f"r{k}_{who}", hx(v[0]), hx(v[1])) for k, v in S.items() if isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], str)}
    rig, info["rigify_s"] = build_rig(sc, who.capitalize(), S, off)
    B = lambda n, e="head": bone_world(rig, n, e)
    bones = set(rig.data.bones.keys())
    info["def_bones"] = len([b for b in bones if b.startswith("DEF-")])

    with OnScreen(sc):
        # ---------------- one continuous skin body (neck, torso core, arms, hands with fingers, legs, feet)
        parts = [seg_capsule(W(0, 90) + off, W(0, 170) + off, 24 * K)]
        core = lathe([[y, xa * 0.86, xb * 0.86] for y, xa, xb in rows_of(S["hood"])], 0.55, 40)
        bmesh.ops.translate(core, verts=core.verts, vec=off)
        parts += [core, sphere_at(W(0, S["joints"]["pelvis"]) + off, 70 * K, 0.6, 0.55)]
        ar0, ar1 = S["arm_r"]; lr0, lr1 = S["leg_r"]
        for s in ("L", "R"):
            parts.append(sphere_at(B(f"upper_arm.{s}" if f"upper_arm.{s}" in bones else f"ORG-upper_arm.{s}"), (ar0 + 4) * K))
            ua, fa, hd = (f"ORG-upper_arm.{s}", f"ORG-forearm.{s}", f"ORG-hand.{s}")
            parts.append(seg_capsule(B(ua), B(ua, "tail"), ar0 * K, (ar0 - 2) * K))
            parts.append(seg_capsule(B(fa), B(fa, "tail"), (ar0 - 2) * K, ar1 * K))
            hh, ht = B(hd), B(hd, "tail")
            palm = ellipsoid(10 * K, 22 * K, 24 * K)
            rot = Vector((0, 0, -1)).rotation_difference((ht - hh).normalized()).to_matrix().to_4x4()
            bmesh.ops.transform(palm, matrix=Matrix.Translation((hh + ht) / 2) @ rot, verts=palm.verts)
            parts.append(palm)
            for f in ("f_index", "f_middle", "f_ring", "f_pinky", "thumb"):
                chain = [n for n in (f"ORG-{f}.01.{s}", f"ORG-{f}.02.{s}", f"ORG-{f}.03.{s}") if n in bones]
                if not chain:
                    continue
                r = (7.5 if f == "thumb" else 6.5) * K
                for n in chain:
                    parts.append(seg_capsule(B(n), B(n, "tail"), r, r * 0.92))
            th, sh_ = f"ORG-thigh.{s}", f"ORG-shin.{s}"
            parts.append(seg_capsule(B(th), B(th, "tail"), lr0 * K, (lr0 - 2) * K))
            parts.append(seg_capsule(B(sh_), B(sh_, "tail"), (lr0 - 2) * K, lr1 * K))
        skin = fused_object(sc, f"{who}_skin", parts, M["skin"], Kk, voxel=0.0075)
        info["skin_polys"] = len(skin.data.polygons)
        # ---------------- hoodie (torso, hood, hem, pushed-up sleeves with bunched cuffs)
        hp = [lathe(rows_of(S["hood"]), 0.62, 56)]
        hem = [r for r in rows_of(S["hood"]) if r[0] >= S["hem"][0] - 4]
        hem = [[y, xa - 3, xb + 3] for y, xa, xb in hem] + [[S["hem"][1], hem[-1][1] - 3, hem[-1][2] + 3]]
        hp.append(lathe(hem, 0.64, 56))
        hp.append(xform(ellipsoid(76 * K, 46 * K, 30 * K), loc=W(0, 136, 46)))
        for b_ in hp:
            bmesh.ops.translate(b_, verts=b_.verts, vec=off)
        for s in ("L", "R"):
            ua = f"ORG-upper_arm.{s}"
            hp.append(sphere_at(B(ua), 32 * K))
            a, b = B(ua), B(ua, "tail")
            hp.append(seg_capsule(a, a + (b - a) * 0.86, 30 * K, 28 * K))
            hp.append(xform(torus(28 * K, 10 * K), loc=a + (b - a) * 0.86))
        hoodie = fused_object(sc, f"{who}_hoodie", hp, M["top"], Kk, voxel=0.009)
        # ---------------- shorts
        sp = [sphere_at(W(0, S["joints"]["pelvis"]) + off, 86 * K, 0.62, 0.52)]
        for s in ("L", "R"):
            th = f"ORG-thigh.{s}"
            a, b = B(th), B(th, "tail")
            sp.append(seg_capsule(a, a + (b - a) * 0.5, 44 * K, 40 * K))
        shorts = fused_object(sc, f"{who}_shorts", sp, M["low"], Kk, voxel=0.009)
        info["remesh_s"] = round(time.time() - t0, 1)
    info["weights"] = auto_weights(sc, rig, [skin, hoodie, shorts])
    sh_z = B("ORG-upper_arm.L").z
    shx = abs(B("ORG-upper_arm.L").x - off.x)
    info["torso_fix"] = [keep_torso_off_arms(hoodie, off.x, shx * 0.78, shx * 1.02, sh_z - 0.04),
                         keep_torso_off_arms(skin, off.x, shx * 0.7, shx * 0.86, sh_z - 0.04)]

    # ---------------- rigid parts on bones: head, hair, ears, face layers, eyes, brows, accessories
    head_bone = "DEF-spine.006" if "DEF-spine.006" in bones else "ORG-spine.006"
    hb = lathe(rows_of(S["face"]), 1.0, 72)
    face_layers = {}
    for layer, push in (("static", 1.3),) + tuple((f"mouth_{e}", 1.7) for e in S["exprs"]):
        img = os.path.join(ASSETS, "decals", f"{who}_{layer}.png")
        me = decal_from(hb, img, push)
        me.transform(Matrix.Translation(off))
        me.materials.append(_t["decal_mat"](f"rdec_{who}_{layer}", img))
        o = add_obj(sc, f"{who}_{layer}", me)
        parent_to_bone(o, rig, head_bone)
        face_layers[layer] = o
    bmesh.ops.translate(hb, verts=hb.verts, vec=off)
    parent_to_bone(simple_object(sc, f"{who}_head", hb, M["skin"], Kk, LINE), rig, head_bone)
    for sx in (-1, 1):
        o = simple_object(sc, f"{who}_ear{sx}", xform(ellipsoid(18 * K, 9 * K, 28 * K), loc=W(95 * sx, -6, 6) + off), M["skin"], Kk, 0.01)
        parent_to_bone(o, rig, head_bone)
    hair = cut_opening(lathe(rows_of("hair_gabby", grow=3), 1.08, 160), PROF["openings"]["gabby"])
    bmesh.ops.translate(hair, verts=hair.verts, vec=off)
    nape = keep_back(lathe(rows_of(S["face"], -110, 40, grow=3), 1.04, 64), 0.12)
    bmesh.ops.translate(nape, verts=nape.verts, vec=off)
    for n, bm_ in (("hair", hair), ("nape", nape)):
        o = simple_object(sc, f"{who}_{n}", bm_, M["hair"], Kk, LINE)
        o.visible_shadow = False
        parent_to_bone(o, rig, head_bone)
    em = eye_mat(f"reye_{who}", S["iris"], 15 * K, 7.5 * K)
    eyes, brows = {}, {}
    for side, s in ((1, "L"), (-1, "R")):
        eyes[s] = eye_object(sc, f"{who}_eye{s}", S, side, em, Kk, off)
        parent_to_bone(eyes[s], rig, head_bone)
        brows[s] = brow_object(sc, f"{who}_brow{s}", S, side, M["hair"], Kk, off)
        parent_to_bone(brows[s], rig, head_bone)
    # hoodie extras + accessories
    dz = front_depth(S["hood"], 0, 200, 0.62)
    chest = "DEF-spine.003" if "DEF-spine.003" in bones else "ORG-spine.003"
    for sx in (-1, 1):
        o = simple_object(sc, f"{who}_string{sx}", xform(capsule(3.5 * K, 80 * K), loc=W(17 * sx, 152, dz - 3) + off), M["white"], Kk, 0.005)
        parent_to_bone(o, rig, chest)
    dp = front_depth(S["hood"], 0, 300, 0.62)
    o = simple_object(sc, f"{who}_pocket", xform(ellipsoid(72 * K, 8 * K, 38 * K), loc=W(0, 298, dp - 1) + off), M["top"], Kk, 0.008)
    parent_to_bone(o, rig, "DEF-spine.001" if "DEF-spine.001" in bones else chest)
    for s in ("L", "R"):
        fb = f"DEF-forearm.{s}.001" if f"DEF-forearm.{s}.001" in bones else f"DEF-forearm.{s}"
        wr = B(f"ORG-hand.{s}")
        o = simple_object(sc, f"{who}_tape{s}", xform(capsule(17.5 * K, 16 * K), loc=wr + Vector((0, 0, 0.05))), M["white"], Kk, 0.006)
        parent_to_bone(o, rig, fb)
        an = B(f"ORG-foot.{s}")
        o = simple_object(sc, f"{who}_shoe{s}", xform(ellipsoid(30 * K, 52 * K, 20 * K), loc=an + Vector((0, -26 * K, -20 * K))), M["shoe"], Kk, LINE)
        parent_to_bone(o, rig, f"DEF-foot.{s}" if f"DEF-foot.{s}" in bones else f"ORG-foot.{s}")
        o = simple_object(sc, f"{who}_sole{s}", xform(ellipsoid(32 * K, 54 * K, 8 * K), loc=an + Vector((0, -26 * K, -36 * K))), M["sole"], Kk, 0.009)
        parent_to_bone(o, rig, f"DEF-foot.{s}" if f"DEF-foot.{s}" in bones else f"ORG-foot.{s}")
        o = simple_object(sc, f"{who}_sock{s}", xform(capsule(19 * K, 14 * K), loc=an + Vector((0, 0, 0.03))), M["white"], Kk, 0.008)
        parent_to_bone(o, rig, f"DEF-shin.{s}.001" if f"DEF-shin.{s}.001" in bones else f"DEF-shin.{s}")
    for o in sc.objects:
        if o.type == "MESH" and any(t in o.name for t in ("_hair", "_nape", "_string", "_pocket")):
            o.visible_shadow = False
    rig["who"] = who
    R = dict(rig=rig, eyes=eyes, brows=brows, face=face_layers, S=S, sc=sc)
    set_face(R, S["exprs"][0])
    info["total_s"] = round(time.time() - t0, 1)
    R["info"] = info
    return R


# ------------------------------------------------------------------ animation controls
def set_face(R, expr, frame=None, look=None, blink=None):
    S = R["S"]
    fe = S["face_expr"].get(expr, {})
    for k, o in R["face"].items():
        if k.startswith("mouth_"):
            o.hide_render = o.hide_viewport = (k != f"mouth_{expr}")
            if frame is not None:
                o.keyframe_insert("hide_render", frame=frame)
    lx, ly = look if look is not None else fe.get("look", (0, 0))
    for s, o in R["eyes"].items():
        o["look_x"], o["look_z"] = lx * K, -ly * K
        kb = o.data.shape_keys.key_blocks
        kb["blink"].value = blink if blink is not None else min(1.0, fe.get("lid", 0) * 1.6)
        kb["squint"].value = fe.get("squint", 0) * 1.6
        kb["wide"].value = fe.get("wide", 0)
        if frame is not None:
            o.keyframe_insert('["look_x"]', frame=frame); o.keyframe_insert('["look_z"]', frame=frame)
            for n in ("blink", "squint", "wide"):
                kb[n].keyframe_insert("value", frame=frame)
    for s, o in R["brows"].items():
        sx = 1 if s == "L" else -1
        rest = Vector(o["rest"])
        o.location = rest + Vector((0, 0, -fe.get("raise_", 0) * K))
        o.rotation_euler = (0, math.radians(-sx * fe.get("ang", 0) * 1.2), 0)
        if frame is not None:
            o.keyframe_insert("location", frame=frame); o.keyframe_insert("rotation_euler", frame=frame)


def fk(R):
    rig = R["rig"]
    for s in ("L", "R"):
        for n in (f"upper_arm_parent.{s}", f"thigh_parent.{s}"):
            if n in rig.pose.bones and "IK_FK" in rig.pose.bones[n]:
                rig.pose.bones[n]["IK_FK"] = 1.0


def rot(R, bone, x=0, y=0, z=0, frame=None):
    pb = R["rig"].pose.bones[bone]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))
    if frame is not None:
        pb.keyframe_insert("rotation_euler", frame=frame)


def demo_rig(who="gabby"):
    R = build_rigged(who)
    sc = R["sc"]
    sun(sc, rot=(56, 0, -34), energy=4)
    camera(sc, (1.3, -8.5, 2.0), (0, 0, 1.6), lens=40)
    fk(R)
    out = {"info": R["info"]}
    out["rest"] = render_still(sc, os.path.join(OUT, f"rig_{who}_rest.png"))
    # bend test: arms up in the salute (shoulders), elbows bent, one knee bent, head tilt, look + squint
    for s, sx in (("L", 1), ("R", -1)):
        rot(R, f"upper_arm_fk.{s}", 0, 0, sx * 140)
        rot(R, f"forearm_fk.{s}", 30, 0, 0)
    rot(R, "thigh_fk.L", -40, 0, 0); rot(R, "shin_fk.L", 70, 0, 0)
    rot(R, "head", 0, 0, 12) if "head" in R["rig"].pose.bones else None
    set_face(R, "grin", look=(8, -2))
    out["pose"] = render_still(sc, os.path.join(OUT, f"rig_{who}_pose.png"))
    set_face(R, "whoa", look=(-6, 2))
    out["whoa"] = render_still(sc, os.path.join(OUT, f"rig_{who}_whoa.png"))
    return out
