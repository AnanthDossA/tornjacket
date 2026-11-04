"""Layer 2b: general creature rig parts + the Sock King.
Tentacles (chains with curl, wave, spring follow-through), wobbly blob bodies,
pose-to-pose params via acting.toon_curve, shared face/mouth drawing."""
import math
import skia
import toon, acting
from toon import C, fillp, strokep, smooth, oval, shape, shade, INK, Spring

# ------------------------------------------------------------------ generic parts
class Tentacle:
    """chain of n segments; angles accumulate: base + curl*i + wave; tip lags via springs"""
    def __init__(self, n=10, length=300, w0=46, w1=16):
        self.n, self.L, self.w0, self.w1 = n, length, w0, w1
        self.springs = [Spring(60 - i * 3, 6) for i in range(n)]

    def points(self, base, ang, curl, t, wave=6, speed=2.0, dt=None):
        pts = [base]; a = ang; seg = self.L / self.n
        for i in range(self.n):
            target = curl * (i / self.n) * 1.6 + wave * math.sin(t * speed - i * 0.6) * (i / self.n)
            off = self.springs[i].step(target, dt) if dt else target
            a += off / self.n * 2.5 if dt else target / self.n * 2.5
            x, y = pts[-1]; r = math.radians(a)
            pts.append((x + seg * math.sin(r), y - seg * math.cos(r)))
        return pts

    def outline(self, pts):
        left, right = [], []
        for i, (x, y) in enumerate(pts):
            j0, j1 = max(0, i - 1), min(len(pts) - 1, i + 1)
            dx, dy = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]; ln = math.hypot(dx, dy) or 1
            w = (self.w0 + (self.w1 - self.w0) * i / (len(pts) - 1)) / 2
            left.append((x - dy / ln * w, y + dx / ln * w)); right.append((x + dy / ln * w, y - dx / ln * w))
        return left, right

    def draw(self, cv, pts, col, stripes=None, cuff=None):
        left, right = self.outline(pts)
        tip = pts[-1]
        body = smooth(left + [tip] + list(reversed(right)), tension=0.8)
        shape(cv, body, col, shadow=7, light=(1, -1))
        cv.save(); cv.clipPath(body, skia.ClipOp.kIntersect, True)
        if stripes:
            for k in range(2, len(pts) - 2, 3):
                (lx, ly), (rx, ry) = left[k], right[k]
                cv.drawLine(lx, ly, rx, ry, strokep(stripes, 12, cap=False))
        cv.restore()
        if cuff:  # ribbed cuff at the base
            (lx, ly), (rx, ry) = left[1], right[1]
            cv.drawLine(lx, ly, rx, ry, strokep(INK, 16)); cv.drawLine(lx, ly, rx, ry, strokep(cuff, 10))
        cv.drawPath(body, strokep(INK, 5))

def creature_face(cv, cx, cy, R, face, look=(1, 0), lid=0.0, eye_gap=1.15, eye_kind="round"):
    ex = face.get("expr", "neutral")
    erx, ery = 0.26 * R, 0.3 * R
    for side in (-1, 1):
        x = cx + side * erx * eye_gap
        ep = oval(x, cy, erx, ery); cv.drawPath(ep, fillp((252, 250, 240)))
        px, py = x + look[0] * erx * 0.4, cy + look[1] * ery * 0.4
        if ex == "love":
            hp = smooth([(px, py + 18), (px - 22, py - 2), (px - 12, py - 18), (px, py - 8), (px + 12, py - 18), (px + 22, py - 2)], tension=0.5)
            cv.drawPath(hp, fillp((230, 50, 90))); cv.drawPath(hp, strokep(INK, 3))
        else:
            pr = 0.09 * R * (0.55 if ex in ("rage", "panic") else 1)
            cv.drawCircle(px, py, pr, fillp(INK if ex != "rage" else (200, 30, 40))); cv.drawCircle(px - pr * 0.3, py - pr * 0.4, pr * 0.3, fillp((255, 255, 255)))
        l = max(lid, face.get("blink", 0))
        if ex == "evil": l = max(l, 0.35)
        if l > 0.01:
            cv.save(); cv.clipPath(ep, skia.ClipOp.kIntersect, True)
            ly = cy - ery + 2 * ery * l
            if ex == "evil":  # slanted angry lids
                p = skia.Path(); p.moveTo(x - erx - 4, cy - ery - 4); p.lineTo(x + erx + 4, cy - ery - 4)
                p.lineTo(x + erx + 4, ly + (-side) * 14); p.lineTo(x - erx - 4, ly + side * 14); p.close()
                cv.drawPath(p, fillp(face.get("lidcol", (200, 200, 200))))
            else:
                cv.drawRect(skia.Rect.MakeLTRB(x - erx - 4, cy - ery - 4, x + erx + 4, ly), fillp(face.get("lidcol", (200, 200, 200))))
            cv.restore()
        cv.drawPath(ep, strokep(INK, 5))
        # brows
        bd = {"evil": 18, "rage": 24, "love": -14, "worried": -16, "shock": -20}.get(ex, 0)
        by = cy - ery - 16
        xi, xo = x - side * erx * 0.9, x + side * erx * 0.9
        cv.drawLine(xo, by - (8 if ex == "shock" else 0), xi, by + bd * 0.6, strokep(INK, 9))
    toon.Character.mouth(None, cv, cx, cy + 0.62 * R, R * 1.25, face)

