"""Layer-1 test: 'The Lost Sock' cold open in a laundromat. 1920x1080 @ 24fps."""
import sys, math, os, subprocess, random, json
sys.path.insert(0, "/root/sg"); sys.path.insert(0, "/root/tj")
import numpy as np, skia
from scipy.io import wavfile
from scipy.signal import lfilter
import toon
from toon import Track, C, fillp, strokep, smooth, oval, shape, shade, INK
from chars import SHIRLEY, GABBY

W, H, FPS = 1920, 1080, 24
OUT = "/root/sg/out"
PREVIEW = "--preview" in sys.argv
FONT_B = "/root/tj/fonts/Bangers-Regular.ttf"; FONT_C = "/root/tj/fonts/Catamaran.ttf"
def font(p, s): return skia.Font(skia.Typeface.MakeFromFile(p), s)
FB, FC = font(FONT_B, 92), font(FONT_C, 30)

# ------------------------------------------------------------------ voices
SR = 24000
LINES = [("G", "Shirl. Shirl! The dryer ate my sock. My lucky sock!", 1.08),
         ("S", "You've never been lucky.", 0.92),
         ("G", "Because it keeps getting eaten!", 1.1)]
cache = f"{OUT}/lines.npz"
if os.path.exists(cache):
    z = np.load(cache, allow_pickle=True); clips = list(z["clips"])
else:
    from voices import Voices
    V = Voices("/root/tj/models")
    clips = [V.say(txt, (GABBY if who == "G" else SHIRLEY)["voice"], spd) for who, txt, spd in LINES]
    np.savez(cache, clips=np.array(clips, dtype=object))
dur = [len(c) / SR for c in clips]

# ------------------------------------------------------------------ timeline
T_STOP = 3.9
t1 = 4.35; t2 = t1 + dur[0] + 0.45; t3 = t2 + dur[1] + 0.35; t_glow = t3 + dur[2] + 0.3
END = t_glow + 2.6
starts = [t1, t2, t3]
SHOTS = [  # (start, cam track (cx, cy, zoom))
    (0.0, Track([(0, (560, 640, 1.12)), (T_STOP + 0.2, (1000, 640, 1.12), "io")])),
    (t1 - 0.12, Track([(0, (1060, 560, 1.55)), (dur[0] + 0.4, (1080, 555, 1.62), "lin")])),
    (t2 - 0.1, Track([(0, (850, 540, 2.15)), (dur[1] + 0.3, (850, 540, 2.28), "lin")])),
    (t3 - 0.1, Track([(0, (1230, 610, 1.95)), (dur[2] + 0.3, (1230, 600, 2.1), "lin")])),
    (t_glow - 0.05, Track([(0, (1250, 620, 1.2)), (0.5, (1330, 600, 1.38), "snap"), (2.6, (1350, 600, 1.46), "lin")])),
]
GX = Track([(0, -150), (T_STOP - 0.3, 1250, "out")])
SX = Track([(0.5, -520), (T_STOP + 0.2, 820, "out")])
G_FACE = Track([(0, 1.0), (T_STOP - 0.1, 1.0), (T_STOP + 0.15, -0.75, "snap"), (t_glow, -0.75), (t_glow + 0.25, 0.85, "snap")])
S_FACE = Track([(0, 1.0), (t2 - 0.3, 1.0), (t2 - 0.1, 0.8), (t_glow + 0.1, 0.8), (t_glow + 0.4, 0.95)])
G_EXPR = Track([(0, "happy"), (t1 - 0.05, "panic"), (t2, "worried"), (t3, "angry"), (t_glow + 0.2, "starstruck")])
S_EXPR = Track([(0, "neutral"), (T_STOP, "deadpan"), (t2 - 0.4, "deadpan"), (t3 + 0.3, "annoyed"), (t_glow + 0.3, "worried")])
S_LID = Track([(0, 0.3), (t_glow + 0.2, 0.3), (t_glow + 0.35, 0.0, "snap")])
G_GEST = [("point_back", Track([(0, 0), (t1 + 1.0, 0), (t1 + 1.25, 1, "back"), (t1 + dur[0] - 0.1, 1), (t1 + dur[0] + 0.3, 0)])),
          ("shrug", Track([(0, 0), (t3 - 0.05, 0), (t3 + 0.2, 1, "back"), (t3 + dur[2], 1), (t3 + dur[2] + 0.3, 0)])),
          ("shrug", Track([(0, 0), (t_glow + 0.3, 0), (t_glow + 0.6, 0.6, "back")]))]
