#!/usr/bin/env python3
"""Write logo.txt: a VU meter. Backlit amber face in a walnut case, needle into the red, with the Arch logo where the
dial prints "VU". intro.py scans it in. Run: python3 make_logo.py"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 50, 36
W, H = L.size(COLS, ROWS2)
BG = (0x1e, 0x16, 0x10)
INK, RED, WOOD = (42, 26, 16, 255), (176, 34, 22, 255), (92, 58, 34, 255)
img = Image.new("RGBA", (W, H), WOOD)
yy, xx = np.mgrid[0:H, 0:W]
glow = np.clip(1 - np.hypot((xx - W / 2) / W, (yy - H * 0.9) / H) * 1.2, 0, 1)[:, :, None]
face = np.array((184, 120, 50), float) * (1 - glow) + np.array((252, 208, 128), float) * glow
m = W // 22
panel = Image.fromarray(face.astype(np.uint8)).convert("RGBA").crop((m, m, W - m, H - m * 2))
img.paste(panel, (m, m))
d = ImageDraw.Draw(img)
cx, cy, r = W / 2, H * 1.15, H * 0.92
span = math.radians(60)
point = lambda a, k: (cx + r * k * math.sin(a), cy - r * k * math.cos(a))
line = max(3, H // 90)
for i in range(13):
    a = -span / 2 + span * i / 12
    d.line([point(a, 1), point(a, 1.06 if i % 3 else 1.1)], fill=RED if i >= 9 else INK, width=line)
d.arc([cx - r, cy - r, cx + r, cy + r], math.degrees(-span / 2) - 90, math.degrees(span * 0.25) - 90, fill=INK, width=line)
d.arc([cx - r, cy - r, cx + r, cy + r], math.degrees(span * 0.25) - 90, math.degrees(span / 2) - 90, fill=RED, width=line * 4)
arch = L.arch(int(H * 0.32))
ink = Image.new("RGBA", arch.size, INK)
ink.putalpha(arch)
img.alpha_composite(ink, (int(cx - arch.width / 2), int(H * 0.42)))
d.line([(cx, cy), point(math.radians(23), 1.04)], fill=(20, 12, 8, 255), width=line * 2)
d.rectangle([m, H - m * 2, W - m, H], fill=WOOD)  # the case hides the pivot
L.write(HERE / "logo.txt", L.blocks(img, COLS, ROWS2, BG))
