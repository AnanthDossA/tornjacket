"""Shirley & Gabby — 'toon' engine, layer 1: rigged characters.
Skia vector drawing (anti-aliased beziers), skeletal FK rigs, walk cycle, gestures,
blinks, eye-look, cel shading, viseme lip-sync from audio, keyframe tracks."""
import math, random
import numpy as np
import skia

INK = (28, 22, 34)

# ------------------------------------------------------------------ paint helpers
def C(rgb, a=255):
    r, g, b = [int(max(0, min(255, v))) for v in rgb[:3]]
    return skia.ColorSetARGB(int(a), r, g, b)

def fillp(rgb, a=255, blur=0, shader=None):
    p = skia.Paint(Color=C(rgb, a), AntiAlias=True)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None: p.setShader(shader)
    return p

def strokep(rgb, w, a=255, cap=True, blur=0):
    p = skia.Paint(Color=C(rgb, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeCap=skia.Paint.kRound_Cap if cap else skia.Paint.kButt_Cap, StrokeJoin=skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p

def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)
def mix(a, b, t): return tuple(int(x + (y - x) * t) for x, y in zip(a, b))

def smooth(pts, closed=True, tension=1.0):
    """Catmull-Rom through points -> cubic bezier path"""
    p = skia.Path(); n = len(pts)
    if n < 2: return p
    p.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]; p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        k = tension / 6
        p.cubicTo(p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k,
                  p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k, p2[0], p2[1])
    if closed: p.close()
    return p

def oval(cx, cy, rx, ry):
    p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)); return p

def shape(cv, path, col, line=5, shadow=None, light=(-1, -1)):
    """flat fill + cel-shadow crescent (away from light) + ink outline"""
    if shadow:
        cv.drawPath(path, fillp(shade(col, 0.78)))
        cv.save(); cv.clipPath(path, skia.ClipOp.kIntersect, True)
        cv.translate(light[0] * shadow, light[1] * shadow); cv.drawPath(path, fillp(col)); cv.restore()
    else:
        cv.drawPath(path, fillp(col))
    if line: cv.drawPath(path, strokep(INK, line))

def hose(cv, pts, col, w, line=5):
    """rubber-hose limb: thick round stroke with ink outline"""
    p = smooth(pts, closed=False) if len(pts) > 2 else None
    if p is None:
        p = skia.Path(); p.moveTo(*pts[0]); p.lineTo(*pts[1])
    cv.drawPath(p, strokep(INK, w + 2 * line))
    cv.drawPath(p, strokep(col, w))

# ------------------------------------------------------------------ easing + tracks
def ease(t, kind="io"):
    t = max(0.0, min(1.0, t))
    if kind == "lin": return t
    if kind == "in": return t * t * t
    if kind == "out": return 1 - (1 - t) ** 3
    if kind == "back":  # overshoot
        s = 1.70158; t -= 1; return t * t * ((s + 1) * t + s) + 1
    if kind == "snap": return 1 - (1 - t) ** 5
    return 3 * t * t - 2 * t * t * t if t < 1 else 1.0

class Track:
    """keys: [(time, value, ease_into_this_key)] ; value may be number or tuple"""
    def __init__(self, keys): self.k = sorted(keys, key=lambda x: x[0])
    def __call__(self, t):
        k = self.k
        if t <= k[0][0]: return k[0][1]
        for (t0, v0, *_), (t1, v1, *e) in zip(k, k[1:]):
            if t <= t1:
                u = ease((t - t0) / max(1e-6, t1 - t0), e[0] if e else "io")
                if isinstance(v0, (tuple, list)): return tuple(a + (b - a) * u for a, b in zip(v0, v1))
                if isinstance(v0, str): return v0 if u < 1 else v1
                return v0 + (v1 - v0) * u
        return k[-1][1]

# ------------------------------------------------------------------ poses
POSE_KEYS = ["thighL", "kneeL", "thighR", "kneeR", "armL", "elbowL", "armR", "elbowR", "lean", "bob", "tilt", "footL", "footR"]

def pose_idle(t, seed=0):
    b = math.sin(t * 2.1 + seed)
    return {"thighL": 4, "kneeL": 3, "thighR": -4, "kneeR": 3, "armL": 8 + 2 * b, "elbowL": 14, "armR": -6 + 2 * b, "elbowR": 12,
            "lean": 1.5 * b * 0.3, "bob": 2.5 * (b * 0.5 + 0.5), "tilt": 1.5 * math.sin(t * 0.9 + seed), "footL": 0, "footR": 0,
            "sq": 1 + 0.012 * math.sin(t * 1.6 + seed)}

