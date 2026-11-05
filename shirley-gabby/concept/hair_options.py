"""Hairstyle options for the teen redesign: 3 modern styles each for Shirley and Gabby (busts).
    python3 hair_options.py -> hair_options.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import teens_sheet as T
from gabby_sheet import SVG, cel, line, text, INK


def bust(S, x, y, who, hair, expr, s=1.0):
    c = T.SH if who == "S" else T.GB
    S.add(f'<g transform="translate({x},{y}) scale({s})">')
    if who == "S":
        cel(S, "M-20,96 L20,96 L22,150 L-22,150 Z", *c["skin"], -8, 10, 4.5)
        cel(S, "M-120,210 C-118,170 -90,150 -50,146 L50,146 C90,150 118,170 120,210 Z", *c["kurta"], -10, -6, 4.5)
        cel(S, "M-26,128 L26,128 L28,150 L-28,150 Z", *c["kurta"], -3, -3, 3.5)
        line(S, "M-28,150 L28,150 M0,150 L0,206", 3, c["gold"][0])
    else:
        cel(S, "M-22,96 L22,96 L24,150 L-24,150 Z", *c["skin"], -8, 10, 4.5)
        cel(S, "M-120,210 C-118,170 -90,150 -50,140 L50,140 C90,150 118,170 120,210 Z", *c["shirt"], -10, -6, 4.5)
        for sx in (-1, 1):
            cel(S, f"M{-44 * sx},134 L{-6 * sx},170 L{-28 * sx},180 L{-52 * sx},154 Z", *c["shirt"], -3, -3, 3.5)
    S.add("</g>")
    (T.shirley_head if who == "S" else T.gabby_head)(S, x, y, s, expr, hair=hair)


def sheet(path_svg):
    W, H = 2400, 1520
    S = SVG(W, H)
    S.add(f'<rect width="{W}" height="{H}" fill="{T.BG}"/>')
    text(S, 60, 84, "HAIRSTYLE OPTIONS", 60, 900)
    text(S, 64, 122, "pick one for each · current style shown first", 24, 500, "#5a4a3c")
    rows = [("S", "SHIRLEY", "#f6b2a6", "#e4877c", "calm",
             [("base", "current: bob + fringe"), ("angled", "A · angled bob, side-swept\nfringe, burgundy streak"),
              ("lob", "B · curtain-bangs lob,\nsoft waves, warm ends"), ("halfup", "C · half-up mini bun,\nwispy fringe, flicked ends")]),
            ("G", "GABBY", "#ffd84d", "#f2a93b", "grin",
             [("base", "current: short wavy"), ("curly", "A · curly top + fade,\nshaved slit"),
              ("quiff", "B · spiky textured quiff,\nfaded sides"), ("curtain", "C · messy middle-part\ncurtain fringe")])]
    for r, (who, name, col, dot, expr, opts) in enumerate(rows):
        y0 = 170 + r * 670
        text(S, 60, y0 + 40, name, 34, 900)
        for i, (k, lab) in enumerate(opts):
            x0 = 60 + i * 580
            T.halftone_bg(S, x0, y0 + 60, 540, 560, col if i else "#ece4d4", dot if i else "#d8cdb8")
            bust(S, x0 + 270, y0 + 320, who, k, expr, 1.0)
            S.add(f'<rect x="{x0 + 16}" y="{y0 + 500}" width="508" height="104" fill="#ffffff" stroke="{INK}" stroke-width="4"/>')
            for j, ln in enumerate(lab.split("\n")):
                text(S, x0 + 34, y0 + 540 + 34 * j, ln, 26 if j == 0 else 24, 800 if j == 0 else 500)
    open(path_svg, "w").write(S.out())


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    svg = os.path.join(here, "hair_options.svg")
    sheet(svg)
    png = os.path.join(here, "hair_options.png")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 2400, "height": 1520})
        pg.goto("file://" + svg)
        pg.screenshot(path=png)
        b.close()
    print(png)
