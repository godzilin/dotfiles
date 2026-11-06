#!/usr/bin/env python3
"""A wet street at night, very simplified: dark blocks, unlabelled lit signs, thin rain and their reflection on the road. No text."""
import random
from pathlib import Path

import cairo

W, H = 1920, 1200
HORIZON = 800
OUT = Path(__file__).resolve().parent / "rotation"
SIGNS = ((1.0, 0.42, 0.42), (1.0, 0.81, 0.42), (0.72, 0.61, 1.0), (0.44, 0.85, 0.88))


def sky(c):
    g = cairo.LinearGradient(0, 0, 0, HORIZON)
    g.add_color_stop_rgb(0, 0.055, 0.04, 0.10)
    g.add_color_stop_rgb(1, 0.20, 0.13, 0.36)
    c.set_source(g)
    c.paint()


def block(c, x, w, top, shade):
    c.set_source_rgb(0.07 * shade, 0.05 * shade, 0.13 * shade)
    c.rectangle(x, top, w, HORIZON - top)
    c.fill()


def sign(c, x, y, w, h, colour):
    """A plain vertical panel with its reflection stretched on the road."""
    r, g, b = colour
    c.set_source_rgba(r, g, b, 0.9)
    c.rectangle(x, y, w, h)
    c.fill()
    glow = cairo.RadialGradient(x + w / 2, y + h / 2, 0, x + w / 2, y + h / 2, h)
    glow.add_color_stop_rgba(0, r, g, b, 0.16)
    glow.add_color_stop_rgba(1, r, g, b, 0)
    c.set_source(glow)
    c.rectangle(x - h, y - h, w + 2 * h, 3 * h)
    c.fill()
    road = cairo.LinearGradient(0, HORIZON, 0, H)
    road.add_color_stop_rgba(0, r, g, b, 0.28)
    road.add_color_stop_rgba(1, r, g, b, 0)
    c.set_source(road)
    c.rectangle(x - 3, HORIZON, w + 6, H - HORIZON)
    c.fill()


def rain(c, rng, n):
    c.set_line_width(1)
    for _ in range(n):
        x, y, length = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(18, 60)
        c.set_source_rgba(0.77, 0.73, 0.86, rng.uniform(0.05, 0.22))
        c.move_to(x, y)
        c.line_to(x - length * 0.12, y + length)
        c.stroke()


def scene(name, seed, blocks, signs, drops):
    rng = random.Random(seed)
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surface)
    sky(c)
    c.set_source_rgb(0.035, 0.027, 0.07)
    c.rectangle(0, HORIZON, W, H - HORIZON)
    c.fill()
    x = 0
    columns = []
    while x < W:
        w = rng.randint(*blocks)
        top = rng.randint(40, 460) if not 700 < x < 1200 else rng.randint(380, 640)  # a gap of sky down the street
        block(c, x, w, top, rng.uniform(0.7, 1.2))
        columns.append((x, w, top))
        x += w
    for _ in range(signs):
        x, w, top = rng.choice(columns)
        sw, sh = rng.randint(22, 42), min(rng.randint(120, 300), HORIZON - top - 40)
        y = rng.randint(top + 20, HORIZON - sh - 20)  # always above the road
        sign(c, x + rng.randint(4, max(5, w - sw - 4)), y, sw, sh, rng.choice(SIGNS))
    rain(c, rng, drops)
    from PIL import Image
    data = bytes(surface.get_data())
    Image.frombuffer("RGB", (W, H), data, "raw", "BGRX", 0, 1).save(OUT / f"{name}.jpg", quality=90)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    scene("a-calle", 8, (120, 260), 9, 700)
    scene("b-esquina", 23, (200, 420), 5, 1400)
    scene("c-tarde", 41, (90, 180), 13, 260)
