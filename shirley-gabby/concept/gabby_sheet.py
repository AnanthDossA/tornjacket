"""Gabby concept sheet (v1) - vector SVG generated in Python, rendered to PNG with Playwright.
Original character design for Shirley & Gabby: Gabby, 22, Indian, loud/optimistic/gullible.
    python3 gabby_sheet.py  ->  gabby_sheet.svg / gabby_sheet.png
"""
import math, os, sys

INK = "#1b1418"
HALFTONE = False  # comic halftone shadows (set True by the teen comic sheet)
P = dict(  # palette: (lit, shadow)
    skin=("#9a6443", "#6e4430"), skin_hi="#b07a55", hair=("#1d1517", "#120c0e"), stub="#3a2419",
    beanie=("#269696", "#1b7070"), cuff=("#1e8080", "#155c5c"), pom=("#2aa4a4", "#1b7474"),
    hoodie=("#de5246", "#a93a34"), hood=("#b8423b", "#8c2f2b"), jeans=("#3e5488", "#2c3c66"), jcuff="#5a70a6",
    shoe=("#f2f1ea", "#c9c8bf"), sole="#d9d7cd", lace="#d8473c", white="#fbfaf4", iris="#5b3820",
    mouth="#3b1519", tongue="#d0625b", chai="#c98a3c", glass="#e8eef0", band="#141012", watch="#2b2b30",
    palm=("#bb8360", "#8e5a3e"), nail="#d9a98c", kurta=("#f1e8d0", "#cfc2a2"), print_=("#8f2d2d", "#e2a83a"),
    kalava=("#d23a2a", "#f2c230"), shine="#60708f")


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.defs, self.body, self.n = w, h, [], [], 0

    def uid(self, p="c"):
        self.n += 1
        return f"{p}{self.n}"

    def add(self, s):
        self.body.append(s)

    def out(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')


def g_open(S, x, y, s=1.0, rot=0, flip=False):
    S.add(f'<g transform="translate({x},{y}) rotate({rot}) scale({-s if flip else s},{s})">')


def g_close(S):
    S.add("</g>")


def cel(S, d, lit, dark, dx=-14, dy=-10, lw=4, stroke=True, extra=""):
    """flat 2-tone cel: shadow everywhere, lit copy shifted toward the light, clipped to the shape, ink outline"""
    cid = S.uid()
    S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    if HALFTONE:  # comic look: lit colour everywhere, shadow side printed as halftone dots
        pid = "ht" + dark.lstrip("#")
        if pid not in getattr(S, "pats", set()):
            S.pats = getattr(S, "pats", set()) | {pid}
            S.defs.append(f'<pattern id="{pid}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
                          f'<circle cx="3.5" cy="3.5" r="2.5" fill="{dark}"/></pattern>')
        S.add(f'<path d="{d}" fill="{lit}"/><path d="{d}" fill="url(#{pid})"/>')
    else:
        S.add(f'<path d="{d}" fill="{dark}"/>')
    S.add(f'<g clip-path="url(#{cid})"><path d="{d}" fill="{lit}" transform="translate({dx},{dy})"/>{extra}</g>')
    if stroke:
        S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{lw}" stroke-linejoin="round" stroke-linecap="round"/>')
    return cid


def line(S, d, w=3, col=INK, op=1.0):
    S.add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>')


def fill(S, d, col, lw=0, op=1.0):
    st = f' stroke="{INK}" stroke-width="{lw}" stroke-linejoin="round"' if lw else ""
    S.add(f'<path d="{d}" fill="{col}"{st} opacity="{op}"/>')


def ell(cx, cy, rx, ry):
    return f"M{cx - rx},{cy} A{rx},{ry} 0 1 0 {cx + rx},{cy} A{rx},{ry} 0 1 0 {cx - rx},{cy} Z"


def hose(S, pts, w, col, lw=4):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + 2 * lw}" stroke-linecap="round" stroke-linejoin="round"/>')
    S.add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def fuzzy(cx, cy, r, bumps=18, amp=0.12):
    pts = []
    for i in range(bumps * 2):
        a = math.pi * i / bumps
        rr = r * (1 + (amp if i % 2 else -amp * 0.3))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts), 2):
        c, e = pts[i], pts[(i + 1) % len(pts)]
        d += f" Q{c[0]:.1f},{c[1]:.1f} {e[0]:.1f},{e[1]:.1f}"
    return d + " Z"


# ------------------------------------------------------------------ head (origin = face centre)
# teen (~16): narrower oval, no jowls, defined chin
HEAD = ("M-90,-80 C-96,-150 96,-150 90,-80 C98,-30 98,26 84,72 "
        "C70,112 40,136 0,138 C-40,136 -70,112 -84,72 C-98,26 -98,-30 -90,-80 Z")

EXPR = {
    "grin":   dict(brow=-4, ang=-6, lid=0.0, look=(4, 2), mouth="grin"),
    "shock":  dict(brow=-18, ang=-10, lid=0.0, look=(0, -4), mouth="shock", small_pupil=True),
    "whine":  dict(brow=-8, ang=16, lid=0.28, lidtilt=-14, look=(0, 6), mouth="whine"),
    "scheme": dict(brow=4, ang=-14, lid=0.45, lidtilt=6, look=(10, 0), mouth="smirk"),
    "deadpan": dict(brow=2, ang=0, lid=0.5, lidtilt=0, look=(0, 2), mouth="flat"),
}


