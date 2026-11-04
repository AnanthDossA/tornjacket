"""Background sets for Shirley & Gabby (world coords, 1920x1080 reference, floor ~ y 960)."""
import math, random
import skia
import toon
from toon import C, fillp, strokep, smooth, oval, shape, shade, INK

SOCK_COLS = [(240, 240, 236), (90, 140, 230), (240, 170, 60), (150, 90, 200), (230, 90, 90), (90, 200, 150), (250, 220, 90), (60, 60, 70)]

def sock(cv, x, y, s, rot, col, stripes=None, line=4, blur=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    p = smooth([(-18, -60), (18, -60), (20, 10), (52, 30), (54, 50), (40, 62), (-6, 50), (-20, 20)], tension=0.6)
    if blur:
        cv.drawPath(p, fillp(col, blur=blur))
    else:
        shape(cv, p, col, line=line / max(s, 0.3), shadow=6, light=(1, -1))
        cv.save(); cv.clipPath(p, skia.ClipOp.kIntersect, True)
        cv.drawRect(skia.Rect.MakeLTRB(-30, -64, 30, -46), fillp(shade(col, 0.8)))
        if stripes:
            for k in range(3): cv.drawRect(skia.Rect.MakeLTRB(-30, -38 + k * 18, 30, -30 + k * 18), fillp(stripes))
        cv.drawPath(oval(44, 48, 14, 12), fillp(shade(col, 0.85)))
        cv.restore()
    cv.restore()

def sock_pile(cv, cx, base, w, h, seed, scale=1.0, blur=0, tint=None):
    rnd = random.Random(seed)
    n = int(w * h / 2600 * (1 / scale))
    for _ in range(n):
        u = rnd.random(); x = cx + (u - 0.5) * w
        top = base - h * (1 - (2 * (u - 0.5)) ** 2)
        y = rnd.uniform(top, base)
        col = rnd.choice(SOCK_COLS)
        if tint: col = toon.mix(col, tint[0], tint[1])
        sock(cv, x, y, scale * rnd.uniform(0.7, 1.2), rnd.uniform(0, 360), col,
             stripes=(rnd.choice(SOCK_COLS) if rnd.random() < 0.35 else None), line=3, blur=blur)

def sock_dimension(cv, t, cx, layer):
    """layer: 'sky' (p=0.2), 'far' (0.45), 'mid' (0.75), 'ground' (1.0), 'fg' (1.3)"""
    if layer == "sky":
        cv.drawRect(skia.Rect.MakeLTRB(-3000, -2000, 6000, 1600), skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [skia.Point(0, -100), skia.Point(0, 900)], [C((40, 16, 80)), C((120, 40, 150)), C((240, 110, 170))], [0, 0.55, 1])))
        # slow cosmic swirl
        sx, sy = 960, 260
        for k in range(10):
            a0 = t * 0.15 + k * 0.63
            p = skia.Path(); p.moveTo(sx, sy)
            for j in range(60):
                r = j * 14; a = a0 + j * 0.09
                p.lineTo(sx + r * math.cos(a), sy + r * math.sin(a) * 0.55)
            cv.drawPath(p, strokep((255, 200, 255), 10, a=26, blur=4))
        rnd = random.Random(2)
        for _ in range(90):
            x = rnd.uniform(-1500, 3500); y = rnd.uniform(-300, 650); tw = 0.5 + 0.5 * math.sin(t * 3 + x)
            cv.drawCircle(x, y, rnd.uniform(1.5, 3.5), fillp((255, 240, 255), int(120 + 120 * tw)))
        cv.drawCircle(1500, 160, 90, fillp((255, 220, 120), 90, blur=40))
        cv.drawCircle(1500, 160, 62, fillp((255, 236, 170)))
        sock(cv, 1500, 160, 0.9, 20, (255, 210, 120), line=0) if False else None
    elif layer == "far":
        for i, (x, w, h) in enumerate([(-900, 1100, 420), (200, 1300, 520), (1400, 1200, 460), (2500, 1300, 500), (3500, 1100, 430)]):
            p = smooth([(x - w / 2, 900), (x - w * 0.25, 900 - h * 0.7), (x, 900 - h), (x + w * 0.3, 900 - h * 0.65), (x + w / 2, 900)], tension=0.8)
            cv.drawPath(p, fillp((120, 60, 140)))
            sock_pile(cv, x, 900, w * 0.8, h * 0.85, 10 + i, scale=0.55, tint=((120, 60, 140), 0.65))
        cv.drawRect(skia.Rect.MakeLTRB(-3000, 700, 6000, 1000), fillp((240, 140, 190), 60, blur=50))
    elif layer == "mid":
        for i, x in enumerate(range(-1400, 4200, 900)):
            sock_pile(cv, x, 960, 700, 330, 30 + i, scale=0.8, tint=((150, 70, 160), 0.55))
        # the throne of socks
        tx = 1700
        sock_pile(cv, tx, 960, 520, 420, 99, scale=0.9)
        back = smooth([(tx - 150, 700), (tx - 170, 420), (tx - 60, 330), (tx + 60, 330), (tx + 170, 420), (tx + 150, 700)], tension=0.7)
        shape(cv, back, (52, 62, 160), shadow=14)
        for k in range(5): sock(cv, tx - 120 + k * 60, 370 + (k % 2) * 20, 0.7, 180 + (k - 2) * 12, SOCK_COLS[k + 1])
        cv.drawRect(skia.Rect.MakeLTRB(tx - 170, 690, tx + 170, 740), fillp((230, 190, 70)))
        cv.drawRect(skia.Rect.MakeLTRB(tx - 170, 690, tx + 170, 740), strokep(INK, 5))
        cv.drawString("HIS MAJESTY", tx - 105, 728, toon_font(36), fillp((120, 40, 60)))
    elif layer == "ground":
        cv.drawRect(skia.Rect.MakeLTRB(-3000, 930, 6000, 1700), fillp((170, 90, 160)))
        rnd = random.Random(7)
        for _ in range(260):
            x = rnd.uniform(-1800, 4200); y = rnd.uniform(940, 1250)
            sock(cv, x, y, rnd.uniform(0.55, 0.9), rnd.uniform(0, 360), toon.mix(rnd.choice(SOCK_COLS), (170, 90, 160), 0.35), line=3)
        # floating socks drift upward
        for k in range(14):
            rr = random.Random(100 + k); x = rr.uniform(-1200, 3600); sp = rr.uniform(25, 60)
            y = 900 - ((t * sp + rr.uniform(0, 900)) % 1100)
            sock(cv, x + 30 * math.sin(t * 0.8 + k), y, rr.uniform(0.5, 0.9), t * rr.uniform(-40, 40) + k * 30, rr.choice(SOCK_COLS), line=3)
    elif layer == "fg":
        rnd = random.Random(55)
        for k in range(6):
            x = -800 + k * 900 + rnd.uniform(-100, 100)
            sock(cv, x, 1130, 2.4, rnd.uniform(-40, 40), shade(rnd.choice(SOCK_COLS), 0.45), blur=6)

