#!/usr/bin/env python3
"""Write logo.txt: a tilted cube lit from the upper left, the Arch logo stamped on its broad face. Strictly the theme's four
greys, with the shading made by ordered dithering as on a 2-bit display, and a white bevel on the near edges.
Run: python3 make_logo.py"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 46, 40
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.47
near = np.array((0.24 * COLS * L.PX_W, 0.98 * ROWS2 * L.PX_H))
e1 = np.array((31.0, -6.0)) * L.PX_W  # to the right, rising
e2 = np.array((-9.0, -6.5)) * L.PX_W  # to the left, rising
up = np.array((0.0, -26.0)) * L.PX_H


def solve(p, o, a, b):
    return np.linalg.solve(np.column_stack((a, b)), p - o)


logo = np.asarray(L.arch(240).resize((240, 240), Image.LANCZOS), float) / 255
px = np.zeros((ROWS2, COLS, 4), np.uint8)
for y in range(ROWS2):
    for x in range(COLS):
        p = np.array(((x + 0.5) * L.PX_W, (y + 0.5) * L.PX_H))
        tone = None
        u, v = solve(p, near, e1, up)  # broad face: dark, lifting towards the top
        if 0 <= u <= 1 and 0 <= v <= 1:
            tone = 0.04 + 0.22 * v
            if logo[int((1 - (v - 0.09) / 0.82) * 239) if 0.09 <= v <= 0.91 else 0, int((u - 0.11) / 0.78 * 239) if 0.11 <= u <= 0.89 else 0] > 0.5 and 0.09 <= v <= 0.91 and 0.11 <= u <= 0.89:
                tone = 0.72 + 0.28 * v
            edge = min(u, 1 - v) < 0.022 or v > 0.975
            tone = 1 if edge else tone
        a, b = solve(p, near, e2, up)
        if tone is None and 0 <= a <= 1 and 0 <= b <= 1:  # side face: in shadow
            tone = 0.02 + 0.2 * (1 - a) * b
        c, e = solve(p, near + up, e1, e2)
        if tone is None and 0 <= c <= 1 and 0 <= e <= 1:  # top: catches the light
            tone = 0.52 + 0.26 * e
        if tone is None:
            continue
        level = int(np.clip(round(tone * 3 + BAYER[y % 4, x % 4]), 0, 3))
        px[y, x] = (level * 85, level * 85, level * 85, 255)
L.write(HERE / "logo.txt", L.blocks(Image.fromarray(px, "RGBA"), COLS, ROWS2, (255, 255, 255), resample=Image.NEAREST))
