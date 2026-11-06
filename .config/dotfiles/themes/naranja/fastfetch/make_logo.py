#!/usr/bin/env python3
"""Write skull.txt: the ship's warning plate. A bone-amber skull whose nasal cavity is the Arch logo, one eye still lit,
over the four diagonal stripes of the theme, with the scanlines of a CRT. intro.py scans it in. Run: python3 make_logo.py"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 50, 40
W, H = L.size(COLS, ROWS2)
BG = (0x1a, 0x18, 0x14)
HOLE = (*BG, 255)
STRIPES = ((224, 195, 106), (233, 162, 59), (217, 101, 43), (200, 85, 61))
img = Image.new("RGBA", (W, H), (*BG, 0))
d = ImageDraw.Draw(img)
band, slope = H * 0.058, H * 0.34
for i, ink in enumerate(STRIPES):
    y0 = H * 0.52 + (i - 2) * band
    d.polygon([(0, y0 + slope), (W, y0 - slope), (W, y0 - slope + band * 0.86), (0, y0 + slope + band * 0.86)], fill=(*ink, 255))
cx = W / 2
skull = Image.new("L", (W, H), 0)
s = ImageDraw.Draw(skull)
s.ellipse([cx - W * 0.31, H * 0.02, cx + W * 0.31, H * 0.74], fill=255)
s.rounded_rectangle([cx - W * 0.18, H * 0.62, cx + W * 0.18, H * 0.97], radius=H // 28, fill=255)
yy = np.arange(H)[:, None] / H
bone = np.array((232, 214, 170), float) * (1 - yy[:, :, None] ** 1.4) + np.array((150, 104, 44), float) * yy[:, :, None] ** 1.4
xx = np.abs(np.arange(W)[None, :] - cx) / (W * 0.31)
bone = np.repeat(bone, W, axis=1) * (1 - 0.4 * (xx ** 3).clip(0, 1))[:, :, None]
head = Image.fromarray(bone.clip(0, 255).astype(np.uint8)).convert("RGBA")
ring = Image.new("RGBA", (W, H), HOLE)
ring.putalpha(skull.filter(ImageFilter.MaxFilter(25)))
img.alpha_composite(ring)
head.putalpha(skull)
img.alpha_composite(head)
d = ImageDraw.Draw(img)
for side in (-1, 1):  # sockets: wide, tilted inwards
    ex, ey, rx, ry = cx + side * W * 0.145, H * 0.40, W * 0.105, H * 0.105
    d.polygon([(ex - rx, ey - ry * 0.25 + side * ry * 0.35), (ex - rx * 0.4, ey - ry * (1.0 + side * 0.25)), (ex + rx * 0.4, ey - ry * (1.0 - side * 0.25)),
               (ex + rx, ey - ry * 0.25 - side * ry * 0.35), (ex + rx * 0.8, ey + ry * 0.9), (ex - rx * 0.8, ey + ry * 0.9)], fill=HOLE)
er = W * 0.024
ex, ey = cx + W * 0.145, H * 0.42
d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(233, 62, 40, 255))
nose = L.arch(int(H * 0.17))
hole = Image.new("RGBA", nose.size, HOLE)
hole.putalpha(nose)
img.alpha_composite(hole, (round(cx - nose.width / 2), round(H * 0.525)))
for i in range(-2, 3):  # teeth
    x = cx + i * W * 0.062
    d.rectangle([x - W * 0.008, H * 0.77, x + W * 0.008, H * 0.97], fill=HOLE)
d.rectangle([cx - W * 0.2, H * 0.755, cx + W * 0.2, H * 0.772], fill=HOLE)

px = np.asarray(img.resize((COLS, ROWS2), Image.BOX)).copy()
px[1::2, :, :3] = (px[1::2, :, :3] * 0.72).astype(np.uint8)  # scanlines
L.write(HERE / "skull.txt", L.blocks(Image.fromarray(px, "RGBA"), COLS, ROWS2, BG, resample=Image.NEAREST))