def pose_walk(ph, energy=1.0):
    s = math.sin(ph); c = math.cos(ph)
    A = 26 * energy
    # left leg: forward when s>0 ; knee bends during swing (forward-moving phase)
    kneeL = 8 + 38 * max(0.0, math.sin(ph + math.pi * 0.55)) * energy
    kneeR = 8 + 38 * max(0.0, math.sin(ph + math.pi * 1.55)) * energy
    sd = math.sin(ph - 0.55)  # forearms drag behind the upper arm
    return {"thighL": A * s, "kneeL": kneeL, "thighR": -A * s, "kneeR": kneeR,
            "armL": -24 * s * energy, "elbowL": 20 + 16 * max(0, -sd), "armR": 24 * s * energy, "elbowR": 20 + 16 * max(0, sd),
            "lean": 6 * energy, "bob": 9 * abs(c) * energy, "tilt": 2.5 * s * energy,
            "footL": (16 * max(0, -s) - 14 * max(0, s) ** 4) * energy, "footR": (16 * max(0, s) - 14 * max(0, -s) ** 4) * energy,
            "sq": 1 + 0.035 * energy * math.cos(2 * ph)}

def blend(a, b, w):
    w = max(0.0, min(1.0, w))
    return {k: a.get(k, 1 if k == "sq" else 0) * (1 - w) + b.get(k, 1 if k == "sq" else 0) * w for k in set(a) | set(b) if k != "hands"} | {"hands": (b if w > 0.5 else a).get("hands", {})}

def apply_gesture(p, name, tr, t, lag=0.07):
    """overlapping action: upper arm leads, forearm follows `lag` s later"""
    g = GESTURES[name]; wu = tr(t); wl = tr(t - lag)
    if wu < 0.001 and wl < 0.001: return p
    q = dict(p)
    for k, v in g.items():
        if k == "hands": continue
        w = wl if k.startswith("elbow") else wu
        q[k] = p.get(k, 0) * (1 - w) + v * w
    if wu > 0.5: q["hands"] = {**p.get("hands", {}), **g.get("hands", {})}
    return q

def override(p, o, w=1.0):
    q = dict(p)
    for k, v in o.items(): q[k] = p.get(k, 0) * (1 - w) + v * w
    return q

GESTURES = {  # partial poses (near arm = R, far arm = L) + hand shapes
    "point_up_back": {"armL": -135, "elbowL": -8, "hands": {"L": "point"}},
    "point_back": {"armL": -100, "elbowL": -4, "hands": {"L": "point"}},
    "point_fwd": {"armR": 85, "elbowR": 5, "hands": {"R": "point"}},
    "shrug": {"armL": 30, "elbowL": 95, "armR": 30, "elbowR": 95, "hands": {"L": "open", "R": "open"}},
    "arms_crossed": {"armL": 12, "elbowL": 123, "armR": 18, "elbowR": -140, "hands": {"L": "tuck", "R": "tuck"}},
    "hands_head": {"armL": 150, "elbowL": 120, "armR": 155, "elbowR": 120, "hands": {"L": "open", "R": "open"}},
    "wave": {"armR": 150, "elbowR": 20, "hands": {"R": "open"}},
    "hip": {"armR": 25, "elbowR": -90, "hands": {"R": "fist"}},
    "fists": {"armL": 20, "elbowL": 70, "armR": 25, "elbowR": 75, "hands": {"L": "fist", "R": "fist"}},
    "present": {"armR": 60, "elbowR": 30, "hands": {"R": "open"}},
}

