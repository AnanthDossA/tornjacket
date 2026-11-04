"""Layer 2a: pose-to-pose cartoon acting.
Strong key poses -> holds (with tiny 'moving hold' drift) -> snappy transitions
(anticipation, fast move, overshoot, settle) -> optional animation on twos,
exaggeration and squash/stretch per character personality."""
import math
import numpy as np

NEUTRAL = {"thighL": 4, "kneeL": 3, "thighR": -4, "kneeR": 3, "armL": 8, "elbowL": 14, "armR": -6, "elbowR": 12,
           "lean": 0, "bob": 0, "tilt": 0, "footL": 0, "footR": 0}

POSES = {  # full-body key poses (merged over NEUTRAL). R = near arm, L = far arm
    "stand":        {},
    "stand_still":  {"armL": 4, "elbowL": 6, "armR": -2, "elbowR": 8},
    "deadpan":      {"armL": 12, "elbowL": 123, "armR": 18, "elbowR": -140, "lean": -2, "tilt": -2, "hands": {"L": "tuck", "R": "tuck"}, "exact": True},
    "deadpan_tilt": {"armL": 12, "elbowL": 123, "armR": 18, "elbowR": -140, "lean": -4, "tilt": -9, "hands": {"L": "tuck", "R": "tuck"}, "exact": True},
    "explain":      {"armL": 12, "elbowL": 123, "armR": 40, "elbowR": 70, "lean": 2, "tilt": 4, "hands": {"L": "tuck", "R": "open"}, "exact": True},
    "shock":        {"armL": 165, "elbowL": 15, "armR": 62, "elbowR": 25, "lean": -16, "tilt": -12, "bob": -10, "thighL": 10, "thighR": -14,
                     "hands": {"L": "open", "R": "open"}},
    "call_out":     {"armL": 150, "elbowL": 25, "armR": 10, "elbowR": 20, "lean": 10, "tilt": 6, "hands": {"L": "open"}},
    "point_back":   {"armL": -88, "elbowL": -4, "armR": 30, "elbowR": 50, "lean": -6, "tilt": -5, "hands": {"L": "point", "R": "open"}},
    "whine":        {"armL": 14, "elbowL": 18, "armR": 18, "elbowR": 14, "lean": 14, "tilt": 10, "bob": 14, "thighL": 14, "kneeL": 26,
                     "thighR": 8, "kneeR": 22, "hands": {"L": "fist", "R": "fist"}},
    "slump":        {"armL": 2, "elbowL": 4, "armR": 2, "elbowR": 4, "lean": 12, "tilt": 16, "bob": 8},
    "shrug_big":    {"armL": 40, "elbowL": 100, "armR": 45, "elbowR": 100, "lean": -4, "tilt": -8, "bob": -6, "hands": {"L": "open", "R": "open"}},
    "present":      {"armR": 70, "elbowR": 20, "lean": 4, "hands": {"R": "open"}},
    "hands_hips":   {"armL": 30, "elbowL": -95, "armR": 30, "elbowR": -95, "lean": -3, "hands": {"L": "fist", "R": "fist"}},
}

PERSONALITY = {
    # frames: transition length @24fps ; antic/over: anticipation & overshoot amount ; exag: pose amplification
    # drift: moving-hold amount ; twos: animate body on twos ; stretch: squash/stretch on moves
    "gabby":   {"frames": 4, "antic": 0.18, "over": 0.16, "exag": 1.25, "drift": 1.0, "twos": True, "stretch": 0.07},
    "shirley": {"frames": 6, "antic": 0.06, "over": 0.05, "exag": 0.85, "drift": 0.25, "twos": True, "stretch": 0.02},
}

def toon_curve(u, antic, over):
    """0..1 -> pose mix: small move backwards (anticipation), fast travel, overshoot, settle"""
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    a = 0.22  # anticipation phase share
    if u < a:
        return -antic * math.sin(math.pi * u / a)
    v = (u - a) / (1 - a)
    if v < 0.45:  # fast travel (ease-out) to overshoot peak
        w = v / 0.45
        return (1 + over) * (1 - (1 - w) ** 3)
    w = (v - 0.45) / 0.55  # settle with one small bounce
    return 1 + over * math.exp(-5 * w) * math.cos(math.pi * 1.5 * w)

