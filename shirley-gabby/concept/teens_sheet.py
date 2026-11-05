"""Shirley & Gabby - comic-style TEEN redesign (v1).
Both are teens now: Shirley (~16, the sensible elder sister) and Gabby (~14, a gymnastics freak).
Comic look: bold ink, flat colour, halftone-dot shadows, panels with halftone backgrounds, caption boxes.
Reuses the drawing kit + organic hands from gabby_sheet.
    python3 teens_sheet.py  ->  teens_sheet.svg / teens_sheet.png
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gabby_sheet as gs
from gabby_sheet import SVG, g_open, g_close, cel, line, fill, ell, hose, text, _digit, _smooth, INK

gs.HALFTONE = True
W_, BG = "#fbfaf4", "#f4eee2"
SH = dict(skin=("#8c5b3d", "#5f3c27"), palm=("#ad7653", "#7d5136"), hair=("#17121a", "#0b080d"), shine="#5d6b8a",
          clip=("#3fae5a", "#24803c"), kurti=("#f2c43c", "#c4952a"), band1="#e8697a", band2="#4caf6a", band3="#e9893a",
          yoke=("#c8323e", "#8e1f2a"), pants=("#3e7a46", "#275230"), gold=("#ecc65e", "#b48c2c"), silver=("#d9dde3", "#9aa1ab"),
          lips="#6e3a2e", sandal=("#c9893c", "#8f5e24"), iris="#3e2416",
          kurta=("#2f8f8c", "#1e6462"), buti="#f4efe2", zh=("#b583c9", "#83579a"), zh_dk="#9b6bb0", tee="#f6f3ec", jeans=("#4d6ea6", "#344d7d"), shoe=("#f4f3ee", "#c6c4bb"))
GB = dict(skin=("#a46f4b", "#774d31"), palm=("#c38f69", "#926242"), hair=("#17121a", "#0b080d"), shine="#5d6b8a",
          shirt=("#24345e", "#151f3c"), leaf="#dfe7f2", hood=("#e5483b", "#ad2f28"), hood_dk="#c23a31", shorts=("#9fb1c6", "#6f8299"), tape="#f4f4ee", band="#e9d27a",
          shoe=("#f2f1ea", "#c3c1b8"), sole="#d84a3c", iris="#3e2416", mouth="#3b1519", tongue="#d0625b")


def skin_hands(c):
    gs.P["skin"], gs.P["palm"] = c["skin"], c["palm"]


# ------------------------------------------------------------------ faces (origin = face centre), proportions from the reference
# Shirley: longer oval face tapering to a small soft chin. Gabby: rounder, full cheeks, big forehead, prominent ears.
FACE_SH = ("M-80,-98 C-86,-162 86,-162 80,-98 C90,-46 88,8 76,46 C62,88 32,118 0,122 "
           "C-32,118 -62,88 -76,46 C-88,8 -90,-46 -80,-98 Z")
# round like the reference but lean (fitness freak): widest at the eyes, clean taper to the chin, no puffy cheeks
FACE_GB = ("M-84,-96 C-91,-164 91,-164 84,-96 C93,-58 93,-8 83,32 C71,78 40,106 0,108 "
           "C-40,106 -71,78 -83,32 C-93,-8 -93,-58 -84,-96 Z")
FACE = FACE_GB


def almond(cx, cy, rx, ry, squint=0.0):
    """almond eye outline; squint pushes the lower lid up (smiling eyes)"""
    lo = ry * (0.9 - 1.1 * squint)
    return (f"M{cx - rx},{cy + 2} C{cx - rx * 0.6},{cy - ry * 1.25} {cx + rx * 0.55},{cy - ry * 1.3} {cx + rx},{cy - 2} "
            f"C{cx + rx * 0.6},{cy + lo} {cx - rx * 0.6},{cy + lo} {cx - rx},{cy + 2} Z")


def eye(S, c, cx, cy=-6, rx=27, ry=19, look=(0, 0), lid=0.0, squint=0.0, lashes=False, spiral=False, wide=False):
    if wide:
        ry *= 1.45
    d = almond(cx, cy, rx, ry, squint)
    cid = S.uid()
    S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    S.add(f'<path d="{d}" fill="{W_}"/>')
    S.add(f'<g clip-path="url(#{cid})">')
    if spiral:
        pts = " ".join(f"{cx + 1.5 * t * math.cos(t):.1f},{cy - 4 + 1.5 * t * math.sin(t):.1f}" for t in [k * 0.35 for k in range(36)])
        S.add(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="3"/>')
    else:
        lx, ly = look
        ir = ry * 0.74 if not wide else ry * 0.5
        S.add(f'<path d="{ell(cx + lx, cy - 2 + ly, ir, ir + 1)}" fill="{c["iris"]}"/>')
        S.add(f'<path d="{ell(cx + lx, cy - 2 + ly, ir * 0.5, ir * 0.55)}" fill="{INK}"/>')
        S.add(f'<path d="{ell(cx + lx - 5, cy - 7 + ly, 3.8, 4.2)}" fill="#fff"/><path d="{ell(cx + lx + 5, cy + 4 + ly, 1.8, 1.8)}" fill="#fff"/>')
    if lid:
        yl = cy - ry * 1.1 + 2 * ry * lid
        S.add(f'<path d="M{cx - 40},{cy - 60} L{cx + 40},{cy - 60} L{cx + 40},{yl} L{cx - 40},{yl} Z" fill="{c["skin"][0]}"/>')
        line(S, f"M{cx - 40},{yl} L{cx + 40},{yl}", 4.5)
    S.add("</g>")
    S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>')
    if not lid:  # heavier upper lid line
        line(S, f"M{cx - rx},{cy + 2} C{cx - rx * 0.6},{cy - ry * 1.25} {cx + rx * 0.55},{cy - ry * 1.3} {cx + rx},{cy - 2}", 5.5)
    sd = 1 if cx > 0 else -1
    line(S, f"M{cx - rx * 0.7},{cy - ry * 1.55} Q{cx},{cy - ry * 1.9} {cx + rx * 0.75},{cy - ry * 1.45}", 1.8, INK, 0.4)  # lid crease
    if squint:
        line(S, f"M{cx - rx * 0.6},{cy + ry * 1.2} Q{cx},{cy + ry * 0.9} {cx + rx * 0.6},{cy + ry * 1.2}", 2.2, INK, 0.5)  # cheek push
    if lashes:
        for k in range(3):
            bx = cx + sd * rx * (0.45 + 0.2 * k)
            by = cy - ry * (0.95 - 0.35 * k)
            line(S, f"M{bx:.1f},{by:.1f} l{6 * sd},{-6}", 2.4)


def brows(S, c, raise_=0, ang=0, thick=7, y0=-48, xo=62):
    for sx in (-1, 1):
        xi, xe = 12 * sx, xo * sx
        yi, ye = y0 + raise_ + ang, y0 + 4 + raise_ - ang * 0.4
        d = (f"M{xi},{yi - thick / 2} Q{(xi + xe) / 2},{min(yi, ye) - 12} {xe},{ye - 1} "
             f"L{xe + 2 * sx},{ye + 2} Q{(xi + xe) / 2},{min(yi, ye) - 4} {xi},{yi + thick / 2} Z")
        fill(S, d, c["hair"][0], lw=1.6)


def nose(S, c, w=1.0, y=0):
    d = f"M{-3 * w},{6 + y} C{-5 * w},{20 + y} {-13 * w},{24 + y} {-11 * w},{33 + y} C{-7 * w},{40 + y} {7 * w},{40 + y} {11 * w},{33 + y}"
    cel(S, f"M{-3 * w},{6 + y} C{-5 * w},{20 + y} {-13 * w},{24 + y} {-11 * w},{33 + y} C{-7 * w},{40 + y} {7 * w},{40 + y} {11 * w},{33 + y} "
           f"C{13 * w},{24 + y} {5 * w},{20 + y} {3 * w},{6 + y} Z", *c["skin"], -3, -3, 0, stroke=False)
    line(S, d, 3.2)
    line(S, f"M{-8 * w},{33 + y} Q{-5 * w},{29 + y} {-2 * w},{34 + y} M{2 * w},{34 + y} Q{5 * w},{29 + y} {8 * w},{33 + y}", 2)


# ---------------- Shirley's head: short bob, wispy fringe, green flower clip
SH_EXPR = {"calm": dict(raise_=0, ang=0, look=(2, 1), mouth="soft"),
           "unimpressed": dict(raise_=4, ang=-2, lid=0.45, look=(6, 2), mouth="flat"),
           "surprised": dict(raise_=-12, ang=-4, look=(0, -1), mouth="o", wide=True),
           "smile": dict(raise_=-3, ang=-3, look=(0, 1), mouth="smile", squint=0.25)}


def flower(S, x, y, r=16):
    for k in range(5):
        a = math.radians(-90 + 72 * k)
        cel(S, ell(x + r * 0.62 * math.cos(a), y + r * 0.62 * math.sin(a), r * 0.55, r * 0.55), *SH["clip"], -2, -2, 2.5)
    fill(S, ell(x, y, r * 0.32, r * 0.32), "#f6e27a", lw=2)


def sh_back_base(S, c, lw):
    bob = "M-100,-104 C-110,-190 110,-190 100,-104 C108,-46 108,14 102,62 Q56,76 0,74 Q-56,76 -102,62 C-108,14 -108,-46 -100,-104 Z"
    cel(S, bob, *c["hair"], -10, -8, lw)


def sh_front_base(S, c, lw):
    for sx in (-1, 1):  # bob side panels
        cel(S, f"M{-94 * sx},-104 L{-74 * sx},-104 C{-76 * sx},-60 {-80 * sx},-24 {-82 * sx},-10 C{-84 * sx},20 {-88 * sx},40 {-92 * sx},62 L{-104 * sx},62 "
               f"C{-108 * sx},14 {-106 * sx},-50 {-94 * sx},-104 Z", *c["hair"], -4 * sx, -4, lw)
    tips = [(-82, -62), (-66, -54), (-50, -64), (-34, -52), (-18, -66), (-2, -54), (14, -66), (30, -54), (46, -64), (62, -52), (78, -62), (90, -80)]
    d = "M-94,-104 C-94,-156 -46,-174 0,-174 C46,-174 94,-156 94,-104 " + " ".join(
        f"L{tx},{ty} L{tx - 8},{ty - 13}" for tx, ty in reversed(tips)) + " Z"
    cel(S, d, *c["hair"], -8, -6, lw)
    for x0 in (-56, -18, 18, 56):
        line(S, f"M{x0 * 0.8},-158 Q{x0},-124 {x0 + 4},-76", 2, c["hair"][1])
    line(S, "M-52,-156 C-22,-168 22,-168 52,-156", 3, c["shine"], 0.9)
    flower(S, -60, -124, 22)


STREAK = "#7a2a3e"


def sh_back_angled(S, c, lw):
    d = ("M-102,-104 C-112,-192 112,-192 102,-104 C110,-46 116,0 114,40 L104,58 L98,48 L92,76 L80,62 "
         "L-80,62 L-92,76 L-98,48 L-104,58 L-114,40 C-116,0 -110,-46 -102,-104 Z")
    cel(S, d, *c["hair"], -10, -8, lw)


def sh_front_angled(S, c, lw):
    """angled bob: longer at the face, piecey ends, deep side-swept fringe, burgundy streak"""
    cel(S, "M-98,-84 C-104,-30 -100,20 -96,64 L-80,80 L-84,60 C-82,20 -80,-30 -84,-72 Z", *c["hair"], -3, -3, lw)
    cel(S, "M100,-100 C106,-40 104,20 98,62 L82,78 L86,58 C86,20 84,-40 86,-96 Z", *c["hair"], 3, -3, lw)
    line(S, "M95,-86 C99,-30 97,20 92,60", 7, STREAK, 0.95)
    cel(S, "M34,-176 C72,-172 98,-146 100,-100 L86,-96 C82,-124 64,-140 40,-146 Z", *c["hair"], -4, -4, lw)
    fr = "M34,-176 C-20,-176 -78,-150 -100,-80 L-90,-56 C-84,-80 -70,-92 -52,-96 C-30,-98 -6,-104 14,-114 C24,-118 32,-124 40,-134 Z"
    cel(S, fr, *c["hair"], -6, -6, lw)
    for d in ("M28,-166 C-10,-160 -50,-140 -82,-88", "M18,-148 C-10,-140 -40,-122 -62,-98", "M30,-140 C10,-126 -10,-114 -30,-104"):
        line(S, d, 2, c["hair"][1])
    line(S, "M10,-170 C-30,-166 -60,-150 -76,-126", 6, STREAK, 0.9)
    line(S, "M60,-160 C76,-150 86,-136 90,-118", 3, c["shine"], 0.9)
    flower(S, 64, -136, 15)


def sh_back_lob(S, c, lw):
    d = ("M-104,-104 C-114,-194 114,-194 104,-104 C112,-40 118,40 116,118 Q104,134 90,126 Q74,140 60,128 "
         "L-60,128 Q-74,140 -90,126 Q-104,134 -116,118 C-118,40 -112,-40 -104,-104 Z")
    cid = cel(S, d, *c["hair"], -10, -8, lw)
    S.add(f'<g clip-path="url(#{cid})"><rect x="-130" y="96" width="260" height="60" fill="#6a3a2c" opacity="0.35"/></g>')  # soft warm ends


def sh_front_lob(S, c, lw):
    """shoulder-length lob with curtain bangs and soft waves"""
    for sx in (-1, 1):
        cel(S, f"M{-100 * sx},-8 C{-110 * sx},30 {-98 * sx},60 {-106 * sx},96 C{-110 * sx},112 {-104 * sx},124 {-96 * sx},132 L{-82 * sx},126 "
               f"C{-90 * sx},110 {-84 * sx},90 {-86 * sx},60 C{-88 * sx},30 {-82 * sx},10 {-84 * sx},-12 Z", *c["hair"], -3 * sx, -3, lw)
        S.add(f'<path d="M{-104 * sx},100 C{-108 * sx},114 {-102 * sx},124 {-96 * sx},132 L{-82 * sx},126 C{-88 * sx},116 {-86 * sx},106 {-86 * sx},96 Z" fill="#6a3a2c" opacity="0.5"/>')
        cel(S, f"M{2 * sx},-174 C{-40 * sx},-172 {-80 * sx},-142 {-92 * sx},-92 C{-96 * sx},-60 {-98 * sx},-32 {-102 * sx},-6 L{-84 * sx},-10 "
               f"C{-82 * sx},-34 {-66 * sx},-54 {-40 * sx},-62 C{-22 * sx},-70 {-8 * sx},-96 {2 * sx},-128 Z", *c["hair"], -5 * sx, -5, lw)
        for k in range(3):  # swooping curtain strands
            line(S, f"M{(-6 - 8 * k) * sx},{-166 + 6 * k} C{(-40 - 6 * k) * sx},{-150 + 6 * k} {(-64 - 4 * k) * sx},{-118 + 8 * k} {(-80 - 3 * k) * sx},{-60 + 10 * k}", 2.2, "#3a3040")
        line(S, f"M{-24 * sx},-168 C{-50 * sx},-162 {-70 * sx},-148 {-80 * sx},-128", 3, c["shine"], 0.8)
    line(S, "M0,-180 L2,-128", 3, INK)  # centre parting


def sh_back_halfup(S, c, lw):
    cel(S, gs.fuzzy(0, -198, 38, 12, 0.06), *c["hair"], -6, -6, lw)  # mini bun
    for k in range(8):
        a = math.pi * 2 * k / 8
        S.add(f'<path d="{ell(30 * math.cos(a), -166 + 8 * math.sin(a), 9, 7)}" fill="{SH["kurta"][0]}" stroke="{INK}" stroke-width="2.5"/>')
    d = ("M-102,-104 C-112,-192 112,-192 102,-104 C108,-46 110,14 106,56 Q112,70 122,64 Q110,82 96,72 "
         "L-96,72 Q-110,82 -122,64 Q-112,70 -106,56 C-110,14 -108,-46 -102,-104 Z")
    cel(S, d, *c["hair"], -10, -8, lw)


def sh_front_halfup(S, c, lw):
    """half-up mini bun with a teal scrunchie, wispy see-through fringe, face-framing tendrils, flicked ends"""
    for sx in (-1, 1):
        cel(S, f"M{-94 * sx},-104 L{-76 * sx},-104 C{-78 * sx},-60 {-82 * sx},-20 {-86 * sx},20 C{-88 * sx},40 {-92 * sx},56 {-100 * sx},70 "
               f"L{-108 * sx},58 C{-110 * sx},14 {-106 * sx},-50 {-94 * sx},-104 Z", *c["hair"], -4 * sx, -4, lw)
        line(S, f"M{-72 * sx},-100 C{-80 * sx},-60 {-70 * sx},-30 {-78 * sx},10", 2.6, c["hair"][0])
    tips = [(-70, -70), (-50, -82), (-30, -66), (-10, -84), (10, -68), (30, -84), (50, -70), (70, -84)]
    d = "M-88,-104 C-88,-156 -44,-176 0,-176 C44,-176 88,-156 88,-104 " + " ".join(
        f"L{tx},{ty} L{tx - 7},{ty - 16}" for tx, ty in reversed(tips)) + " Z"
    cel(S, d, *c["hair"], -8, -6, lw)
    line(S, "M-50,-160 C-20,-172 20,-172 50,-160", 3, c["shine"], 0.9)


SH_HAIR = {"base": (sh_back_base, sh_front_base), "angled": (sh_back_angled, sh_front_angled),
           "lob": (sh_back_lob, sh_front_lob), "halfup": (sh_back_halfup, sh_front_halfup)}
SH_STYLE = "base"


def shirley_head(S, x, y, s=1.0, expr="calm", lw=4.5, hair=None, features_only=False):
    """features_only=True draws just the face features (for 3D face decals)"""
    c, e = SH, SH_EXPR[expr]
    back, front = SH_HAIR[hair or SH_STYLE]
    if features_only:
        back = front = (lambda *a: None)
    g_open(S, x, y, s)
    back(S, c, lw)
    if not features_only:
        for sx in (-1, 1):  # small ears just peeking out of the bob
            cel(S, ell(84 * sx, 0, 11, 19), *c["skin"], -3 * sx, -3, lw)
        cel(S, FACE_SH, *c["skin"], -12, -10, lw)
    S.add(f'<path d="{ell(-46, 34, 18, 10)}" fill="#c4505c" opacity="0.16"/><path d="{ell(46, 34, 18, 10)}" fill="#c4505c" opacity="0.16"/>')
    front(S, c, lw)
    for sx in (-1, 1):
        eye(S, c, 37 * sx, -8, 30, 22, look=e["look"], lid=e.get("lid", 0), squint=e.get("squint", 0), lashes=True, wide=e.get("wide", False))
    brows(S, c, e["raise_"], e["ang"], 6, -46, 62)
    nose(S, c, 0.85, 4)
    m = e["mouth"]
    if m == "o":
        cel(S, ell(0, 74, 11, 14), "#3b1519", "#3b1519", 0, 0, 3.2)
    elif m == "flat":
        line(S, "M-17,72 Q0,74 17,70", 4)
    else:
        sm = 7 if m == "smile" else 3
        cel(S, f"M-22,68 Q0,{70 + sm + 9} 22,68 Q0,{70 + sm} -22,68 Z", c["lips"], c["lips"], 0, 0, 3)
        line(S, f"M-22,68 Q0,{64 - sm} 22,68", 3)
        line(S, f"M-26,65 q-3,3 0,7 M26,65 q3,3 0,7", 2, INK, 0.5)
    line(S, "M-10,96 Q0,100 10,96", 2, INK, 0.35)  # small chin
    g_close(S)


# ---------------- Gabby's head: round with full cheeks, big ears, short thick wavy hair, wide toothy smile
GB_EXPR = {"grin": dict(raise_=-6, ang=-4, look=(2, 0), mouth="grin", squint=0.35),
           "focus": dict(raise_=6, ang=12, look=(0, -1), mouth="tongue", lid=0.32),
           "dizzy": dict(raise_=-10, ang=-8, mouth="wobble", spiral=True),
           "whoa": dict(raise_=-16, ang=-6, look=(0, 0), mouth="o", wide=True)}


def gb_hair_base(S, c, lw):
    hair = ("M-86,-74 C-99,-156 -36,-196 9,-188 C68,-182 103,-148 86,-74 "
            "L76,-84 Q65,-104 52,-88 Q40,-110 25,-92 Q11,-114 -5,-94 Q-22,-112 -36,-92 Q-50,-108 -65,-88 Q-77,-102 -86,-74 Z")
    cel(S, hair, *c["hair"], -8, -6, lw)
    for d in ("M-60,-156 q10,-14 24,-6", "M-20,-172 q12,-12 26,-2", "M24,-166 q12,-10 24,0", "M58,-146 q10,-8 18,4", "M-84,-116 q6,-12 18,-8"):
        line(S, d, 3, c["shine"], 0.85)
    for sx in (-1, 1):
        fill(S, f"M{76 * sx},-88 L{88 * sx},-82 C{90 * sx},-62 {86 * sx},-48 {81 * sx},-40 C{79 * sx},-58 {78 * sx},-72 {76 * sx},-88 Z", c["hair"][0], lw=2)


def _fade(S, c, slit=False):
    """short faded sides: stubble-dots tint on the sides of the head, clipped to the head"""
    cid = S.uid()
    S.defs.append(f'<clipPath id="{cid}"><path d="{FACE_GB}"/></clipPath>')
    pid = S.uid("stub")
    S.defs.append(f'<pattern id="{pid}" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{c["hair"][0]}"/>'
                  f'<circle cx="5" cy="5" r="1" fill="{c["hair"][0]}"/></pattern>')
    band = "M-100,-130 L-62,-130 C-66,-100 -70,-70 -78,-44 L-100,-40 Z M100,-130 L62,-130 C66,-100 70,-70 78,-44 L100,-40 Z"
    S.add(f'<g clip-path="url(#{cid})"><path d="{band}" fill="{c["hair"][0]}" opacity="0.3"/><path d="{band}" fill="url(#{pid})" opacity="0.8"/></g>')
    if slit:
        line(S, "M66,-96 L80,-80 M70,-102 L84,-86", 3.2, c["skin"][0])


def gb_hair_curly(S, c, lw):
    """curly top + low fade + a shaved slit"""
    _fade(S, c, slit=True)
    pts = []
    for k in range(26):
        a = math.pi * (1.02 + 0.96 * k / 25)
        r = 1 + (0.09 if k % 2 else 0)
        pts.append((84 * r * math.cos(a), -112 + 92 * r * math.sin(a)))
    pts += [(78, -98), (64, -104), (50, -94), (36, -104), (20, -92), (4, -102), (-12, -92), (-28, -102), (-44, -92), (-60, -102), (-76, -96)]
    cel(S, _smooth(pts), *c["hair"], -8, -6, lw)
    for cx_, cy_ in ((-50, -160), (-14, -180), (24, -176), (56, -150), (-66, -128), (-30, -140), (8, -146), (44, -124), (-8, -116), (28, -112)):
        line(S, f"M{cx_ - 8},{cy_ + 4} a9,9 0 1 1 12,6", 2.6, c["shine"], 0.85)


def gb_hair_quiff(S, c, lw):
    """textured spiky quiff swept up and to the side, short faded sides"""
    _fade(S, c)
    d = ("M-80,-94 C-88,-146 -44,-184 6,-192 L22,-214 L32,-194 L56,-210 L56,-188 L84,-188 L74,-166 L92,-160 L80,-140 "
         "C88,-120 86,-104 80,-94 C50,-108 20,-112 -10,-110 C-40,-108 -62,-102 -80,-94 Z")
    cel(S, d, *c["hair"], -8, -6, lw)
    for dd in ("M-60,-120 C-40,-150 -10,-176 20,-206", "M-30,-114 C-10,-140 20,-166 50,-200", "M0,-112 C20,-136 50,-160 80,-180",
               "M30,-110 C50,-126 70,-142 86,-156"):
        line(S, dd, 2.2, c["hair"][1])
    line(S, "M-50,-150 C-30,-170 -6,-184 16,-190", 3, c["shine"], 0.85)


def gb_hair_curtain(S, c, lw):
    """messy middle-part curtain fringe, volume on top, sides over the ear tops"""
    d = ("M-90,-76 C-102,-160 -40,-202 0,-198 C40,-202 102,-160 90,-76 L80,-66 C74,-98 54,-112 30,-116 "
         "C18,-112 8,-104 2,-90 C-6,-104 -18,-112 -30,-116 C-54,-112 -74,-98 -80,-66 Z")
    cel(S, d, *c["hair"], -8, -6, lw)
    for sx in (-1, 1):
        line(S, f"M{-4 * sx},-186 C{-30 * sx},-170 {-60 * sx},-130 {-74 * sx},-80", 2.2, c["hair"][1])
        line(S, f"M{-2 * sx},-160 C{-20 * sx},-146 {-40 * sx},-130 {-52 * sx},-110", 2.2, c["hair"][1])
        fill(S, f"M{-86 * sx},-84 L{-96 * sx},-60 L{-84 * sx},-66 L{-90 * sx},-46 L{-76 * sx},-64 Z", c["hair"][0], lw=2)
        line(S, f"M{-20 * sx},-184 C{-44 * sx},-176 {-66 * sx},-150 {-76 * sx},-124", 3, c["shine"], 0.85)


GB_HAIR = {"base": gb_hair_base, "curly": gb_hair_curly, "quiff": gb_hair_quiff, "curtain": gb_hair_curtain}
GB_STYLE = "base"


def gabby_head(S, x, y, s=1.0, expr="grin", lw=4.5, hair=None, features_only=False):
    c, e = GB, GB_EXPR[expr]
    g_open(S, x, y, s)
    if not features_only:
        for sx in (-1, 1):
            cel(S, ell(89 * sx, -6, 19, 29), *c["skin"], -6 * sx, -4, lw)
            line(S, f"M{84 * sx},-18 Q{97 * sx},-6 {86 * sx},12", 3, INK, 0.7)
        cel(S, FACE_GB, *c["skin"], -14, -10, lw)
    if e["mouth"] == "grin":  # cheeks bunch up when he smiles
        line(S, "M-56,40 q-5,6 -2,12 M56,40 q5,6 2,12", 2.4, INK, 0.5)  # smile dimples
    if not features_only:
        GB_HAIR[hair or GB_STYLE](S, c, lw)
    for sx in (-1, 1):
        eye(S, c, 36 * sx, -12, 29, 22, look=e.get("look", (0, 0)), lid=e.get("lid", 0), squint=e.get("squint", 0),
            spiral=e.get("spiral", False), wide=e.get("wide", False))
    brows(S, c, e["raise_"], e["ang"], 9, -54, 62)
    nose(S, c, 1.25, 4)
    m = e["mouth"]
    if m == "grin":  # wide smile showing the upper teeth
        d = "M-43,52 Q0,61 43,52 Q36,86 0,88 Q-36,86 -43,52 Z"
        cid = S.uid(); S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        S.add(f'<path d="{d}" fill="{c["mouth"]}"/><g clip-path="url(#{cid})"><rect x="-60" y="48" width="120" height="22" fill="{W_}"/>'
              + "".join(f'<line x1="{x0}" y1="54" x2="{x0}" y2="70" stroke="{INK}" stroke-width="1.4" opacity="0.35"/>' for x0 in (-30, -10, 10, 30))
              + f'<path d="{ell(0, 92, 20, 13)}" fill="{c["tongue"]}"/></g>')
        S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
        line(S, "M-48,46 Q-52,54 -45,58 M48,46 Q52,54 45,58", 3)
    elif m == "tongue":
        line(S, "M-28,70 Q0,76 28,68", 5)
        cel(S, "M6,70 Q8,90 20,88 Q28,82 24,69 Z", c["tongue"], "#a84a44", -2, -2, 3)
    elif m == "wobble":
        line(S, "M-34,72 q8,-8 17,0 q8,8 17,0 q8,-8 17,0 q8,8 17,0", 4.5)
    else:
        cel(S, ell(0, 76, 16, 20), c["mouth"], c["mouth"], 0, 0, 4)
    g_close(S)


# ------------------------------------------------------------------ bodies (origin = face centre)
def shirley_body(S, x, y, s=1.0, lw=4.5):
    """modern fitted look: slim-cut teal kurti (mandarin collar, 3/4 sleeves, side slits, white buti print),
    slim jeans, white sneakers, gold bangle"""
    c = SH
    skin_hands(c)
    g_open(S, x, y, s)
    cel(S, "M-66,150 C-74,112 -36,100 0,102 C36,100 74,112 66,150 C46,162 -46,162 -66,150 Z", c["zh_dk"], c["zh"][1], -5, -5, lw)  # hood down
    cel(S, "M-20,108 L20,108 L22,156 L-22,156 Z", *c["skin"], -8, 10, lw)
    # slim jeans + sneakers
    for sx in (-1, 1):
        leg = (f"M{-4 * sx},420 L{-68 * sx},420 C{-70 * sx},520 {-62 * sx},620 {-56 * sx},700 L{-22 * sx},700 "
               f"C{-20 * sx},620 {-12 * sx},520 {-4 * sx},460 Z")
        cel(S, leg, *c["jeans"], -8 * sx, 0, lw)
        line(S, f"M{-40 * sx},470 C{-42 * sx},560 {-40 * sx},640 {-38 * sx},696", 1.8, INK, 0.35)
        line(S, f"M{-58 * sx},560 q{8 * sx},4 {16 * sx},0", 1.8, INK, 0.4)
        lx = -40 * sx
        cel(S, f"M{lx + 16 * sx},694 C{lx + 26 * sx},696 {lx + 30 * sx},712 {lx + 24 * sx},724 L{lx - 50 * sx},724 "
               f"C{lx - 58 * sx},712 {lx - 46 * sx},696 {lx - 26 * sx},694 Z", *c["shoe"], -3, -3, lw)
        fill(S, f"M{lx + 26 * sx},718 L{lx - 54 * sx},718 L{lx - 54 * sx},728 L{lx + 26 * sx},728 Z", "#d9d6cc", lw=2.5)
        line(S, f"M{lx - 18 * sx},704 l{-10 * sx},-3 M{lx - 16 * sx},710 l{-10 * sx},-3", 2, INK, 0.6)
    # fitted lilac zip hoodie (half-zipped over a white tee), ribbed hem at the hip
    zh = ("M-46,146 C-66,150 -80,160 -82,190 C-84,236 -74,270 -68,300 C-70,340 -74,380 -78,418 "
          "L78,418 C74,380 70,340 68,300 C74,270 84,236 82,190 C80,160 66,150 46,146 Z")
    cel(S, zh, *c["zh"], -12, -8, lw)
    fill(S, "M-26,146 L0,236 L26,146 Z", c["tee"], lw=3)  # tee showing in the open zip
    fill(S, "M-26,146 Q0,160 26,146", c["skin"][0], lw=0)
    line(S, "M-26,146 Q0,162 26,146", 3)
    S.add(f'<g transform="translate(0,196) scale(0.6)"><circle r="10" fill="none" stroke="{c["zh"][1]}" stroke-width="3"/>'
          f'<ellipse rx="22" ry="7" fill="none" stroke="{c["zh"][1]}" stroke-width="3" transform="rotate(-20)"/></g>')  # little planet print
    line(S, "M-26,146 L0,236 L26,146", 4)
    line(S, "M0,236 L0,414", 3, INK, 0.8)
    fill(S, "M-4,236 L4,236 L5,256 L-5,256 Z", "#d8d8de", lw=2)  # zip pull
    cel(S, "M-80,404 Q0,414 80,404 L78,428 Q0,436 -78,428 Z", c["zh_dk"], c["zh"][1], -4, -3, lw)
    for k in range(-4, 5):
        line(S, f"M{k * 17},410 L{k * 17},430", 1.5, c["zh"][1], 0.7)
    for sx in (-1, 1):
        line(S, f"M{20 * sx},150 C{22 * sx},180 {17 * sx},204 {22 * sx},226", 5.5, INK)
        line(S, f"M{20 * sx},150 C{22 * sx},180 {17 * sx},204 {22 * sx},226", 2.6, "#fbfaf4")
    line(S, "M-62,300 Q0,310 62,300", 2, INK, 0.35)
    # 3/4 sleeves; screen-left arm relaxed with a gold bangle, screen-right hand on hip
    hose(S, [(-70, 166), (-90, 290), (-95, 392)], 34, c["zh"][0], lw)  # full sleeve, ribbed cuff
    cel(S, "M-114,384 L-76,386 L-77,404 L-114,402 Z", c["zh_dk"], c["zh"][1], -2, -2, 3.5)
    hose(S, [(-95, 404), (-96, 420)], 24, c["skin"][0], lw)
    line(S, "M-112,412 Q-96,420 -80,412", 7, INK)
    line(S, "M-112,412 Q-96,420 -80,412", 4, c["gold"][0])
    S.add('<g transform="translate(-96,428) rotate(180) scale(0.58)">')
    gs.hand_open(S, 0.5, False)
    S.add("</g>")
    hose(S, [(70, 166), (134, 266), (96, 306)], 34, c["zh"][0], lw)
    cel(S, "M86,292 L108,318 L94,330 L74,304 Z", c["zh_dk"], c["zh"][1], -2, -2, 3.5)
    hose(S, [(90, 314), (84, 318)], 24, c["skin"][0], lw)
    S.add('<g transform="translate(84,320) rotate(-120) scale(0.56)">')
    gs.hand_fist(S)
    S.add("</g>")
    g_close(S)


def gabby_body(S, x, y, s=1.0, lw=4.5, salute=True):
    """gymnast 'ta-da' salute: arms up in a V, chest out, open palms; chalky hands + wrist tape"""
    c = GB
    skin_hands(c)
    g_open(S, x, y, s)
    cel(S, "M-80,150 C-90,108 -40,94 0,98 C40,94 90,108 80,150 C54,166 -54,166 -80,150 Z", c["hood_dk"], c["hood"][1], -6, -6, lw)  # hood down
    cel(S, "M-22,110 L22,110 L24,156 L-24,156 Z", *c["skin"], -8, 10, lw)
    # legs (skin), denim shorts, sneakers; band-aid on one knee
    for sx in (-1, 1):
        hose(S, [(38 * sx, 430), (42 * sx, 560), (40 * sx, 668)], 36, c["skin"][0], lw)
        lx = 40 * sx  # sneaker, toe pointing outward
        cel(S, f"M{lx - 14 * sx},690 C{lx - 26 * sx},692 {lx - 32 * sx},708 {lx - 26 * sx},722 L{lx + 60 * sx},722 "
               f"C{lx + 70 * sx},708 {lx + 56 * sx},692 {lx + 34 * sx},690 Z", *c["shoe"], -4, -3, lw)
        fill(S, f"M{lx - 28 * sx},716 L{lx + 64 * sx},716 L{lx + 64 * sx},726 L{lx - 28 * sx},726 Z", c["sole"], lw=2.5)
        line(S, f"M{40 * sx - 8},{700} l16,-4 M{40 * sx - 8},{706} l16,-4", 2.5, c["sole"])
        cel(S, f"M{40 * sx - 18},676 L{40 * sx + 18},676 L{40 * sx + 20},694 L{40 * sx - 20},694 Z", "#ffffff", "#d8d6cf", -2, -2, 3)  # sock
    fill(S, "M-50,548 L-30,544 L-28,560 L-48,564 Z", "#e9c98f", lw=2.5)  # band-aid
    line(S, "M-43,548 L-41,562 M-36,546 L-34,560", 1.5, INK, 0.5)
    shorts = "M-84,350 L84,350 C92,400 92,440 86,470 L8,470 L3,420 L-3,420 L-8,470 L-86,470 C-92,440 -92,400 -84,350 Z"
    cel(S, shorts, *c["shorts"], -10, 0, lw)
    for sx in (-1, 1):
        for k in range(5):
            line(S, f"M{(12 + 15 * k) * sx},470 l{3 * sx},8", 2, INK, 0.6)  # frayed hem
    line(S, "M-60,380 l10,0 M60,380 l-10,0", 2, INK, 0.4)
    S.add(f'<path d="{ell(-52, 420, 14, 11)}" fill="#ffffff" opacity="0.55"/><path d="{ell(56, 410, 12, 9)}" fill="#ffffff" opacity="0.5"/>')  # chalk handprints
    # sporty red hoodie (hood down), drawstrings, kangaroo pocket, ribbed hem
    hoodie = "M-50,128 C-80,132 -96,148 -100,184 C-106,244 -102,300 -98,350 L98,350 C102,300 106,244 100,184 C96,148 80,132 50,128 Z"
    cel(S, hoodie, *c["hood"], -14, -8, lw)
    cel(S, "M-100,340 Q0,350 100,340 L98,368 Q0,378 -98,368 Z", c["hood_dk"], c["hood"][1], -6, -3, lw)
    for k in range(-5, 6):
        line(S, f"M{k * 17},346 L{k * 17},372", 1.5, c["hood"][1], 0.7)
    pocket = "M-66,262 Q0,252 66,262 L78,334 Q0,342 -78,334 Z"
    cel(S, pocket, *c["hood"], -8, -5, lw)
    line(S, "M-66,262 L-78,334 M66,262 L78,334", 4.5)
    for sx in (-1, 1):
        line(S, f"M{16 * sx},146 C{18 * sx},180 {13 * sx},206 {18 * sx},234", 6, INK)
        line(S, f"M{16 * sx},146 C{18 * sx},180 {13 * sx},206 {18 * sx},234", 3, "#fbfaf4")
        fill(S, f"M{13 * sx},232 L{23 * sx},232 L{22 * sx},248 L{14 * sx},248 Z", "#c9c8bf", lw=2.2)
    for d in ("M-84,214 q-6,30 -2,60", "M84,214 q6,30 2,60", "M-40,190 q20,10 40,4"):
        line(S, d, 2.2, INK, 0.4)
    S.add(f'<path d="{ell(-30, 300, 12, 9)}" fill="#ffffff" opacity="0.5"/>')  # chalk smudge
    if salute:
        for sx in (-1, 1):
            sh, el, wr = (74 * sx, 160), (124 * sx, 40), (160 * sx, -80)
            hose(S, [sh, el, wr], 32, c["skin"][0], lw)
            ang = math.degrees(math.atan2(el[0] - sh[0], -(el[1] - sh[1])))
            S.add(f'<g transform="translate({sh[0]},{sh[1]}) rotate({ang:.1f})">')
            cel(S, "M-34,14 C-38,-20 -34,-80 -28,-112 L28,-112 C34,-80 38,-20 34,14 Z", *c["hood"], -4, -4, lw)  # sleeve pushed up
            cel(S, "M-30,-104 Q0,-110 30,-104 L32,-126 Q0,-134 -32,-126 Z", c["hood_dk"], c["hood"][1], -3, -3, 3.5)
            line(S, "M-20,-60 q8,6 16,0 M-16,-30 q8,6 16,0", 2, INK, 0.4)
            S.add("</g>")
            ang2 = math.degrees(math.atan2(wr[0] - el[0], -(wr[1] - el[1])))
            S.add(f'<g transform="translate({wr[0]},{wr[1]}) rotate({ang2:.1f})">')
            fill(S, "M-17,-6 L17,-6 L17,14 L-17,14 Z", c["tape"], lw=3)  # wrist tape
            line(S, "M-17,2 L17,2", 1.5, INK, 0.4)
            g_open(S, 0, -6, 0.66, 0)
            gs.hand_open(S, 1.05, True)
            g_close(S)
            S.add("</g>")
            for k in range(3):  # chalk puffs
                px, py = wr[0] + sx * (30 + 14 * k), wr[1] - 60 - 18 * k
                S.add(f'<path d="{gs.fuzzy(px, py, 9 - 2 * k, 8, 0.25)}" fill="#ffffff" opacity="0.8" stroke="{INK}" stroke-width="1.5"/>')
    g_close(S)


def handstand(S, x, y, s=0.42):
    """inset: Gabby in a handstand (whole figure flipped), with motion arcs"""
    g_open(S, x, y, s, 180)
    gabby_body(S, 0, 0, 1.0, 5, salute=False)
    for sx in (-1, 1):  # arms straight 'up' (= down to the floor when flipped)
        hose(S, [(74 * sx, 160), (90 * sx, 30), (98 * sx, -120)], 32, GB["skin"][0], 5)
        fill(S, f"M{98 * sx - 17},-124 L{98 * sx + 17},-124 L{98 * sx + 17},-104 L{98 * sx - 17},-104 Z", GB["tape"], lw=3)
        S.add(f'<g transform="translate({98 * sx},-124) scale(0.66)">')
        gs.hand_open(S, 0.7, False)
        S.add("</g>")
    gabby_head(S, 0, 0, 1.0, "focus", 5)
    g_close(S)


# ------------------------------------------------------------------ sheet
def halftone_bg(S, x, y, w, h, col, dot, burst=None):
    pid = S.uid("bg")
    S.defs.append(f'<pattern id="{pid}" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(20)">'
                  f'<circle cx="8" cy="8" r="3.4" fill="{dot}"/></pattern>')
    S.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})" opacity="0.55"/>')
    if burst:
        cx, cy, r0, r1, bc = burst
        pts = []
        for k in range(36):
            r = r1 if k % 2 == 0 else r0
            a = math.pi * 2 * k / 36
            pts.append(f"{cx + r * math.cos(a):.0f},{cy + r * math.sin(a):.0f}")
        cid = S.uid()
        S.defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
        S.add(f'<g clip-path="url(#{cid})"><polygon points="{" ".join(pts)}" fill="{bc}"/></g>')
    S.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="8"/>')


def caption(S, x, y, w, lines, col="#ffe36e"):
    h = 26 + 30 * len(lines)
    S.add(f'<rect x="{x + 6}" y="{y + 6}" width="{w}" height="{h}" fill="{INK}"/>')
    S.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" stroke="{INK}" stroke-width="4"/>')
    for i, (t, b) in enumerate(lines):
        text(S, x + 16, y + 36 + 30 * i, t, 22 if not b else 26, 800 if b else 500)


def sheet(path_svg):
    Wd, Ht = 2400, 1760
    S = SVG(Wd, Ht)
    S.add(f'<rect width="{Wd}" height="{Ht}" fill="{BG}"/>')
    text(S, 60, 84, "SHIRLEY &amp; GABBY", 64, 900)
    text(S, 64, 122, "comic-style teen redesign · v4 (hoodies)", 24, 500, "#5a4a3c")
    # panels
    halftone_bg(S, 40, 150, 1140, 1100, "#f6b2a6", "#e4877c")
    halftone_bg(S, 1220, 150, 1140, 1100, "#ffd84d", "#f2a93b", burst=(1790, 640, 300, 560, "#ffe98a"))
    shirley_body(S, 560, 440, 0.98)
    shirley_head(S, 560, 440, 0.98, "calm")
    S.add(f'<ellipse cx="560" cy="1158" rx="160" ry="16" fill="#000" opacity="0.12"/>')
    gabby_body(S, 1720, 440, 0.98)
    gabby_head(S, 1720, 440, 0.98, "grin")
    S.add(f'<ellipse cx="1730" cy="1172" rx="170" ry="16" fill="#000" opacity="0.12"/>')
    # handstand inset
    S.add(f'<rect x="2040" y="830" width="290" height="390" fill="#fff6c9" stroke="{INK}" stroke-width="5"/>')
    S.add(f'<rect x="2040" y="1150" width="290" height="70" fill="#e9d9a8"/><line x1="2040" y1="1150" x2="2330" y2="1150" stroke="{INK}" stroke-width="4"/>')
    handstand(S, 2185, 1084, 0.34)
    for k in range(3):
        line(S, f"M{2090 + 12 * k},{900 + 40 * k} q-18,30 0,60", 3, "#8a6a2a", 0.7)
    text(S, 2185, 1196, "can't pass a wall without this", 17, 800, INK, "middle")
    caption(S, 790, 1100, 360, [("SHIRLEY · 16", True), ("the sensible big sister", False), ("bob, fringe, flower clip", False)], "#ffffff")
    caption(S, 1250, 1100, 330, [("GABBY · 14", True), ("gymnastics freak", False), ("always upside down", False)])
    # expressions
    text(S, 60, 1310, "EXPRESSIONS", 30, 900)
    for i, k in enumerate(("calm", "unimpressed", "surprised", "smile")):
        cx = 150 + i * 270
        S.add(f'<rect x="{cx - 120}" y="1340" width="240" height="330" fill="#ffffff" stroke="{INK}" stroke-width="4"/>')
        shirley_head(S, cx, 1500, 0.8, k)
        text(S, cx, 1650, k, 22, 800, "#5a4a3c", "middle")
    for i, k in enumerate(("grin", "focus", "whoa", "dizzy")):
        cx = 1330 + i * 270
        S.add(f'<rect x="{cx - 120}" y="1340" width="240" height="330" fill="#ffffff" stroke="{INK}" stroke-width="4"/>')
        gabby_head(S, cx, 1500, 0.8, k)
        text(S, cx, 1650, {"focus": "before a flip", "whoa": "whoa!", "dizzy": "after a flip"}.get(k, k), 22, 800, "#5a4a3c", "middle")
    open(path_svg, "w").write(S.out())


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    svg = os.path.join(here, "teens_sheet.svg")
    sheet(svg)
    png = os.path.join(here, "teens_sheet.png")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 2400, "height": 1760})
        pg.goto("file://" + svg)
        pg.screenshot(path=png)
        b.close()
    print(png)