def eye(S, ex, side, e):
    cx, cy, rx, ry = ex, -14, 31, 39
    d = ell(cx, cy, rx, ry)
    cid = S.uid()
    S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    S.add(f'<path d="{d}" fill="{P["white"]}"/>')
    lx, ly = e["look"]
    pr = 6 if e.get("small_pupil") else 9
    S.add(f'<g clip-path="url(#{cid})">')
    S.add(f'<path d="{ell(cx + lx, cy + 4 + ly, 17, 18)}" fill="{P["iris"]}"/>')
    S.add(f'<path d="{ell(cx + lx, cy + 4 + ly, pr, pr + 1)}" fill="{INK}"/>')
    S.add(f'<path d="{ell(cx + lx - 6, cy - 3 + ly, 4.5, 5)}" fill="#ffffff"/>')
    S.add(f'<path d="{ell(cx + lx + 6, cy + 12 + ly, 2, 2)}" fill="#ffffff" opacity="0.8"/>')
    lid = e.get("lid", 0)
    if lid:  # skin lid from the top, tilted (inner end = toward the nose)
        t = e.get("lidtilt", 0) * (-1 if side < 0 else 1)
        yl = cy - ry + 2 * ry * lid
        S.add(f'<path d="M{cx - 40},{cy - 60} L{cx + 40},{cy - 60} L{cx + 40},{yl - t} L{cx - 40},{yl + t} Z" fill="{P["skin"][0]}"/>')
        line(S, f"M{cx - 40},{yl + t} L{cx + 40},{yl - t}", 5)
    S.add("</g>")
    S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4"/>')
    if not lid:  # upper lash line, thicker
        line(S, f"M{cx - rx + 3},{cy - 14} Q{cx},{cy - ry - 6} {cx + rx - 3},{cy - 14}", 6)
    line(S, f"M{cx - 14},{cy + ry + 8} Q{cx},{cy + ry + 12} {cx + 14},{cy + ry + 8}", 2.2, op=0.55)  # under-eye bag


def brow(S, side, e):
    # thick, slightly bushy; inner end at x=+-16, outer at +-82
    raise_, ang = e["brow"], e["ang"]
    s = side
    yi, yo = -66 + raise_ + ang, -66 + raise_ - ang * 0.4
    xi, xo = 12 * s, 74 * s
    top = f"M{xi},{yi - 7} Q{(xi + xo) / 2},{min(yi, yo) - 18} {xo},{yo - 2}"
    bot = f"L{xo + 3 * s},{yo + 3} Q{(xi + xo) / 2},{min(yi, yo) - 5} {xi},{yi + 7} Z"
    fill(S, top + " " + bot, P["hair"][0], lw=2.5)
    for k in range(4):  # little hair flicks on top
        x = xi + (xo - xi) * (0.2 + 0.2 * k)
        y = yi + (yo - yi) * (0.2 + 0.2 * k) - 14
        line(S, f"M{x},{y + 4} l{6 * s},{-6}", 2.2, P["hair"][0])


def mouth(S, kind):
    if kind == "grin":
        d = "M-46,64 Q0,74 46,64 Q40,112 0,114 Q-40,112 -46,64 Z"
        cid = S.uid(); S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        S.add(f'<path d="{d}" fill="{P["mouth"]}"/><g clip-path="url(#{cid})">'
              f'<rect x="-60" y="58" width="120" height="20" fill="{P["white"]}"/>'
              f'<path d="{ell(0, 118, 30, 18)}" fill="{P["tongue"]}"/></g>')
        S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
        line(S, "M-52,58 Q-56,66 -48,70", 3)
        line(S, "M52,58 Q56,66 48,70", 3)
    elif kind == "shock":
        d = ell(0, 90, 24, 32)
        cid = S.uid(); S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        S.add(f'<path d="{d}" fill="{P["mouth"]}"/><g clip-path="url(#{cid})"><path d="{ell(0, 120, 20, 14)}" fill="{P["tongue"]}"/>'
              f'<rect x="-30" y="56" width="60" height="9" fill="{P["white"]}"/></g>')
        S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4"/>')
    elif kind == "whine":
        d = "M-44,96 Q-24,72 0,80 Q24,72 44,96 Q22,88 0,92 Q-22,88 -44,96 Z"
        cid = S.uid(); S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        S.add(f'<path d="{d}" fill="{P["mouth"]}"/><g clip-path="url(#{cid})"><rect x="-50" y="70" width="100" height="14" fill="{P["white"]}"/></g>')
        S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
        line(S, "M-14,104 Q0,110 14,104", 2.5, op=0.6)  # chin wobble
    elif kind == "smirk":
        line(S, "M-36,84 Q4,96 44,70", 5)
        line(S, "M44,70 Q52,66 50,58", 3)
    else:
        line(S, "M-30,84 Q0,88 30,84", 5)