S_GEST = [("arms_crossed", Track([(0, 0), (T_STOP + 0.1, 0), (T_STOP + 0.5, 1, "back"), (t_glow, 1), (t_glow + 0.3, 0.3)]))]
G_LOOK = Track([(0, (1, 0)), (T_STOP + 0.2, (1, 0.1)), (t2, (1, 0.1)), (t2 + 0.1, (0.6, 0.3)), (t3, (1, 0)), (t_glow + 0.2, (1, -0.3))])
S_LOOK = Track([(0, (1, 0.1)), (t2 - 0.2, (1, 0)), (t3, (0.9, 0.2)), (t_glow + 0.3, (1, -0.2))])
GLOW = Track([(0, 0.15), (t_glow - 0.1, 0.2), (t_glow + 0.2, 1.0, "snap"), (END, 0.9)])

# ------------------------------------------------------------------ lip-sync tables
G_VIS, S_VIS = {}, {}
for (who, _, _), clip, st in zip(LINES, clips, starts):
    (G_VIS if who == "G" else S_VIS).update(toon.visemes(clip, SR, FPS, st, None))

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

# ------------------------------------------------------------------ characters
G, S = toon.Character(GABBY), toon.Character(SHIRLEY)
state = {"G": {"ph": 0.0, "px": GX(0)}, "S": {"ph": 1.4, "px": SX(0)}}
STRIDE = {"G": 2 * 4 * 90 * math.sin(math.radians(26)) * 0.5, "S": 2 * 4 * 104 * math.sin(math.radians(26)) * 0.5}
steps = []  # footstep times

def char_pose(key, t, xtrack, gests):
    st = state[key]; x = xtrack(t); dx = x - st["px"]; st["px"] = x
    speed = abs(dx) * FPS
    old = st["ph"]; st["ph"] += abs(dx) / STRIDE[key] * 2 * math.pi
    if int(old / math.pi) != int(st["ph"] / math.pi) and speed > 30: steps.append((t, key))
    w = min(1.0, speed / 160)
    p = toon.blend(toon.pose_idle(t, 1 if key == "S" else 0), toon.pose_walk(st["ph"], 1.0), w)
    for name, tr in gests:
        g = tr(t)
        if g > 0.001: p = toon.override(p, toon.GESTURES[name], g)
    return x, p

def face_for(char, vis, f, expr, look, lid=None):
    v, o = vis.get(f, ("X", 0.0))
    d = {"expr": expr, "look": look, "vis": v, "open": o, "blink": char.blink(f / FPS)}
    if lid is not None: d["lid"] = lid
    return d

# ------------------------------------------------------------------ render loop
def shot_at(t):
    cur = SHOTS[0]
    for s in SHOTS:
        if t >= s[0]: cur = s
    return cur[1](t - cur[0])

