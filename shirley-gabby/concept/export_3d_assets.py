"""Export what the Blender build needs from the FINAL 2D designs (teens_sheet.py):
  - profiles.json : front-silhouette widths (y -> xmin,xmax) of faces, hair, hoodies, so 3D shapes match the sheet
  - decals/<who>_<expr>.png : transparent face-feature art (eyes, brows, nose, mouth, blush) per expression
Units are the sheet's head-local units (origin = face centre, y down). Blender scale is applied there.
    python3 export_3d_assets.py  -> ./assets3d/
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgpathtools import parse_path, Line
import teens_sheet as T
from gabby_sheet import SVG

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets3d")
os.makedirs(os.path.join(OUT, "decals"), exist_ok=True)

SHAPES = {
    "face_shirley": T.FACE_SH,
    "face_gabby": T.FACE_GB,
    "bob_shirley": "M-100,-104 C-110,-190 110,-190 100,-104 C108,-46 108,14 102,62 Q56,76 0,74 Q-56,76 -102,62 C-108,14 -108,-46 -100,-104 Z",
    "hair_gabby": ("M-86,-74 C-99,-156 -36,-196 9,-188 C68,-182 103,-148 86,-74 "
                   "L76,-84 Q65,-104 52,-88 Q40,-110 25,-92 Q11,-114 -5,-94 Q-22,-112 -36,-92 Q-50,-108 -65,-88 Q-77,-102 -86,-74 Z"),
    "hoodie_gabby": "M-50,128 C-80,132 -96,148 -100,184 C-106,244 -102,300 -98,350 L98,350 C102,300 106,244 100,184 C96,148 80,132 50,128 Z",
    "hoodie_shirley": ("M-46,146 C-66,150 -80,160 -82,190 C-84,236 -74,270 -68,300 C-70,340 -74,380 -78,418 "
                       "L78,418 C74,380 70,340 68,300 C74,270 84,236 82,190 C80,160 66,150 46,146 Z"),
}
# where the face shows through the hair in the front view (polygons, sheet units)
SH_TIPS = [(-82, -62), (-66, -54), (-50, -64), (-34, -52), (-18, -66), (-2, -54), (14, -66), (30, -54), (46, -64), (62, -52), (78, -62), (90, -80)]
OPENINGS = {
    "shirley": [(-74, -104 + 30)] + SH_TIPS + [(80, -60), (82, -10), (88, 40), (92, 62), (92, 220), (-92, 220), (-88, 40), (-82, -10), (-80, -60)],
    "gabby": [(-90, -74), (-77, -102), (-65, -88), (-50, -108), (-36, -92), (-22, -112), (-5, -94), (11, -114), (25, -92), (40, -110),
              (52, -88), (65, -104), (76, -84), (90, -74), (110, 220), (-110, 220)],
}


def profile(d, step=2.0):
    p = parse_path(d)
    xs = [p.point(t / 400).real for t in range(401)]
    ys = [p.point(t / 400).imag for t in range(401)]
    x0, x1, y0, y1 = min(xs) - 5, max(xs) + 5, min(ys), max(ys)
    rows, y = [], y0 + 0.01
    while y < y1:
        hits = []
        for seg in p:
            for (t1, _t2) in seg.intersect(Line(complex(x0, y), complex(x1, y))):
                hits.append(seg.point(t1).real)
        if len(hits) >= 2:
            rows.append([round(y, 2), round(min(hits), 2), round(max(hits), 2)])
        y += step
    rows.append([round(y1, 2), rows[-1][1] * 0.3, rows[-1][2] * 0.3]) if rows else None
    return rows


def decal(who, expr, path_png):
    VB = (-120, -190, 240, 340)  # x, y, w, h in sheet units
    S = SVG(240 * 4, 340 * 4)
    S.add(f'<g transform="scale(4) translate({-VB[0]},{-VB[1]})">')
    (T.shirley_head if who == "shirley" else T.gabby_head)(S, 0, 0, 1.0, expr, features_only=True)
    S.add("</g>")
    svg = path_png.replace(".png", ".svg")
    open(svg, "w").write(S.out())
    return svg, VB


if __name__ == "__main__":
    data = {"units": "sheet units, origin = face centre, y down", "shapes": {k: profile(v) for k, v in SHAPES.items()},
            "openings": OPENINGS, "decal_viewbox": [-120, -190, 240, 340], "decals": {}}
    jobs = []
    for who, exprs in (("shirley", T.SH_EXPR), ("gabby", T.GB_EXPR)):
        for e in exprs:
            png = os.path.join(OUT, "decals", f"{who}_{e}.png")
            svg, _ = decal(who, e, png)
            jobs.append((svg, png))
            data["decals"].setdefault(who, []).append(e)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 960, "height": 1360})
        for svg, png in jobs:
            pg.goto("file://" + svg)
            pg.screenshot(path=png, omit_background=True)
            os.remove(svg)
        b.close()
    json.dump(data, open(os.path.join(OUT, "profiles.json"), "w"))
    print(len(jobs), "decals;", {k: len(v) for k, v in data["shapes"].items()})