def head(S, x, y, s=1.0, expr="grin", lw=4, sheet_pin=True):
    e = EXPR[expr]
    g_open(S, x, y, s)
    sk, sd = P["skin"]
    # ears
    for sx in (-1, 1):
        cel(S, ell(94 * sx, 4, 17, 28), sk, sd, -6 * sx, -4, lw)
        line(S, f"M{89 * sx},{-10} Q{101 * sx},{4} {91 * sx},{20}", 3, op=0.7)
    hc = cel(S, HEAD, sk, sd, -15, -10, lw)
    # shadow under the beanie cuff + a faint teen fuzz on the upper lip (no beard)
    S.add(f'<g clip-path="url(#{hc})"><path d="M-100,-70 L100,-70 L100,-50 Q0,-40 -100,-50 Z" fill="{sd}" opacity="0.6"/></g>')
    # messy wavy hair escaping the beanie: short sideburns + lots of curls
    for sx in (-1, 1):
        fill(S, f"M{72 * sx},-74 L{98 * sx},-74 C{100 * sx},-52 {94 * sx},-32 {86 * sx},-18 C{86 * sx},-38 {80 * sx},-54 {72 * sx},-74 Z",
             P["hair"][0], lw=2.5)
        for hx, hy, k in ((104, -80, 1.0), (116, -68, 1.15), (110, -52, 0.9), (98, -90, 0.8)):
            fill(S, f"M{(hx - 16) * sx},{hy} q{20 * sx * k},{-8 * k} {26 * sx * k},{9 * k} q{-12 * sx * k},{-3 * k} {-16 * sx * k},{9 * k} Z",
                 P["hair"][0], lw=2)
    fill(S, "M-62,-74 C-64,-48 -44,-40 -40,-56 C-36,-38 -14,-40 -12,-58 C-6,-40 16,-42 16,-60 "
            "C22,-46 40,-48 40,-74 Z", P["hair"][0], lw=2.5)  # forehead curls
    for d in ("M-54,-66 q6,-7 14,-5", "M-30,-60 q6,-6 12,-3", "M-6,-62 q6,-6 12,-3", "M20,-64 q6,-5 12,-2",
              "M-102,-84 q6,-4 12,-2", "M96,-84 q6,-4 12,-2", "M84,-62 q4,8 2,16", "M-90,-62 q-4,8 -2,16"):
        line(S, d, 2.4, P["shine"], 0.85)
    # beanie: dome (ribbed), cuff, pom-pom, chai-glass pin
    dome = "M-110,-76 C-118,-172 -56,-210 0,-210 C56,-210 118,-172 110,-76 Z"
    cel(S, dome, P["beanie"][0], P["beanie"][1], -18, -10, lw)
    for k in range(-5, 6):
        x = k * 20
        line(S, f"M{x * 1.02},-82 Q{x * 0.82},-150 {x * 0.34},-200", 2, P["beanie"][1], op=0.7)
    cuff = "M-118,-108 Q0,-122 118,-108 L114,-68 Q0,-80 -114,-68 Z"
    cel(S, cuff, P["cuff"][0], P["cuff"][1], -10, -6, lw)
    for k in range(-10, 11):
        x = k * 10.5
        line(S, f"M{x},{-112 - 4 * (1 - (k / 11) ** 2)} L{x * 0.98},{-72 - 4 * (1 - (k / 11) ** 2)}", 1.8, P["cuff"][1], op=0.8)
    cel(S, fuzzy(0, -222, 32), P["pom"][0], P["pom"][1], -8, -8, lw)
    if sheet_pin:  # cutting-chai glass pin on the cuff
        g = "M50,-106 L76,-106 L72,-78 L54,-78 Z"
        fill(S, g, P["glass"], lw=2.5)
        fill(S, "M52,-98 L74,-98 L72,-80 L54,-80 Z", P["chai"])
        for k in range(4):
            line(S, f"M{55 + 5 * k},-104 L{56 + 4.4 * k},-80", 1.3, INK, 0.45)
        line(S, g, 2.5)
    for sx in (-1, 1):
        eye(S, 41 * sx, sx, e)
    for sx in (-1, 1):
        brow(S, sx, e)
    nose = "M-5,-6 C-8,14 -20,20 -17,32 C-13,43 10,44 17,34 C22,23 10,14 7,-6"
    cel(S, nose + " Z", sk, sd, -6, -6, 0, stroke=False)
    line(S, nose, lw)
    line(S, "M-12,32 Q-7,28 -3,34", 2.5)
    line(S, "M5,34 Q10,28 14,34", 2.5)
    fill(S, "M-36,56 Q-18,48 0,52 Q18,48 36,56 Q18,54 0,57 Q-18,54 -36,56 Z", P["hair"][0], op=0.35)  # peach fuzz
    mouth(S, e["mouth"])
    S.add(f'<circle cx="-58" cy="30" r="3.2" fill="#8a4a3a"/><circle cx="62" cy="-38" r="2.6" fill="#8a4a3a"/>')  # a couple of spots
    line(S, "M-70,38 Q-62,50 -66,58", 2.5, op=0.4)
    line(S, "M70,38 Q62,50 66,58", 2.5, op=0.4)
    g_close(S)


