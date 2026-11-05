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
          kurta=("#2f8f8c", "#1e6462"), buti="#f4efe2", jeans=("#4d6ea6", "#344d7d"), shoe=("#f4f3ee", "#c6c4bb"))
GB = dict(skin=("#a46f4b", "#774d31"), palm=("#c38f69", "#926242"), hair=("#17121a", "#0b080d"), shine="#5d6b8a",
          shirt=("#24345e", "#151f3c"), leaf="#dfe7f2", shorts=("#9fb1c6", "#6f8299"), tape="#f4f4ee", band="#e9d27a",
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


def shirley_head(S, x, y, s=1.0, expr="calm", lw=4.5):
    c, e = SH, SH_EXPR[expr]
    g_open(S, x, y, s)
    bob = "M-100,-104 C-110,-190 110,-190 100,-104 C108,-46 108,14 102,62 Q56,76 0,74 Q-56,76 -102,62 C-108,14 -108,-46 -100,-104 Z"
    cel(S, bob, *c["hair"], -10, -8, lw)
    for sx in (-1, 1):  # small ears just peeking out of the bob
        cel(S, ell(84 * sx, 0, 11, 19), *c["skin"], -3 * sx, -3, lw)
    cel(S, FACE_SH, *c["skin"], -12, -10, lw)
    S.add(f'<path d="{ell(-46, 34, 18, 10)}" fill="#c4505c" opacity="0.16"/><path d="{ell(46, 34, 18, 10)}" fill="#c4505c" opacity="0.16"/>')
    for sx in (-1, 1):  # bob side panels
        cel(S, f"M{-94 * sx},-104 L{-74 * sx},-104 C{-76 * sx},-60 {-80 * sx},-24 {-82 * sx},-10 C{-84 * sx},20 {-88 * sx},40 {-92 * sx},62 L{-104 * sx},62 "
               f"C{-108 * sx},14 {-106 * sx},-50 {-94 * sx},-104 Z", *c["hair"], -4 * sx, -4, lw)
    # wispy fringe down to the brows
    tips = [(-82, -62), (-66, -54), (-50, -64), (-34, -52), (-18, -66), (-2, -54), (14, -66), (30, -54), (46, -64), (62, -52), (78, -62), (90, -80)]
    d = "M-94,-104 C-94,-156 -46,-174 0,-174 C46,-174 94,-156 94,-104 " + " ".join(
        f"L{tx},{ty} L{tx - 8},{ty - 13}" for tx, ty in reversed(tips)) + " Z"
    cel(S, d, *c["hair"], -8, -6, lw)
    for x0 in (-56, -18, 18, 56):
        line(S, f"M{x0 * 0.8},-158 Q{x0},-124 {x0 + 4},-76", 2, c["hair"][1])
    line(S, "M-52,-156 C-22,-168 22,-168 52,-156", 3, c["shine"], 0.9)
    flower(S, -60, -124, 22)
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


def gabby_head(S, x, y, s=1.0, expr="grin", lw=4.5):
    c, e = GB, GB_EXPR[expr]
    g_open(S, x, y, s)
    for sx in (-1, 1):
        cel(S, ell(89 * sx, -6, 19, 29), *c["skin"], -6 * sx, -4, lw)
        line(S, f"M{84 * sx},-18 Q{97 * sx},-6 {86 * sx},12", 3, INK, 0.7)
    cel(S, FACE_GB, *c["skin"], -14, -10, lw)
    if e["mouth"] == "grin":  # cheeks bunch up when he smiles
        line(S, "M-56,40 q-5,6 -2,12 M56,40 q5,6 2,12", 2.4, INK, 0.5)  # smile dimples
    hair = ("M-86,-74 C-99,-156 -36,-196 9,-188 C68,-182 103,-148 86,-74 "
            "L76,-84 Q65,-104 52,-88 Q40,-110 25,-92 Q11,-114 -5,-94 Q-22,-112 -36,-92 Q-50,-108 -65,-88 Q-77,-102 -86,-74 Z")
    cel(S, hair, *c["hair"], -8, -6, lw)
    for d in ("M-60,-156 q10,-14 24,-6", "M-20,-172 q12,-12 26,-2", "M24,-166 q12,-10 24,0", "M58,-146 q10,-8 18,4", "M-84,-116 q6,-12 18,-8"):
        line(S, d, 3, c["shine"], 0.85)
    for sx in (-1, 1):
        fill(S, f"M{76 * sx},-88 L{88 * sx},-82 C{90 * sx},-62 {86 * sx},-48 {81 * sx},-40 C{79 * sx},-58 {78 * sx},-72 {76 * sx},-88 Z", c["hair"][0], lw=2)
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
    # fitted kurti: shaped at the waist, slight flare to mid-thigh, side slits
    kurti = ("M-46,146 C-66,150 -80,160 -82,190 C-84,236 -74,270 -66,300 C-70,350 -80,400 -88,466 "
             "L88,466 C80,400 70,350 66,300 C74,270 84,236 82,190 C80,160 66,150 46,146 Z")
    cid = cel(S, kurti, *c["kurta"], -12, -8, lw)
    pid = S.uid("buti")
    S.defs.append(f'<pattern id="{pid}" width="26" height="26" patternUnits="userSpaceOnUse">'
                  + "".join(f'<circle cx="{13 + 3.2 * math.cos(math.radians(90 * k))}" cy="{13 + 3.2 * math.sin(math.radians(90 * k))}" r="2.4" fill="{c["buti"]}"/>' for k in range(4))
                  + f'<circle cx="0" cy="0" r="1.6" fill="{c["buti"]}"/><circle cx="26" cy="26" r="1.6" fill="{c["buti"]}"/></pattern>')
    S.add(f'<g clip-path="url(#{cid})"><path d="{kurti}" fill="url(#{pid})" opacity="0.85"/>'
          f'<rect x="-100" y="440" width="200" height="30" fill="{c["gold"][0]}"/>'
          + "".join(f'<path d="M{-90 + 14 * i},455 l5,-7 l5,7 l-5,7 Z" fill="{c["yoke"][0]}"/>' for i in range(14)) + "</g>")
    S.add(f'<path d="{kurti}" fill="none" stroke="{INK}" stroke-width="{lw}" stroke-linejoin="round"/>')
    for sx in (-1, 1):  # side slits
        fill(S, f"M{74 * sx},410 L{84 * sx},464 L{64 * sx},464 Z", c["jeans"][0], lw=3)
    line(S, "M-64,300 Q0,312 64,300", 2, INK, 0.35)  # waist shaping
    for d in ("M-40,320 q-6,60 -14,130", "M40,320 q6,60 14,130"):
        line(S, d, 2, INK, 0.3)
    # mandarin collar + short placket with gold buttons and piping
    cel(S, "M-26,136 L26,136 L28,156 L-28,156 Z", *c["kurta"], -3, -3, 3.5)
    line(S, "M-28,156 L28,156", 3, c["gold"][0])
    line(S, "M0,156 L0,226", 3, c["gold"][0])
    line(S, "M0,156 L0,226", 1, INK, 0.5)
    for by in (172, 192, 212):
        fill(S, ell(6, by, 3.5, 3.5), c["gold"][0], lw=1.4)
    # 3/4 sleeves; screen-left arm relaxed with a gold bangle, screen-right hand on hip
    hose(S, [(-70, 166), (-90, 290)], 34, c["kurta"][0], lw)
    line(S, "M-108,286 L-72,290", 4, c["gold"][0])
    hose(S, [(-90, 296), (-96, 420)], 26, c["skin"][0], lw)
    line(S, "M-112,412 Q-96,420 -80,412", 7, INK)
    line(S, "M-112,412 Q-96,420 -80,412", 4, c["gold"][0])
    S.add('<g transform="translate(-96,428) rotate(180) scale(0.58)">')
    gs.hand_open(S, 0.5, False)
    S.add("</g>")
    hose(S, [(70, 166), (134, 266)], 34, c["kurta"][0], lw)
    line(S, "M120,280 L150,256", 4, c["gold"][0])
    hose(S, [(136, 272), (84, 318)], 26, c["skin"][0], lw)
    S.add('<g transform="translate(84,320) rotate(-120) scale(0.56)">')
    gs.hand_fist(S)
    S.add("</g>")
    g_close(S)


def gabby_body(S, x, y, s=1.0, lw=4.5, salute=True):
    """gymnast 'ta-da' salute: arms up in a V, chest out, open palms; chalky hands + wrist tape"""
    c = GB
    skin_hands(c)
    g_open(S, x, y, s)
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
    # leaf-print navy shirt (short sleeves), chest out
    shirt = "M-50,128 C-80,132 -96,148 -100,184 C-106,244 -102,300 -96,356 L96,356 C102,300 106,244 100,184 C96,148 80,132 50,128 Z"
    cid = cel(S, shirt, *c["shirt"], -14, -8, lw)
    pid = S.uid("leaf")
    S.defs.append(f'<pattern id="{pid}" width="46" height="46" patternUnits="userSpaceOnUse" patternTransform="rotate(18)">'
                  f'<path d="M6,30 C10,14 26,8 34,10 C30,22 20,32 6,30 Z" fill="{c["leaf"]}" opacity="0.9"/>'
                  f'<path d="M8,29 L30,12" stroke="{c["shirt"][0]}" stroke-width="1.5"/>'
                  f'<path d="M28,44 C30,36 38,32 44,34 C42,40 36,44 28,44 Z" fill="{c["leaf"]}" opacity="0.7"/></pattern>')
    S.add(f'<g clip-path="url(#{cid})"><path d="{shirt}" fill="url(#{pid})"/></g>')
    S.add(f'<path d="{shirt}" fill="none" stroke="{INK}" stroke-width="{lw}" stroke-linejoin="round"/>')
    for sx in (-1, 1):
        cel(S, f"M{-48 * sx},126 L{-6 * sx},168 L{-30 * sx},178 L{-58 * sx},150 Z", *c["shirt"], -3, -3, 3.5)
    line(S, "M0,168 L0,352", 2.5, INK, 0.7)
    for by in (200, 240, 280, 320):
        fill(S, ell(6, by, 4, 4), "#e8ecf2", lw=1.5)
    if salute:
        for sx in (-1, 1):
            sh, el, wr = (74 * sx, 160), (124 * sx, 40), (160 * sx, -80)
            hose(S, [sh, el, wr], 32, c["skin"][0], lw)
            ang = math.degrees(math.atan2(el[0] - sh[0], -(el[1] - sh[1])))
            S.add(f'<g transform="translate({sh[0]},{sh[1]}) rotate({ang:.1f})">')
            cel(S, "M-34,14 C-38,-20 -30,-50 -26,-62 L26,-62 C30,-50 38,-20 34,14 Z", *c["shirt"], -4, -4, lw)
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
    text(S, 64, 122, "comic-style teen redesign · v2", 24, 500, "#5a4a3c")
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