# ------------------------------------------------------------------ hands
def hand(cv, x, y, a, kind, col, far=False, line=4):
    """cartoon hand at wrist (x,y); a = forearm angle (0 = down). kinds: relax point open fist"""
    if kind == "tuck": return  # hand hidden (e.g. tucked under the other arm)
    cv.save(); cv.translate(x, y); cv.rotate(-a)
    caps = []  # (pts, width)
    if kind == "point":
        caps += [([(-4, 22), (-4, 50)], 10), ([(6, 24), (8, 32)], 10), ([(13, 22), (14, 29)], 9)]
        thumb = ([(-12, 12), (-17, 26)], 10)
    elif kind == "open":
        for ang, ln in ((-28, 22), (-9, 26), (9, 26), (27, 21)):
            r = math.radians(ang); caps.append(([(math.sin(r) * 10, 22), (math.sin(r) * (10 + ln), 22 + math.cos(r) * ln)], 9))
        thumb = ([(-13, 10), (-29, 16)], 10)
    elif kind == "fist":
        caps += [([(-9, 28), (-7, 31)], 10), ([(1, 30), (2, 32)], 10), ([(10, 28), (10, 30)], 10)]
        thumb = ([(-13, 14), (-8, 24)], 10)
    else:  # relax: fingers slightly curled
        caps += [([(-8, 24), (-11, 38), (-6, 44)], 9), ([(1, 26), (-1, 42), (4, 48)], 9), ([(10, 24), (9, 38), (13, 43)], 9)]
        thumb = ([(-13, 12), (-20, 24)], 10)
    caps.append(thumb)
    palm = oval(0, 18, 16, 15)
    def cp(pts):
        if len(pts) > 2: return smooth(pts, closed=False)
        p = skia.Path(); p.moveTo(*pts[0]); p.lineTo(*pts[1]); return p
    for pts, w in caps: cv.drawPath(cp(pts), strokep(INK, w + 2 * line))
    cv.drawPath(palm, strokep(INK, 2 * line))
    for pts, w in caps: cv.drawPath(cp(pts), strokep(col, w))
    cv.drawPath(palm, fillp(col))
    if kind == "fist":
        for kx in (-5, 5): cv.drawLine(kx, 24, kx, 30, strokep(shade(col, 0.6), 2.5))
    cv.restore()

# ------------------------------------------------------------------ secondary motion
class Spring:
    def __init__(self, k=90.0, d=7.0): self.x = 0.0; self.v = 0.0; self.k = k; self.d = d
    def step(self, target, dt):
        for _ in range(4):
            h = dt / 4; a = self.k * (target - self.x) - self.d * self.v
            self.v += a * h; self.x += self.v * h
        return self.x

# ------------------------------------------------------------------ rig
def dirv(a): r = math.radians(a); return (math.sin(r), math.cos(r))

