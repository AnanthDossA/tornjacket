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
    mouth="#3b1519", tongue="#d0625b", chai="#c98a3c", glass="#e8eef0", band="#141012", watch="#2b2b30")


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
HEAD = ("M-104,-80 C-112,-150 112,-150 104,-80 C116,-30 122,30 104,78 "
        "C88,116 48,132 0,132 C-48,132 -88,116 -104,78 C-122,30 -116,-30 -104,-80 Z")

EXPR = {
    "grin":   dict(brow=-4, ang=-6, lid=0.0, look=(4, 2), mouth="grin"),
    "shock":  dict(brow=-18, ang=-10, lid=0.0, look=(0, -4), mouth="shock", small_pupil=True),
    "whine":  dict(brow=-8, ang=16, lid=0.28, lidtilt=-14, look=(0, 6), mouth="whine"),
    "scheme": dict(brow=4, ang=-14, lid=0.45, lidtilt=6, look=(10, 0), mouth="smirk"),
    "deadpan": dict(brow=2, ang=0, lid=0.5, lidtilt=0, look=(0, 2), mouth="flat"),
}


def eye(S, ex, side, e):
    cx, cy, rx, ry = ex, -14, 33, 40
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
    xi, xo = 14 * s, 84 * s
    top = f"M{xi},{yi - 8} Q{(xi + xo) / 2},{min(yi, yo) - 20} {xo},{yo - 3}"
    bot = f"L{xo + 4 * s},{yo + 4} Q{(xi + xo) / 2},{min(yi, yo) - 4} {xi},{yi + 9} Z"
    fill(S, top + " " + bot, P["hair"][0], lw=2.5)
    for k in range(4):  # little hair flicks on top
        x = xi + (xo - xi) * (0.2 + 0.2 * k)
        y = yi + (yo - yi) * (0.2 + 0.2 * k) - 14
        line(S, f"M{x},{y + 4} l{6 * s},{-6}", 2.2, P["hair"][0])