_F = {}
def toon_font(s):
    if s not in _F: _F[s] = skia.Font(skia.Typeface.MakeFromFile("/root/tj/fonts/Bangers-Regular.ttf"), s)
    return _F[s]

SOCK_LAYERS = [("sky", 0.2), ("far", 0.45), ("mid", 0.75), ("ground", 1.0)]

def portal(cv, W, H, k, t):
    """green swirl iris transition: k 0->1 closes to full green, 1->2 opens"""
    if k <= 0 or k >= 2: return
    cover = k if k <= 1 else 2 - k
    R = math.hypot(W, H) * 0.6
    cv.save(); cv.translate(W / 2, H / 2)
    cv.drawCircle(0, 0, R * 1.2, fillp((120, 255, 150), int(255 * min(1, cover * 1.6))))
    for j in range(14):
        a0 = t * 6 + j * 2 * math.pi / 14 + (k * 3)
        p = skia.Path(); p.moveTo(0, 0)
        for s in range(40):
            r = s / 40 * R * 1.2; a = a0 + s * 0.12
            p.lineTo(r * math.cos(a), r * math.sin(a))
        cv.drawPath(p, strokep((230, 255, 220), 22 * cover + 2, a=int(200 * cover)))
    cv.drawCircle(0, 0, R * (1 - cover) ** 2 * 0.0 + 30 * cover, fillp((255, 255, 255), int(255 * cover), blur=20))
    cv.restore()


# ================================================================== LAUNDROMAT
import os
FONT_B = "/root/tj/fonts/Bangers-Regular.ttf"; FONT_C = "/root/tj/fonts/Catamaran.ttf"
def font(p, s): return skia.Font(skia.Typeface.MakeFromFile(p), s)
FB, FC = font(FONT_B, 92), font(FONT_C, 30)
# ------------------------------------------------------------------ background (world coords)
WALL_P, FG_P = 0.82, 1.3
FLOOR_Y = 700
MACH = [(-500 + i * 236) for i in range(14)]
DRYER = 9  # index of the cursed dryer
rnd = random.Random(5)
RUNNING = {i for i in range(14) if rnd.random() < 0.5} | {DRYER}

