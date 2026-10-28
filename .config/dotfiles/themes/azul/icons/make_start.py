#!/usr/bin/env python3
"""Write start.png (16 px) for the Inicio button: the Arch logo (archlinux.svg) as pixel art in the
four panes of the old waving flag, outlined in black like the Chicago95 icons. Needs rsvg-convert. Run: python3 make_start.py"""
import io
import subprocess
from pathlib import Path

from PIL import Image

here = Path(__file__).parent
COLORS = [(255, 0, 0), (0, 170, 0), (0, 0, 255), (255, 204, 0)]  # top-left, top-right, bottom-left, bottom-right


def icon(size):
    inner = size - 2  # one pixel of outline round the shape
    png = subprocess.run(["rsvg-convert", "-w", str(inner * 10), "-h", str(inner * 10), str(here / "archlinux.svg")],
                         capture_output=True, check=True).stdout
    a = Image.open(io.BytesIO(png)).split()[-1].resize((inner, inner), Image.BOX)
    on = [[a.getpixel((x, y)) > 100 for x in range(inner)] for y in range(inner)]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(size):
        for x in range(size):
            ix, iy = x - 1, y - 1
            inside = 0 <= ix < inner and 0 <= iy < inner and on[iy][ix]
            near = any(0 <= ix + dx < inner and 0 <= iy + dy < inner and on[iy + dy][ix + dx]
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if inside:
                img.putpixel((x, y), COLORS[(y >= size // 2) * 2 + (x >= size // 2)] + (255,))
            elif near:
                img.putpixel((x, y), (0, 0, 0, 255))
    return img


icon(16).save(here / "start.png")