# ------------------------------------------------------------------ full body (origin = face centre)
def body(S, x, y, s=1.0, lw=4):
    """lanky teen: narrow shoulders, baggy hoodie on a skinny frame, skinny jeans, big sneakers"""
    g_open(S, x, y, s)
    hd, hdk = P["hoodie"]
    cel(S, "M-98,152 C-108,108 -50,96 0,100 C50,96 108,108 98,152 C66,166 -66,166 -98,152 Z", P["hood"][0], P["hood"][1], -8, -6, lw)
    cel(S, "M-24,112 L24,112 L26,160 L-26,160 Z", P["skin"][0], P["skin"][1], -8, 10, 0, stroke=False)  # thin neck
    # skinny jeans + big sneakers
    jeans = ("M-100,428 L100,428 C102,540 94,640 88,712 L22,712 C18,620 12,540 6,486 L-6,486 "
             "C-12,540 -18,620 -22,712 L-88,712 C-94,640 -102,540 -100,428 Z")
    cel(S, jeans, P["jeans"][0], P["jeans"][1], -10, 0, lw)
    line(S, "M0,440 L0,486", 3)
    for sx in (-1, 1):
        cel(S, f"M{-90 * sx},686 L{-20 * sx},686 L{-18 * sx},716 L{-92 * sx},716 Z", P["jcuff"], P["jeans"][1], -5 * sx, -4, lw)
        line(S, f"M{-80 * sx},584 q{16 * sx},8 {32 * sx},0", 2.5, op=0.6)
        line(S, f"M{-74 * sx},606 q{11 * sx},5 {22 * sx},-2", 2.5, op=0.6)
        line(S, f"M{-92 * sx},452 q{20 * sx},16 {42 * sx},8", 2.5, op=0.5)
        sh = (f"M{-98 * sx},714 C{-126 * sx},718 {-152 * sx},744 {-140 * sx},768 L{-8 * sx},768 "
              f"C{4 * sx},756 {0 * sx},728 {-16 * sx},714 Z")
        cel(S, sh, P["shoe"][0], P["shoe"][1], -8 * sx, -6, lw)
        fill(S, f"M{-142 * sx},756 L{-6 * sx},756 L{-8 * sx},772 L{-140 * sx},772 Z", P["sole"], lw=3)
        fill(S, f"M{-36 * sx},720 C{-26 * sx},730 {-22 * sx},742 {-30 * sx},754 L{-10 * sx},754 C{-2 * sx},738 {-8 * sx},724 {-16 * sx},716 Z",
             P["beanie"][0], lw=2.5)
        for k in range(3):
            line(S, f"M{(-98 + 13 * k) * sx},{730 - 2 * k} l{10 * sx},{-8}", 3, P["lace"])
        line(S, f"M{-130 * sx},756 q{28 * sx},-10 {64 * sx},-4", 2, op=0.4)
    # cream kurta peeking out under the hoodie, block-print border + side slits
    cel(S, "M-120,420 L120,420 L124,504 Q0,512 -124,504 Z", P["kurta"][0], P["kurta"][1], -10, -4, lw)
    fill(S, "M-123,486 Q0,494 123,486 L124,504 Q0,512 -124,504 Z", P["print_"][0], lw=2.5)
    for i in range(-5, 6):
        bx = i * 22
        fill(S, f"M{bx - 4},{500} C{bx - 9},{494} {bx - 4},{488} {bx + 1},{490} C{bx + 6},{492} {bx + 4},{499} {bx - 4},{500} Z", P["print_"][1])
    for sx in (-1, 1):
        line(S, f"M{110 * sx},470 L{112 * sx},506", 3)
    # baggy hoodie on a skinny frame: narrow shoulders, hangs long
    torso = ("M-60,130 C-98,134 -122,150 -128,190 C-138,264 -136,350 -132,420 L132,420 "
             "C136,350 138,264 128,190 C122,150 98,134 60,130 Z")
    cel(S, torso, hd, hdk, -16, -8, lw)
    cel(S, "M-134,408 Q0,422 134,408 L132,444 Q0,456 -132,444 Z", P["hood"][0], P["hood"][1], -8, -4, lw)
    for k in range(-6, 7):
        line(S, f"M{k * 20},418 L{k * 20},444", 1.6, P["hood"][1], 0.7)
    g_open(S, 54, 224, 0.82, -12)  # winged-sock print
    fill(S, "M-10,-26 L10,-26 L12,6 C30,8 36,22 26,30 C14,36 -6,30 -12,18 Z", "#f4d06f", lw=2.5, op=0.9)
    line(S, "M-10,-18 L10,-18 M-11,-10 L11,-10", 2.5, "#d9473c")
    fill(S, "M-12,-6 C-34,-24 -48,-12 -40,0 C-48,4 -40,16 -26,8 C-30,16 -18,18 -12,8 Z", "#fbfaf4", lw=2)
    g_close(S)
    for sx in (-1, 1):
        line(S, f"M{20 * sx},152 C{22 * sx},196 {16 * sx},228 {22 * sx},262", 7, INK)
        line(S, f"M{20 * sx},152 C{22 * sx},196 {16 * sx},228 {22 * sx},262", 3.5, P["white"])
        fill(S, f"M{16 * sx},260 L{28 * sx},260 L{27 * sx},278 L{17 * sx},278 Z", "#c9c8bf", lw=2.5)
    for wire in ("M-42,150 C-50,200 -52,236 -54,262", "M42,150 C52,196 58,228 60,250", "M-54,264 C-40,290 -6,296 8,308"):
        line(S, wire, 3.2, "#2b2b30")
    for bx, by in ((-54, 266), (60, 254)):
        fill(S, ell(bx, by, 7, 9), "#2b2b30", lw=2)
        S.add(f'<circle cx="{bx - 2}" cy="{by - 3}" r="2" fill="#8890a0"/>')
    for a, b, c, d in [(-96, 250, -80, 300), (96, 250, 82, 296), (-112, 336, -102, 380), (110, 340, 104, 380)]:
        line(S, f"M{a},{b} Q{(a + c) / 2 + 8},{(b + d) / 2} {c},{d}", 2.5, op=0.55)
    hose(S, [(118, 176), (140, 290), (78, 352)], 50, hd, lw)  # hand in pocket
    line(S, "M124,232 q8,14 4,30", 2.5, op=0.5)
    pocket = "M-84,306 Q0,292 84,306 L98,398 Q0,408 -98,398 Z"
    cel(S, pocket, hd, hdk, -10, -6, lw)
    line(S, "M-84,306 L-98,398", 5)
    line(S, "M84,306 L98,398", 5)
    line(S, "M-70,322 Q0,312 70,322", 2, op=0.4)
    hose(S, [(-118, 176), (-160, 304), (-196, 212)], 50, hd, lw)  # thumbs-up arm
    line(S, "M-140,272 q-4,16 8,26", 2.5, op=0.5)
    g_open(S, -196, 212, 0.82, -18)
    sleeve(S, 36)
    fill(S, "M-24,-22 L24,-22 L24,6 L-24,6 Z", P["skin"][0], lw=0)
    line(S, "M-25,-16 Q0,-12 25,-16", 4, P["band"])  # black thread
    line(S, "M-25,-5 Q0,-1 25,-5", 6, P["kalava"][0])  # red kalava thread
    S.add(f'<path d="M-25,-5 Q0,-1 25,-5" fill="none" stroke="{P["kalava"][1]}" stroke-width="2" stroke-dasharray="5 4"/>')
    g_open(S, 0, -18, 1, 0)
    hand_thumbs(S)
    g_close(S)
    g_close(S)
    g_close(S)