class Character:
    def __init__(self, spec):
        self.s = spec; self.blink_t = []
        rnd = random.Random(spec.get("seed", 1)); t = rnd.uniform(0.5, 2)
        while t < 600: self.blink_t.append(t); t += rnd.uniform(1.8, 4.5)
        self.sp_lean = Spring(70, 9); self.sp_hair = Spring(55, 5); self.sp_head = Spring(90, 10); self.sp_bob = Spring(120, 8)
        self._wr = {}; self._fs = 1
        self.px = None; self.vx = 0.0; self.expr = None; self.expr_t = -9; self.dyn = {"hair": 0, "lean": 0, "head": 0, "pop": 1}

    def update(self, t, x, dt, pose, facing, expr):
        """advance springs: inertia lean, head lag, hair/pom swing, expression pop"""
        if self.px is None: self.px = x
        vx = (x - self.px) / dt; ax = (vx - self.vx) / dt; self.px = x; self.vx = vx
        sgn = 1 if facing >= 0 else -1
        ax = max(-2500, min(2500, ax))
        self.dyn["lean"] = self.sp_lean.step(-ax * sgn * 0.004, dt)
        self.dyn["head"] = self.sp_head.step(-ax * sgn * 0.003 + pose.get("tilt", 0) * 0.0, dt)
        bobv = self.sp_bob.step(pose.get("bob", 0), dt)
        self.dyn["hair"] = self.sp_hair.step(-vx * sgn * 0.022 - ax * sgn * 0.006 + (pose.get("bob", 0) - bobv) * 2.5, dt)
        if expr != self.expr: self.expr = expr; self.expr_t = t
        d = t - self.expr_t
        self.dyn["pop"] = 1 + 0.07 * math.exp(-d * 9) * math.cos(d * 26) if d < 1 else 1.0

    def blink(self, t):
        for b in self.blink_t:
            d = t - b
            if 0 <= d < 0.16: return 1 - abs(d - 0.08) / 0.08
            if b > t: break
        return 0.0

    def draw(self, cv, x, y, sc, pose, facing=1.0, face=None):
        """x,y = feet ground point. facing in [-1,1] (sign = direction, magnitude = 3/4 amount)"""
        sp = self.s; face = face or {}
        L = sp.get("leg", 100); TW = sp.get("torso_w", 80); TH = sp.get("torso_h", 150); HR = sp.get("head_r", 90)
        cv.save(); cv.translate(x, y); cv.scale(sc * (1 if facing >= 0 else -1), sc)
        q = abs(facing)
        if (1 if facing >= 0 else -1) != self._fs: self._wr = {}; self._fs = 1 if facing >= 0 else -1
        # ground shadow
        cv.drawOval(skia.Rect.MakeLTRB(-TW * 0.9, -10, TW * 0.9, 12), fillp((0, 0, 0), 70, blur=6))
        hip = (0, -2 * L * 0.97 + pose["bob"])
        def leg(side):
            a1 = pose["thigh" + side]; a2 = a1 - pose["knee" + side]
            knee = (hip[0] + dirv(a1)[0] * L, hip[1] + dirv(a1)[1] * L)
            ank = (knee[0] + dirv(a2)[0] * L, knee[1] + dirv(a2)[1] * L)
            ank = (ank[0], min(ank[1], 0))
            return knee, ank
        def draw_leg(side, far):
            knee, ank = leg(side); pc = shade(sp["pants"], 0.82 if far else 1.0)
            hip_s = (hip[0] + (-10 if far else 10), hip[1])
            hose(cv, [hip_s, knee, ank], pc, sp.get("leg_w", 34))
            if pose["knee" + side] > 18:
                kd = dirv(pose["thigh" + side] - pose["knee" + side] / 2 - 90)
                cv.drawLine(knee[0] - kd[0] * 10, knee[1] - kd[1] * 10, knee[0] + kd[0] * 4, knee[1] + kd[1] * 4, strokep(shade(pc, 0.62), 3))
            cv.drawLine(ank[0] - 16, ank[1] - 12, ank[0] + 14, ank[1] - 14, strokep(shade(pc, 0.6), 3))
            fa = pose["foot" + side]; fl = sp.get("foot_l", 46)
            r = math.radians(-fa)
            toe = (ank[0] + fl * math.cos(r), ank[1] + fl * math.sin(r) * -1)
            shoe = smooth([(ank[0] - 14, ank[1] - 14), (toe[0] + 4, toe[1] - 10), (toe[0] + 8, toe[1] + 4), (ank[0] - 16, ank[1] + 6)])
            shape(cv, shoe, shade(sp["shoes"], 0.85 if far else 1.0), line=4, shadow=4)
        # torso frame
        dyn = self.dyn; sq = pose.get("sq", 1.0)
        lean = pose["lean"] + dyn["lean"]; tl = math.radians(lean)
        def T(px, py):  # torso local (origin hip, up = -y) rotated by lean, squash/stretch
            px = px / sq ** 0.5; py = py * sq
            return (hip[0] + px * math.cos(tl) - py * math.sin(tl), hip[1] + px * math.sin(tl) + py * math.cos(tl))
        sh_near = T(TW * 0.30, -TH * 0.86); sh_far = T(-TW * 0.25, -TH * 0.88)
        def arm(side, far):
            s0 = sh_far if far else sh_near
            a1 = pose["arm" + side] + lean; a2 = a1 + pose["elbow" + side]
            UA = sp.get("arm", 78)
            el = (s0[0] + dirv(a1)[0] * UA, s0[1] + dirv(a1)[1] * UA)
            wr = (el[0] + dirv(a2)[0] * UA * 0.95, el[1] + dirv(a2)[1] * UA * 0.95)
            sl = shade(sp["top"], 0.82 if far else 1.0); sk = shade(sp["skin"], 0.85 if far else 1.0)
            mid = ((el[0] + wr[0]) / 2, (el[1] + wr[1]) / 2)
            hose(cv, [s0, el, mid], sl, sp.get("arm_w", 26))
            hose(cv, [mid, wr], sk if sp.get("short_sleeve") else sl, sp.get("arm_w", 26) - 4)
            # smear: tapered streak from the previous wrist position on fast moves
            pw = self._wr.get(side); self._wr[side] = wr
            if pw and pose.get("smear", 0) > 0 and math.hypot(wr[0] - pw[0], wr[1] - pw[1]) > 25:
                dx, dy = wr[0] - pw[0], wr[1] - pw[1]; ln = math.hypot(dx, dy); nx, ny = -dy / ln, dx / ln
                sm = skia.Path(); sm.moveTo(*pw); sm.lineTo(wr[0] + nx * 16, wr[1] + ny * 16); sm.lineTo(wr[0] - nx * 16, wr[1] - ny * 16); sm.close()
                cv.drawPath(sm, fillp(sk, 150))
                for k in (-1, 1):
                    cv.drawLine(pw[0] + nx * 22 * k - dx * 0.2, pw[1] + ny * 22 * k - dy * 0.2, wr[0] + nx * 22 * k - dx * 0.5, wr[1] + ny * 22 * k - dy * 0.5, strokep(INK, 3, a=150))
            # elbow fold line on the sleeve
            ed = dirv((a1 + a2) / 2 + 90)
            if abs(pose["elbow" + side]) > 25:
                cv.drawLine(el[0] - ed[0] * 8, el[1] - ed[1] * 8, el[0] + ed[0] * 6, el[1] + ed[1] * 6, strokep(shade(sl, 0.65), 3))
            hand(cv, wr[0] - dirv(a2)[0] * 4, wr[1] - dirv(a2)[1] * 4, a2, pose.get("hands", {}).get(side, "relax"), sk, far)
        # draw order: far arm, far leg, near leg, torso, head, near arm
        arm("L", True); draw_leg("L", True); draw_leg("R", False)
        tp = sp.get("torso_shape", "slim")
        if tp == "round":
            pts = [T(-TW * 0.5, 0), T(-TW * 0.62, -TH * 0.45), T(-TW * 0.42, -TH * 0.92), T(TW * 0.42, -TH * 0.95), T(TW * 0.7, -TH * 0.5), T(TW * 0.55, 0)]
        else:
            pts = [T(-TW * 0.45, 0), T(-TW * 0.42, -TH * 0.5), T(-TW * 0.38, -TH * 0.95), T(TW * 0.4, -TH * 0.95), T(TW * 0.46, -TH * 0.5), T(TW * 0.5, 0)]
        body = smooth(pts)
        shape(cv, body, sp["top"], shadow=10, light=(1, -1))
        cv.save(); cv.clipPath(body, skia.ClipOp.kIntersect, True)
        hem = smooth([T(-TW, -TH * 0.08), T(0, -TH * 0.1), T(TW, -TH * 0.08)], closed=False)
        cv.drawPath(hem, strokep(shade(sp["top"], 0.7), 3)); cv.restore()
        if sp.get("buttons"):
            for k in range(3): cv.drawCircle(*T(TW * 0.18, -TH * (0.72 - k * 0.2)), 4, fillp(shade(sp["top"], 0.6)))
        if sp.get("hoodie"):
            pk = smooth([T(TW * 0.0, -TH * 0.18), T(TW * 0.42, -TH * 0.2), T(TW * 0.44, -TH * 0.42), T(TW * 0.02, -TH * 0.42)])
            shape(cv, pk, shade(sp["top"], 0.9), line=4)
            for dx in (0.05, 0.22):
                a = T(TW * dx, -TH * 0.94); sw = dyn["hair"] * 0.6
                b = (a[0] + 40 * math.sin(math.radians(sw)), a[1] + 40 * math.cos(math.radians(sw)))
                cv.drawLine(*a, *b, strokep(INK, 4)); cv.drawCircle(*b, 5, fillp((235, 235, 230)))
        if sp.get("collar"):
            col_p = smooth([T(-TW * 0.05, -TH * 0.97), T(TW * 0.32, -TH * 0.98), T(TW * 0.16, -TH * 0.8)])
            shape(cv, col_p, shade(sp["top"], 1.12), line=4)
        # neck + head
        neck = T(TW * 0.08, -TH * 0.95)
        hc = (neck[0] + 6, neck[1] - HR * 0.92)
        nk = smooth([(neck[0] - 14, neck[1] + 6), (neck[0] - 12, neck[1] - 28), (neck[0] + 16, neck[1] - 28), (neck[0] + 16, neck[1] + 6)])
        shape(cv, nk, shade(sp["skin"], 0.85), line=4)
        cv.save(); cv.translate(*hc); cv.rotate(pose["tilt"] + dyn["head"] + lean * 0.4); cv.scale(dyn["pop"], dyn["pop"])
        self.head(cv, HR, q, face, pose)
        cv.restore()
        arm("R", False)
        cv.restore()

    # ------------------------------------------------------------- head + face
    def head(self, cv, R, q, face, pose):
        sp = self.s; skin = sp["skin"]; hair = sp["hair"]; hk = sp.get("head", "round")
        f = 0.28 * R * q  # 3/4 face offset
        rx, ry = (R * 0.8, R * 1.04) if hk == "tall" else (R, R * 0.96)
        sw = self.dyn["hair"]
        if sp.get("bun"):
            cv.save(); cv.translate(-rx * 0.35, -ry * 0.8); cv.rotate(sw * 0.35); cv.translate(rx * 0.35, ry * 0.8)
            shape(cv, oval(-rx * 0.35, -ry * 1.02, R * 0.36, R * 0.33), hair, shadow=6)
            cv.restore()
            cv.drawPath(oval(-rx * 0.35 + 6, -ry * 0.72, 9, 6), fillp(shade(hair, 1.6)))
        if sp.get("hair_back"):
            shape(cv, smooth([(-rx * 1.04, -ry * 0.1), (-rx * 0.95, -ry * 0.8), (0, -ry * 1.08), (rx * 0.7, -ry * 0.85), (rx * 0.2, -ry * 0.2), (-rx * 0.7, ry * 0.5)]), hair)
        hp = oval(0, 0, rx, ry) if hk != "jowl" else smooth([(-R, -R * 0.2), (-R * 0.7, -R * 0.9), (0, -R * 1.0), (R * 0.75, -R * 0.85), (R * 1.02, -R * 0.1), (R * 0.9, R * 0.6), (R * 0.3, R * 0.98), (-R * 0.5, R * 0.9), (-R * 0.95, R * 0.4)])
        shape(cv, hp, skin, shadow=12, light=(1, -0.6))
        # ear on back side
        ex = -rx * 0.62 + f * 0.3
        shape(cv, oval(ex, ry * 0.05, R * 0.15, R * 0.2), shade(skin, 0.92), line=4)
        cv.drawPath(smooth([(ex - 4, -6), (ex + 6, 2), (ex - 2, 12)], closed=False), strokep(INK, 3))
        if sp.get("earrings"):
            ea = math.radians(sw * 1.5); e0 = (ex, ry * 0.05 + R * 0.18); e1 = (e0[0] + 16 * math.sin(ea), e0[1] + 16 * math.cos(ea))
            cv.drawLine(*e0, *e1, strokep((200, 160, 50), 3)); cv.drawCircle(*e1, 7, fillp((240, 196, 60))); cv.drawCircle(*e1, 7, strokep(INK, 2.5))
        # hair front
        hs = sp.get("hair_style")
        if hs == "part":
            shape(cv, smooth([(-rx * 1.02, ry * 0.05), (-rx * 0.98, -ry * 0.6), (-rx * 0.4, -ry * 1.03), (rx * 0.45, -ry * 0.98), (rx * 0.95, -ry * 0.5), (rx * 0.6, -ry * 0.58), (f + rx * 0.1, -ry * 0.7), (-rx * 0.3, -ry * 0.45), (-rx * 0.62, -ry * 0.1)]), hair, shadow=6)
            cv.drawPath(smooth([(-rx * 0.2, -ry * 0.88), (rx * 0.35, -ry * 0.7)], closed=False), strokep(shade(hair, 1.8), 3))
            # loose strands that swing
            for k, (sx0, ln) in enumerate(((rx * 0.62, 70), (rx * 0.78, 58))):
                a = math.radians(sw * (1.0 + 0.3 * k) + 8)
                p0 = (sx0, -ry * 0.55); p2 = (p0[0] + ln * math.sin(a), p0[1] + ln * math.cos(a))
                p1 = (p0[0] + 10 + ln * 0.5 * math.sin(a * 0.5), p0[1] + ln * 0.5)
                pth = smooth([p0, p1, p2], closed=False)
                cv.drawPath(pth, strokep(INK, 9)); cv.drawPath(pth, strokep(hair, 5))
            if sp.get("pencil"):
                cv.save(); cv.translate(-rx * 0.35, -ry * 1.05); cv.rotate(-35 + sw * 0.5)
                shape(cv, smooth([(-6, -60), (6, -60), (6, 40), (-6, 40)], tension=0.2), (250, 200, 50), line=3)
                shape(cv, smooth([(-6, 40), (6, 40), (0, 56)], tension=0.1), (240, 210, 170), line=3)
                cv.restore()
        if hs == "beanie":
            # tufts
            for k in range(5):
                tx = -rx * 0.95 + k * 12; shape(cv, smooth([(tx, -ry * 0.52), (tx - 14, -ry * 0.3), (tx + 10, -ry * 0.38)]), hair, line=3)
            bc = sp["beanie"]
            dome = smooth([(-rx * 1.06, -ry * 0.55), (-rx * 0.92, -ry * 1.0), (0, -ry * 1.3), (rx * 0.92, -ry * 1.0), (rx * 1.06, -ry * 0.55)])
            shape(cv, dome, bc, shadow=8, light=(1, -0.5))
            for k in range(-3, 4):
                cv.drawPath(smooth([(k * rx * 0.24, -ry * 0.7), (k * rx * 0.26, -ry * 1.08 + abs(k) * 6)], closed=False), strokep(shade(bc, 0.75), 3))
            band = smooth([(-rx * 1.1, -ry * 0.5), (-rx * 1.08, -ry * 0.76), (rx * 1.08, -ry * 0.76), (rx * 1.1, -ry * 0.5)], tension=0.4)
            shape(cv, band, shade(bc, 0.85), line=5)
            pa = math.radians(180 + sw * 1.2); pl = R * 0.3
            pl = R * 0.16; pr_ = math.radians(-sw * 1.2)
            ppx, ppy = rx * 0.02 + pl * math.sin(pr_), -ry * 1.28 - pl * math.cos(pr_)
            shape(cv, oval(ppx, ppy, R * 0.2, R * 0.18), (240, 236, 220), line=4)
            for k in range(5):
                aa = k * 1.26; cv.drawLine(ppx + 6 * math.cos(aa), ppy + 6 * math.sin(aa), ppx + 14 * math.cos(aa), ppy + 14 * math.sin(aa), strokep((205, 200, 186), 2.5))
        # face
        exprs = face.get("expr", "neutral"); look = face.get("look", (1, 0))
        lid = max(face.get("lid", sp.get("lid", 0.0)), face.get("blink", 0.0))
        es = sp.get("eye_size", 1.0)
        erx, ery = 21 * es * R / 90, 25 * es * R / 90
        ey = -ry * sp.get("eye_y", 0.12)
        brow_shape = {"neutral": (0, 0), "annoyed": (-14, 0), "angry": (-22, 4), "worried": (16, -2), "panic": (20, -12), "happy": (4, -6), "deadpan": (0, 4), "smug": (-6, 2), "starstruck": (8, -12)}.get(exprs, (0, 0))
        for side, ex_ in ((-1, f - erx * 1.1), (1, f + erx * 1.1)):
            far = (side == -1)
            wx = erx * (0.86 if far else 1.0)
            ep = oval(ex_, ey, wx, ery)
            cv.drawPath(ep, fillp((252, 250, 242)))
            pr = 6.5 * es * R / 90 * (0.6 if exprs == "panic" else 1.0)
            px = ex_ + look[0] * wx * 0.45; py = ey + look[1] * ery * 0.4
            if exprs == "starstruck":
                cv.drawPath(star(px, py, pr * 2.2), fillp((240, 190, 40)))
            else:
                cv.drawCircle(px, py, pr, fillp(INK)); cv.drawCircle(px - pr * 0.35, py - pr * 0.4, pr * 0.3, fillp((255, 255, 255)))
            if lid > 0.01:
                cv.save(); cv.clipPath(ep, skia.ClipOp.kIntersect, True)
                ly = ey - ery + 2 * ery * min(1, lid)
                lp = skia.Path(); lp.addRect(skia.Rect.MakeLTRB(ex_ - wx - 4, ey - ery - 4, ex_ + wx + 4, ly))
                cv.drawPath(lp, fillp(shade(skin, 0.92)))
                cv.restore()
                cv.drawLine(ex_ - wx + 2, ly, ex_ + wx - 2, ly, strokep(INK, 4))
            cv.drawPath(ep, strokep(INK, 4))
            # brow: inner end moves (down = angry, up = worried)
            idy = -brow_shape[0] * 0.6; by = ey - ery - sp.get("brow_gap", 12) + brow_shape[1]
            xl, xr = ex_ - wx * 0.8, ex_ + wx * 0.8
            yl, yr = (by, by + idy) if far else (by + idy, by)
            cv.drawLine(xl, yl, xr, yr, strokep(sp.get("brow", INK), 6))
        if sp.get("glasses"):
            gp = strokep(sp.get("glasses_col", (40, 34, 40)), 5)
            for ex_ in (f - erx * 1.1, f + erx * 1.1):
                cv.drawPath(oval(ex_, ey, erx * 1.28, ery * 1.12), gp)
            cv.drawLine(f - erx * 0.0 - 3, ey - 4, f + 3, ey - 4, gp)
            cv.drawLine(f - erx * 2.5, ey - 6, -rx * 0.55, ey - 2, gp)
        # nose
        nx = f + erx * 0.35
        cv.drawPath(smooth([(nx, ey + ery * 0.6), (nx + R * 0.2 * (0.4 + q), ey + ery * 1.6), (nx + 2, ey + ery * 1.85)], closed=False), strokep(INK, 4))
        if sp.get("stubble"):
            rnd = random.Random(3)
            for _ in range(26):
                a = rnd.uniform(0.15, 0.95) * math.pi; rr = rnd.uniform(0.55, 0.85)
                cv.drawCircle(f * 0.6 + math.cos(a) * rx * rr * 0.9, math.sin(a) * ry * rr * 0.95 + 4, 2, fillp(shade(skin, 0.6)))
        self.mouth(cv, f + 4, ry * 0.46, R, face)

    def mouth(self, cv, mx, my, R, face):
        v = face.get("vis", "X"); o = face.get("open", 0.0); ex = face.get("expr", "neutral")
        k = R / 90
        smile = {"happy": 1, "smug": 0.6, "starstruck": 1, "annoyed": -0.4, "angry": -0.8, "worried": -0.6, "panic": -0.3, "deadpan": -0.1}.get(ex, 0.1)
        if v == "X" or o < 0.08:
            w = 34 * k
            p = skia.Path(); p.moveTo(mx - w / 2, my - smile * 4); p.quadTo(mx, my + smile * 12 * k, mx + w / 2, my - smile * 4 - (6 if ex == "smug" else 0))
            cv.drawPath(p, strokep(INK, 5)); return
        W, H, teeth = {"A": (40, 34, True), "E": (48, 18, True), "O": (24, 30, False), "U": (20, 18, False), "F": (36, 14, True)}.get(v, (36, 26, True))
        if ex == "panic": W, H = W * 1.15, H * 1.3
        W *= k * (0.7 + 0.3 * o); H *= k * o
        top = my - H * 0.35 - smile * 3; bot = my + H * 0.65 + smile * 3
        mp = smooth([(mx - W / 2, my - smile * 3), (mx, top), (mx + W / 2, my - smile * 3), (mx, bot)], tension=0.9 if v in "OU" else 0.7)
        cv.drawPath(mp, fillp((84, 22, 36)))
        cv.save(); cv.clipPath(mp, skia.ClipOp.kIntersect, True)
        cv.drawPath(oval(mx, bot, W * 0.38, H * 0.4), fillp((214, 96, 110)))
        if teeth: cv.drawRect(skia.Rect.MakeLTRB(mx - W, top - 4, mx + W, top + max(4, H * 0.22)), fillp((250, 248, 240)))
        cv.restore(); cv.drawPath(mp, strokep(INK, 4.5))

