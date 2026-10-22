#!/usr/bin/env python3
"""Draw logo.txt for fastfetch: an isometric cube in half-block characters (each row is two square pixels).
$1 top face, $2 left face, $3 right face (colours set in config.jsonc). Run: python3 make_logo.py"""
from pathlib import Path

COLS, ROWS = 27, 14
R = 13.0                      # cube "radius": centre to any outer corner
CX, CY = 13.5, 14.0
DX, DY = R * 0.866, R * 0.5   # isometric offsets of the side corners


def inside(p, a, b, c, d):
    """Point p inside the convex quad a-b-c-d (any winding)."""
    pts = [a, b, c, d]
    signs = []
    for i in range(4):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 4]
        signs.append((x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) >= 0)
    return all(signs) or not any(signs)


def pixel(x, y):
    p = (x + 0.5, y + 0.5)
    top, centre, bottom = (CX, CY - R), (CX, CY), (CX, CY + R)
    lt, rt = (CX - DX, CY - DY), (CX + DX, CY - DY)
    lb, rb = (CX - DX, CY + DY), (CX + DX, CY + DY)
    if inside(p, top, rt, centre, lt):
        return 1
    if inside(p, lt, centre, bottom, lb):
        return 2
    if inside(p, centre, rt, rb, bottom):
        return 3
    return 0


lines = []
for r in range(ROWS):
    out, cur = "", None
    for c in range(COLS):
        t, b = pixel(c, 2 * r), pixel(c, 2 * r + 1)
        if t == b == 0:
            out += " "
            continue
        ch, col = ("█", t) if t and b else (("▀", t) if t else ("▄", b))  # two faces in one cell: the top one wins
        if col != cur:
            out += f"${col}"
            cur = col
        out += ch
    lines.append(out.rstrip())
Path(__file__).with_name("logo.txt").write_text("\n".join(lines) + "\n")
print("\n".join(l.replace("$1", "").replace("$2", "").replace("$3", "") for l in lines))