# ------------------------------------------------------------------ hands (wrist at origin, fingers point up = -y)
# Organic hands: one smooth silhouette per hand (Catmull-Rom through tapered, slightly bent fingers,
# webbing valleys, fleshy thumb pad and palm heel), not separate tubes.
def _smooth(pts, closed=True, t=1.0):
    n = len(pts)
    P_ = pts if closed else [pts[0]] + pts + [pts[-1]]
    m = len(P_)
    d = f"M{P_[0 if closed else 1][0]:.1f},{P_[0 if closed else 1][1]:.1f}"
    rng = range(n) if closed else range(1, m - 2)
    for i in rng:
        p0, p1, p2, p3 = P_[(i - 1) % m], P_[i % m], P_[(i + 1) % m], P_[(i + 2) % m]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * t, p1[1] + (p2[1] - p0[1]) / 6 * t)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * t, p2[1] - (p3[1] - p1[1]) / 6 * t)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + (" Z" if closed else "")


def _digit(base, ang, L, w0, w1, bend=0.0, n=7, wf=1.0):
    """tapered, gently bent finger: returns (left side base->tip, tip arc, right side tip->base, centreline)"""
    cx, cy = base
    cl, step = [], L / n
    for k in range(n + 1):
        t = k / n
        cl.append((cx, cy, t))
        a = math.radians(ang + bend * t)
        cx, cy = cx + math.sin(a) * step, cy - math.cos(a) * step
    left, right = [], []
    for x, y, t in cl[:-1]:
        a = math.radians(ang + bend * t)
        nx, ny = math.cos(a), math.sin(a)
        w = (w0 + (w1 - w0) * t) * wf * (1 + 0.05 * math.sin(math.pi * t * 2.6))  # slight knuckle swell
        left.append((x - nx * w / 2, y - ny * w / 2))
        right.append((x + nx * w / 2, y + ny * w / 2))
    tx, ty, _ = cl[-1]
    a = math.radians(ang + bend)
    r = w1 * wf / 2
    tip = []
    for k in range(5):  # round fingertip
        th = math.pi + math.pi * k / 4  # from left (-normal) over the top to right (+normal)
        ux, uy = math.cos(th), math.sin(th)
        # rotate (ux,uy) from local (normal, -dir) frame
        nx, ny = math.cos(a), math.sin(a)
        dx, dy = math.sin(a), -math.cos(a)
        tip.append((tx - dx * r * 0.6 + nx * ux * r - dx * uy * r, ty - dy * r * 0.6 + ny * ux * r - dy * uy * r))
    return left, tip, right[::-1], cl


FINGERS_OPEN = [  # base (x,y), angle, length, base width, tip width, bend
    ((-21, -50), -9, 54, 23, 18, 5), ((-2, -54), -2, 62, 24, 18.5, 3), ((16, -52), 6, 57, 23, 18, 1), ((32, -45), 15, 43, 19.5, 15.5, -2)]
THUMB_OPEN = ((-31, -6), -58, 44, 25, 18, 22)


