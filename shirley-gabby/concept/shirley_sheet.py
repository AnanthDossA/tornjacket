"""Shirley concept sheet (v1) - vector SVG generated in Python, rendered to PNG with Playwright.
Original character for Shirley & Gabby: Shirley, Gabby's elder sister. Indian, modern, science-minded,
deadpan; likes makeup and modern Indo-western clothes. Reuses the drawing kit + organic hands from gabby_sheet.
    python3 shirley_sheet.py  ->  shirley_sheet.svg / shirley_sheet.png
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gabby_sheet as gs
from gabby_sheet import SVG, g_open, g_close, cel, line, fill, ell, hose, text, _digit, _smooth, INK

Q = dict(
    skin=("#a36a47", "#77482f"), palm=("#c48d69", "#96613f"), hair=("#18121a", "#0c090e"), hi="#6e2a3a",
    shirt=("#e2aa3c", "#b07f22"), shirt_dk="#c9922c", trousers=("#6b3a6e", "#4a2650"), belt="#2a1c22",
    gold=("#ecc65e", "#b48c2c"), lips=("#93304f", "#6a1f3a"), liner="#141014", polish="#93304f", white="#fbfaf4",
    iris="#4a2c1a", lens="#dfe9ef", tablet="#25262b", screen="#86dccd", shoe=("#25222a", "#141216"),
    blush="#c4505c", pencil=("#f2c94c", "#c99a24"), eraser="#e98a9a", wood="#e9c9a0")

# ------------------------------------------------------------------ head (origin = face centre)
# softer, rounder face (owner didn't like the long one): fuller cheeks, short gentle heart-shaped jaw
HEAD = ("M-86,-104 C-92,-160 92,-160 86,-104 C98,-50 100,6 88,48 C74,92 40,114 0,116 "
        "C-40,114 -74,92 -88,48 C-100,6 -98,-50 -86,-104 Z")

EXPR = {  # brow raise per side (L = screen left), brow angle, lid, look, mouth, glare
    "deadpan": dict(bl=0, br=0, ang=0, lid=0.46, look=(0, 2), mouth="flat"),
    "eyeroll": dict(bl=-8, br=-8, ang=-4, lid=0.3, look=(4, -16), mouth="flat_side"),
    "smug":    dict(bl=4, br=-16, ang=0, lid=0.4, look=(-4, 0), mouth="smirk"),
    "shocked": dict(bl=-18, br=-18, ang=-6, lid=0.0, look=(0, 0), mouth="o", small=True),
    "focused": dict(bl=6, br=6, ang=8, lid=0.56, look=(2, 2), mouth="flat", glare=True),
    "proud":   dict(bl=-4, br=-4, ang=-4, lid=0.38, look=(0, 2), mouth="smile"),
}


def eye(S, side, e):
    cx, cy, rx, ry = 36 * side, -14, 26, 30
    d = ell(cx, cy, rx, ry)
    cid = S.uid()
    S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    S.add(f'<path d="{d}" fill="{Q["white"]}"/>')
    lx, ly = e["look"]
    S.add(f'<g clip-path="url(#{cid})">')
    S.add(f'<path d="{ell(cx + lx, cy + 4 + ly, 14, 15)}" fill="{Q["iris"]}"/>')
    pr = 4.5 if e.get("small") else 7
    S.add(f'<path d="{ell(cx + lx, cy + 4 + ly, pr, pr + 1)}" fill="{INK}"/>')
    S.add(f'<path d="{ell(cx + lx - 5, cy - 2 + ly, 3.6, 4)}" fill="#fff"/>')
    lid = e["lid"]
    yl = cy - ry + 2 * ry * lid
    if lid:
        S.add(f'<path d="M{cx - 34},{cy - 50} L{cx + 34},{cy - 50} L{cx + 34},{yl} L{cx - 34},{yl} Z" fill="{Q["skin"][0]}"/>')
        line(S, f"M{cx - 30},{yl - 9} Q{cx},{yl - 14} {cx + 30},{yl - 9}", 1.8, INK, 0.45)  # lid crease
    S.add("</g>")
    S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3"/>')
    # eyeliner along the lid edge + a wing at the outer corner
    if lid:
        half = math.sqrt(max(0, 1 - ((yl - cy) / ry) ** 2)) * rx
        line(S, f"M{cx - half},{yl} L{cx + half},{yl}", 5.5, Q["liner"])
        ox, oy = cx + side * half, yl
    else:
        line(S, f"M{cx - rx + 2},{cy - 10} Q{cx},{cy - ry - 5} {cx + rx - 2},{cy - 10}", 5.5, Q["liner"])
        ox, oy = cx + side * (rx - 2), cy - 10
    fill(S, f"M{ox - side * 4},{oy - 2} L{ox + side * 16},{oy - 12} L{ox + side * 2},{oy + 3} Z", Q["liner"])
    for k in range(3):  # lashes
        bx = cx + side * (rx * (0.35 + 0.22 * k))
        by = (oy if lid else cy - ry * 0.75 + 6 * k) - 1
        line(S, f"M{bx},{by} l{side * 5},{-7}", 2.2, Q["liner"])
    line(S, f"M{cx - 14},{cy + ry - 2} Q{cx},{cy + ry + 3} {cx + 16 * side},{cy + ry - 4}", 1.8, INK, 0.5)


def brow(S, side, e):
    r = e["bl"] if side < 0 else e["br"]
    ang = e["ang"]
    xi, xo = 12 * side, 70 * side
    yi, yo = -62 + r + ang, -60 + r - ang * 0.3
    peak = (xi + (xo - xi) * 0.62, min(yi, yo) - 14)
    d = (f"M{xi},{yi + 4} Q{xi + (peak[0] - xi) * 0.4},{yi - 6} {peak[0]},{peak[1]} Q{(peak[0] + xo) / 2 + 4 * side},{peak[1] + 2} {xo},{yo + 4} "
         f"Q{(peak[0] + xo) / 2},{peak[1] + 8} {peak[0]},{peak[1] + 7} Q{xi + (peak[0] - xi) * 0.4},{yi + 2} {xi},{yi + 9} Z")
    fill(S, d, Q["hair"][0], lw=1.5)


def mouth(S, kind):
    up = "M-26,72 Q-14,63 -5,67 Q0,63 5,67 Q14,63 26,72 Q0,75 -26,72 Z"
    lo = "M-26,72 Q0,75 26,72 Q16,87 0,88 Q-16,87 -26,72 Z"
    if kind in ("flat", "flat_side", "smile", "smirk"):
        g = {"flat": "", "flat_side": "translate(4,0) rotate(-4)", "smile": "", "smirk": "rotate(-7)"}[kind]
        S.add(f'<g transform="{g}">')
        if kind == "smile":
            up = "M-30,68 Q-14,62 -5,66 Q0,62 5,66 Q14,62 30,68 Q0,76 -30,68 Z"
            lo = "M-30,68 Q0,76 30,68 Q18,86 0,87 Q-18,86 -30,68 Z"
        cel(S, lo, Q["lips"][0], Q["lips"][1], -3, -4, 2.5)
        cel(S, up, Q["lips"][1], Q["lips"][1], 0, 0, 2.5)
        line(S, "M-26,72 Q0,75 26,72" if kind != "smile" else "M-30,68 Q0,76 30,68", 2.5)
        line(S, "M-10,78 q8,-3 14,0", 1.6, "#fff", 0.55)  # gloss
        if kind == "smile":
            line(S, "M-34,64 q-4,4 -2,8 M34,64 q4,4 2,8", 2, INK, 0.6)
        S.add("</g>")
    else:  # "o"
        cel(S, ell(0, 80, 18, 22), Q["lips"][0], Q["lips"][1], -2, -3, 2.5)
        S.add(f'<path d="{ell(0, 81, 10, 14)}" fill="#3b1519"/>')


def pencil(S, x0, y0, x1, y1, w=12):
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    S.add(f'<g transform="translate({x0},{y0}) rotate({ang})">')
    fill(S, f"M0,{-w / 2} L{L - 28},{-w / 2} L{L - 28},{w / 2} L0,{w / 2} Z", Q["pencil"][0], lw=3)
    line(S, f"M2,0 L{L - 30},0", 1.5, Q["pencil"][1], 0.9)
    fill(S, f"M{L - 28},{-w / 2} L{L},0 L{L - 28},{w / 2} Z", Q["wood"], lw=3)
    fill(S, f"M{L - 9},{-w * 0.16} L{L},0 L{L - 9},{w * 0.16} Z", "#3a3a40")
    fill(S, f"M-14,{-w / 2} L0,{-w / 2} L0,{w / 2} L-14,{w / 2} Z", "#b9bcc4", lw=3)
    fill(S, f"M-26,{-w / 2} L-14,{-w / 2} L-14,{w / 2} L-26,{w / 2} Q-30,0 -26,{-w / 2} Z", Q["eraser"], lw=3)
    S.add("</g>")


def jhumka(S, x, y):
    fill(S, ell(x, y, 5, 5), Q["gold"][0], lw=2)
    line(S, f"M{x},{y + 5} L{x},{y + 12}", 2, Q["gold"][1])
    d = f"M{x - 12},{y + 26} Q{x - 10},{y + 10} {x},{y + 10} Q{x + 10},{y + 10} {x + 12},{y + 26} Z"
    cel(S, d, Q["gold"][0], Q["gold"][1], -3, -2, 2.2)
    for k in range(5):
        fill(S, ell(x - 10 + 5 * k, y + 30, 2.2, 2.6), Q["gold"][0], lw=1.2)


def head(S, x, y, s=1.0, expr="deadpan", lw=4):
    e = EXPR[expr]
    g_open(S, x, y, s)
    sk, sd = Q["skin"]
    # short blunt bob ("Dora cut"): back mass to the jaw, cut straight
    bob = "M-102,-100 C-114,-184 114,-184 102,-100 C110,-40 112,20 106,62 Q0,72 -106,62 C-112,20 -110,-40 -102,-100 Z"
    cel(S, bob, Q["hair"][0], Q["hair"][1], -10, -8, lw)
    hc = cel(S, HEAD, sk, sd, -14, -10, lw)
    # screen-right side is tucked behind the ear; pencil rests behind that ear (ear covers its middle)
    pencil(S, 102, -116, 124, 30, 11)
    cel(S, ell(99, -4, 14, 23), sk, sd, 4, -3, lw)
    line(S, "M95,-16 Q106,-4 97,10", 2.5, INK, 0.6)
    jhumka(S, 99, 18)
    S.add(f'<g clip-path="url(#{hc})">'
          f'<path d="{ell(-54, 32, 24, 13)}" fill="{Q["blush"]}" opacity="0.24"/><path d="{ell(54, 32, 24, 13)}" fill="{Q["blush"]}" opacity="0.24"/>'
          f'<path d="M-90,-84 L90,-84 L90,-70 Q0,-62 -90,-70 Z" fill="{sd}" opacity="0.5"/></g>')
    # screen-left side panel falls straight past the cheek to the jaw
    side = "M-98,-96 L-74,-96 C-76,-40 -78,10 -78,58 L-106,62 C-110,10 -106,-50 -98,-96 Z"
    cel(S, side, Q["hair"][0], Q["hair"][1], -4, -4, lw)
    line(S, "M-88,-60 L-90,40", 2, Q["hi"], 0.7)
    # tucked side: a short strand sweeping back over the ear
    cel(S, "M74,-98 L104,-100 C110,-74 108,-46 104,-30 C96,-52 88,-68 74,-82 Z", Q["hair"][0], Q["hair"][1], 3, -3, lw)
    # straight blunt bangs, a few tiny notches on the cut line
    notch = " ".join(f"L{x},{-78 + (4 if i % 2 else 0)}" for i, x in enumerate(range(88, -91, -12)))
    bangs = f"M-96,-100 C-94,-152 -44,-166 0,-166 C44,-166 94,-152 96,-100 L94,-78 {notch} L-96,-78 Z"
    cel(S, bangs, Q["hair"][0], Q["hair"][1], -8, -6, lw)
    for x in (-60, -30, 0, 30, 60):
        line(S, f"M{x * 0.8},-150 Q{x},-120 {x},-84", 1.8, Q["hair"][1], 0.9)
    line(S, "M-60,-150 C-30,-162 30,-162 60,-150", 3, Q["hi"], 0.85)  # burgundy sheen
    # face
    for sx in (-1, 1):
        eye(S, sx, e)
    for sx in (-1, 1):
        brow(S, sx, e)
    nose = "M-4,-4 C-6,14 -14,22 -12,30 C-8,38 8,38 12,30 C14,22 6,14 4,-4"
    cel(S, nose + " Z", sk, sd, -4, -4, 0, stroke=False)
    line(S, "M-4,-4 C-6,14 -14,22 -12,30 C-8,38 8,38 12,30", 3.2)
    fill(S, ell(-11, 30, 3, 3), Q["gold"][0], lw=1.5)  # nose pin
    S.add(f'<circle cx="-12" cy="29" r="1" fill="#fff"/>')
    mouth(S, e["mouth"])
    # round gold-rim glasses
    for sx in (-1, 1):
        c = ell(38 * sx, -12, 37, 36)
        S.add(f'<path d="{c}" fill="{Q["lens"]}" opacity="0.18"/>')
        S.add(f'<path d="{c}" fill="none" stroke="{INK}" stroke-width="6.5"/><path d="{c}" fill="none" stroke="{Q["gold"][0]}" stroke-width="3"/>')
        line(S, f"M{38 * sx - 18},-34 l14,-10 M{38 * sx - 22},-20 l26,-20", 2.2 if not e.get("glare") else 5, "#fff", 0.55 if not e.get("glare") else 0.9)
        line(S, f"M{75 * sx},-14 L{86 * sx},-10", 4)
    line(S, "M-2,-18 Q0,-26 2,-18", 6.5)
    line(S, "M-2,-18 Q0,-26 2,-18", 3, Q["gold"][0])
    g_close(S)


# ------------------------------------------------------------------ hands (slim, polished)
def shirley_hands():
    """switch gabby_sheet's hand kit to Shirley: slimmer, longer fingers, palm/skin tones, berry polish"""
    gs.FINGERS_OPEN = [((-19, -50), -9, 58, 19, 14.5, 5), ((-3, -54), -2, 67, 20, 15, 3),
                       ((13, -52), 6, 62, 19, 14.5, 1), ((28, -45), 15, 47, 16.5, 12.5, -2)]
    gs.THUMB_OPEN = ((-29, -6), -56, 44, 22, 16, 22)
    gs.P["skin"], gs.P["palm"], gs.P["nail"] = Q["skin"], Q["palm"], Q["polish"]


