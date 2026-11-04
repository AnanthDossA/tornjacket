"""Layer 2 test: the Sock King scene (pose-to-pose humans + creature rig)."""
import sys, math, os, subprocess
sys.path.insert(0, "/root/sg"); sys.path.insert(0, "/root/tj")
import numpy as np, skia
from scipy.io import wavfile
from scipy.signal import resample
import toon, sets, acting, creature
from toon import Track, C, fillp
from chars import SHIRLEY, GABBY

W, H, FPS, SR = 1920, 1080, 24, 24000; DT = 1 / FPS; OUT = "/root/sg/out"
PREVIEW = "--preview" in sys.argv

cache = f"{OUT}/king_lines.npz"
if os.path.exists(cache):
    z = np.load(cache, allow_pickle=True); L = {k: (z[k + "_c"], list(z[k + "_p"])) for k in ("k1", "s1", "k2", "k3", "g1")}
else:
    from voices import Voices
    V = Voices("/root/tj/models")
    def king(phr, pauses):
        c, p = acting.say_phrases(V, phr, "am_onyx", 0.9, pauses)
        f = 1.16; c = resample(c, int(len(c) * f)).astype(np.float32)  # pitch down -> booming
        echo = np.zeros(len(c) + 4000, np.float32); echo[:len(c)] += c; echo[3600:3600 + len(c)] += c * 0.3
        return echo, [x * f for x in p]
    L = {"k1": king(["Who dares enter", "with a matching pair?"], [0.3, 0.0]),
         "s1": acting.say_phrases(V, ["Gabby.", "Run."], SHIRLEY["voice"], 0.9, [0.55, 0.0]),
         "k2": king(["Wait."], [0.0]),
         "k3": king(["She's", "perfect."], [0.6, 0.0]),
         "g1": acting.say_phrases(V, ["Oh no."], GABBY["voice"], 1.0, [0.0])}
    np.savez(cache, **{k + "_c": v[0] for k, v in L.items()}, **{k + "_p": np.array(v[1]) for k, v in L.items()})
dur = {k: len(v[0]) / SR for k, v in L.items()}

# ---- timeline
tk1 = 1.6; ts1 = tk1 + dur["k1"] + 0.5; tk2 = ts1 + dur["s1"] + 0.35; tk3 = tk2 + dur["k2"] + 0.6; tg1 = tk3 + dur["k3"] + 0.6
END = tg1 + dur["g1"] + 1.3
ST = {"k1": tk1, "s1": ts1, "k2": tk2, "k3": tk3, "g1": tg1}
ph = {k: [ST[k] + p for p in L[k][1]] for k in L}

KX, KY, KS = 1700, 742, 0.72      # king stands on the throne (mid layer, parallax 0.75)
SX, GX = 820, 1090
def king_cam(z, cy):  # camera centred on the king despite parallax
    return (KX - 240) / 0.75, cy, z
SHOTS = [
    (0.0, Track([(0, (1300, 560, 0.92)), (tk1 - 0.1, (1330, 560, 0.96))])),
    (tk1 - 0.05, Track([(0, king_cam(1.45, 460)), (dur["k1"], king_cam(1.62, 450), "lin")])),
    (ts1 - 0.1, Track([(0, (SX + 20, 560, 2.1)), (dur["s1"], (SX + 20, 570, 2.25), "lin")])),
    (tk2 - 0.08, Track([(0, king_cam(1.15, 470)), (0.4, king_cam(1.3, 470), "snap")])),
    (tk3 - 0.1, Track([(0, king_cam(1.5, 450)), (dur["k3"] + 0.3, king_cam(1.75, 440), "lin")])),
    (tg1 - 0.1, Track([(0, (1000, 560, 1.4)), (END - tg1, (1010, 560, 1.48), "lin")])),
]
KING = creature.PoseTrack([(0, "regal"), (tk1 - 0.15, "loom"), (tk1 + dur["k1"] + 0.3, "regal"), (tk2 - 0.1, "point"), (ph["k3"][1] - 0.15, "swoon")],
                          creature.KING_POSES, frames=5, antic=0.2, over=0.14)
