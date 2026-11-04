"""Layer-1 (fixed) test: laundromat -> dryer portal -> Sock Dimension. 1920x1080 @ 24fps.
Lines can use recorded audio: put a wav path as the 4th item of a LINES entry."""
import sys, math, os, subprocess, random, json
sys.path.insert(0, "/root/sg"); sys.path.insert(0, "/root/tj")
import numpy as np, skia
from scipy.io import wavfile
from scipy.signal import lfilter, resample_poly
import toon, sets
from toon import Track, C, fillp, strokep
from chars import SHIRLEY, GABBY

W, H, FPS = 1920, 1080, 24; DT = 1 / FPS
OUT = "/root/sg/out"; PREVIEW = "--preview" in sys.argv

# ------------------------------------------------------------------ voices (TTS or recorded wav)
SR = 24000
LINES = [("G", "Shirl. Shirl! The dryer ate my sock. My lucky sock!", 1.08, None),
         ("S", "You've never been lucky.", 0.92, None),
         ("G", "Because it keeps getting eaten!", 1.1, None),
         ("G", "Shirl. It's beautiful. It's every sock I ever lost.", 1.0, None),
         ("S", "Why do they all smell like you?", 0.92, None)]
def load_wav(path):
    sr, a = wavfile.read(path); a = a.astype(np.float32)
    if a.ndim > 1: a = a.mean(1)
    a /= max(1e-6, np.abs(a).max()); g = math.gcd(sr, SR)
    return resample_poly(a, SR // g, sr // g).astype(np.float32) * 0.9
key = json.dumps([l[:3] for l in LINES]); cache = f"{OUT}/lines_ep.npz"
clips = None
if os.path.exists(cache):
    z = np.load(cache, allow_pickle=True)
    if str(z["key"]) == key: clips = list(z["clips"])
if clips is None:
    from voices import Voices
    V = Voices("/root/tj/models")
    clips = [V.say(txt, (GABBY if who == "G" else SHIRLEY)["voice"], spd) for who, txt, spd, _ in LINES]
    np.savez(cache, clips=np.array(clips, dtype=object), key=key)
clips = [load_wav(l[3]) if l[3] and os.path.exists(l[3]) else c for l, c in zip(LINES, clips)]
dur = [len(c) / SR for c in clips]

# ------------------------------------------------------------------ timeline
T_STOP = 3.9
t1 = 4.35; t2 = t1 + dur[0] + 0.45; t3 = t2 + dur[1] + 0.35; t_glow = t3 + dur[2] + 0.3
t_p = t_glow + 1.7                 # portal starts closing
t_sd = t_p + 0.55                  # Sock Dimension appears
g_land = t_sd + 0.75; s_land = g_land + 0.45
t4 = s_land + 0.7; t5 = t4 + dur[3] + 0.4
END = t5 + dur[4] + 1.3
starts = [t1, t2, t3, t4, t5]

SHOTS = [
    (0.0, "laund", Track([(0, (560, 640, 1.12)), (T_STOP + 0.2, (1000, 640, 1.12), "io")])),
    (t1 - 0.12, "laund", Track([(0, (1060, 560, 1.55)), (dur[0] + 0.4, (1080, 555, 1.62), "lin")])),
    (t2 - 0.1, "laund", Track([(0, (850, 540, 2.15)), (dur[1] + 0.3, (850, 540, 2.28), "lin")])),
    (t3 - 0.1, "laund", Track([(0, (1230, 610, 1.95)), (dur[2] + 0.3, (1230, 600, 2.1), "lin")])),
    (t_glow - 0.05, "laund", Track([(0, (1250, 620, 1.2)), (0.5, (1330, 600, 1.38), "snap"), (t_p - t_glow + 0.6, (1420, 600, 1.9), "in")])),
    (t_sd, "sock", Track([(0, (1000, 520, 0.95)), (t4 - t_sd - 0.1, (1020, 560, 1.02), "io")])),
    (t4 - 0.1, "sock", Track([(0, (1110, 620, 1.75)), (dur[3] + 0.3, (1110, 610, 1.85), "lin")])),
    (t5 - 0.1, "sock", Track([(0, (830, 560, 2.15)), (dur[4] + 0.3, (830, 560, 2.3), "lin")])),
    (t5 + dur[4] + 0.25, "sock", Track([(0, (1000, 560, 1.15)), (1.2, (1000, 560, 1.05), "out")])),
]
# positions: (x track, ground y, fall offset track)
GX = Track([(0, -150), (T_STOP - 0.3, 1250, "out"), (t_sd - 0.01, 1250), (t_sd, 1090)])
SX = Track([(0.5, -520), (T_STOP + 0.2, 820, "out"), (t_sd - 0.01, 820), (t_sd, 830)])
G_Y = Track([(0, 985), (t_sd - 0.01, 985), (t_sd, 1000)]); S_Y = Track([(0, 960), (t_sd - 0.01, 960), (t_sd, 980)])
G_FALL = Track([(0, 0), (t_sd - 0.01, 0), (t_sd, -1300), (g_land - 0.45, -1300), (g_land, 0, "in")])
S_FALL = Track([(0, 0), (t_sd - 0.01, 0), (t_sd, -1300), (s_land - 0.45, -1300), (s_land, 0, "in")])
def land_tracks(tl):
    sq = Track([(0, 1.0), (tl - 0.12, 1.0), (tl - 0.01, 1.12), (tl, 0.82), (tl + 0.12, 1.06, "out"), (tl + 0.26, 0.98), (tl + 0.4, 1.0)])
    w = Track([(0, 0), (tl - 0.01, 0), (tl + 0.03, 1, "snap"), (tl + 0.25, 1), (tl + 0.55, 0)])
    return sq, w
G_SQ, G_LANDW = land_tracks(g_land); S_SQ, S_LANDW = land_tracks(s_land)
toon.GESTURES["land"] = {"thighL": 38, "kneeL": 74, "thighR": 30, "kneeR": 66, "bob": 34, "armL": 70, "elbowL": 30, "armR": 80, "elbowR": 25, "lean": 14,
                         "hands": {"L": "open", "R": "open"}}
toon.GESTURES["flail"] = {"armL": 160, "elbowL": 30, "armR": 150, "elbowR": -30, "thighL": 30, "kneeL": 60, "thighR": -10, "kneeR": 20, "hands": {"L": "open", "R": "open"}}
G_FLAIL = Track([(0, 0), (t_sd - 0.01, 0), (t_sd, 1), (g_land - 0.02, 1), (g_land, 0)])
S_FLAIL = Track([(0, 0), (t_sd - 0.01, 0), (t_sd, 1), (s_land - 0.02, 1), (s_land, 0)])

G_FACE = Track([(0, 1.0), (T_STOP - 0.1, 1.0), (T_STOP + 0.15, -0.75, "snap"), (t_glow, -0.75), (t_glow + 0.25, 0.85, "snap"), (t4 + 1.0, 0.85), (t4 + 1.25, -0.8, "snap")])
S_FACE = Track([(0, 1.0), (t2 - 0.3, 1.0), (t2 - 0.1, 0.8), (t_glow + 0.1, 0.8), (t_glow + 0.4, 0.95)])
G_EXPR = Track([(0, "happy"), (t1 - 0.05, "panic"), (t2, "worried"), (t3, "angry"), (t_glow + 0.2, "starstruck"), (t_sd, "panic"), (g_land + 0.5, "starstruck"), (t5 + dur[4], "happy")])
S_EXPR = Track([(0, "neutral"), (T_STOP, "deadpan"), (t3 + 0.3, "annoyed"), (t_glow + 0.3, "worried"), (t_sd, "panic"), (s_land + 0.4, "annoyed"), (t5, "deadpan")])
S_LID = Track([(0, 0.3), (t_glow + 0.2, 0.3), (t_glow + 0.35, 0.0, "snap"), (s_land + 0.3, 0.0), (s_land + 0.6, 0.38)])
G_GEST = [("point_back", Track([(0, 0), (t1 + 1.0, 0), (t1 + 1.25, 1, "back"), (t1 + dur[0] - 0.1, 1), (t1 + dur[0] + 0.3, 0)])),
          ("fists", Track([(0, 0), (t3 - 0.05, 0), (t3 + 0.2, 1, "back"), (t3 + dur[2], 1), (t3 + dur[2] + 0.3, 0)])),
          ("present", Track([(0, 0), (t_glow + 0.3, 0), (t_glow + 0.6, 1, "back"), (t_p, 1), (t_p + 0.2, 0)])),
          ("shrug", Track([(0, 0), (t4 + 0.1, 0), (t4 + 0.4, 1, "back"), (t4 + dur[3], 1), (t4 + dur[3] + 0.4, 0)])),
          ("flail", G_FLAIL), ("land", G_LANDW)]
S_GEST = [("arms_crossed", Track([(0, 0), (T_STOP + 0.1, 0), (T_STOP + 0.5, 1, "back"), (t_glow, 1), (t_glow + 0.3, 0), (s_land + 0.6, 0), (s_land + 0.95, 1, "back")])),
          ("flail", S_FLAIL), ("land", S_LANDW)]
G_LOOK = Track([(0, (1, 0)), (T_STOP + 0.2, (1, 0.1)), (t2, (1, 0.1)), (t2 + 0.1, (0.6, 0.3)), (t3, (1, 0)), (t_glow + 0.2, (1, -0.3)), (t_sd, (0, -1)), (g_land, (1, -0.4))])
S_LOOK = Track([(0, (1, 0.1)), (t2 - 0.2, (1, 0)), (t3, (0.9, 0.2)), (t_glow + 0.3, (1, -0.2)), (t_sd, (0, -1)), (s_land, (1, 0.1))])
GLOW = Track([(0, 0.15), (t_glow - 0.1, 0.2), (t_glow + 0.2, 1.0, "snap"), (t_p, 1.0)])
PORTAL = Track([(0, 0), (t_p, 0), (t_sd, 1.0, "in"), (t_sd + 0.5, 2.0, "out")])

G_VIS, S_VIS = {}, {}
for (who, *_), clip, st in zip(LINES, clips, starts):
    (G_VIS if who == "G" else S_VIS).update(toon.visemes(clip, SR, FPS, st, None))

# ------------------------------------------------------------------ characters
G, S = toon.Character(GABBY), toon.Character(SHIRLEY)
state = {"G": {"ph": 0.0, "px": GX(0)}, "S": {"ph": 1.4, "px": SX(0)}}
STRIDE = {"G": 170.0, "S": 190.0}
steps = []

def char_pose(key, ch, t, xt, gests, sqt, facing, expr):
    st = state[key]; x = xt(t); dx = x - st["px"]; st["px"] = x
    if abs(dx) > 60: dx = 0  # teleport between sets
    speed = abs(dx) * FPS; old = st["ph"]; st["ph"] += abs(dx) / STRIDE[key] * 2 * math.pi
    if int(old / math.pi) != int(st["ph"] / math.pi) and speed > 30: steps.append((t, key))
    p = toon.blend(toon.pose_idle(t, 1 if key == "S" else 0), toon.pose_walk(st["ph"], 1.0), min(1.0, speed / 160))
    for name, tr in gests: p = toon.apply_gesture(p, name, tr, t)
    p["sq"] = p.get("sq", 1) * sqt(t)
    if abs(xt(t) - xt(t - DT)) > 60: ch.px = x
    ch.update(t, x, DT, p, facing, expr)
    return x, p

def face_for(ch, vis, f, expr, look, lid=None):
    v, o = vis.get(f, ("X", 0.0))
    d = {"expr": expr, "look": look, "vis": v, "open": o, "blink": ch.blink(f / FPS)}
    if lid is not None: d["lid"] = lid
    return d

def shot_at(t):
    cur = SHOTS[0]
    for s in SHOTS:
        if t >= s[0]: cur = s
    return cur[1], cur[2](t - cur[0])

def render():
    N = int(END * FPS) + 1
    arr = np.zeros((H, W, 4), np.uint8); cv = skia.Surface(arr).getCanvas()
    grain = [np.random.default_rng(k).integers(-6, 7, (H, W, 1), dtype=np.int16) for k in range(4)]
    vign = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), W * 0.62, [C((0, 0, 0), 0), C((0, 0, 0), 0), C((20, 10, 30), 120)], [0, 0.6, 1.0])
    ff = None if PREVIEW else subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", f"{OUT}/ep_video.mp4"], stdin=subprocess.PIPE)
    sheet = []
    for f in range(N):
        t = f / FPS
        world, (cx, cy, z) = shot_at(t); glow = GLOW(t)
        gfa, sfa = G_FACE(t), S_FACE(t); ge, se = G_EXPR(t), S_EXPR(t)
        gx, gp = char_pose("G", G, t, GX, G_GEST, G_SQ, gfa, ge); sx, sp_ = char_pose("S", S, t, SX, S_GEST, S_SQ, sfa, se)
        cv.clear(C((30, 30, 40)))
        def layer(p, fn):
            cv.save(); cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-cx * p - (1 - p) * 960, -cy); fn(); cv.restore()
        def chars():
            S.draw(cv, sx, S_Y(t) + S_FALL(t), 1.0, sp_, sfa, face_for(S, S_VIS, f, se, S_LOOK(t), S_LID(t)))
            G.draw(cv, gx, G_Y(t) + G_FALL(t), 1.0, gp, gfa, face_for(G, G_VIS, f, ge, G_LOOK(t)))
        if world == "laund":
            layer(sets.WALL_P, lambda: sets.wall_layer(cv, t, glow))
            layer(1.0, lambda: sets.floor_layer(cv, cx))
            layer(sets.WALL_P, lambda: sets.glow_fx(cv, glow, t))
            layer(1.0, chars)
            layer(sets.FG_P, lambda: sets.fg_layer(cv, t))
            if glow > 0.3: cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), fillp((80, 255, 120), int(38 * (glow - 0.3))))
        else:
            for name, p in sets.SOCK_LAYERS:
                layer(p, lambda name=name: sets.sock_dimension(cv, t, cx, name))
            layer(1.0, chars)
            layer(1.3, lambda: sets.sock_dimension(cv, t, cx, "fg"))
        sets.portal(cv, W, H, PORTAL(t), t)
        cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), skia.Paint(Shader=vign))
        if t < 0.5: cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), fillp((0, 0, 0), int(255 * (1 - t / 0.5))))
        if t > END - 0.5: cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), fillp((0, 0, 0), int(255 * min(1, (t - END + 0.5) / 0.5))))
        img = np.clip(arr[:, :, :3].astype(np.int16) + grain[f % 4], 0, 255).astype(np.uint8)
        if ff: ff.stdin.write(img.tobytes())
        if PREVIEW and f % 12 == 0: sheet.append(img[::4, ::4].copy())
        if f % 96 == 0: print("frame", f, "/", N, flush=True)
    if ff: ff.stdin.close(); ff.wait()
    if PREVIEW:
        from PIL import Image
        cols = 8; rows = (len(sheet) + cols - 1) // cols; h, w = sheet[0].shape[:2]
        im = Image.new("RGB", (cols * w, rows * h))
        for k, s in enumerate(sheet): im.paste(Image.fromarray(s), ((k % cols) * w, (k // cols) * h))
        im.save(f"{OUT}/ep_sheet.jpg", quality=85)

def audio():
    L = int(END * SR) + SR; mixd = np.zeros(L, np.float32); rng = np.random.default_rng(1)
    def add(sig, at, g=1.0):
        i = int(at * SR); n = min(len(sig), L - i)
        if n > 0 and i >= 0: mixd[i:i + n] += np.asarray(sig[:n], np.float32) * g
    tt = np.arange(L) / SR; inl = (tt < t_sd).astype(np.float32)
    noise = rng.standard_normal(L).astype(np.float32)
    rum = lfilter([0.02], [1, -0.98], noise); mixd += (rum / (np.abs(rum).max() + 1e-9) * 0.03 + 0.006 * np.sin(2 * np.pi * 120 * tt)) * inl
    for k in np.arange(0.3, t_sd, 0.62):
        n = int(0.12 * SR); add(np.exp(-np.arange(n) / (0.03 * SR)) * np.sin(2 * np.pi * 55 * np.arange(n) / SR), k, 0.05)
    for t, key in steps:
        n = int(0.09 * SR); s = lfilter([0.3], [1, -0.7], rng.standard_normal(n)) * np.exp(-np.arange(n) / (0.015 * SR))
        add(s, t, 0.22 if key == "G" else 0.15)
    n = int(2.4 * SR); t2_ = np.arange(n) / SR
    add(np.sin(2 * np.pi * (60 + 40 * t2_) * t2_) * (0.5 + 0.5 * np.sin(2 * np.pi * 6 * t2_)) * np.minimum(1, t2_ * 4) * np.exp(-t2_ * 0.4), t_glow, 0.25)
    add(sum(np.sin(2 * np.pi * f0 * t2_) for f0 in (523, 659, 784, 1046)) * np.exp(-t2_ * 2.2), t_glow + 0.05, 0.05)
    # portal whoosh: band-passed noise sweep
    n = int(1.3 * SR); w = rng.standard_normal(n); env = np.sin(np.linspace(0, np.pi, n)) ** 2
    out = np.zeros(n); y1 = 0
    for i in range(n):
        a = 0.02 + 0.5 * (i / n); y1 = y1 + a * (w[i] - y1); out[i] = y1
    add(out * env * 0.5, t_p - 0.2, 1.0)
    # falling whistle + landing thuds
    for tl in (g_land, s_land):
        m = int(0.45 * SR); tw = np.arange(m) / SR
        add(np.sin(2 * np.pi * (1400 - 1500 * tw) * tw) * 0.5 * np.minimum(1, tw * 8), tl - 0.45, 0.06)
        k = int(0.25 * SR); tk = np.arange(k) / SR
        add((np.sin(2 * np.pi * 70 * tk) + 0.5 * lfilter([0.2], [1, -0.8], rng.standard_normal(k))) * np.exp(-tk * 18), tl, 0.35)
    # sock dimension pad (dreamy chord)
    n = int((END - t_sd) * SR); tp = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * f0 * tp + 0.3 * np.sin(2 * np.pi * 0.3 * tp)) for f0 in (220, 277.2, 329.6, 440)) / 4
    add(pad * np.minimum(1, tp / 1.5) * 0.07, t_sd)
    for clip, st in zip(clips, starts): add(clip, st, 0.95)
    mixd = mixd / max(1.0, np.abs(mixd).max() / 0.95)
    wavfile.write(f"{OUT}/ep_mix.wav", SR, (mixd * 32767).astype(np.int16))

if __name__ == "__main__":
    render()
    if not PREVIEW:
        audio()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/ep_video.mp4", "-i", f"{OUT}/ep_mix.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{OUT}/04_layer1_fixed.mp4"], check=True)
        print("done", round(END, 1))