def hand_pinch(S):
    """'precisely': thumb and index tips meet in a small ring at the side, other fingers up and fanned"""
    def nail(x, y, rot):
        S.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f})"><path d="M-4.5,5 C-5.5,-2 -3.5,-7 0,-7.5 C3.5,-7 5.5,-2 4.5,5 Q0,7 -4.5,5 Z" '
              f'fill="{Q["polish"]}" stroke="{INK}" stroke-width="1.6"/></g>')
    for (b, a, L, w0, w1, bend) in [((-3, -54), -2, 64, 20, 15, 6), ((13, -52), 9, 58, 19, 14.5, 8), ((28, -45), 20, 44, 16.5, 12.5, 10)]:
        l, tip, r, cl = _digit(b, a, L, w0, w1, bend)
        cel(S, _smooth([(b[0] - 8, b[1] + 14)] + l + tip + r + [(b[0] + 8, b[1] + 14)]), *Q["skin"], -3, -3, 3.5)
        nail(*cl[-2][:2], a + bend)
    palm = _smooth([(-20, 30), (-34, 6), (-34, -30), (-24, -54), (4, -60), (30, -50), (38, -20), (38, 6), (22, 30)])
    cel(S, palm, *Q["skin"], -6, -5, 4)
    for x in (-8, 6, 20):
        line(S, f"M{x},-38 C{x},-20 {x * 0.8},-4 {x * 0.6},12", 1.4, INK, 0.2)
    l, tip, r, clt = _digit((-30, -8), -20, 58, 22, 16, 10)  # thumb reaching up
    cel(S, _smooth([(-36, 6)] + l + tip + r + [(-22, -22)]), *Q["skin"], -3, -3, 3.5)
    nail(*clt[-2][:2], -10)
    l, tip, r, cli = _digit((-19, -50), -70, 40, 19, 14.5, 40)  # index curling down to meet it
    cel(S, _smooth([(-12, -38)] + l + tip + r + [(-24, -58)]), *Q["skin"], -3, -3, 3.5)
    nail(*cli[-2][:2], -30)
    line(S, f"M{cli[3][0] - 4},{cli[3][1] - 4} q4,4 8,2", 1.6, INK, 0.45)