K_EXPR = Track([(0, "smug"), (tk1 - 0.1, "evil"), (tk2 - 0.1, "rage"), (tk3 - 0.05, "shock"), (ph["k3"][1] - 0.15, "love")])
K_LOOK = Track([(0, (1, 0.2)), (tk2, (1, 0.5)), (tk3, (1, 0.3))])
A_S = acting.Acting([(0, "deadpan"), (tk1 + 0.2, "shock"), (ts1 - 0.2, "stand_still"), (tk2 + 0.1, "shock"), (tk3 + 0.6, "stand_still"), (tg1, "deadpan_tilt")], "shirley", seed=2)
A_G = acting.Acting([(0, "present"), (tk1 + 0.1, "shock"), (ts1 + 0.4, "whine"), (tk3 + dur["k3"] + 0.2, "shrug_big"), (tg1 + 0.5, "slump")], "gabby", seed=1)
S_EXPR = Track([(0, "annoyed"), (tk1 + 0.2, "panic"), (ts1 - 0.2, "worried"), (tk2, "panic"), (tk3 + 0.8, "deadpan")])
G_EXPR = Track([(0, "starstruck"), (tk1 + 0.1, "panic"), (tk3 + dur["k3"], "worried"), (tg1, "happy")])
S_LOOK = Track([(0, (1, -0.2)), (ts1 - 0.25, (0.2, 1), "snap"), (ph["s1"][1] - 0.1, (-1, 0), "snap"), (tk2, (1, -0.3), "snap"), (tg1 - 0.2, (1, -0.3)), (tg1 + 0.4, (0.2, 0.2))])
S_LID = Track([(0, 0.3), (tk1 + 0.15, 0.0, "snap"), (tk3 + 0.8, 0.0), (tk3 + 1.1, 0.45)])
S_FACE = Track([(0, 0.85)]); G_FACE = Track([(0, 0.85), (tg1 - 0.1, 0.85), (tg1 + 0.05, -0.8, "snap")])

VIS = {"S": {}, "G": {}, "K": {}}
for k, who in (("k1", "K"), ("s1", "S"), ("k2", "K"), ("k3", "K"), ("g1", "G")):
    VIS[who].update(toon.visemes(L[k][0], SR, FPS, ST[k], None))

S, G, K = toon.Character(SHIRLEY), toon.Character(GABBY), creature.SockKing()

def shot(t):
    cur = SHOTS[0]
    for s in SHOTS:
        if t >= s[0]: cur = s
    return cur[1](t - cur[0])

