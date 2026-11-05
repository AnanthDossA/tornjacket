"""Gabby concept sheet (v1) - vector SVG generated in Python, rendered to PNG with Playwright.
Original character design for Shirley & Gabby: Gabby, 22, Indian, loud/optimistic/gullible.
    python3 gabby_sheet.py  ->  gabby_sheet.svg / gabby_sheet.png
"""
import math, os, sys

INK = "#1b1418"
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
def finger(S, x, y, ang, L, w, nail=False, creases=2, palm=False):
    lit, dk = P["palm"] if palm else P["skin"]
    g_open(S, x, y, 1, ang)
    d = f"M{-w / 2},6 L{-w / 2},{-L + w / 2} A{w / 2},{w / 2} 0 0 1 {w / 2},{-L + w / 2} L{w / 2},6 Z"
    cel(S, d, lit, dk, -4, -2, 3.5)
    if nail:
        nw, nh = w * 0.62, w * 0.62
        fill(S, f"M{-nw / 2},{-L + w * 0.22 + nh} L{-nw / 2},{-L + w * 0.22 + nw / 2} A{nw / 2},{nw / 2} 0 0 1 {nw / 2},{-L + w * 0.22 + nw / 2} "
                f"L{nw / 2},{-L + w * 0.22 + nh} Q0,{-L + w * 0.22 + nh + 3} {-nw / 2},{-L + w * 0.22 + nh} Z", P["nail"], lw=2)
        line(S, f"M{-nw / 4},{-L + w * 0.22 + nw / 2} q{nw / 4},-3 {nw / 2},0", 1.4, "#ffffff", 0.7)
    for k in range(creases):
        yy = -L * (0.42 + 0.27 * k)
        line(S, f"M{-w * 0.28},{yy} Q0,{yy + 3} {w * 0.28},{yy}", 2, INK, 0.55)
    g_close(S)


def sleeve(S, w=40):
    cel(S, f"M{-w},6 L{w},6 L{w - 4},34 L{-w + 4},34 Z", P["hood"][0], P["hood"][1], -4, -4, 4)


def hand_open(S, spread=1.0, palm_side=True):
    fs = [(-23, -50, -10, 58, 20), (-7, -55, -2, 68, 21), (10, -53, 6, 63, 20), (25, -46, 15, 49, 17)]
    for x, y, a, L, w in fs:
        finger(S, x, y, a * spread, L, w, nail=not palm_side, palm=palm_side)
    palm = "M-35,-56 C-40,-20 -34,14 -16,22 C4,30 28,24 35,4 C41,-20 40,-46 35,-56 Q0,-64 -35,-56 Z"
    cel(S, palm, *(P["palm"] if palm_side else P["skin"]), -6, -6, 4)
    if palm_side:
        line(S, "M-28,-32 Q2,-42 31,-34", 2.2, INK, 0.45)
        line(S, "M-32,-18 Q-6,-24 20,-10", 2.2, INK, 0.45)
        line(S, "M-22,-40 Q-30,-4 -12,18", 2.2, INK, 0.45)
    else:
        for x in (-16, 0, 16):
            line(S, f"M{x},-44 L{x * 0.7},-6", 2, INK, 0.25)
    finger(S, -32, -8, -58 * spread, 46, 22, nail=not palm_side, creases=1, palm=palm_side)


def hand_point(S):
    finger(S, -16, -48, -4, 74, 21, nail=True)
    fist = "M-31,-50 C-32,-66 26,-68 31,-50 L33,4 C31,20 -31,20 -33,4 Z"
    cel(S, fist, *P["skin"], -6, -6, 4)
    line(S, "M-6,-58 q8,-9 16,0 q8,-9 16,0", 3)
    for x in (2, 18):
        line(S, f"M{x},-50 L{x},-32", 2, INK, 0.5)
    for x in (-12, 4, 18):
        line(S, f"M{x},-28 L{x * 0.8},0", 2, INK, 0.25)
    finger(S, -32, -14, 84, 44, 20, nail=True, creases=1)


def hand_thumbs(S):
    palm = "M-26,-14 C-30,-50 -18,-70 6,-70 C28,-68 34,-44 30,-14 Z"
    cel(S, palm, *P["skin"], -8, -6, 4)
    for k in range(4):
        yk = -62 + 13.5 * k
        cel(S, f"M-42,{yk} C-49,{yk} -49,{yk + 13} -42,{yk + 13} L-4,{yk + 13} C2,{yk + 13} 2,{yk} -4,{yk} Z", *P["skin"], -4, -3, 3.5)
        line(S, f"M-22,{yk + 3} L-22,{yk + 10}", 1.8, INK, 0.5)
    finger(S, 10, -64, 4, 58, 24, nail=True, creases=1)


def hand_fist(S):
    block = "M-40,-52 C-42,-66 40,-66 40,-52 L40,4 C38,20 -38,20 -40,4 Z"
    cel(S, block, *P["skin"], -6, -6, 4)
    for i in range(4):
        x0 = -40 + 20 * i
        cel(S, f"M{x0 + 1},-30 L{x0 + 1},-54 Q{x0 + 10},-66 {x0 + 19},-54 L{x0 + 19},-30 Z", *P["skin"], -3, -3, 3)
        line(S, f"M{x0 + 5},-42 Q{x0 + 10},-39 {x0 + 15},-42", 1.8, INK, 0.5)
    finger(S, -38, -16, 92, 56, 21, nail=True, creases=1)


def hand_kya(S):
    """the 'kya?!' gesture: hand up, palm turned up, fingers loosely spread, twisting"""
    g_open(S, 4, -12, 1, -16)
    hand_open(S, spread=1.25, palm_side=True)
    g_close(S)
    line(S, "M-70,-96 Q-40,-128 -2,-120", 3, "#5a4a3c", 0.8)
    line(S, "M-8,-128 l8,8 l-10,4", 3, "#5a4a3c", 0.8)
    line(S, "M58,-70 Q76,-40 64,-14", 3, "#5a4a3c", 0.8)


HAND_POSES = [("open", "open palm", lambda S: hand_open(S)), ("back", "back of hand", lambda S: hand_open(S, 0.8, False)),
              ("point", "pointing", hand_point), ("thumbs", "thumbs up", hand_thumbs), ("fist", "fist", hand_fist),
              ("kya", "\u201ckya?!\u201d gesture", hand_kya)]


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
