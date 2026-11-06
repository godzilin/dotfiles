#!/usr/bin/env python3
"""Write logo.txt: a night drive. A lavender sun cut into slices sets behind the Arch logo, a dark peak with a thin lit rim,
and a perspective grid runs off to the horizon. No pink and no glow: this theme is the sober one. Run: python3 make_logo.py"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 48, 42
W, H = L.size(COLS, ROWS2)
BG = (0x12, 0x04, 0x27)
HORIZON = H * 0.70
LAV, VIO, DEEP, CYAN = (195, 174, 230), (157, 123, 255), (106, 74, 158), (45, 226, 230)
cx, r = W / 2, H * 0.40
sy = H * 0.42
yy, xx = np.mgrid[0:H, 0:W]
t = np.clip((yy - (sy - r)) / (2 * r), 0, 1)[:, :, None]
sun = np.array(LAV, float) * (1 - t) + np.array(DEEP, float) * t
disc = (np.hypot(xx - cx, yy - sy) < r) & (yy < HORIZON)
for i in range(6):  # the slices, wider towards the horizon
    y0 = sy - r * 0.10 + i * i * r * 0.052 + i * r * 0.09
    disc &= ~((yy > y0) & (yy < y0 + r * (0.022 + 0.017 * i)))
a = np.dstack([sun, disc * 255.0]).astype(np.uint8)
img = Image.fromarray(a, "RGBA")
d = ImageDraw.Draw(img)
# the grid: rays from the vanishing point, and rows that crowd towards the horizon
line = max(3, H // 150)
for i in range(-9, 10):
    d.line([(cx + i * W * 0.012, HORIZON), (cx + i * W * 0.17, H)], fill=(*VIO, 255), width=line)
for i in range(1, 7):
    y = HORIZON + (H - HORIZON) * (i / 6) ** 2.1
    d.line([(0, y), (W, y)], fill=(*VIO, 255), width=line)
d.line([(0, HORIZON), (W, HORIZON)], fill=(*CYAN, 255), width=line * 2)
# the peak: rim of light first, dark body inside it
mask = L.arch(int(H * 0.60))
x, y = (W - mask.width) // 2, int(HORIZON) - mask.height + line
rim = Image.new("RGBA", mask.size, (*VIO, 255))
rim.putalpha(mask.filter(ImageFilter.MaxFilter(11)))
img.alpha_composite(rim, (x, y))
body = Image.new("RGBA", mask.size, (*BG, 255))
body.putalpha(mask.filter(ImageFilter.MinFilter(5)))
img.alpha_composite(body, (x, y))
L.write(HERE / "logo.txt", L.blocks(img, COLS, ROWS2, BG, cut=90))