def wall_layer(cv, t, glow):
    cv.drawRect(skia.Rect.MakeLTRB(-900, 80, 3600, FLOOR_Y), fillp((168, 210, 192)))
    cv.drawRect(skia.Rect.MakeLTRB(-900, 80, 3600, FLOOR_Y), fillp((0, 0, 0), shader=skia.GradientShader.MakeLinear([skia.Point(0, 80), skia.Point(0, FLOOR_Y)], [C((255, 255, 255), 40), C((0, 0, 0), 30)])))
    for yy in range(560, FLOOR_Y, 34): cv.drawLine(-900, yy, 3600, yy, strokep(shade((168, 210, 192), 0.88), 2))
    for xx in range(-900, 3600, 34): cv.drawLine(xx, 560, xx, FLOOR_Y, strokep(shade((168, 210, 192), 0.88), 2))
    cv.drawRect(skia.Rect.MakeLTRB(-900, 548, 3600, 562), fillp((120, 160, 150)))
    # ceiling + lights
    cv.drawRect(skia.Rect.MakeLTRB(-900, -200, 3600, 86), fillp((58, 60, 72)))
    for lx in range(-700, 3600, 520):
        flick = 0.45 if (lx == 1380 and int(t * 13) % 7 == 0) else 1.0
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(lx, 64, lx + 300, 84), 8, 8), fillp((250, 252, 240), int(255 * flick)))
        cv.drawRect(skia.Rect.MakeLTRB(lx - 40, 80, lx + 340, 200), fillp((255, 255, 230), int(40 * flick), blur=40))
    # neon sign
    txt = "SPIN CYCLE"; x0 = 560; y0 = 230
    for blur, a in ((22, 170), (8, 200)):
        cv.drawString(txt, x0, y0, FB, fillp((255, 70, 160), a, blur=blur))
    cv.drawString(txt, x0, y0, FB, fillp((255, 214, 236)))
    cv.drawString("OPEN 24 HRS   ·   NO DYEING", x0 + 30, y0 + 50, FC, fillp((60, 90, 84)))
    # poster: lost socks board
    px, py = 1700, 150
    cv.drawRect(skia.Rect.MakeLTRB(px, py, px + 230, py + 250), fillp((250, 244, 214)))
    cv.drawRect(skia.Rect.MakeLTRB(px, py, px + 230, py + 250), strokep(INK, 5))
    cv.drawString("LOST SOCKS?", px + 22, py + 50, font(FONT_B, 40), fillp((200, 50, 60)))
    for k in range(3):
        sx, sy = px + 40 + k * 60, py + 90 + (k % 2) * 30
        shape(cv, smooth([(sx, sy), (sx + 22, sy), (sx + 22, sy + 70), (sx + 40, sy + 92), (sx + 20, sy + 110), (sx, sy + 86)], tension=0.5), [(80, 140, 220), (240, 160, 60), (150, 90, 200)][k], line=3)
    cv.drawString("DON'T ASK.", px + 40, py + 232, font(FONT_C, 28), fillp(INK))
    # clock
    cv.drawCircle(300, 200, 54, fillp((250, 250, 244))); cv.drawCircle(300, 200, 54, strokep(INK, 6))
    a = t * 0.6; cv.drawLine(300, 200, 300 + 34 * math.sin(a), 200 - 34 * math.cos(a), strokep(INK, 5)); cv.drawLine(300, 200, 322, 190, strokep(INK, 6))
    # machines
    for i, mx in enumerate(MACH): machine(cv, i, mx, t, glow if i == DRYER else 0)

