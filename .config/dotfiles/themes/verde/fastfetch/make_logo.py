#!/usr/bin/env python3
"""Draw the fastfetch logo into logo.txt: a round vignette at dusk, painted with the same
functions as the wallpapers (wallpapers/bosque.py) and packed into truecolor half blocks (one cell = two pixels,
foreground on top, background below): the Teide over the mist with firs in front. Run: python3 make_logo.py"""
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "wallpapers"))
import bosque as b  # noqa: E402

ROWS2 = 28  # pixel rows (= text rows * 2)
COLS = 34  # a half-block pixel is ~9x11 screen px in alacritty, so the circle needs more columns than rows
K = 12  # render this many times larger, then average down: smooth edges at a tiny size
SW, SH = COLS * K, ROWS2 * K
U = SH / 100  # drawing unit: 1% of the height

img = b.gradient(b.mix(b.SUN, b.TEXT, 0.35), b.mix(b.BARK, b.BG2, 0.35), SW, SH, power=1.3).convert("RGBA")
img.alpha_composite(b.glow(img.size, [(SW * 0.68, 34 * U, 11 * U)], b.mix(b.SUN, b.TEXT, 0.6), 7 * U))
d = ImageDraw.Draw(img)
peak = [(-10 * U, 78 * U), (SW * 0.30, 40 * U), (SW * 0.40, 33 * U), (SW * 0.47, 33 * U), (SW * 0.58, 41 * U),
        (SW + 10 * U, 70 * U), (SW, SH), (0, SH)]  # a volcano with a flat top, the Teide from the forest
d.polygon(peak, fill=b.mix(b.SKY, b.BG2, 0.45))
img.alpha_composite(b.mist(img.size, 66 * U, 12 * U, b.mix(b.SUN, b.TEXT, 0.4), 130))
d = ImageDraw.Draw(img)
rng = random.Random(3)
ridge = b.ridge(rng, 74 * U, 3 * U, w=SW, octaves=2)
d.polygon([(0, SH)] + [(x, ridge[x]) for x in range(0, SW, 4)] + [(SW - 1, SH)], fill=b.mix(b.FERN, b.BG1, 0.45))


def fir(x, ground, h, color):
    """Broad fir in three tiers: the wallpapers' firs are too slim to read at 30 pixels."""
    d.rectangle([x - h * 0.04, ground - h * 0.15, x + h * 0.04, ground], fill=color)
    for top, bottom, half in [(0.0, 0.42, 0.20), (0.22, 0.68, 0.30), (0.45, 0.9, 0.40)]:
        d.polygon([(x, ground - h + top * h), (x + half * h, ground - h + bottom * h), (x - half * h, ground - h + bottom * h)],
                  fill=color)


for x, h, t in [(0.30, 34, 0.55), (0.78, 40, 0.6), (0.12, 52, 0.75), (0.93, 36, 0.75)]:  # darkest in front
    fir(SW * x, SH - 8 * U, h * U, b.mix(b.FERN, b.NIGHT, t))
d.rectangle([0, SH - 10 * U, SW, SH], fill=b.rgb(b.NIGHT))

mask = Image.new("L", (SW, SH), 0)
ImageDraw.Draw(mask).ellipse([K // 2, K // 2, SW - K // 2, SH - K // 2], fill=255)
img.putalpha(mask)
px = np.asarray(img.resize((COLS, ROWS2), Image.BOX)).astype(int)


def cell(top, bottom):
    on_t, on_b = top[3] > 160, bottom[3] > 160
    fg = lambda p: f"\x1b[38;2;{p[0]};{p[1]};{p[2]}m"
    bg = lambda p: f"\x1b[48;2;{p[0]};{p[1]};{p[2]}m"
    if on_t and on_b:
        return fg(top) + bg(bottom) + "▀\x1b[0m"
    if on_t:
        return fg(top) + "▀\x1b[0m"
    if on_b:
        return fg(bottom) + "▄\x1b[0m"
    return " "


lines = ["".join(cell(px[r, c], px[r + 1, c]) for c in range(COLS)).rstrip() for r in range(0, ROWS2, 2)]
with open(os.path.join(HERE, "logo.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
