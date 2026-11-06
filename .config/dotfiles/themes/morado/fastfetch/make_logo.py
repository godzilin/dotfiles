#!/usr/bin/env python3
"""Write logo.txt: a lit vertical sign in the rain with the Arch logo cut out of it, reflected on the wet road. Run: python3 make_logo.py"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 44, 42
W, H = L.size(COLS, ROWS2)
BG = (0x15, 0x10, 0x2a)
VIOLET, NIGHT = (183, 155, 255, 255), (14, 10, 26, 255)
ROAD = int(H * 0.80)
img = Image.new("RGBA", (W, H), (*BG, 0))
d = ImageDraw.Draw(img)
sw = int(W * 0.52)
x0, y0 = (W - sw) // 2, int(H * 0.02)
d.rectangle([x0, y0, x0 + sw, ROAD], fill=VIOLET)
arch = L.arch(int(sw * 0.82))
hole = Image.new("RGBA", arch.size, NIGHT)
hole.putalpha(arch)
img.alpha_composite(hole, ((W - arch.width) // 2, (y0 + ROAD - arch.height) // 2))
d = ImageDraw.Draw(img)
for i in range(ROAD, H, H // 42):  # the reflection breaks up towards the viewer
    fade = 1 - (i - ROAD) / (H - ROAD)
    ink = [round(v * fade * 0.7 + b * (1 - fade * 0.7)) for v, b in zip(VIOLET[:3], BG)]
    d.rectangle([x0, i, x0 + sw, i + H // 84], fill=(*ink, 255))
rng = random.Random(7)
for _ in range(26):
    x, y = rng.randrange(W), rng.randrange(H)
    d.line([(x, y), (x - W // 40, y + H // 9)], fill=(111, 217, 224, 255), width=max(3, H // 150))
L.write(HERE / "logo.txt", L.blocks(img, COLS, ROWS2, BG))