def machine(cv, i, mx, t, glow):
    x0, x1, y0, y1 = mx, mx + 210, 430, FLOOR_Y + 6
    body = (234, 234, 226)
    shape(cv, smooth([(x0, y0 + 10), (x0 + 10, y0), (x1 - 10, y0), (x1, y0 + 10), (x1, y1), (x0, y1)], tension=0.25), body, shadow=10, light=(1, -0.2))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 12, y0 + 12, x1 - 12, y0 + 52), fillp((210, 212, 206)))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 12, y0 + 12, x1 - 12, y0 + 52), strokep(INK, 3))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 24, y0 + 22, x0 + 84, y0 + 42), fillp((30, 40, 36)))
    on = i in RUNNING
    cv.drawString(f"{(int(t * 0.7) + 37 + i * 7) % 60:02d}" if on else "--", x0 + 34, y0 + 41, font(FONT_C, 22), fillp((90, 240, 140) if on else (90, 110, 100)))
    for k in range(2): cv.drawCircle(x1 - 40 - k * 40, y0 + 32, 12, fillp((190, 190, 196))); cv.drawCircle(x1 - 40 - k * 40, y0 + 32, 12, strokep(INK, 3))
    cx, cy, R = (x0 + x1) / 2, y0 + 165, 72
    cv.drawCircle(cx, cy, R + 14, fillp((196, 200, 210))); cv.drawCircle(cx, cy, R + 14, strokep(INK, 5))
    glass = oval(cx, cy, R, R)
    if glow > 0:
        g = toon.mix((40, 60, 70), (120, 255, 140), glow)
        cv.drawPath(glass, fillp(g, shader=skia.GradientShader.MakeRadial(skia.Point(cx, cy), R, [C((230, 255, 220)), C(g)])))
    else:
        cv.drawPath(glass, fillp((52, 70, 98)))
    cv.save(); cv.clipPath(glass, skia.ClipOp.kIntersect, True)
    if on:
        sp = t * (5.0 if glow < 0.5 else 11.0) + i
        for k, colr in enumerate([(220, 90, 80), (90, 140, 230), (240, 200, 70), (240, 240, 240)]):
            a = sp + k * 1.6; rr = 30 + 12 * math.sin(a * 0.7 + k)
            cv.drawPath(oval(cx + rr * math.cos(a), cy + 18 + rr * math.sin(a) * 0.6, 28, 18), fillp(colr, 230))
    cv.drawPath(oval(cx - 26, cy - 30, 26, 14), fillp((255, 255, 255), 70))
    cv.restore()
    cv.drawPath(glass, strokep(INK, 5))
    cv.drawRect(skia.Rect.MakeLTRB(cx + R + 4, cy - 14, cx + R + 18, cy + 14), fillp((150, 150, 158)))
    cv.drawString(str(i + 1), x0 + 16, y1 - 16, font(FONT_C, 24), fillp((120, 120, 120)))

def glow_fx(cv, glow, t):
    if glow <= 0.05: return
    cx = MACH[DRYER] + 105; cy = 595
    pulse = 0.85 + 0.15 * math.sin(t * 9)
    cv.drawCircle(cx, cy, 260 * glow * pulse, fillp((120, 255, 140), int(110 * glow), blur=80))
    if glow > 0.6:
        rr = random.Random(int(t * 12))
        for _ in range(int(14 * glow)):
            a = rr.uniform(0, 6.28); d = rr.uniform(90, 200)
            cv.drawPath(toon.star(cx + d * math.cos(a), cy + d * math.sin(a), rr.uniform(6, 14)), fillp((220, 255, 210), 220))

def floor_layer(cv, cam_x):
    cv.drawRect(skia.Rect.MakeLTRB(-1200, FLOOR_Y, 3800, 1400), fillp((214, 208, 196)))
    vx, vy = cam_x, 320
    ys = [FLOOR_Y + (1400 - FLOOR_Y) * ((k / 9) ** 1.7) for k in range(10)]
    for r in range(9):
        for c in range(-24, 25):
            def X(y, cc): return vx + (cc * 120 - 0) * (y - vy) / (FLOOR_Y - vy) + (cam_x * 0)
            ya, yb = ys[r], ys[r + 1]
            if (r + c) % 2: continue
            p = skia.Path(); p.moveTo(X(ya, c) + (cam_x - vx), ya)
            p.lineTo(X(ya, c + 1), ya); p.lineTo(X(yb, c + 1), yb); p.lineTo(X(yb, c), yb); p.close()
            cv.drawPath(p, fillp((186, 180, 170)))
    cv.drawRect(skia.Rect.MakeLTRB(-1200, FLOOR_Y, 3800, FLOOR_Y + 40), fillp((0, 0, 0), 50, blur=14))

def fg_layer(cv, t):
    # plastic chairs + laundry cart in the foreground (blurred, dark)
    cv.save(); cv.translate(0, 140); cv.scale(1.0, 1.0)
    for x, colr in ():
        p = smooth([(x, 960), (x + 130, 960), (x + 140, 1010), (x + 10, 1010)], tension=0.3)
        cv.drawPath(p, fillp(shade(colr, 0.55), blur=3)); cv.drawRect(skia.Rect.MakeLTRB(x + 10, 1010, x + 22, 1120), fillp((40, 40, 46), blur=3))
        cv.drawRect(skia.Rect.MakeLTRB(x + 115, 1010, x + 127, 1120), fillp((40, 40, 46), blur=3))
        cv.drawRect(skia.Rect.MakeLTRB(x + 4, 860, x + 130, 960), fillp(shade(colr, 0.5), blur=3))
    x = 2050
    cv.drawRect(skia.Rect.MakeLTRB(x, 900, x + 300, 1060), fillp((70, 70, 84), blur=3))
    for k in range(6): cv.drawLine(x + k * 60, 900, x + k * 60, 1060, strokep((110, 110, 124), 6, blur=2))
    for k, colr in enumerate([(240, 240, 240), (90, 140, 230), (220, 90, 80)]):
        cv.drawPath(oval(x + 70 + k * 80, 895, 70, 30), fillp(shade(colr, 0.7), blur=3))
    cv.restore()