def hand_two(S):
    """counting 'two' (back of hand): index + middle up, ring + pinky + thumb folded"""
    S.add('<g transform="scale(-1,1)">')
    palm = _smooth([(-20, 30), (-34, 8), (-34, -36), (-20, -56), (8, -60), (32, -50), (40, -22), (40, 6), (22, 30)])
    for b, a, L, w0, w1, bend in [((-19, -50), -12, 58, 19, 14.5, 4), ((-3, -54), 2, 66, 20, 15, 2)]:
        l, tip, r, cl = _digit(b, a, L, w0, w1, bend)
        cel(S, _smooth([(b[0] - 10, b[1] + 12)] + l + tip + r + [(b[0] + 10, b[1] + 12)]), *Q["skin"], -3, -3, 3.5)
        x, y, _ = cl[-2]
        S.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({a + bend:.0f})"><path d="M-4.5,5 C-5.5,-2 -3.5,-7 0,-7.5 C3.5,-7 5.5,-2 4.5,5 Q0,7 -4.5,5 Z" '
              f'fill="{Q["polish"]}" stroke="{INK}" stroke-width="1.6"/></g>')
    cel(S, palm, *Q["skin"], -6, -5, 4)
    for x0 in (12, 28):  # folded ring + pinky knuckles
        cel(S, _smooth([(x0 - 9, -50), (x0, -60), (x0 + 9, -50), (x0 + 8, -36), (x0 - 8, -36)]), *Q["skin"], -2, -2, 3)
    l, tip, r, cl = _digit((-30, -6), 70, 40, 22, 16, 14)
    cel(S, _smooth([(-34, 6)] + l + tip + r + [(-30, -20)]), *Q["skin"], -3, -3, 3.5)
    fill(S, "M-11,-72 L5,-72 L5,-66 L-11,-66 Z", Q["gold"][0], lw=1.5)  # thin ring on the middle finger
    S.add("</g>")


