#!/usr/bin/env python3
"""Write logo.txt: a constructivist poster. The Arch logo is a red wedge thrust into a black disc from the lower left, with
black bars and a red block driving along the same diagonal; flat ink on the terminal's paper. Run: python3 make_logo.py"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 50, 42
W, H = L.size(COLS, ROWS2)
PAPER, RED, BLACK = (0xef, 0xe6, 0xd2), (212, 42, 30, 255), (20, 20, 20, 255)
img = Image.new("RGBA", (W, H), (*PAPER, 0))
d = ImageDraw.Draw(img)
r = H * 0.33
cx, cy = W * 0.66, H * 0.36
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLACK)
# bars along the diagonal, on a layer turned as a whole
bars = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
b = ImageDraw.Draw(bars)
mx, my = W, H
for off, length, thick, ink, along in ((H * 0.40, H * 0.82, H * 0.055, BLACK, 0), (H * 0.50, H * 0.46, H * 0.03, BLACK, H * 0.1), (-H * 0.42, H * 0.34, H * 0.05, RED, -H * 0.3)):
    b.rectangle([mx - length / 2 + along, my + off, mx + length / 2 + along, my + off + thick], fill=ink)
bars = bars.rotate(38, Image.BICUBIC, center=(mx, my))
img.alpha_composite(bars.crop((W // 2, H // 2, W // 2 + W, H // 2 + H)))
# the wedge
mask = L.arch(H * 74 // 100)
sheet = Image.new("L", (mask.width * 2, mask.height * 2), 0)
sheet.paste(mask, (mask.width // 2, mask.height // 2))
sheet = sheet.rotate(-24, Image.BICUBIC)
ink = Image.new("RGBA", sheet.size, RED)
ink.putalpha(sheet)
img.alpha_composite(ink.crop(ink.getbbox()), (round(W * 0.03), round(H * 0.19)))
L.write(HERE / "logo.txt", L.blocks(img, COLS, ROWS2, PAPER, cut=128))
