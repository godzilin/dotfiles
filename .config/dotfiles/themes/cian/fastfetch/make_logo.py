#!/usr/bin/env python3
"""Write logo.txt: the Arch Linux logo (../icons/archlinux.svg) in solid half blocks, striped top to bottom from white to
the blue of the paper, like a line drawing fading out (the colours are in config.jsonc).
Needs rsvg-convert (librsvg). Run: python3 make_logo.py"""
import io
import subprocess
from pathlib import Path

from PIL import Image

W, H = 44, 40  # pixels; two pixel rows per text row
here = Path(__file__).parent
png = subprocess.run(["rsvg-convert", "-w", "440", "-h", "440", str(here.parent / "icons/archlinux.svg")],
                     capture_output=True, check=True).stdout
a = Image.open(io.BytesIO(png)).split()[-1].resize((W, H), Image.BOX)
px = [[a.getpixel((x, y)) > 110 for x in range(W)] for y in range(H)]
for y in range(1, H - 1):  # fill one-pixel holes the small size leaves inside the shape
    for x in range(1, W - 1):
        px[y][x] |= px[y - 1][x] + px[y + 1][x] + px[y][x - 1] + px[y][x + 1] >= 3
on = lambda x, y: px[y][x]
rows = H // 2
out = []
for r in range(rows):
    cells = "".join("█" if on(x, 2 * r) and on(x, 2 * r + 1) else "▀" if on(x, 2 * r) else "▄" if on(x, 2 * r + 1) else " "
                    for x in range(W))
    out.append(f"${1 + r * 4 // rows}{cells.rstrip()}")
(here / "logo.txt").write_text("\n".join(out) + "\n")