def star(x, y, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return smooth(pts, tension=0.1)

# ------------------------------------------------------------------ lip-sync
def visemes(audio, sr, fps, start, out_len):
    """per-frame (viseme, openness) from an audio clip placed at `start` seconds"""
    hop = int(sr / fps); res = []
    n = int(len(audio) / hop) + 1
    env = []
    for i in range(n):
        seg = audio[i * hop: i * hop + hop * 2]
        if len(seg) < 16: env.append((0, 0)); continue
        rms = float(np.sqrt(np.mean(seg ** 2)))
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); fr = np.fft.rfftfreq(len(seg), 1 / sr)
        cen = float((sp * fr).sum() / (sp.sum() + 1e-9))
        env.append((rms, cen))
    peak = max(1e-6, np.percentile([e[0] for e in env], 90))
    seq = {}
    prev = "X"; hold = 0
    for i, (rms, cen) in enumerate(env):
        o = min(1.0, rms / peak)
        if o < 0.12: v = "X"
        elif cen > 3200: v = "E" if o > 0.4 else "F"
        elif cen < 1300: v = "O" if o > 0.5 else "U"
        else: v = "A"
        if v != prev and hold < 2 and v != "X": v = prev  # hold shapes >= 2 frames
        hold = hold + 1 if v == prev else 0; prev = v
        seq[int(round(start * fps)) + i] = (v, o)
    return seq
