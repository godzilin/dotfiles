#!/usr/bin/env python3
"""Write logo.txt: the Arch logo as a drawing on the blueprint. White outline, dash-dot centre line, dimension lines with
ticks and a construction circle, plotted in Braille dots (2 x 4 per text cell) so the lines stay as thin as a pen's,
and a title line under it. Run: python3 make_logo.py"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS = 42, 18
W, H = COLS * 2, ROWS * 4
S = 8
WHITE, PALE = "\x1b[38;2;243;248;254m", "\x1b[38;2;142;174;214m"
BIT = ((0x01, 0x08), (0x02, 0x10), (0x04, 0x20), (0x40, 0x80))

mask = L.arch(int(H * 0.80) * S)
mask = mask.resize((int(mask.width * 0.95), mask.height), Image.LANCZOS).point(lambda v: 255 * (v > 128))
edge = Image.new("L", (W * S, H * S), 0)
x0, y0 = (W * S - mask.width) // 2 - 4 * S, 3 * S
outline = Image.fromarray(np.asarray(mask.filter(ImageFilter.MaxFilter(5))).astype(int).__sub__(np.asarray(mask.filter(ImageFilter.MinFilter(5)))).astype(np.uint8))
edge.paste(outline, (x0, y0))
dims = Image.new("L", (W * S, H * S), 0)
d = ImageDraw.Draw(dims)
ax = x0 + mask.width // 2
for y in range(0, H * S, 10 * S):  # centre line, dash-dot
    d.line([(ax, y), (ax, y + 5 * S)], fill=255, width=S)
    d.line([(ax, y + 7 * S), (ax, y + 8 * S)], fill=255, width=S)
base = y0 + mask.height
foot = base + 5 * S
d.line([(x0, base + S), (x0, foot + 2 * S)], fill=255, width=S)  # width of the logo
d.line([(x0 + mask.width, base + S), (x0 + mask.width, foot + 2 * S)], fill=255, width=S)
d.line([(x0, foot), (x0 + mask.width, foot)], fill=255, width=S)
right = x0 + mask.width + 6 * S
d.line([(ax + 3 * S, y0), (right + 2 * S, y0)], fill=255, width=S)  # height of the logo
d.line([(x0 + mask.width + S, base), (right + 2 * S, base)], fill=255, width=S)
d.line([(right, y0), (right, base)], fill=255, width=S)
for px_, py_ in ((x0, foot), (x0 + mask.width, foot), (right, y0), (right, base)):  # 45 degree ticks, as draughtsmen do
    d.line([(px_ - 2 * S, py_ + 2 * S), (px_ + 2 * S, py_ - 2 * S)], fill=255, width=S)
r = int(mask.height * 0.20)
d.ellipse([ax - r, y0 + mask.height * 0.72 - r, ax + r, y0 + mask.height * 0.72 + r], outline=255, width=S)
down = lambda im: np.asarray(im.resize((W, H), Image.BOX)) > 40
line, dim = down(edge), down(dims)
out = []
for row in range(ROWS):
    s = ""
    for col in range(COLS):
        a, b = line[row * 4:row * 4 + 4, col * 2:col * 2 + 2], dim[row * 4:row * 4 + 4, col * 2:col * 2 + 2]
        n = sum(BIT[y][x] for y in range(4) for x in range(2) if a[y, x] or b[y, x])
        s += ((WHITE if a.any() else PALE) + chr(0x2800 + n) + "\x1b[0m") if n else " "
    out.append(s.rstrip())
out.append(PALE + "  PLANO A-01    ESC 1:1    ROLLING RELEASE\x1b[0m")
L.write(HERE / "logo.txt", out)