def hand_outline(spread=1.0, wf=1.0, inset=0.0, curl=None):
    """closed silhouette of an open hand (palm toward viewer, thumb on the left)"""
    curl = curl or [0, 0, 0, 0]
    pts = [(-21 + inset, 32), (-35 + inset, 12)]
    tb, ta, tL, tw0, tw1, tbend = THUMB_OPEN
    l, tip, r, _ = _digit(tb, ta * spread, tL * (1 - inset / 60), tw0, tw1, tbend, wf=wf)
    pts += l[1:] + tip + r[:-1]
    pts.append((-26 + inset * 0.5, -40 + inset * 0.3))  # thumb-index web
    for i, ((bx, by), a, L, w0, w1, bend) in enumerate(FINGERS_OPEN):
        l, tip, r, _ = _digit((bx, by), a * spread, L * (1 - curl[i]) - inset * 0.6, w0, w1, bend + 40 * curl[i], wf=wf)
        pts += l + tip + r
        if i < 3:  # webbing valley between fingers
            nb = FINGERS_OPEN[i + 1][0]
            pts.append(((bx + nb[0]) / 2, (by + nb[1]) / 2 + 2 + inset * 0.3))
    pts += [(40 - inset, -22), (41 - inset, 4), (24 - inset, 32)]
    return _smooth(pts)


def sleeve(S, w=40):
    cel(S, f"M{-w},6 L{w},6 L{w - 4},34 L{-w + 4},34 Z", P["hood"][0], P["hood"][1], -4, -4, 4)


def _creases(S, spread, op=0.5, back=False):
    for (bx, by), a, L, w0, w1, bend in FINGERS_OPEN:
        _, _, _, cl = _digit((bx, by), a * spread, L, w0, w1, bend)
        for t in ((0.36, 0.64) if not back else (0.3, 0.58)):
            x, y, _ = cl[int(t * (len(cl) - 1))]
            aa = math.radians(a * spread + bend * t)
            nx, ny = math.cos(aa), math.sin(aa)
            w = (w0 + (w1 - w0) * t) * 0.32
            if back:  # knuckle wrinkles: two tiny arcs
                for o in (-2, 2):
                    line(S, f"M{x - nx * w:.1f},{y - ny * w + o:.1f} Q{x:.1f},{y - 3 + o:.1f} {x + nx * w:.1f},{y + ny * w + o:.1f}", 1.6, INK, 0.4)
            else:
                line(S, f"M{x - nx * w:.1f},{y - ny * w:.1f} Q{x:.1f},{y + 2.5:.1f} {x + nx * w:.1f},{y + ny * w:.1f}", 1.8, INK, op)


def _nails(S, spread):
    digits = [d for d in FINGERS_OPEN]
    for (bx, by), a, L, w0, w1, bend in digits:
        _, _, _, cl = _digit((bx, by), a * spread, L, w0, w1, bend)
        x, y, _ = cl[-2]
        aa = math.degrees(math.radians(a * spread + bend))
        S.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({aa:.1f})">'
              f'<path d="M-5.5,6 C-6.5,-2 -4,-8 0,-8.5 C4,-8 6.5,-2 5.5,6 Q0,8 -5.5,6 Z" fill="{P["nail"]}" stroke="{INK}" stroke-width="1.8"/>'
              f'<path d="M-2.5,-4 q2.5,-2 5,0" fill="none" stroke="#fff" stroke-width="1.3" opacity="0.7"/></g>')


def hand_open(S, spread=1.0, palm_side=True):
    outer = hand_outline(spread)
    if palm_side:
        # darker back-of-hand skin shows around the edges, lighter palm inside
        cid = cel(S, outer, P["skin"][0], P["skin"][1], -6, -5, 0, stroke=False)
        inner = hand_outline(spread, wf=0.7, inset=5)
        S.add(f'<g clip-path="url(#{cid})"><path d="{inner}" fill="{P["palm"][1]}"/>'
              f'<path d="{inner}" fill="{P["palm"][0]}" transform="translate(-4,-4)"/></g>')
        S.add(f'<path d="{outer}" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
        _creases(S, spread)
        line(S, "M-20,-34 C-4,-42 18,-40 34,-30", 2.2, INK, 0.45)       # heart line
        line(S, "M-26,-24 C-10,-26 6,-20 18,-10", 2.2, INK, 0.45)       # head line
        line(S, "M-20,-38 C-30,-20 -26,6 -12,22", 2.2, INK, 0.45)       # life line (around the thumb pad)
        line(S, "M2,22 C4,4 6,-10 6,-22", 1.6, INK, 0.25)               # faint fate line
        line(S, "M-38,-14 q8,4 10,12", 1.8, INK, 0.4)                   # thumb joint crease
    else:
        S.add('<g transform="scale(-1,1)">')
        cel(S, outer, P["skin"][0], P["skin"][1], -6, -5, 4)
        _creases(S, spread, back=True)
        _nails(S, spread)
        for x in (-14, 0, 14, 26):
            line(S, f"M{x * 0.9},-34 C{x},-20 {x * 0.7},-4 {x * 0.5},12", 1.6, INK, 0.2)  # tendons
        S.add("</g>")


def _blob(pts):
    return _smooth(pts, True, 1.0)


def hand_point(S):
    l, tip, r, cl = _digit((-14, -46), -3, 68, 23, 18, 4)
    idx = _smooth([(-26, -30)] + l + tip + r + [(-2, -30)])
    cel(S, idx, *P["skin"], -4, -4, 4)
    x, y, _ = cl[-2]
    S.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate(1)"><path d="M-5.5,6 C-6.5,-2 -4,-8 0,-8.5 C4,-8 6.5,-2 5.5,6 Q0,8 -5.5,6 Z" '
          f'fill="{P["nail"]}" stroke="{INK}" stroke-width="1.8"/></g>')
    for t in (0.34, 0.6):
        xx, yy, _ = cl[int(t * 7)]
        line(S, f"M{xx - 5},{yy} q5,-3 10,0", 1.6, INK, 0.45)
    fist = _blob([(-32, -40), (-24, -54), (-6, -56), (4, -60), (14, -56), (22, -58), (32, -50), (36, -28), (34, 4), (22, 26), (-20, 26), (-34, 6)])
    cel(S, fist, *P["skin"], -6, -6, 4)
    line(S, "M-4,-54 q4,8 0,16", 2, INK, 0.45)
    line(S, "M12,-54 q4,8 0,16", 2, INK, 0.45)
    line(S, "M-10,-26 C-6,-12 -8,2 -10,14", 1.6, INK, 0.2)
    line(S, "M10,-26 C12,-12 10,2 8,14", 1.6, INK, 0.2)
    l, tip, r, cl = _digit((-30, -10), 80, 40, 22, 17, 12)  # thumb tucked across the front
    cel(S, _smooth([(-34, 2)] + l + tip + r + [(-30, -22)]), *P["skin"], -4, -4, 3.5)
    x, y, _ = cl[-2]
    S.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate(92)"><path d="M-5,6 C-6,-2 -4,-8 0,-8 C4,-8 6,-2 5,6 Q0,8 -5,6 Z" '
          f'fill="{P["nail"]}" stroke="{INK}" stroke-width="1.8"/></g>')


