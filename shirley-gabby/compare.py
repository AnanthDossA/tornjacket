"""Side-by-side: smooth (layer 1) vs pose-to-pose acting (layer 2a), same lines."""
import sys, math, subprocess
sys.path.insert(0, "/root/sg")
import numpy as np, skia
from scipy.io import wavfile
import toon, sets, acting
from toon import Track, C, fillp
from chars import SHIRLEY, GABBY

W, H, FPS, SR = 1920, 1080, 24, 24000; DT = 1 / FPS; OUT = "/root/sg/out"
import os
sys.path.insert(0, "/root/tj")
cache = f"{OUT}/cmp_lines.npz"
if os.path.exists(cache):
    z = np.load(cache, allow_pickle=True); clips = list(z["clips"]); PH = list(z["ph"])
else:
    from voices import Voices
    V = Voices("/root/tj/models")
    c0, PH = acting.say_phrases(V, ["Shirl.", "Shirl!", "The dryer ate my sock.", "My lucky sock!"], GABBY["voice"], 1.05, [0.25, 0.35, 0.3, 0.0])
    c1 = V.say("You've never been lucky.", SHIRLEY["voice"], 0.92)
    clips = [c0, c1]; np.savez(cache, clips=np.array(clips, dtype=object), ph=np.array(PH))
d0, d1 = len(clips[0]) / SR, len(clips[1]) / SR
t1 = 0.8; t2 = t1 + d0 + 0.5; END = t2 + d1 + 1.4
ph = [t1 + p for p in PH]
print("phrases", [round(p, 2) for p in ph])
while len(ph) < 4: ph.append(ph[-1] + 0.4)
G_VIS = toon.visemes(clips[0], SR, FPS, t1, None); S_VIS = toon.visemes(clips[1], SR, FPS, t2, None)

# ---- BEFORE: smooth continuous gestures (layer-1 style)
B_G = [("point_back", Track([(0, 0), (ph[2], 0), (ph[2] + 0.35, 1), (ph[3] + 0.3, 1), (ph[3] + 0.7, 0)])),
       ("fists", Track([(0, 0), (ph[3] + 0.3, 0), (ph[3] + 0.7, 1), (t2 + 0.5, 1), (t2 + 1.0, 0)]))]
B_S = [("arms_crossed", Track([(0, 1)])), ("present", Track([(0, 0), (t2, 0), (t2 + 0.4, 0.6), (t2 + d1, 0.6), (t2 + d1 + 0.4, 0)]))]
# ---- AFTER: key poses, holds, snaps
A_G = acting.Acting([(0, "stand"), (ph[0] - 0.12, "call_out"), (ph[1] - 0.1, "shock"), (ph[2] - 0.1, "point_back"),
                     (ph[3] - 0.1, "whine"), (t2 + 0.35, "slump")], "gabby", seed=1)
A_S = acting.Acting([(0, "deadpan"), (ph[3] + 0.25, "deadpan_tilt"), (t2 - 0.12, "explain"), (t2 + d1 + 0.15, "deadpan")], "shirley", seed=2)

G_EXPR_B = Track([(0, "neutral"), (t1, "panic"), (t2, "worried")])
G_EXPR_A = Track([(0, "neutral"), (ph[0] - 0.1, "worried"), (ph[1] - 0.1, "panic"), (ph[3] - 0.1, "angry"), (t2 + 0.3, "worried")])
S_EXPR = Track([(0, "deadpan"), (t2 + d1, "smug")])
S_LOOK_A = Track([(0, (1, 0)), (ph[3] + 0.1, (1, 0)), (ph[3] + 0.25, (0.3, -1), "snap"), (t2 - 0.25, (0.3, -1)), (t2 - 0.1, (1, 0.1), "snap")])
S_LOOK_B = Track([(0, (1, 0))])

def make():
    return {"G": toon.Character(GABBY), "S": toon.Character(SHIRLEY)}
VERS = {"before": make(), "after": make()}
GX, SX = 1010, 700

def draw_panel(cv, ox, label, ver, f):
    t = f / FPS; ch = VERS[ver]
    cx, cy, zz = 860, 560, 1.32
    cv.save(); cv.clipRect(skia.Rect.MakeLTRB(ox, 0, ox + 960, H)); cv.translate(ox, 0)
    def layer(p, fn):
        cv.save(); cv.translate(480, H / 2); cv.scale(zz, zz); cv.translate(-cx * p - (1 - p) * 960, -cy); fn(); cv.restore()
    layer(sets.WALL_P, lambda: sets.wall_layer(cv, t, 0.15)); layer(1.0, lambda: sets.floor_layer(cv, cx))
    if ver == "before":
        gp = toon.pose_idle(t, 0); sp_ = toon.pose_idle(t, 1)
        for n, tr in B_G: gp = toon.apply_gesture(gp, n, tr, t)
        for n, tr in B_S: sp_ = toon.apply_gesture(sp_, n, tr, t)
        ge, sl = G_EXPR_B(t), S_LOOK_B(t)
    else:
        gp = A_G(t); sp_ = A_S(t); ge, sl = G_EXPR_A(t), S_LOOK_A(t)
    se = S_EXPR(t)
    ch["G"].update(t, GX, DT, gp, -0.75, ge); ch["S"].update(t, SX, DT, sp_, 0.8, se)
    def chars():
        v, o = S_VIS.get(f, ("X", 0)); ch["S"].draw(cv, SX, 960, 1.0, sp_, 0.8, {"expr": se, "look": sl, "vis": v, "open": o, "blink": ch["S"].blink(t), "lid": 0.34})
        v, o = G_VIS.get(f, ("X", 0)); ch["G"].draw(cv, GX, 985, 1.0, gp, -0.75, {"expr": ge, "look": (1, 0), "vis": v, "open": o, "blink": ch["G"].blink(t)})
    layer(1.0, chars)
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, 960, 86), fillp((20, 16, 28), 200))
    cv.drawString(label, 30, 60, sets.font(sets.FONT_B, 52), fillp((255, 230, 120) if ver == "after" else (230, 230, 230)))
    cv.restore()

arr = np.zeros((H, W, 4), np.uint8); cv = skia.Surface(arr).getCanvas()
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", f"{OUT}/cmp_v.mp4"], stdin=subprocess.PIPE)
N = int(END * FPS)
for f in range(N):
    cv.clear(C((0, 0, 0)))
    draw_panel(cv, 0, "BEFORE: SMOOTH", "before", f)
    draw_panel(cv, 960, "AFTER: POSE-TO-POSE", "after", f)
    cv.drawRect(skia.Rect.MakeLTRB(956, 0, 964, H), fillp((10, 10, 14)))
    ff.stdin.write(arr.tobytes())
ff.stdin.close(); ff.wait()
L = int(END * SR) + SR; mix = np.zeros(L, np.float32)
for c, st in ((clips[0], t1), (clips[1], t2)): i = int(st * SR); mix[i:i + len(c)] += c * 0.95
wavfile.write(f"{OUT}/cmp_a.wav", SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/cmp_v.mp4", "-i", f"{OUT}/cmp_a.wav", "-c:v", "copy", "-c:a", "aac", "-shortest", f"{OUT}/06_before_after_acting.mp4"], check=True)
print("done", round(END, 1))