def crown(cv, x, y, w, rot=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    p = smooth([(-w / 2, 0), (-w / 2, -w * 0.55), (-w * 0.25, -w * 0.25), (0, -w * 0.7), (w * 0.25, -w * 0.25), (w / 2, -w * 0.55), (w / 2, 0)], tension=0.15)
    shape(cv, p, (246, 196, 58), shadow=6)
    for k, col in ((-0.25, (220, 40, 70)), (0, (60, 140, 230)), (0.25, (60, 200, 120))):
        cv.drawCircle(w * k, -w * 0.12, w * 0.06, fillp(col)); cv.drawCircle(w * k, -w * 0.12, w * 0.06, strokep(INK, 3))
    for px_ in (-w / 2, 0, w / 2):
        cv.drawCircle(px_, -w * (0.55 if px_ else 0.7), w * 0.05, fillp((255, 236, 150)))
    cv.restore()

# ------------------------------------------------------------------ Sock King
KING_POSES = {  # params: lean, rise (stretch tall), armL/armR (base angle: 0 up, 90 right, 180 down), curlL/curlR, tilt, wave
    "regal":   {"lean": 0, "rise": 0, "armL": -120, "armR": 120, "curlL": -120, "curlR": 120, "tilt": 0, "wave": 5},
    "loom":    {"lean": -10, "rise": 1, "armL": -35, "armR": 35, "curlL": -80, "curlR": 80, "tilt": -8, "wave": 14},
    "point":   {"lean": 12, "rise": 0.6, "armL": -150, "armR": 72, "curlL": -60, "curlR": 4, "tilt": 6, "wave": 2},
    "swoon":   {"lean": 6, "rise": 0.2, "armL": 200, "armR": 160, "curlL": -110, "curlR": 110, "tilt": 14, "wave": 2},
    "flex":    {"lean": -4, "rise": 0.8, "armL": -70, "armR": 70, "curlL": 95, "curlR": -95, "tilt": -4, "wave": 4},
}

class PoseTrack:
    """pose-to-pose for any param dict (creatures): holds, toon curve, twos"""
    def __init__(self, keys, poses, frames=5, antic=0.15, over=0.12, fps=24, twos=True):
        self.keys = sorted(keys, key=lambda k: k[0]); self.poses = poses
        self.frames, self.antic, self.over, self.fps, self.twos = frames, antic, over, fps, twos
    def __call__(self, t):
        if self.twos: t = math.floor(t * self.fps / 2) * 2 / self.fps
        ks = self.keys; i = 0
        while i + 1 < len(ks) and ks[i + 1][0] <= t: i += 1
        cur = self.poses[ks[i][1]]; prev = self.poses[ks[i - 1][1]] if i > 0 else cur
        u = (t - ks[i][0]) / (self.frames / self.fps * 1.6) if i > 0 else 1
        m = acting.toon_curve(u, self.antic, self.over)
        out = {k: prev[k] + (cur[k] - prev[k]) * m for k in cur}
        out["_u"] = u
        return out

class SockKing:
    def __init__(self):
        self.col = (196, 70, 120); self.stripe = (250, 210, 90); self.cuffc = (240, 236, 220)
        self.armL, self.armR = Tentacle(12, 330, 70, 30), Tentacle(12, 330, 70, 30)
        self.sp_crown = Spring(50, 4); self.sp_body = Spring(80, 6); self.last_rise = 0

    def draw(self, cv, x, y, sc, p, t, dt, face, flip=False):
        cv.save(); cv.translate(x, y); cv.scale(sc * (-1 if flip else 1), sc)
        rise = p["rise"]; H = 560 * (1 + 0.18 * rise); W = 250
        jig = self.sp_body.step(rise, dt); stretch = 1 + (rise - jig) * 0.25
        cv.drawOval(skia.Rect.MakeLTRB(-W * 0.9, -14, W * 0.9, 16), fillp((0, 0, 0), 80, blur=10))
        cv.save(); cv.scale(1 / stretch ** 0.5, stretch); cv.rotate(p["lean"])
        # foot (the heel/toe of the sock) sits on the ground
        foot = smooth([(-W * 0.5, -150), (-W * 0.55, -40), (-W * 0.3, 0), (W * 0.75, 0), (W * 0.95, -50), (W * 0.7, -120), (W * 0.4, -160)], tension=0.7)
        top = -H
        # arms behind body (far) and in front (near)
        def arm(side, front):
            base = (side * W * 0.45, top + H * 0.42)
            a = p["armL"] if side < 0 else p["armR"]; c = p["curlL"] if side < 0 else p["curlR"]
            ten = self.armL if side < 0 else self.armR
            pts = ten.points(base, a, c, t, wave=p["wave"], dt=dt)
            ten.draw(cv, pts, shade(self.col, 0.85 if not front else 1.0), stripes=self.stripe, cuff=self.cuffc)
        arm(-1, False)
        tube = smooth([(-W / 2, top + 20), (-W / 2 - 6, top + H * 0.5), (-W * 0.5, -130), (W * 0.45, -150), (W * 0.5, top + H * 0.5), (W / 2, top + 20)], tension=0.55)
        shape(cv, foot, self.col, shadow=12, light=(1, -0.5)); shape(cv, tube, self.col, shadow=16, light=(1, -0.5))
        cv.save(); cv.clipPath(tube, skia.ClipOp.kIntersect, True)
        for k in range(3): cv.drawRect(skia.Rect.MakeLTRB(-W, top + H * (0.62 + k * 0.1), W, top + H * (0.62 + k * 0.1) + 22), fillp(self.stripe))
        cv.restore()
        cv.drawPath(tube, strokep(INK, 5))
        # heel patch
        cv.drawPath(oval(-W * 0.3, -60, 60, 50), fillp(shade(self.col, 0.75))); cv.drawPath(oval(W * 0.72, -45, 45, 38), fillp(shade(self.col, 0.75)))
        # ribbed cuff + crown
        cuff = smooth([(-W / 2 - 12, top + 70), (-W / 2 - 10, top - 10), (W / 2 + 10, top - 10), (W / 2 + 12, top + 70)], tension=0.3)
        shape(cv, cuff, self.cuffc, shadow=6)
        for k in range(-5, 6): cv.drawLine(k * W * 0.09, top, k * W * 0.09, top + 62, strokep(shade(self.cuffc, 0.75), 4))
        cr = self.sp_crown.step(-p["lean"] * 0.8 - p["tilt"] * 0.6 + (rise - jig) * 30, dt)
        crown(cv, 0, top - 4, W * 0.7, rot=cr)
        # face
        fc = (0, top + H * 0.3)
        cv.save(); cv.translate(*fc); cv.rotate(p["tilt"])
        f2 = dict(face); f2["lidcol"] = shade(self.col, 0.92)
        creature_face(cv, 0, 0, 150, f2, look=face.get("look", (0, 0.2)))
        cv.restore()
        arm(1, True)
        cv.restore(); cv.restore()