def hand_thumbs(S):
    # side view: curled fingers as soft rolls of slightly different sizes, thumb up and bent back a little
    l, tip, r, cl = _digit((10, -58), 2, 56, 25, 19, -14)
    cel(S, _smooth([(0, -40)] + l + tip + r + [(26, -36)]), *P["skin"], -4, -4, 4)
    x, y, _ = cl[-2]
    S.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate(-10)"><path d="M-6,6 C-7,-2 -4.5,-9 0,-9.5 C4.5,-9 7,-2 6,6 Q0,8.5 -6,6 Z" '
          f'fill="{P["nail"]}" stroke="{INK}" stroke-width="1.8"/><path d="M-3,-5 q3,-2 6,0" fill="none" stroke="#fff" stroke-width="1.3" opacity="0.7"/></g>')
    line(S, f"M{cl[3][0] - 7},{cl[3][1] + 2} q7,-4 14,0", 1.8, INK, 0.45)
    back = _blob([(-16, -58), (8, -64), (28, -50), (32, -20), (28, 6), (8, 22), (-16, 20), (-24, -10)])
    cel(S, back, *P["skin"], -6, -6, 4)
    for k, (yy, ln) in enumerate(((-52, 36), (-36, 40), (-20, 38), (-5, 32))):  # curled finger rolls
        roll = _blob([(-12, yy - 6), (-12 - ln * 0.5, yy - 7), (-12 - ln, yy - 2), (-14 - ln, yy + 6), (-12 - ln * 0.9, yy + 10),
                      (-12 - ln * 0.4, yy + 10), (-12, yy + 9)])
        cel(S, roll, *P["skin"], -3, -3, 3.5)
        line(S, f"M{-12 - ln * 0.55},{yy - 4} q-3,6 0,12", 1.6, INK, 0.45)


def hand_fist(S):
    block = _blob([(-38, -44), (-30, -60), (32, -60), (40, -44), (40, 2), (26, 24), (-26, 24), (-40, 2)])
    cel(S, block, *P["skin"], -6, -6, 4)
    for i, h in enumerate((0, -4, -2, 4)):  # finger fronts, uneven
        x0 = -36 + 19 * i
        f = _blob([(x0, -26), (x0 - 1, -48 + h), (x0 + 9, -60 + h), (x0 + 19, -48 + h), (x0 + 18, -26), (x0 + 9, -22)])
        cel(S, f, *P["skin"], -3, -3, 3)
        line(S, f"M{x0 + 4},{-42 + h} q5,3 10,0", 1.6, INK, 0.45)
    l, tip, r, cl = _digit((-34, -14), 88, 52, 22, 17, 10)
    cel(S, _smooth([(-40, -2)] + l + tip + r + [(-36, -26)]), *P["skin"], -4, -4, 3.5)
    x, y, _ = cl[-2]
    S.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate(96)"><path d="M-5,6 C-6,-2 -4,-8 0,-8 C4,-8 6,-2 5,6 Q0,8 -5,6 Z" '
          f'fill="{P["nail"]}" stroke="{INK}" stroke-width="1.8"/></g>')


def hand_kya(S):
    """the 'kya?!' gesture: hand up, palm turned up and out, fingers loosely spread and curved, twisting"""
    g_open(S, 4, -10, 1, -16)
    hand_open(S, spread=1.3, palm_side=True)
    g_close(S)
    line(S, "M-58,-106 Q-24,-132 12,-118", 3, "#5a4a3c", 0.8)
    line(S, "M4,-126 l9,8 l-11,4", 3, "#5a4a3c", 0.8)
    line(S, "M62,-70 Q78,-40 66,-14", 3, "#5a4a3c", 0.8)


