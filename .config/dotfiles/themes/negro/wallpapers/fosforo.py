#!/usr/bin/env python3
"""Generate the "negro" wallpapers into rotation/ (hyprpaper cycles that folder): vector-display pictures drawn as thin
green lines with a glow, like a scope or an arcade monitor. No text, and kept dim so windows stay readable over them.
Needs numpy and Pillow. Run: python3 fosforo.py"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).parent / "rotation"
W, H = 1920, 1200
SS = 2  # supersampling for smooth lines
GREEN = (51, 255, 77)
TAU = 2 * math.pi
rng = np.random.default_rng(7)


def canvas():
    img = Image.new("RGB", (W * SS, H * SS), (0, 0, 0))
    return img, ImageDraw.Draw(img)


def line(d, pts, level=1.0, width=1.5):
    col = tuple(int(c * level) for c in GREEN)
    d.line([(x * SS, y * SS) for x, y in pts], fill=col, width=max(1, round(width * SS)))


def finish(img, name, haze=0.05, dim=1.0, dest=None):
    """Line art + two blurs for the glow + a faint raster haze brighter in the middle, as on a lit tube."""
    img = img.resize((W, H), Image.LANCZOS)
    if dim != 1.0:
        img = img.point(lambda v: int(v * dim))
    a = np.asarray(img, float) / 255
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(3)), float) / 255 * 0.9
    wide = np.asarray(img.filter(ImageFilter.GaussianBlur(14)), float) / 255 * 1.2
    y, x = np.mgrid[0:H, 0:W]
    r2 = ((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2
    base = (np.array([0.2, 1.0, 0.3]) * haze * np.clip(1.1 - r2 * 0.6, 0, 1)[..., None])
    out = np.clip(a + glow + wide + base, 0, 1)
    out = out + rng.normal(0, 0.006, out.shape) * (out.max(axis=2, keepdims=True) > 0.02)  # a little grain
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save((dest or OUT) / name, optimize=True)


def terrain(hor_frac=0.46, sun=True, dim=1.0, name="terreno.png", dest=None):
    """Wireframe landscape under a horizon, rows fading with distance, a sun of horizontal bars behind it."""
    img, d = canvas()
    hor = H * hor_frac
    # sun: arc of bars that get thinner towards the bottom
    cx, cy, R = W / 2, hor - 30, 190
    for i in range(14 if sun else 0):
        y = cy - R + i * (R * 2 / 14) * 0.62 + 6
        if y > hor - 4:
            break
        half = math.sqrt(max(R * R - (y - cy) ** 2, 0))
        line(d, [(cx - half, y), (cx + half, y)], 0.55, 1 + i * 0.18)
    # ridges: rows from far to near; height from summed sines, taller towards the sides
    rows = 34
    for k in range(rows):
        t = (k / rows) ** 2.2                     # 0 far .. 1 near
        y0 = hor + (H - hor) * 1.05 * t + 2
        amp = 8 + 150 * t
        pts = []
        for xi in range(0, W + 8, 8):
            u = (xi - W / 2) / (W / 2)
            ridge = (math.sin(u * 5.1 + k * 0.35) * 0.5 + math.sin(u * 11.3 - k * 0.2) * 0.25) * abs(u) ** 1.3
            pts.append((xi, y0 - amp * max(ridge, 0) * (1 if abs(u) > 0.18 else abs(u) / 0.18)))
        line(d, pts, 0.25 + 0.55 * t ** 0.6, 1.0 + 0.8 * t)
    # perspective lines converging on the vanishing point
    for i in range(-14, 15):
        x_near = W / 2 + i * 150
        line(d, [(W / 2 + i * 6, hor), (x_near, H + 40)], 0.18, 1.0)
    line(d, [(0, hor), (W, hor)], 0.9, 1.6)
    finish(img, name, 0.045, dim, dest)


def radar():
    """Plan position indicator: rings, ticks, a sweep with a fading wake and a few echoes."""
    img, d = canvas()
    cx, cy, R = W / 2, H / 2, 470
    for k in range(1, 5):
        r = R * k / 4
        line(d, [(cx + r * math.cos(a * TAU / 360), cy + r * math.sin(a * TAU / 360)) for a in range(361)], 0.35, 1.2)
    for a in range(0, 360, 5):
        t = a * TAU / 360
        l = 22 if a % 30 == 0 else 10
        line(d, [(cx + (R - l) * math.cos(t), cy + (R - l) * math.sin(t)), (cx + R * math.cos(t), cy + R * math.sin(t))], 0.6, 1.2)
    for a in range(0, 360, 90):
        t = a * TAU / 360
        line(d, [(cx, cy), (cx + R * math.cos(t), cy + R * math.sin(t))], 0.2, 1.0)
    # sweep wake: many lines, each dimmer than the one before
    head = math.radians(-35)
    for i in range(70):
        t = head - i * math.radians(0.9)
        line(d, [(cx, cy), (cx + R * math.cos(t), cy + R * math.sin(t))], 0.5 * (1 - i / 70) ** 2 + (1.0 if i == 0 else 0), 1.4)
    # echoes: short bright dashes just behind the head, as if the beam had passed them
    for ang, rad in [(-48, 0.62), (-61, 0.35), (-83, 0.81), (-120, 0.5), (-160, 0.7), (150, 0.28), (112, 0.9)]:
        t, r = math.radians(ang), R * rad
        line(d, [(cx + r * math.cos(t) - 5, cy + r * math.sin(t)), (cx + r * math.cos(t) + 5, cy + r * math.sin(t))], 0.9, 4)
    finish(img, "radar.png", 0.04)


def scope():
    """Oscilloscope: graticule with fine ticks on the middle axes and two interfering traces."""
    img, d = canvas()
    gx, gy = 120, 100                              # division size
    left, top = W / 2 - gx * 8, H / 2 - gy * 5
    for i in range(0, 17):
        line(d, [(left + i * gx, top), (left + i * gx, top + gy * 10)], 0.28 if i not in (0, 8, 16) else 0.5, 1.0)
    for j in range(0, 11):
        line(d, [(left, top + j * gy), (left + gx * 16, top + j * gy)], 0.28 if j not in (0, 5, 10) else 0.5, 1.0)
    for i in range(0, 16 * 5 + 1):                 # subdivisions on the centre axes
        x = left + i * gx / 5
        line(d, [(x, H / 2 - 5), (x, H / 2 + 5)], 0.6, 1.0)
    for j in range(0, 10 * 5 + 1):
        y = top + j * gy / 5
        line(d, [(W / 2 - 5, y), (W / 2 + 5, y)], 0.6, 1.0)
    xs = np.linspace(left, left + gx * 16, 1600)
    u = (xs - left) / (gx * 16)
    a = H / 2 - gy * 2.1 * np.sin(TAU * 4.0 * u) * np.sin(TAU * 0.5 * u + 0.7)
    b = H / 2 + gy * 1.2 + gy * 0.9 * np.sin(TAU * 9.0 * u + 1.2) * (0.6 + 0.4 * np.sin(TAU * 1.5 * u))
    line(d, list(zip(xs, a)), 1.0, 2.2)
    line(d, list(zip(xs, b)), 0.7, 1.8)
    finish(img, "osciloscopio.png", 0.05)


def lissajous():
    """Lissajous figure on a bare graticule: the picture a scope gives with two sines in a 3:4 ratio."""
    img, d = canvas()
    cx, cy = W / 2, H / 2
    for k in range(-8, 9):
        line(d, [(cx + k * 110, 0), (cx + k * 110, H)], 0.16, 1.0)
    for k in range(-5, 6):
        line(d, [(0, cy + k * 110), (W, cy + k * 110)], 0.16, 1.0)
    t = np.linspace(0, TAU, 5000)
    for n, (ph, lvl) in enumerate([(0.0, 0.35), (0.12, 0.55), (0.24, 1.0)]):
        x = cx + 520 * np.sin(3 * t + ph)
        y = cy + 440 * np.sin(4 * t)
        line(d, list(zip(x, y)), lvl, 1.6 + n * 0.3)
    finish(img, "lissajous.png", 0.045)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for f in (terrain, radar, scope, lissajous):
        f()
    terrain(0.66, False, 0.55, "bloqueo.png", OUT.parent)  # lock screen: land only in the lower third, the panel sits on black