def mouth(S, kind):
    if kind == "grin":
        d = "M-52,64 Q0,74 52,64 Q44,114 0,116 Q-44,114 -52,64 Z"
        cid = S.uid(); S.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        S.add(f'<path d="{d}" fill="{P["mouth"]}"/><g clip-path="url(#{cid})">'
              f'<rect x="-60" y="58" width="120" height="20" fill="{P["white"]}"/>'
              f'<path d="{ell(0, 118, 30, 18)}" fill="{P["tongue"]}"/></g>')
        S.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
        line(S, "M-58,58 Q-62,66 -54,70", 3)
        line(S, "M58,58 Q62,66 54,70", 3)
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
    # ears + hair curls behind
    for sx in (-1, 1):
        cel(S, ell(112 * sx, 6, 20, 30), sk, sd, -6 * sx, -4, lw)
        line(S, f"M{112 * sx - 6 * sx},{-8} Q{112 * sx + 8 * sx},{6} {112 * sx - 4 * sx},{22}", 3, op=0.7)
    # head (jowly), cel shaded
    hc = cel(S, HEAD, sk, sd, -16, -10, lw)
    # stubble + cheek shading, clipped to the head
    sid = S.uid("dots")
    S.defs.append(f'<pattern id="{sid}" width="9" height="9" patternUnits="userSpaceOnUse">'
                  f'<circle cx="2" cy="2" r="1.3" fill="{P["stub"]}"/><circle cx="6.5" cy="6" r="1.1" fill="{P["stub"]}"/></pattern>')
    jaw = "M-112,20 C-100,60 -70,52 -40,50 C-20,62 20,62 40,50 C70,52 100,60 112,20 L120,150 L-120,150 Z"
    S.add(f'<g clip-path="url(#{hc})"><path d="{jaw}" fill="{P["stub"]}" opacity="0.32"/><path d="{jaw}" fill="url(#{sid})" opacity="0.75"/>'
          f'<path d="M-104,-70 L104,-70 L104,-50 Q0,-40 -104,-50 Z" fill="{sd}" opacity="0.6"/></g>')
    # sideburns + hair flicks from under the beanie
    for sx in (-1, 1):
        d = (f"M{86 * sx},-74 L{118 * sx},-74 C{122 * sx},-44 {114 * sx},-14 {100 * sx},8 "
             f"C{102 * sx},-16 {96 * sx},-40 {86 * sx},-74 Z")
        fill(S, d, P["hair"][0], lw=2.5)
        for k, (hx, hy) in enumerate(((122, -78), (132, -66), (126, -52))):
            fill(S, f"M{(hx - 14) * sx},{hy} q{18 * sx},{-6} {22 * sx},{8} q{-10 * sx},{-2} {-14 * sx},{8} Z", P["hair"][0], lw=2)
    # forehead curls
    fill(S, "M-46,-74 C-46,-52 -28,-46 -26,-60 C-20,-44 -2,-46 0,-62 C6,-50 18,-52 16,-74 Z", P["hair"][0], lw=2.5)
    # beanie: dome (ribbed), cuff, pom-pom, chai-glass pin
    dome = "M-124,-76 C-132,-172 -62,-210 0,-210 C62,-210 132,-172 124,-76 Z"
    cel(S, dome, P["beanie"][0], P["beanie"][1], -18, -10, lw)
    for k in range(-5, 6):
        x = k * 22
        line(S, f"M{x * 1.05},-82 Q{x * 0.85},-150 {x * 0.35},-200", 2, P["beanie"][1], op=0.7)
    cuff = "M-132,-108 Q0,-122 132,-108 L128,-68 Q0,-80 -128,-68 Z"
    cel(S, cuff, P["cuff"][0], P["cuff"][1], -10, -6, lw)
    for k in range(-11, 12):
        x = k * 11
        line(S, f"M{x},{-112 - 4 * (1 - (k / 12) ** 2)} L{x * 0.98},{-72 - 4 * (1 - (k / 12) ** 2)}", 1.8, P["cuff"][1], op=0.8)
    cel(S, fuzzy(0, -222, 34), P["pom"][0], P["pom"][1], -8, -8, lw)
    if sheet_pin:  # cutting-chai glass pin on the cuff
        g = "M58,-106 L84,-106 L80,-78 L62,-78 Z"
        fill(S, g, P["glass"], lw=2.5)
        fill(S, "M60,-98 L82,-98 L80,-80 L62,-80 Z", P["chai"])
        for k in range(4):
            line(S, f"M{63 + 5 * k},-104 L{64 + 4.4 * k},-80", 1.3, INK, 0.45)
        line(S, "M58,-106 L84,-106 L80,-78 L62,-78 Z", 2.5)
    # brows, eyes, nose, moustache, mouth
    for sx in (-1, 1):
        eye(S, 45 * sx, sx, e)
    for sx in (-1, 1):
        brow(S, sx, e)
    nose = "M-6,-6 C-10,14 -24,20 -20,34 C-15,46 12,47 20,36 C26,24 12,14 8,-6"
    cel(S, nose + " Z", sk, sd, -6, -6, 0, stroke=False)
    line(S, nose, lw)
    line(S, "M-14,34 Q-8,30 -4,36", 2.5)
    line(S, "M6,36 Q12,30 16,36", 2.5)
    fill(S, "M-46,56 Q-22,42 0,48 Q22,42 46,56 Q24,52 0,57 Q-24,52 -46,56 Z", P["hair"][0], lw=2)  # thin moustache
    mouth(S, e["mouth"])
    line(S, "M-80,40 Q-70,52 -74,62", 2.5, op=0.45)  # cheek creases
    line(S, "M80,40 Q70,52 74,62", 2.5, op=0.45)
    g_close(S)