HAND_POSES = [("open", "open palm", lambda S: hand_open(S)), ("back", "back of hand", lambda S: hand_open(S, 0.85, False)),
              ("point", "pointing", hand_point), ("thumbs", "thumbs up", hand_thumbs), ("fist", "fist", hand_fist),
              ("kya", "“kya?!” gesture", hand_kya)]


# ------------------------------------------------------------------ sheet
def text(S, x, y, s, size=22, weight=400, col=INK, anchor="start", family="DejaVu Sans, Arial, sans-serif"):
    S.add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{col}" text-anchor="{anchor}">{s}</text>')


def sheet(path_svg):
    W, H = 2400, 1900
    S = SVG(W, H)
    S.add(f'<rect width="{W}" height="{H}" fill="#f3ead6"/>')
    for gx in range(0, W, 40):
        S.add(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}" stroke="#e6dbc2" stroke-width="1"/>')
    for gy in range(0, H, 40):
        S.add(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}" stroke="#e6dbc2" stroke-width="1"/>')
    text(S, 60, 86, "GABBY", 64, 800)
    text(S, 64, 126, "Shirley &amp; Gabby · character sheet · concept v3 (teen)", 24, 400, "#5a4a3c")
    # hero: full body (head drawn after body so it sits on the hood)
    body(S, 560, 475, 1.25)
    head(S, 560, 475, 1.25, "grin")
    S.add(f'<ellipse cx="560" cy="1446" rx="230" ry="20" fill="#000" opacity="0.08"/>')
    # expressions
    ex = [("grin", "excited"), ("shock", "shocked"), ("whine", "whiny"), ("scheme", "scheming"), ("deadpan", "unimpressed")]
    x0, y0 = 1170, 400
    text(S, x0 - 120, 120, "EXPRESSIONS", 30, 800)
    for i, (k, lab) in enumerate(ex):
        cx = x0 + (i % 3) * 330
        cy = y0 + (i // 3) * 440
        head(S, cx, cy, 0.85, k, sheet_pin=False)
        text(S, cx, cy + 172, lab, 24, 700, "#5a4a3c", "middle")
    # palette
    px, py = 1990, 640
    text(S, px - 30, py - 40, "PALETTE", 30, 800)
    sw = [("skin", P["skin"][0], P["skin"][1]), ("hair", P["hair"][0], P["hair"][1]), ("beanie", P["beanie"][0], P["beanie"][1]),
          ("hoodie", P["hoodie"][0], P["hoodie"][1]), ("jeans", P["jeans"][0], P["jeans"][1]), ("sneakers", P["shoe"][0], P["shoe"][1])]
    for i, (n, a, b) in enumerate(sw):
        yy = py + i * 64
        S.add(f'<rect x="{px - 30}" y="{yy}" width="56" height="48" rx="8" fill="{a}" stroke="{INK}" stroke-width="3"/>')
        S.add(f'<rect x="{px + 30}" y="{yy}" width="56" height="48" rx="8" fill="{b}" stroke="{INK}" stroke-width="3"/>')
        text(S, px + 100, yy + 20, n, 18, 700)
        text(S, px + 100, yy + 42, f"{a} / {b}", 15, 400, "#5a4a3c")
    # notes
    nx, ny = 1080, 1170
    # hands
    text(S, 60, 1555, "HANDS", 30, 800)
    text(S, 190, 1555, "4 fingers + thumb · nails on the back · lighter palms with lines · knuckle creases", 21, 400, "#5a4a3c")
    for i, (k, lab, fn) in enumerate(HAND_POSES):
        hx, hy = 220 + i * 390, 1765
        g_open(S, hx, hy, 1.55)
        fill(S, "M-22,-24 L22,-24 L22,10 L-22,10 Z", P["skin"][1], lw=0)  # wrist
        line(S, "M-22,-24 L-22,10 M22,-24 L22,10", 4)
        sleeve(S)
        g_open(S, 0, -6 if k == "thumbs" else 4, 1, 0)
        fn(S)
        g_close(S)
        g_close(S)
        text(S, hx, hy + 100, lab, 22, 700, "#5a4a3c", "middle")
    notes = [
        "16, Indian, lanky teen. Loud, optimistic, gullible; starts every adventure.",
        "Warm brown skin, slim oval face, big brown eyes, thick brows, a couple of spots.",
        "Thick wavy black hair escaping the beanie: sideburns and curls.",
        "No beard yet: just a faint fuzz on the lip. Characterful nose.",
        "Teal ribbed beanie with pom-pom and a cutting-chai glass pin.",
        "Red hoodie (hood, strings, pocket, winged-sock print) over a cream kurta with block-print border.",
        "Red kalava + black thread on the wrist, wired earphones, oiled curls. Skinny jeans, big sneakers.",
        "Moves fast and bouncy; overacts; does the \u201ckya?!\u201d hand twist. Voice: am_puck.",
    ]
    text(S, nx - 30, ny - 40, "DESIGN NOTES", 30, 800)
    for i, n in enumerate(notes):
        text(S, nx, ny + i * 36, "• " + n, 21, 400)
    open(path_svg, "w").write(S.out())


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    svg = os.path.join(here, "gabby_sheet.svg")
    sheet(svg)
    png = os.path.join(here, "gabby_sheet.png")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 2400, "height": 1900})
        pg.goto("file://" + svg)
        pg.screenshot(path=png)
        b.close()
    print(png)