def render():
    os.makedirs(OUT, exist_ok=True)
    N = int(END * FPS) + 1
    frames = list(range(N))
    arr = np.zeros((H, W, 4), np.uint8); surf = skia.Surface(arr); cv = surf.getCanvas()
    grain = [np.random.default_rng(k).integers(-7, 8, (H, W, 1), dtype=np.int16) for k in range(4)]
    vign = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), W * 0.62, [C((0, 0, 0), 0), C((0, 0, 0), 0), C((20, 10, 30), 120)], [0, 0.6, 1.0])
    ff = None if PREVIEW else subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", f"{OUT}/video.mp4"], stdin=subprocess.PIPE)
    sheet = []
    for f in frames:
        t = f / FPS
        cx, cy, z = shot_at(t); glow = GLOW(t)
        gx, gp = char_pose("G", t, GX, G_GEST); sx, sp_ = char_pose("S", t, SX, S_GEST)
        cv.clear(C((30, 30, 40)))
        def layer(p, fn):
            cv.save(); cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-cx * p - (1 - p) * 960, -cy); fn(); cv.restore()
        layer(WALL_P, lambda: wall_layer(cv, t, glow))
        layer(1.0, lambda: floor_layer(cv, cx))
        layer(WALL_P, lambda: glow_fx(cv, glow, t))
        def chars():
            S.draw(cv, sx, 960, 1.0, sp_, S_FACE(t), face_for(S, S_VIS, f, S_EXPR(t), S_LOOK(t), S_LID(t)))
            G.draw(cv, gx, 985, 1.0, gp, G_FACE(t), face_for(G, G_VIS, f, G_EXPR(t), G_LOOK(t)))
        layer(1.0, chars)
        layer(FG_P, lambda: fg_layer(cv, t))
        if glow > 0.3:  # green spill over everything
            cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), fillp((80, 255, 120), int(38 * (glow - 0.3))))
        cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), skia.Paint(Shader=vign))
        if t < 0.5: cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), fillp((0, 0, 0), int(255 * (1 - t / 0.5))))
        img = arr[:, :, :3].astype(np.int16) + grain[f % 4]
        img = np.clip(img, 0, 255).astype(np.uint8)
        if ff: ff.stdin.write(img.tobytes())
        if PREVIEW and f % 12 == 0: sheet.append(img[::4, ::4].copy())
        if f % 48 == 0: print("frame", f, "/", N, flush=True)
    if ff: ff.stdin.close(); ff.wait()
    if PREVIEW:
        from PIL import Image
        cols = 6; rows = (len(sheet) + cols - 1) // cols; h, w = sheet[0].shape[:2]
        im = Image.new("RGB", (cols * w, rows * h))
        for k, s in enumerate(sheet): im.paste(Image.fromarray(s), ((k % cols) * w, (k // cols) * h))
        im.save(f"{OUT}/sheet.jpg", quality=85)
    return N

def audio(N):
    L = int(END * SR) + SR; mixd = np.zeros(L, np.float32); rng = np.random.default_rng(1)
    def add(sig, at, g=1.0):
        i = int(at * SR); n = min(len(sig), L - i)
        if n > 0: mixd[i:i + n] += sig[:n] * g
    # room tone: low rumble + hum + washer thumps
    noise = rng.standard_normal(L).astype(np.float32)
    rum = lfilter([0.02], [1, -0.98], noise); mixd += 0.6 * rum / (np.abs(rum).max() + 1e-9) * 0.05
    tt = np.arange(L) / SR; mixd += 0.006 * np.sin(2 * np.pi * 120 * tt)
    for k in np.arange(0.3, END, 0.62): add(np.exp(-np.arange(int(0.12 * SR)) / (0.03 * SR)) * np.sin(2 * np.pi * 55 * np.arange(int(0.12 * SR)) / SR), k, 0.05)
    # footsteps
    for t, key in steps:
        n = int(0.09 * SR); env = np.exp(-np.arange(n) / (0.015 * SR))
        s = lfilter([0.3], [1, -0.7], rng.standard_normal(n)) * env
        add(s.astype(np.float32), t, 0.22 if key == "G" else 0.15)
    for clip, st in zip(clips, starts): add(clip, st, 0.95)
    # glow: rising wub + sting
    n = int(2.4 * SR); tt2 = np.arange(n) / SR
    wub = np.sin(2 * np.pi * (60 + 40 * tt2) * tt2) * (0.5 + 0.5 * np.sin(2 * np.pi * 6 * tt2)) * np.minimum(1, tt2 * 4) * np.exp(-tt2 * 0.4)
    add(wub.astype(np.float32), t_glow, 0.25)
    sting = sum(np.sin(2 * np.pi * f0 * tt2) for f0 in (523, 659, 784, 1046)) * np.exp(-tt2 * 2.2)
    add(sting.astype(np.float32), t_glow + 0.05, 0.06)
    mixd = mixd / max(1.0, np.abs(mixd).max() / 0.95)
    wavfile.write(f"{OUT}/mix.wav", SR, (mixd * 32767).astype(np.int16))

if __name__ == "__main__":
    N = render()
    if not PREVIEW:
        audio(N)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/video.mp4", "-i", f"{OUT}/mix.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{OUT}/lost_sock_layer1.mp4"], check=True)
        print("done", END)