# ------------------------------------------------------------------ full body (origin = face centre)
def body(S, x, y, s=1.0, lw=4):
    g_open(S, x, y, s)
    hd, hdk = P["hoodie"]
    # hood bunched behind the neck
    cel(S, "M-118,150 C-130,104 -60,92 0,96 C60,92 130,104 118,150 C80,166 -80,166 -118,150 Z", P["hood"][0], P["hood"][1], -8, -6, lw)
    cel(S, "M-34,112 L34,112 L36,158 L-36,158 Z", P["skin"][0], P["skin"][1], -10, 10, 0, stroke=False)  # neck
    # legs (jeans) + sneakers
    jeans = "M-128,418 L128,418 C130,500 126,580 122,648 L22,648 C18,580 12,520 6,478 L-6,478 C-12,520 -18,580 -22,648 L-122,648 C-126,580 -130,500 -128,418 Z"
    cel(S, jeans, P["jeans"][0], P["jeans"][1], -12, 0, lw)
    line(S, "M0,430 L0,478", 3)
    for sx in (-1, 1):
        cel(S, f"M{-122 * sx},620 L{-22 * sx},620 L{-20 * sx},652 L{-124 * sx},652 Z", P["jcuff"], P["jeans"][1], -6 * sx, -4, lw)
        line(S, f"M{-108 * sx},540 q{20 * sx},10 {40 * sx},0", 2.5, op=0.6)
        line(S, f"M{-100 * sx},565 q{14 * sx},6 {28 * sx},-2", 2.5, op=0.6)
        line(S, f"M{-118 * sx},440 q{24 * sx},18 {50 * sx},10", 2.5, op=0.5)
        # sneaker
        sh = (f"M{-128 * sx},650 C{-150 * sx},654 {-172 * sx},678 {-160 * sx},700 L{-12 * sx},700 "
              f"C{-2 * sx},690 {-4 * sx},664 {-20 * sx},650 Z")
        cel(S, sh, P["shoe"][0], P["shoe"][1], -8 * sx, -6, lw)
        fill(S, f"M{-162 * sx},690 L{-10 * sx},690 L{-12 * sx},704 L{-160 * sx},704 Z", P["sole"], lw=3)
        fill(S, f"M{-40 * sx},656 C{-30 * sx},664 {-26 * sx},676 {-34 * sx},688 L{-14 * sx},688 C{-6 * sx},672 {-12 * sx},660 {-20 * sx},652 Z",
             P["beanie"][0], lw=2.5)  # teal heel panel
        for k in range(3):
            line(S, f"M{(-120 + 14 * k) * sx},{664 - 2 * k} l{10 * sx},{-8}", 3, P["lace"])
        line(S, f"M{-150 * sx},690 q{30 * sx},-10 {70 * sx},-4", 2, op=0.4)
    # torso
    torso = ("M-74,128 C-122,132 -152,150 -160,192 C-172,262 -168,340 -162,412 L162,412 "
             "C168,340 172,262 160,192 C152,150 122,132 74,128 Z")
    cel(S, torso, hd, hdk, -18, -8, lw)
    cel(S, "M-164,400 Q0,414 164,400 L162,436 Q0,448 -162,436 Z", P["hood"][0], P["hood"][1], -8, -4, lw)  # hem band
    for k in range(-7, 8):
        line(S, f"M{k * 21},{410 + 0.004 * (k * 21) ** 2 * 0 + 8} L{k * 21},{436}", 1.6, P["hood"][1], 0.7)
    # winged-sock print (faded)
    g_open(S, 64, 222, 0.9, -12)
    fill(S, "M-10,-26 L10,-26 L12,6 C30,8 36,22 26,30 C14,36 -6,30 -12,18 Z", "#f4d06f", lw=2.5, op=0.9)
    line(S, "M-10,-18 L10,-18 M-11,-10 L11,-10", 2.5, "#d9473c")
    fill(S, "M-12,-6 C-34,-24 -48,-12 -40,0 C-48,4 -40,16 -26,8 C-30,16 -18,18 -12,8 Z", "#fbfaf4", lw=2)
    g_close(S)
    # drawstrings
    for sx in (-1, 1):
        line(S, f"M{22 * sx},150 C{24 * sx},190 {18 * sx},220 {24 * sx},250", 7, INK)
        line(S, f"M{22 * sx},150 C{24 * sx},190 {18 * sx},220 {24 * sx},250", 3.5, P["white"])
        fill(S, f"M{18 * sx},248 L{30 * sx},248 L{29 * sx},266 L{19 * sx},266 Z", "#c9c8bf", lw=2.5)
    fold = [(-120, 250, -100, 300), (120, 250, 104, 296), (-140, 330, -128, 372), (138, 336, 130, 374)]
    for a, b, c, d in fold:
        line(S, f"M{a},{b} Q{(a + c) / 2 + 8},{(b + d) / 2} {c},{d}", 2.5, op=0.55)
    # arm into pocket (his left = screen right)
    hose(S, [(146, 176), (172, 286), (100, 348)], 66, hd, lw)
    line(S, "M150,230 q10,14 6,30", 2.5, op=0.5)
    # kangaroo pocket (covers the hand)
    pocket = "M-104,300 Q0,286 104,300 L120,392 Q0,402 -120,392 Z"
    cel(S, pocket, hd, hdk, -10, -6, lw)
    line(S, "M-104,300 L-120,392", 5)
    line(S, "M104,300 L120,392", 5)
    line(S, "M-86,316 Q0,306 86,316", 2, op=0.4)
    # thumbs-up arm (his right = screen left): upper arm down, forearm up
    hose(S, [(-146, 176), (-194, 300), (-232, 206)], 66, hd, lw)
    line(S, "M-170,268 q-4,16 8,26", 2.5, op=0.5)
    # sleeve cuff + black thread band + fist with thumb up
    g_open(S, -232, 206, 1.0, -18)
    cel(S, "M-36,-6 L36,-6 L32,18 L-32,18 Z", P["hood"][0], P["hood"][1], -4, -4, lw)
    fill(S, "M-24,-16 L24,-16 L24,-6 L-24,-6 Z", P["skin"][0], lw=0)
    line(S, "M-24,-12 Q0,-8 24,-12", 4, P["band"])  # black thread wristband
    palm = "M-26,-14 C-30,-50 -18,-70 6,-70 C28,-68 34,-44 30,-14 Z"
    cel(S, palm, P["skin"][0], P["skin"][1], -8, -6, lw)
    for k in range(4):  # curled fingers, knuckles toward camera
        yk = -62 + 13 * k
        cel(S, f"M-40,{yk} C-46,{yk} -46,{yk + 13} -40,{yk + 13} L-6,{yk + 13} C0,{yk + 13} 0,{yk} -6,{yk} Z",
            P["skin"][0], P["skin"][1], -4, -3, 3.5)
    thumb = "M-2,-66 C-8,-96 -2,-122 14,-122 C30,-122 30,-96 22,-66 Z"
    cel(S, thumb, P["skin"][0], P["skin"][1], -6, -5, lw)
    line(S, "M6,-114 q8,-3 14,2", 2.5, op=0.6)
    g_close(S)
    g_close(S)