def body(S, x, y, s=1.0, lw=4):
    g_open(S, x, y, s)
    sh, shd = Q["shirt"]
    # neck + wide-leg trousers + shoes
    cel(S, "M-22,104 L22,104 L24,170 L-24,170 Z", Q["skin"][0], Q["skin"][1], -8, 12, lw)
    trousers = ("M-100,370 L100,370 C110,520 124,680 134,820 L18,820 C14,680 8,560 4,470 L-4,470 "
                "C-8,560 -14,680 -18,820 L-134,820 C-124,680 -110,520 -100,370 Z")
    cel(S, trousers, *Q["trousers"], -12, 0, lw)
    for sx in (-1, 1):
        line(S, f"M{66 * sx},420 C{70 * sx},560 {74 * sx},700 {76 * sx},814", 2, INK, 0.35)
        cel(S, f"M{-118 * sx},816 C{-150 * sx},818 {-168 * sx},830 {-158 * sx},844 L{-30 * sx},844 C{-24 * sx},834 {-28 * sx},820 {-40 * sx},816 Z",
            *Q["shoe"], -5 * sx, -3, lw)
        fill(S, f"M{-96 * sx},820 L{-70 * sx},820 L{-70 * sx},826 L{-96 * sx},826 Z", Q["gold"][0], lw=1.5)
    # satin shirt, tucked in
    torso = "M-40,158 C-82,160 -112,172 -118,202 C-124,252 -116,322 -100,372 L100,372 C116,322 124,252 118,202 C112,172 82,160 40,158 Z"
    cel(S, torso, sh, shd, -14, -8, lw)
    fill(S, "M-24,156 L0,214 L24,156 Z", Q["skin"][0], lw=0)
    line(S, "M-24,156 L0,214 L24,156", 3)
    line(S, "M-20,160 Q-6,196 0,204 Q6,196 20,160", 1.6, Q["gold"][1])  # chain
    hexa = " ".join(f"{9 * math.cos(math.pi / 3 * k + math.pi / 6):.1f},{208 + 9 * math.sin(math.pi / 3 * k + math.pi / 6):.1f}" for k in range(6))
    S.add(f'<polygon points="{hexa}" fill="none" stroke="{INK}" stroke-width="4.5"/><polygon points="{hexa}" fill="none" stroke="{Q["gold"][0]}" stroke-width="2.4"/>')
    S.add(f'<circle cx="0" cy="208" r="4" fill="none" stroke="{Q["gold"][1]}" stroke-width="1.6"/>')
    for sx in (-1, 1):  # pointed collar
        cel(S, f"M{-44 * sx},150 L{-4 * sx},198 L{-30 * sx},210 L{-58 * sx},170 Z", Q["shirt_dk"], shd, -3, -3, 3.5)
    line(S, "M0,216 L0,368", 2.5, INK, 0.6)
    for by in (246, 282, 318, 352):
        fill(S, ell(6, by, 4, 4), "#f5e7c4", lw=1.5)
    for d in ("M-90,330 q10,20 30,30", "M88,326 q-10,22 -28,32", "M-60,350 q20,10 40,8", "M70,240 q8,26 4,50"):
        line(S, d, 2.2, INK, 0.4)
    line(S, "M-60,210 Q-30,190 -20,230", 2, "#fff", 0.35)  # satin sheen
    fill(S, "M-102,364 L102,364 L102,382 L-102,382 Z", Q["belt"], lw=3)
    fill(S, "M-12,362 L12,362 L12,384 L-12,384 Z", Q["gold"][0], lw=2.5)
    # tablet arm (screen right): rolled sleeve, smartwatch, tablet against the hip
    hose(S, [(108, 190), (138, 300)], 46, sh, lw)
    cel(S, "M114,284 L164,296 L158,322 L108,310 Z", Q["shirt_dk"], shd, -3, -3, 3.5)  # rolled cuff
    hose(S, [(134, 312), (100, 384)], 30, Q["skin"][0], lw)
    S.add('<g transform="translate(120,404) rotate(8)">')
    fill(S, "M-58,-80 L58,-80 Q66,-80 66,-72 L66,72 Q66,80 58,80 L-58,80 Q-66,80 -66,72 L-66,-72 Q-66,-80 -58,-80 Z", Q["tablet"], lw=4)
    fill(S, "M-54,-68 L54,-68 L54,68 L-54,68 Z", "#1b2a33")
    line(S, "M-46,40 L-26,10 L-6,24 L16,-18 L44,-40", 3.5, Q["screen"])
    for k in range(4):
        fill(S, f"M{-44 + 22 * k},{58} L{-34 + 22 * k},{58} L{-34 + 22 * k},{58 - 12 - 8 * k} L{-44 + 22 * k},{58 - 12 - 8 * k} Z", "#e2aa3c", op=0.85)
    S.add("</g>")
    for k in range(4):  # fingertips wrapped over the tablet edge, polished
        fx, fy = 60 + 2 * k, 372 + 15 * k
        cel(S, f"M{fx - 14},{fy - 6} Q{fx + 6},{fy - 9} {fx + 10},{fy} Q{fx + 6},{fy + 8} {fx - 14},{fy + 6} Z", *Q["skin"], -2, -2, 3)
        fill(S, ell(fx + 4, fy, 4.5, 3.5), Q["polish"], lw=1.4)
    fill(S, "M88,370 L112,374 L110,388 L86,384 Z", "#2b2b30", lw=2.5)  # smartwatch
    fill(S, "M93,373 L107,375 L106,385 L92,383 Z", "#5ec8b8")
    g_close(S)


