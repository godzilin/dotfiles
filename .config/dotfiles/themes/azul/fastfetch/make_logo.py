#!/usr/bin/env python3
"""Write logo.txt: the Arch logo as a waving four-pane flag shedding a trail of square pixels to the left, in hard 16-colour
VGA pixels with no smoothing, the way a boot screen of the time drew it. Run: python3 make_logo.py"""
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 58, 40
PANES = ((255, 0, 0), (0, 170, 0), (0, 0, 255), (255, 204, 0))
FX, FW, FH = 17, 38, 32  # where the flag starts and its size, in pixels before the wave

m = L.arch(FH * 8)
m = np.asarray(m.resize((FW * 8, FH * 8), Image.LANCZOS)) > 128
img = np.zeros((ROWS2, COLS, 4), np.uint8)
for y in range(ROWS2):
    for x in range(FX - 2, COLS):
        u = x - FX
        v = y - 4 - 2.2 * math.sin(u / FW * 2 * math.pi * 0.95 + 0.4) + u * 0.04  # the wave, and a slight perspective
        if not (0 <= u < FW and 0 <= v < FH) or not m[int(v * 8), u * 8]:
            continue
        cx, cy = u - FW / 2, v - FH * 0.56
        if abs(cy) < 0.6 or (abs(cx) < 0.5 and cy > 0):  # the black lines between the panes; the apex is too thin to split
            continue
        img[y, x] = (*PANES[(cy > 0) * 2 + (cx > 0)], 255)
rng = random.Random(95)
for x in range(0, FX, 2):  # the trail: blocks of 2 x 2, thinner and rarer as they fall behind
    for y in range(4, ROWS2 - 8, 2):
        wave = 22 + 2.2 * math.sin((x - FX) / FW * 2 * math.pi * 0.95 + 0.4)
        if abs(y - wave) < 10 * x / FX + 2 and rng.random() < (x / FX) ** 2.2 * 0.8:
            pane = (y > wave) * 2
            img[y:y + 2, x:x + 2] = (*PANES[pane], 255)
L.write(HERE / "logo.txt", L.blocks(Image.fromarray(img, "RGBA"), COLS, ROWS2, (0, 0, 0), resample=Image.NEAREST))
