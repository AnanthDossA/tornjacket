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
          lips="#6e3a2e", sandal=("#c9893c", "#8f5e24"), iris="#3e2416")
GB = dict(skin=("#93613f", "#66422a"), palm=("#b07a56", "#805338"), hair=("#17121a", "#0b080d"), shine="#5d6b8a",
          shirt=("#24345e", "#151f3c"), leaf="#dfe7f2", shorts=("#9fb1c6", "#6f8299"), tape="#f4f4ee", band="#e9d27a",
          shoe=("#f2f1ea", "#c3c1b8"), sole="#d84a3c", iris="#3e2416", mouth="#3b1519", tongue="#d0625b")


def skin_hands(c):
    gs.P["skin"], gs.P["palm"] = c["skin"], c["palm"]


# ------------------------------------------------------------------ faces (origin = face centre)
FACE = ("M-92,-84 C-98,-154 98,-154 92,-84 C102,-34 102,20 88,62 C74,102 40,122 0,124 "
        "C-40,122 -74,102 -88,62 C-102,20 -102,-34 -92,-84 Z")


def eye(S, c, cx, look=(0, 0), lid=0.0, lashes=False, spiral=False, ry=36, rx=28):
    cy = -12
    d = ell(cx, cy, rx, ry)
    cid = S.uid()
    S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    S.add(f'<path d="{d}" fill="{W_}"/>')
    S.add(f'<g clip-path="url(#{cid})">')
    if spiral:
        pts = " ".join(f"{cx + 1.7 * t * math.cos(t):.1f},{cy + 1.7 * t * math.sin(t):.1f}" for t in [k * 0.35 for k in range(40)])
        S.add(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="3"/>')
    else:
        lx, ly = look
        S.add(f'<path d="{ell(cx + lx, cy + 5 + ly, 16, 18)}" fill="{c["iris"]}"/>')
        S.add(f'<path d="{ell(cx + lx, cy + 5 + ly, 8, 9)}" fill="{INK}"/>')
        S.add(f'<path d="{ell(cx + lx - 6, cy - 2 + ly, 4.5, 5)}" fill="#fff"/><path d="{ell(cx + lx + 6, cy + 13 + ly, 2, 2)}" fill="#fff"/>')
    if lid:
        yl = cy - ry + 2 * ry * lid
        S.add(f'<path d="M{cx - 40},{cy - 60} L{cx + 40},{cy - 60} L{cx + 40},{yl} L{cx - 40},{yl} Z" fill="{c["skin"][0]}"/>')
        line(S, f"M{cx - 40},{yl} L{cx + 40},{yl}", 5)
    S.add("</g>")
    S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4"/>')
    if not lid:
        line(S, f"M{cx - rx + 3},{cy - 12} Q{cx},{cy - ry - 6} {cx + rx - 3},{cy - 12}", 5.5)
    if lashes:
        sd = 1 if cx > 0 else -1
        for k in range(3):
            ang = math.radians(-60 + 20 * k) if sd > 0 else math.radians(-120 - 20 * k)
            bx, by = cx + rx * 0.82 * math.cos(ang), cy + ry * 0.82 * math.sin(ang)
            line(S, f"M{bx:.1f},{by:.1f} l{7 * sd},{-6}", 2.6)


def brows(S, c, raise_=0, ang=0, thick=9):
    for sx in (-1, 1):
        xi, xo = 14 * sx, 70 * sx
        yi, yo = -64 + raise_ + ang, -64 + raise_ - ang * 0.4
        d = (f"M{xi},{yi - thick / 2} Q{(xi + xo) / 2},{min(yi, yo) - 15} {xo},{yo - 2} "
             f"L{xo + 3 * sx},{yo + 3} Q{(xi + xo) / 2},{min(yi, yo) - 4} {xi},{yi + thick / 2} Z")
        fill(S, d, c["hair"][0], lw=2)


def nose(S, c):
    d = "M-4,-2 C-7,14 -16,20 -13,30 C-9,39 9,39 13,30 C16,20 7,14 4,-2"
    cel(S, d + " Z", *c["skin"], -4, -4, 0, stroke=False)
    line(S, d, 3.5)
    line(S, "M-10,30 Q-6,26 -2,31 M3,31 Q7,26 11,30", 2.2)


# ---------------- Shirley's head: bob with a wispy fringe + green flower clip
SH_EXPR = {"calm": dict(raise_=0, ang=0, lid=0.18, look=(2, 2), mouth="soft"),
           "unimpressed": dict(raise_=4, ang=-2, lid=0.46, look=(6, 2), mouth="flat"),
           "surprised": dict(raise_=-14, ang=-6, lid=0.0, look=(0, -2), mouth="o"),
           "smile": dict(raise_=-4, ang=-4, lid=0.12, look=(0, 2), mouth="smile")}


def flower(S, x, y, r=16):
    for k in range(5):
        a = math.radians(-90 + 72 * k)
        cel(S, ell(x + r * 0.62 * math.cos(a), y + r * 0.62 * math.sin(a), r * 0.55, r * 0.55), *SH["clip"], -2, -2, 2.5)
    fill(S, ell(x, y, r * 0.32, r * 0.32), "#f6e27a", lw=2)


def shirley_head(S, x, y, s=1.0, expr="calm", lw=4.5):
    c, e = SH, SH_EXPR[expr]
    g_open(S, x, y, s)
    bob = "M-108,-96 C-118,-186 118,-186 108,-96 C116,-40 116,20 110,66 Q60,80 0,78 Q-60,80 -110,66 C-116,20 -116,-40 -108,-96 Z"
    cel(S, bob, *c["hair"], -10, -8, lw)
    cel(S, FACE, *c["skin"], -14, -10, lw)
    S.add(f'<path d="{ell(-56, 34, 20, 11)}" fill="#c4505c" opacity="0.18"/><path d="{ell(56, 34, 20, 11)}" fill="#c4505c" opacity="0.18"/>')
    for sx in (-1, 1):  # side panels of the bob over the cheeks
        cel(S, f"M{-100 * sx},-96 L{-78 * sx},-96 C{-82 * sx},-40 {-86 * sx},10 {-90 * sx},66 L{-110 * sx},66 C{-114 * sx},10 {-110 * sx},-50 {-100 * sx},-96 Z",
            *c["hair"], -4 * sx, -4, lw)
    # wispy fringe: uneven pointed strands
    tips = [(-92, -70), (-74, -58), (-58, -72), (-40, -60), (-22, -74), (-4, -62), (14, -76), (32, -62), (50, -74), (68, -60), (86, -72), (98, -88)]
    d = "M-100,-96 C-100,-150 -50,-170 0,-170 C50,-170 100,-150 100,-96 " + " ".join(
        f"L{tx},{ty} L{tx - 9},{ty - 14}" for tx, ty in reversed(tips)) + " Z"
    cel(S, d, *c["hair"], -8, -6, lw)
    for x0 in (-60, -20, 20, 60):
        line(S, f"M{x0 * 0.8},-156 Q{x0},-120 {x0 + 4},-84", 2, c["hair"][1])
    line(S, "M-56,-150 C-24,-164 24,-164 56,-150", 3, c["shine"], 0.9)
    flower(S, -66, -120, 23)
    eye_kw = dict(look=e["look"], lid=e["lid"], lashes=True)
    for sx in (-1, 1):
        eye(S, c, 40 * sx, **eye_kw)
    brows(S, c, e["raise_"], e["ang"], 7)
    nose(S, c)
    m = e["mouth"]
    if m == "o":
        cel(S, ell(0, 80, 14, 18), "#3b1519", "#3b1519", 0, 0, 3.5)
    elif m == "flat":
        line(S, "M-22,80 Q0,82 22,78", 4.5)
    else:
        sm = 10 if m == "smile" else 5
        cel(S, f"M-28,74 Q0,{74 + sm + 10} 28,74 Q0,{74 + sm} -28,74 Z", c["lips"], c["lips"], 0, 0, 3.5)
        line(S, f"M-32,70 q-3,4 0,8 M32,70 q3,4 0,8", 2.2, INK, 0.6)
    g_close(S)


# ---------------- Gabby's head: thick short wavy hair, big ears, toothy grin
GB_EXPR = {"grin": dict(raise_=-6, ang=-6, look=(3, 0), mouth="grin"),
           "focus": dict(raise_=6, ang=14, look=(0, -2), mouth="tongue", lid=0.3),
           "dizzy": dict(raise_=-10, ang=-8, mouth="wobble", spiral=True),
           "whoa": dict(raise_=-18, ang=-8, look=(0, 0), mouth="o")}


def gabby_head(S, x, y, s=1.0, expr="grin", lw=4.5):
    c, e = GB, GB_EXPR[expr]
    g_open(S, x, y, s)
    for sx in (-1, 1):
        cel(S, ell(98 * sx, 0, 22, 30), *c["skin"], -6 * sx, -4, lw)
        line(S, f"M{92 * sx},-12 Q{106 * sx},2 {94 * sx},18", 3, INK, 0.7)
    cel(S, FACE, *c["skin"], -14, -10, lw)
    hair = ("M-98,-66 C-112,-150 -40,-190 10,-182 C74,-176 114,-142 98,-66 "
            "L86,-74 Q72,-96 58,-80 Q44,-102 28,-84 Q12,-106 -6,-86 Q-24,-104 -40,-84 Q-56,-100 -72,-80 Q-86,-94 -98,-66 Z")
    cel(S, hair, *c["hair"], -8, -6, lw)
    for d in ("M-60,-150 q10,-14 24,-6", "M-20,-166 q12,-12 26,-2", "M24,-160 q12,-10 24,0", "M58,-140 q10,-8 18,4", "M-84,-110 q6,-12 18,-8"):
        line(S, d, 3, c["shine"], 0.85)
    for sx in (-1, 1):
        fill(S, f"M{86 * sx},-80 L{100 * sx},-74 C{102 * sx},-56 {98 * sx},-44 {92 * sx},-36 C{90 * sx},-52 {88 * sx},-66 {86 * sx},-80 Z", c["hair"][0], lw=2)
    for sx in (-1, 1):
        eye(S, c, 40 * sx, look=e.get("look", (0, 0)), lid=e.get("lid", 0), spiral=e.get("spiral", False), ry=37, rx=30)
    brows(S, c, e["raise_"], e["ang"], 11)
    nose(S, c)
    m = e["mouth"]
    if m == "grin":
        d = "M-50,60 Q0,72 50,60 Q44,112 0,114 Q-44,112 -50,60 Z"
        cid = S.uid(); S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        S.add(f'<path d="{d}" fill="{c["mouth"]}"/><g clip-path="url(#{cid})"><rect x="-60" y="54" width="120" height="22" fill="{W_}"/>'
              f'<path d="{ell(0, 118, 28, 18)}" fill="{c["tongue"]}"/></g>')
        S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
        line(S, "M-56,54 Q-60,62 -52,66 M56,54 Q60,62 52,66", 3)
    elif m == "tongue":
        line(S, "M-30,80 Q0,86 30,78", 5)
        cel(S, "M6,80 Q8,100 20,98 Q28,92 24,79 Z", c["tongue"], "#a84a44", -2, -2, 3)
    elif m == "wobble":
        line(S, "M-34,82 q8,-8 17,0 q8,8 17,0 q8,-8 17,0 q8,8 17,0", 4.5)
    else:
        cel(S, ell(0, 84, 20, 26), c["mouth"], c["mouth"], 0, 0, 4)
    g_close(S)


# ------------------------------------------------------------------ bodies (origin = face centre)
def shirley_body(S, x, y, s=1.0, lw=4.5):
    c = SH
    skin_hands(c)
    g_open(S, x, y, s)
    cel(S, "M-22,110 L22,110 L24,160 L-24,160 Z", *c["skin"], -8, 10, lw)
    # dhoti pants: baggy, draped, gathered at the ankles
    pants = ("M-96,400 L96,400 C126,480 132,580 112,676 C104,700 92,712 70,716 L22,716 C18,640 10,560 4,520 "
             "L-4,520 C-10,560 -18,640 -22,716 L-70,716 C-92,712 -104,700 -112,676 C-132,580 -126,480 -96,400 Z")
    cel(S, pants, *c["pants"], -12, 0, lw)
    for d in ("M-90,440 C-110,520 -100,600 -82,680", "M-60,470 C-70,560 -64,640 -50,700", "M80,450 C104,520 100,600 86,680",
              "M54,480 C64,560 60,640 48,700", "M-20,420 C-10,470 -6,500 0,520"):
        line(S, d, 2.4, INK, 0.45)
    for sx in (-1, 1):
        cel(S, f"M{-74 * sx},706 L{-20 * sx},706 L{-22 * sx},724 L{-76 * sx},724 Z", *c["pants"], -3, -3, 3.5)
        cel(S, f"M{-58 * sx},722 L{-34 * sx},722 L{-34 * sx},742 L{-58 * sx},742 Z", *c["skin"], -3, -3, 3)
        line(S, f"M{-60 * sx},736 Q{-46 * sx},742 {-32 * sx},736", 5, INK)  # silver anklet
        line(S, f"M{-60 * sx},736 Q{-46 * sx},742 {-32 * sx},736", 2.6, c["silver"][0])
        for k in range(4):
            fill(S, ell(-56 * sx + 7 * k * sx, 741, 1.8, 2.2), c["silver"][0], lw=1)
        cel(S, f"M{-86 * sx},742 C{-96 * sx},744 {-102 * sx},756 {-92 * sx},762 L{-22 * sx},762 C{-16 * sx},752 {-20 * sx},744 {-30 * sx},742 Z",
            *c["sandal"], -3, -3, lw)
    # printed kurti top: yellow base, coloured print bands, embroidered red yoke, flared hem
    kurti = "M-50,150 C-88,154 -108,170 -112,206 C-118,280 -122,360 -132,428 L132,428 C122,360 118,280 112,206 C108,170 88,154 50,150 Z"
    cid = cel(S, kurti, *c["kurti"], -14, -8, lw)
    bands = ""
    for k, (yy, col) in enumerate(((300, c["band1"]), (330, c["band2"]), (352, c["band3"]), (384, c["band1"]), (408, c["band2"]))):
        bands += f'<rect x="-140" y="{yy}" width="280" height="{12 if k % 2 else 16}" fill="{col}"/>'
        bands += "".join(f'<circle cx="{-130 + 16 * i}" cy="{yy + (6 if k % 2 else 8)}" r="2.6" fill="#fbfaf4" opacity="0.8"/>' for i in range(17))
    S.add(f'<g clip-path="url(#{cid})">{bands}</g>')
    S.add(f'<path d="{kurti}" fill="none" stroke="{INK}" stroke-width="{lw}" stroke-linejoin="round"/>')
    yoke = "M-62,154 C-40,150 -24,160 0,196 C24,160 40,150 62,154 L70,236 Q0,262 -70,236 Z"
    cel(S, yoke, *c["yoke"], -6, -6, lw)
    for i in range(9):  # little embroidered motifs on the yoke
        ax, ay = -56 + 14 * i, 240 + 6 * math.sin(i)
        fill(S, ell(ax, ay - 8, 3.2, 3.2), c["gold"][0], lw=1)
    line(S, "M-58,232 Q0,256 58,232", 2.4, c["gold"][0])
    fill(S, "M-24,152 Q0,186 24,152 Q12,166 0,170 Q-12,166 -24,152 Z", c["skin"][0], lw=0)
    for d in ("M-96,300 q-8,40 -10,90", "M96,300 q8,40 10,90", "M-40,420 q4,-30 0,-60"):
        line(S, d, 2.2, INK, 0.4)
    # cap sleeves
    for sx in (-1, 1):
        cel(S, f"M{-86 * sx},160 C{-116 * sx},164 {-136 * sx},184 {-138 * sx},214 L{-102 * sx},224 Z", *c["kurti"], -4, -4, lw)
    # screen-left arm relaxed with gold bangle; screen-right hand on hip
    hose(S, [(-120, 206), (-140, 330), (-142, 430)], 30, c["skin"][0], lw)
    line(S, "M-160,424 Q-142,432 -124,424", 7, INK)
    line(S, "M-160,424 Q-142,432 -124,424", 4, c["gold"][0])
    S.add('<g transform="translate(-142,436) rotate(180) scale(0.62)">')
    gs.hand_open(S, 0.5, False)
    S.add("</g>")
    hose(S, [(120, 206), (190, 300), (132, 376)], 30, c["skin"][0], lw)
    S.add('<g transform="translate(134,378) rotate(-120) scale(0.6)">')
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
        hose(S, [(46 * sx, 430), (52 * sx, 560), (50 * sx, 668)], 40, c["skin"][0], lw)
        lx = 46 * sx  # sneaker, toe pointing outward
        cel(S, f"M{lx - 14 * sx},690 C{lx - 26 * sx},692 {lx - 32 * sx},708 {lx - 26 * sx},722 L{lx + 60 * sx},722 "
               f"C{lx + 70 * sx},708 {lx + 56 * sx},692 {lx + 34 * sx},690 Z", *c["shoe"], -4, -3, lw)
        fill(S, f"M{lx - 28 * sx},716 L{lx + 64 * sx},716 L{lx + 64 * sx},726 L{lx - 28 * sx},726 Z", c["sole"], lw=2.5)
        line(S, f"M{46 * sx - 8},{700} l16,-4 M{46 * sx - 8},{706} l16,-4", 2.5, c["sole"])
        cel(S, f"M{46 * sx - 20},676 L{46 * sx + 20},676 L{46 * sx + 22},694 L{46 * sx - 22},694 Z", "#ffffff", "#d8d6cf", -2, -2, 3)  # sock
    fill(S, "M-58,548 L-36,544 L-34,560 L-56,564 Z", "#e9c98f", lw=2.5)  # band-aid
    line(S, "M-50,548 L-48,562 M-42,546 L-40,560", 1.5, INK, 0.5)
    shorts = "M-96,350 L96,350 C104,400 104,440 98,470 L10,470 L4,420 L-4,420 L-10,470 L-98,470 C-104,440 -104,400 -96,350 Z"
    cel(S, shorts, *c["shorts"], -10, 0, lw)
    for sx in (-1, 1):
        for k in range(5):
            line(S, f"M{(14 + 18 * k) * sx},470 l{3 * sx},8", 2, INK, 0.6)  # frayed hem
    line(S, "M-60,380 l10,0 M60,380 l-10,0", 2, INK, 0.4)
    S.add(f'<path d="{ell(-60, 420, 16, 12)}" fill="#ffffff" opacity="0.55"/><path d="{ell(64, 410, 14, 10)}" fill="#ffffff" opacity="0.5"/>')  # chalk handprints
    # leaf-print navy shirt (short sleeves), chest out
    shirt = "M-56,128 C-92,132 -112,148 -116,184 C-122,244 -118,300 -110,356 L110,356 C118,300 122,244 116,184 C112,148 92,132 56,128 Z"
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
            sh, el, wr = (84 * sx, 160), (138 * sx, 40), (176 * sx, -80)
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
        hose(S, [(84 * sx, 160), (100 * sx, 30), (108 * sx, -120)], 32, GB["skin"][0], 5)
        fill(S, f"M{108 * sx - 17},-124 L{108 * sx + 17},-124 L{108 * sx + 17},-104 L{108 * sx - 17},-104 Z", GB["tape"], lw=3)
        S.add(f'<g transform="translate({108 * sx},-124) scale(0.66)">')
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
    text(S, 64, 122, "comic-style teen redesign · v1", 24, 500, "#5a4a3c")
    # panels
    halftone_bg(S, 40, 150, 1140, 1100, "#7fd0c8", "#4fa79f")
    halftone_bg(S, 1220, 150, 1140, 1100, "#ffd84d", "#f2a93b", burst=(1790, 640, 300, 560, "#ffe98a"))
    shirley_body(S, 560, 440, 0.98)
    shirley_head(S, 560, 440, 0.98, "calm")
    S.add(f'<ellipse cx="560" cy="1196" rx="190" ry="16" fill="#000" opacity="0.12"/>')
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
