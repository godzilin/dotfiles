#!/usr/bin/env python3
"""Generate the NeXTSTEP wallpapers into rotation/ (hyprpaper cycles that folder). Run: python3 next.py
Everything is drawn in grey and then reduced to the four greys of the NeXT 2-bit display with a Bayer ordered
dither, the way a MegaPixel monitor showed shaded pictures."""
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 1920, 1200
LEVELS = np.array([0, 85, 170, 255], dtype=np.uint8)  # black, dark grey, light grey, white
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.5
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)


def dither(v):
    """v: float image 0..1 -> uint8 image in the four greys (ordered dither, 2 px cells so it reads on HiDPI)."""
    t = np.tile(np.kron(BAYER, np.ones((2, 2))), (H // 8 + 1, W // 8 + 1))[:H, :W]
    return LEVELS[np.clip(np.floor(v * 3 + 0.5 + t), 0, 3).astype(int)]


def workspace():
    """The plain dark grey Workspace with a very soft light from the top-left."""
    return dither(1 / 3 + 0.12 * (1 - np.hypot(X / W, Y / H) / 1.4))


def cube():
    """A big matte black cube standing on the dark grey floor, lit from the top-left, with its shadow."""
    v = np.full((H, W), 1 / 3, np.float32)
    L = 420.0
    base = np.array([W * 0.5, H * 0.80])          # front-bottom corner
    left = np.array([-0.87 * L, -0.5 * L])        # towards the bottom-left corner
    right = np.array([0.87 * L, -0.5 * L])        # towards the bottom-right corner
    up = np.array([0.0, -L])

    def face(o, a, b):
        """Mask and (u, w) coordinates of the parallelogram o + u*a + w*b, u and w in [0, 1]."""
        inv = np.linalg.inv(np.array([[a[0], b[0]], [a[1], b[1]]]))
        dx, dy = X - o[0], Y - o[1]
        u, w = inv[0, 0] * dx + inv[0, 1] * dy, inv[1, 0] * dx + inv[1, 1] * dy
        return (u >= 0) & (u <= 1) & (w >= 0) & (w <= 1), u, w

    m, _, _ = face(base, right, np.array([0.9 * L, 0.18 * L]))  # shadow thrown to the bottom-right
    v[m] = 0.08
    m, u, w = face(base, left, up)
    v[m] = 0.20 + 0.10 * w[m]          # lit side, a little lighter towards the top
    m, u, w = face(base, right, up)
    v[m] = 0.04 + 0.05 * w[m]          # the side away from the light is almost black
    m, u, w = face(base + up, left, right)
    v[m] = 0.42 + 0.18 * (1 - w[m])    # the top catches the light
    return dither(v)


def spheres():
    """Three shaded spheres on a checkered floor, like the rendering demos that shipped with the system."""
    v = 0.30 + 0.25 * (((X // 120 + np.floor((Y - 700) / 60)) % 2) * (Y > 760))
    v = np.where(Y > 760, v, 0.18 + 0.2 * Y / 760)
    light = np.array([-0.5, -0.7, 0.5]); light /= np.linalg.norm(light)
    for sx, sy, r in [(620, 640, 230), (1160, 700, 170), (1480, 600, 120)]:
        dx, dy = (X - sx) / r, (Y - sy) / r
        d2 = dx * dx + dy * dy
        m = d2 <= 1
        dz = np.sqrt(np.clip(1 - d2, 0, 1))
        lam = np.clip(dx * light[0] + dy * light[1] + dz * light[2], 0, 1)
        spec = lam ** 40
        sh = (X - sx - 0.5 * r) ** 2 / (1.2 * r) ** 2 + (Y - sy - 0.95 * r) ** 2 / (0.25 * r) ** 2 < 1  # floor shadow
        v = np.where(sh & ~m, v * 0.4, v)
        v = np.where(m, 0.08 + 0.75 * lam + 0.4 * spec, v)
    return dither(np.clip(v, 0, 1))


def mandel():
    """The Mandelbrot set, a classic of every 1990 workstation demo, in four greys."""
    x0, y0, scale = -0.745, 0.11, 0.009
    c = (x0 + (X - W / 2) * scale / H * 2) + 1j * (y0 + (Y - H / 2) * scale / H * 2)
    z = np.zeros_like(c)
    n = np.zeros(c.shape, np.float32)
    for i in range(160):
        live = np.abs(z) <= 2
        z[live] = z[live] ** 2 + c[live]
        n[live] += 1
    v = np.where(n >= 160, 0, (n % 24) / 24)
    return dither(0.15 + 0.7 * v)


def gradient():
    """A pure dither study: a diagonal ramp from white to black across the screen."""
    return dither(1 - (X / W * 0.6 + Y / H * 0.4))


out = Path(__file__).with_name("rotation")
out.mkdir(exist_ok=True)
for name, fn in [("a-workspace", workspace), ("b-cube", cube), ("c-spheres", spheres), ("d-mandelbrot", mandel),
                 ("e-dither", gradient)]:
    path = out / f"{name}.png"
    Image.fromarray(fn(), "L").save(path, optimize=True)
    print(path)
