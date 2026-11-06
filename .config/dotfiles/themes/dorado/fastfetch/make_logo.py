#!/usr/bin/env python3
"""Write logo.txt: a brass astrolabe. Graduated limb, plate with almucantars, a crescent and stars on the rete, the Arch
logo engraved at the centre, with the light falling on the metal from the upper left.
Run: python3 make_logo.py"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 50, 42
W, H = L.size(COLS, ROWS2)
BG = (0x13, 0x18, 0x24)
INK, DEEP = (0x1c, 0x23, 0x34), (0x0d, 0x11, 0x1a)
GOLD, BRASS, OLD = (230, 203, 130), (214, 177, 106), (125, 98, 64)
cx, cy, R = W / 2, H / 2, H * 0.485
yy, xx = np.mgrid[0:H, 0:W]
dist = np.hypot(xx - cx, yy - cy)
sheen = (0.5 + 0.5 * np.cos(np.arctan2(yy - cy, xx - cx) + 2.3))[:, :, None] ** 1.4  # bright towards the upper left
metal = np.array(OLD, float) * (1 - sheen) + np.array(GOLD, float) * sheen
a = np.dstack([metal, (dist < R) * 255.0]).astype(np.uint8)
img = Image.fromarray(a, "RGBA")
d = ImageDraw.Draw(img)
ring = lambda r, **kw: d.ellipse([cx - r, cy - r, cx + r, cy + r], **kw)
for deg in range(0, 360, 10):  # the limb, cut into the metal
    t = math.radians(deg)
    inner = R * (0.80 if deg % 30 == 0 else 0.86)
    d.line([(cx + inner * math.cos(t), cy + inner * math.sin(t)), (cx + R * 0.97 * math.cos(t), cy + R * 0.97 * math.sin(t))], fill=(*DEEP, 255), width=9)
ring(R * 0.76, fill=(*INK, 255))
for f, up in ((0.30, 0.20), (0.46, 0.27), (0.62, 0.32)):  # almucantars
    ring_r = R * f
    d.arc([cx - ring_r, cy - up * R - ring_r, cx + ring_r, cy - up * R + ring_r], 0, 360, fill=(*BRASS, 70), width=5)
# the crescent and two stars on the rete
mx, my, mr = cx + R * 0.46, cy - R * 0.40, R * 0.13
d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(*GOLD, 255))
d.ellipse([mx - mr * 0.62, my - mr * 1.1, mx + mr * 1.25, my + mr * 0.8], fill=(*INK, 255))
for sx, sy in ((-0.48, -0.34), (0.52, 0.28), (-0.5, 0.36)):
    p = (cx + R * sx, cy + R * sy)
    d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=(*GOLD, 255))
# the logo
mask = L.arch(int(R * 0.86))
shade = np.linspace(1, 0, mask.height)[:, None, None]
fill = np.array(GOLD, float) * shade + np.array(BRASS, float) * 0.8 * (1 - shade)
logo = Image.fromarray(np.repeat(fill, mask.width, axis=1).astype(np.uint8)).convert("RGBA")
logo.putalpha(mask)
img.alpha_composite(logo, (round(cx - mask.width / 2), round(cy - mask.height * 0.53)))
L.write(HERE / "logo.txt", L.blocks(img, COLS, ROWS2, BG))