def glasses_arm(S, x, y, s=1.0, lw=4):
    """arm up adjusting the glasses at the outer rim (drawn after the head)"""
    g_open(S, x, y, s)
    sh, shd = Q["shirt"]
    hose(S, [(-108, 190), (-150, 250)], 46, sh, lw)
    cel(S, "M-176,232 L-128,232 L-126,262 L-176,262 Z", Q["shirt_dk"], shd, -3, -3, 3.5)
    hose(S, [(-150, 246), (-94, 74)], 30, Q["skin"][0], lw)
    S.add('<g transform="translate(-94,74) rotate(14) scale(0.78)">')
    gs.hand_point(S)
    S.add("</g>")
    g_close(S)


# ------------------------------------------------------------------ sheet
def sheet(path_svg):
    shirley_hands()
    W, H = 2400, 1900
    S = SVG(W, H)
    S.add(f'<rect width="{W}" height="{H}" fill="#efe6dc"/>')
    for gx in range(0, W, 40):
        S.add(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}" stroke="#e2d6c9" stroke-width="1"/>')
    for gy in range(0, H, 40):
        S.add(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}" stroke="#e2d6c9" stroke-width="1"/>')
    text(S, 60, 86, "SHIRLEY", 64, 800)
    text(S, 64, 126, "Shirley &amp; Gabby · character sheet · concept v3", 24, 400, "#5a4a3c")
    hx, hy, hs = 640, 430, 1.1
    body(S, hx, hy, hs)
    head(S, hx, hy, hs, "deadpan")
    glasses_arm(S, hx, hy, hs)
    S.add(f'<ellipse cx="{hx}" cy="{hy + 846 * hs}" rx="230" ry="20" fill="#000" opacity="0.08"/>')
    ex = [("deadpan", "deadpan (default)"), ("eyeroll", "eye-roll"), ("smug", "one-brow smug"),
          ("shocked", "shocked (rare)"), ("focused", "analysing"), ("proud", "secretly proud")]
    x0, y0 = 1180, 400
    text(S, x0 - 120, 120, "EXPRESSIONS", 30, 800)
    for i, (k, lab) in enumerate(ex):
        cx, cy = x0 + (i % 3) * 330, y0 + (i // 3) * 440
        head(S, cx, cy, 0.8, k)
        text(S, cx, cy + 140, lab, 24, 700, "#5a4a3c", "middle")
    # palette
    px, py = 2150, 260
    text(S, px - 30, py - 40, "PALETTE", 30, 800)
    sw = [("skin", *Q["skin"]), ("hair", Q["hair"][0], Q["hi"]), ("shirt", *Q["shirt"]), ("trousers", *Q["trousers"]),
          ("lips/nails", *Q["lips"]), ("gold", *Q["gold"])]
    for i, (n, a, b) in enumerate(sw):
        yy = py + i * 64
        S.add(f'<rect x="{px - 30}" y="{yy}" width="44" height="44" rx="8" fill="{a}" stroke="{INK}" stroke-width="3"/>')
        S.add(f'<rect x="{px + 20}" y="{yy}" width="44" height="44" rx="8" fill="{b}" stroke="{INK}" stroke-width="3"/>')
        text(S, px + 76, yy + 20, n, 18, 700)
        text(S, px + 76, yy + 40, a, 14, 400, "#5a4a3c")
    notes = [
        "~29, Indian. Gabby's elder sister. Sharp, deadpan, permanently tired; secretly the bravest.",
        "Modern and science-minded: questions everything, tablet full of graphs, smartwatch.",
        "Soft round face. Short blunt bob with straight bangs (\u201cDora cut\u201d), pencil tucked behind her ear.",
        "Makeup: winged liner, groomed arched brows, berry lips, soft blush, berry nail polish.",
        "Round gold-rim glasses (pushes them up at the rim when she's about to be right).",
        "Gold nose pin, mini gold jhumkas, benzene-ring pendant. Burgundy sheen in her hair.",
        "Mustard satin shirt (rolled sleeves) tucked into plum high-waist wide-leg trousers.",
        "Moves minimally and slowly; barely gestures; rolls her eyes. Voice: bf_emma.",
    ]
    nx, ny = 1080, 1130
    text(S, nx - 30, ny - 40, "DESIGN NOTES", 30, 800)
    for i, n in enumerate(notes):
        text(S, nx, ny + i * 36, "• " + n, 21, 400)
    # hands
    text(S, 60, 1555, "HANDS", 30, 800)
    text(S, 190, 1555, "slimmer, longer fingers · berry polish · thin gold ring · precise, small gestures", 21, 400, "#5a4a3c")
    poses = [("open palm", lambda S: gs.hand_open(S)), ("back of hand", lambda S: gs.hand_open(S, 0.85, False)),
             ("“actually…”", gs.hand_point), ("“one sec.”", lambda S: gs.hand_open(S, 0.45)), ("“two reasons”", hand_two)]
    for i, (lab, fn) in enumerate(poses):
        hx2, hy2 = 240 + i * 460, 1765
        g_open(S, hx2, hy2, 1.55)
        fill(S, "M-20,-24 L20,-24 L20,10 L-20,10 Z", Q["skin"][1], lw=0)
        line(S, "M-20,-24 L-20,10 M20,-24 L20,10", 4)
        cel(S, "M-36,6 L36,6 L32,34 L-32,34 Z", Q["shirt_dk"], Q["shirt"][1], -4, -4, 4)
        g_open(S, 0, 4, 1, 0)
        fn(S)
        g_close(S)
        g_close(S)
        text(S, hx2, hy2 + 100, lab, 22, 700, "#5a4a3c", "middle")
    open(path_svg, "w").write(S.out())


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    svg = os.path.join(here, "shirley_sheet.svg")
    sheet(svg)
    png = os.path.join(here, "shirley_sheet.png")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 2400, "height": 1900})
        pg.goto("file://" + svg)
        pg.screenshot(path=png)
        b.close()
    print(png)