def _full(name_or_dict, exag):
    p = dict(NEUTRAL); src = POSES[name_or_dict] if isinstance(name_or_dict, str) else name_or_dict
    for k, v in src.items():
        if k in ("hands", "exact"): continue
        e = 1.0 if (src.get("exact") and (k.startswith("arm") or k.startswith("elbow"))) else exag
        base = NEUTRAL.get(k, 0); p[k] = base + (v - base) * e
    p["hands"] = dict(src.get("hands", {}))
    return p

class Acting:
    """keys: [(t, pose_name_or_dict)] -- t = moment the move starts"""
    def __init__(self, keys, personality, fps=24, seed=0):
        self.P = PERSONALITY[personality] if isinstance(personality, str) else personality
        self.fps = fps; self.seed = seed
        self.keys = sorted(keys, key=lambda k: k[0])
        self.full = [_full(p, self.P["exag"]) for _, p in self.keys]

    def __call__(self, t):
        P = self.P
        if P["twos"]: t = math.floor(t * self.fps / 2) * 2 / self.fps
        ks = self.keys; i = 0
        while i + 1 < len(ks) and ks[i + 1][0] <= t: i += 1
        cur = self.full[i]; prev = self.full[i - 1] if i > 0 else cur
        dur = P["frames"] / self.fps * 1.6  # incl. anticipation + settle
        u = (t - ks[i][0]) / dur if i > 0 else 1.0
        m = toon_curve(u, P["antic"], P["over"])
        out = {k: prev.get(k, 0) + (cur.get(k, 0) - prev.get(k, 0)) * m for k in NEUTRAL}
        out["hands"] = cur["hands"] if u > 0.35 else prev["hands"]
        # moving hold: tiny drift + breathing so holds never look frozen
        d = P["drift"]; s = self.seed
        out["tilt"] += d * 1.6 * math.sin(t * 1.3 + s); out["lean"] += d * 0.8 * math.sin(t * 0.9 + s)
        out["armL"] += d * 1.5 * math.sin(t * 1.1 + s + 1); out["armR"] += d * 1.5 * math.sin(t * 1.2 + s + 2)
        out["bob"] += 1.5 * d * (0.5 + 0.5 * math.sin(t * 1.7 + s))
        # squash & stretch on the move: stretch while travelling, squash on the settle
        sq = 1.0
        if 0 < u < 1:
            sq += P["stretch"] * math.sin(math.pi * min(1, max(0, (u - 0.2) / 0.35))) if u < 0.55 else -P["stretch"] * 0.7 * math.sin(math.pi * min(1, (u - 0.55) / 0.45))
        out["sq"] = sq
        out["smear"] = 1.0 if 0.22 < u < 0.5 and P["frames"] <= 4 else 0.0
        return out

def phrase_starts(clip, sr, gap=0.11, thr=0.04):
    """start times (s) of voiced phrases inside a line, split on silences > gap"""
    hop = int(sr * 0.01); env = np.array([np.sqrt(np.mean(clip[i:i + hop] ** 2)) for i in range(0, len(clip) - hop, hop)])
    on = env > thr * env.max(); starts = []; silent = gap
    for k, v in enumerate(on):
        if v and silent >= gap: starts.append(k * 0.01)
        silent = 0 if v else silent + 0.01
    return starts

def say_phrases(V, phrases, voice, speed=1.0, pause=0.22, sr=24000):
    """TTS each phrase separately and join with comic pauses -> (clip, phrase start times)"""
    parts, starts, t = [], [], 0.0
    pauses = pause if isinstance(pause, (list, tuple)) else [pause] * len(phrases)
    for ph, ps in zip(phrases, pauses):
        a = V.say(ph, voice, speed); starts.append(t); parts.append(a); t += len(a) / sr
        gap = np.zeros(int(ps * sr), np.float32); parts.append(gap); t += ps
    return np.concatenate(parts[:-1]).astype(np.float32), starts