def render():
    N = int(END * FPS) + 1
    arr = np.zeros((H, W, 4), np.uint8); cv = skia.Surface(arr).getCanvas()
    grain = [np.random.default_rng(k).integers(-6, 7, (H, W, 1), dtype=np.int16) for k in range(4)]
    vign = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), W * 0.62, [C((0, 0, 0), 0), C((0, 0, 0), 0), C((20, 10, 30), 120)], [0, 0.6, 1.0])
    ff = None if PREVIEW else subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                                "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", f"{OUT}/king_v.mp4"], stdin=subprocess.PIPE)
    sheet = []
    for f in range(N):
        t = f / FPS; cx, cy, z = shot(t)
        sp_, gp = A_S(t), A_G(t); kp = KING(t)
        S.update(t, SX, DT, sp_, S_FACE(t), S_EXPR(t)); G.update(t, GX, DT, gp, G_FACE(t), G_EXPR(t))
        def fc(ch, who, expr, look, lid=None):
            v, o = VIS[who].get(f, ("X", 0)); d = {"expr": expr, "look": look, "vis": v, "open": o, "blink": ch.blink(t) if ch else 0}
            if lid is not None: d["lid"] = lid
            return d
        cv.clear(C((30, 30, 40)))
        def layer(p, fn):
            cv.save(); cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-cx * p - (1 - p) * 960, -cy); fn(); cv.restore()
        for name, p in sets.SOCK_LAYERS:
            if name == "mid":
                def mid():
                    sets.sock_dimension(cv, t, cx, "mid")
                    K.draw(cv, KX, KY, KS, kp, t, DT, fc(None, "K", K_EXPR(t), K_LOOK(t)) | {"blink": 0}, flip=True)
                layer(p, mid)
            elif name == "ground":
                def gr():
                    sets.sock_dimension(cv, t, cx, "ground")
                    S.draw(cv, SX, 980, 1.0, sp_, S_FACE(t), fc(S, "S", S_EXPR(t), S_LOOK(t), S_LID(t)))
                    G.draw(cv, GX, 1000, 1.0, gp, G_FACE(t), fc(G, "G", G_EXPR(t), (1, -0.3)))
                layer(p, gr)
            else:
                layer(p, lambda name=name: sets.sock_dimension(cv, t, cx, name))
        layer(1.3, lambda: sets.sock_dimension(cv, t, cx, "fg"))
        if KING(t)["_u"] < 0.6 and K_EXPR(t) == "love":  # swoon sparkle
            pass
        cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), skia.Paint(Shader=vign))
        if t < 0.4: cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), fillp((0, 0, 0), int(255 * (1 - t / 0.4))))
        if t > END - 0.4: cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), fillp((0, 0, 0), int(255 * min(1, (t - END + 0.4) / 0.4))))
        img = np.clip(arr[:, :, :3].astype(np.int16) + grain[f % 4], 0, 255).astype(np.uint8)
        if ff: ff.stdin.write(img.tobytes())
        if PREVIEW and f % 12 == 0: sheet.append(img[::4, ::4].copy())
    if ff: ff.stdin.close(); ff.wait()
    if PREVIEW:
        from PIL import Image
        cols = 8; rows = (len(sheet) + cols - 1) // cols; h, w = sheet[0].shape[:2]
        im = Image.new("RGB", (cols * w, rows * h))
        for k, s in enumerate(sheet): im.paste(Image.fromarray(s), ((k % cols) * w, (k // cols) * h))
        im.save(f"{OUT}/king_sheet.jpg", quality=85)

def audio():
    n = int(END * SR) + SR; mix = np.zeros(n, np.float32); tp = np.arange(n) / SR
    mix += sum(np.sin(2 * np.pi * f0 * tp + 0.3 * np.sin(2 * np.pi * 0.3 * tp)) for f0 in (220, 277.2, 329.6, 440)) / 4 * 0.05
    # ominous drone under the king's first line, harp-ish gliss on the swoon
    i = int(tk1 * SR); m = int((dur["k1"] + 0.8) * SR); tt = np.arange(m) / SR
    mix[i:i + m] += (np.sin(2 * np.pi * 55 * tt) + 0.5 * np.sin(2 * np.pi * 82.4 * tt)) * np.minimum(1, tt * 3) * np.exp(-tt * 0.6) * 0.18
    i = int((ph["k3"][1] - 0.1) * SR)
    for k, f0 in enumerate([523, 587, 659, 784, 880, 1046, 1175, 1318]):
        m = int(0.9 * SR); tt = np.arange(m) / SR; j = i + int(k * 0.05 * SR)
        mix[j:j + m] += np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 4) * 0.05
    for k, (c, _) in L.items():
        j = int(ST[k] * SR); mix[j:j + len(c)] += c * 0.95
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    wavfile.write(f"{OUT}/king_a.wav", SR, (mix * 32767).astype(np.int16))

if __name__ == "__main__":
    render()
    if not PREVIEW:
        audio()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/king_v.mp4", "-i", f"{OUT}/king_a.wav", "-c:v", "copy", "-c:a", "aac", "-shortest", f"{OUT}/09_sock_king_scene.mp4"], check=True)
    print("done", round(END, 1))