# ------------------------------------------------------------------ sheet
def text(S, x, y, s, size=22, weight=400, col=INK, anchor="start", family="DejaVu Sans, Arial, sans-serif"):
    S.add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{col}" text-anchor="{anchor}">{s}</text>')


def sheet(path_svg):
    W, H = 2400, 1500
    S = SVG(W, H)
    S.add(f'<rect width="{W}" height="{H}" fill="#f3ead6"/>')
    for gx in range(0, W, 40):
        S.add(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}" stroke="#e6dbc2" stroke-width="1"/>')
    for gy in range(0, H, 40):
        S.add(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}" stroke="#e6dbc2" stroke-width="1"/>')
    text(S, 60, 86, "GABBY", 64, 800)
    text(S, 64, 126, "Shirley &amp; Gabby · character sheet · concept v1", 24, 400, "#5a4a3c")
    # hero: full body (head drawn after body so it sits on the hood)
    body(S, 560, 470, 1.25)
    head(S, 560, 470, 1.25, "grin")
    S.add(f'<ellipse cx="560" cy="1350" rx="260" ry="22" fill="#000" opacity="0.08"/>')
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
    px, py = 2010, 880
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
    notes = [
        "22, Indian. Loud, optimistic, gullible; starts every adventure.",
        "Warm brown skin, jowly round face, big brown eyes, thick bushy brows.",
        "Thick wavy black hair escaping the beanie: sideburns and curls.",
        "Thin moustache + stubble. Characterful nose. Cheek creases when he grins.",
        "Teal ribbed beanie with pom-pom and a cutting-chai glass pin.",
        "Red hoodie: hood, drawstrings, kangaroo pocket, faded winged-sock print.",
        "Black thread band on his right wrist. Rolled jeans, chunky white sneakers.",
        "Moves fast and bouncy; overacts. Voice: am_puck.",
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
        pg = b.new_page(viewport={"width": 2400, "height": 1500})
        pg.goto("file://" + svg)
        pg.screenshot(path=png)
        b.close()
    print(png)
