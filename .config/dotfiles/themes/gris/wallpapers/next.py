#!/usr/bin/env python3
"""Generate the NeXTSTEP wallpapers into rotation/ (hyprpaper cycles that folder). Run: python3 next.py
Everything is drawn in grey and then reduced to the four greys of the NeXT 2-bit display with a Bayer ordered
dither, the way a MegaPixel monitor showed shaded pictures."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1200
LEVELS = np.array([0, 85, 170, 255], dtype=np.uint8)  # black, dark grey, light grey, white
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.5
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
FONT_BIG = ImageFont.truetype("/usr/share/fonts/gsfonts/NimbusSans-Bold.otf", 64)  # gsfonts, as the theme
FONT_MONO = ImageFont.truetype("/usr/share/fonts/gsfonts/NimbusMonoPS-Regular.otf", 30)


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


def lines_on(img):
    """Draw on an already dithered image with the four exact greys (lines stay crisp, not dithered)."""
    im = Image.fromarray(img, "L")
    return im, ImageDraw.Draw(im)


def plot():
    """A Mathematica surface plot (NeXT shipped it in the box): sin(r)/r as a light grey mesh with hidden lines."""
    im, d = lines_on(dither(0.28 + 0.06 * Y / H))
    n, span = 44, 14.0
    def P(i, j):
        x, y = (i / n - 0.5) * span, (j / n - 0.5) * span
        r = np.hypot(x, y) + 1e-6
        z = np.sin(r) / r
        return W / 2 + (x - y) * 62, H * 0.56 + (x + y) * 30 - z * 330
    # painter's order, back to front: each quad filled then outlined, so nearer quads hide the farther ones
    for k in range(2 * n - 1):
        for i in range(n):
            j = k - i
            if 0 <= j < n:
                q = [P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)]
                d.polygon(q, fill=85, outline=170)
    d.text((80, H - 90), "Plot3D[Sin[r]/r, {x, -7, 7}, {y, -7, 7}]", fill=170, font=FONT_MONO)
    return np.array(im)


def postscript():
    """The Display PostScript demo: a word set again and again round a point, each copy turned and a step lighter."""
    im = Image.new("L", (W, H), 85)
    for i in range(24):
        t = Image.new("L", (W, H), 0)
        ImageDraw.Draw(t).text((W / 2 + 150, H / 2), "Display PostScript", fill=255, font=FONT_BIG, anchor="lm")
        t = t.rotate(i * 15, center=(W / 2, H / 2), resample=Image.BICUBIC)
        grey = [255, 170, 0][i % 3]
        im.paste(grey, mask=t.point(lambda a: 255 if a > 110 else 0))
    return np.array(im)


def torus():
    """A shaded torus floating over the Workspace, ray-cast and lit from the top-left."""
    R, r = 330.0, 140.0
    tilt = 0.9  # rotation round the x axis
    v = np.full((H, W), 0.30 + 0.05 * Y / H, np.float32)
    px, py = (X - W / 2), (Y - H / 2)
    light = np.array([-0.5, -0.6, 0.62]); light /= np.linalg.norm(light)
    # march along z for every pixel (orthographic view)
    ct, st = np.cos(tilt), np.sin(tilt)
    z = np.full(X.shape, -600.0, np.float32)
    hit = np.zeros(X.shape, bool)
    for _ in range(90):
        # point in torus space
        x, y, zz = px, py * ct - z * st, py * st + z * ct
        q = np.hypot(x, zz) - R
        dist = np.hypot(q, y) - r
        hit |= dist < 0.5
        z = np.where(hit, z, z + np.maximum(dist, 1.0))
    x, y, zz = px, py * ct - z * st, py * st + z * ct
    q = np.hypot(x, zz) + 1e-6
    nx, ny, nz = x * (1 - R / q), y, zz * (1 - R / q)
    # back to view space
    vy, vz = ny * ct + nz * st, -ny * st + nz * ct
    norm = np.sqrt(nx * nx + vy * vy + vz * vz) + 1e-6
    lam = np.clip((nx * light[0] + vy * light[1] - vz * light[2]) / norm, 0, 1)
    v = np.where(hit, 0.06 + 0.8 * lam + 0.35 * lam ** 30, v)
    return dither(np.clip(v, 0, 1))


def julia():
    """A Julia set: the Mandelbrot's sibling, the other demo every workstation ran."""
    c = -0.8 + 0.156j
    z = (X - W / 2) / H * 2.6 + 1j * (Y - H / 2) / H * 2.6
    n = np.zeros(z.shape, np.float32)
    for i in range(120):
        live = np.abs(z) <= 2
        z[live] = z[live] ** 2 + c
        n[live] += 1
    v = np.where(n >= 120, 1, (n % 18) / 18 * 0.75)
    return dither(0.1 + 0.85 * v)


def cubes():
    """A city of grey cubes in isometric view, each block a different height, lit like the big cube."""
    im, d = lines_on(dither(1 / 3 + 0.08 * (1 - Y / H)))
    rng = np.random.default_rng(7)
    s = 46  # half width of a block
    heights = rng.integers(0, 6, (12, 12))
    for gy in range(12):
        for gx in range(12):
            h = heights[gy, gx]
            if h == 0:
                continue
            cx, cy = W / 2 + (gx - gy) * s, 330 + (gx + gy) * s / 2
            top = cy - h * 28
            d.polygon([(cx, top - s / 2), (cx + s, top), (cx, top + s / 2), (cx - s, top)], fill=255, outline=0)
            d.polygon([(cx - s, top), (cx, top + s / 2), (cx, cy + s / 2), (cx - s, cy)], fill=170, outline=0)
            d.polygon([(cx + s, top), (cx, top + s / 2), (cx, cy + s / 2), (cx + s, cy)], fill=0, outline=0)
    return np.array(im)


def lorenz():
    """The Lorenz attractor drawn in light grey on black, as a long single stroke."""
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    x, y, z = 0.1, 0.0, 0.0
    pts = []
    for i in range(60000):
        dx, dy, dz = 10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z
        x, y, z = x + dx * 0.004, y + dy * 0.004, z + dz * 0.004
        pts.append((W / 2 + x * 26, H - 120 - z * 19))
    d.line(pts[:30000], fill=85, width=2)
    d.line(pts[30000:], fill=170, width=2)
    d.line(pts[-4000:], fill=255, width=2)
    return np.array(im)


def moire():
    """Two sets of rings slightly apart: the moiré a 2-bit screen makes with nothing but black and white."""
    a = np.hypot(X - W * 0.42, Y - H * 0.5)
    b = np.hypot(X - W * 0.58, Y - H * 0.5)
    v = ((a // 9) % 2) * 0.5 + ((b // 9) % 2) * 0.5
    return LEVELS[np.clip(np.floor(v * 3 + 0.5), 0, 3).astype(int)]


def contours():
    """A topographic map: contour lines over smooth hills, every fifth line darker."""
    rng = np.random.default_rng(3)
    hgt = np.zeros((H, W), np.float32)
    for _ in range(9):
        cx, cy, sx, a = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(160, 420), rng.uniform(-1, 1)
        hgt += a * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2 * sx * sx))
    level = hgt * 14
    frac = np.abs(level - np.round(level))
    major = (np.round(level) % 5) == 0
    img = dither(0.7 + 0.25 * (hgt - hgt.min()) / (np.ptp(hgt) + 1e-6))
    img = np.where(frac < 0.06, np.where(major, 0, 85), img).astype(np.uint8)
    return img


def galaxy():
    """A spiral galaxy: two dithered arms of light and a scatter of white stars."""
    rng = np.random.default_rng(11)
    dx, dy = (X - W / 2) / 1.0, (Y - H / 2) / 0.55
    r = np.hypot(dx, dy) + 1e-3
    th = np.arctan2(dy, dx)
    arms = np.cos(2 * (th - np.log(r) * 1.6)) * 0.5 + 0.5
    v = np.exp(-r / 650) * (0.3 + 0.7 * arms ** 2) + 0.9 * np.exp(-r / 110)
    img = dither(np.clip(v * 0.9, 0, 1))
    sx, sy = rng.integers(0, W, 900), rng.integers(0, H, 900)
    img[sy, sx] = 255
    return img


def lissajous():
    """An oscilloscope on the bench: a Lissajous figure in white over a grey graticule."""
    im, d = lines_on(dither(0.08 + 0.1 * np.exp(-((X - W / 2) ** 2 + (Y - H / 2) ** 2) / (2 * 700.0 ** 2))))
    for gx in range(0, W + 1, 120):
        d.line([(gx, 0), (gx, H)], fill=85)
    for gy in range(0, H + 1, 120):
        d.line([(0, gy), (W, gy)], fill=85)
    t = np.linspace(0, 2 * np.pi, 4000)
    xs, ys = W / 2 + 620 * np.sin(3 * t + 0.6), H / 2 + 420 * np.sin(4 * t)
    d.line(list(zip(xs, ys)), fill=170, width=7)
    d.line(list(zip(xs, ys)), fill=255, width=3)
    return np.array(im)


out = Path(__file__).with_name("rotation")
out.mkdir(exist_ok=True)
for name, fn in [("a-workspace", workspace), ("b-cube", cube), ("c-spheres", spheres), ("d-mandelbrot", mandel),
                 ("e-dither", gradient),
                 ("f-plot3d", plot), ("g-postscript", postscript), ("h-torus", torus), ("i-julia", julia),
                 ("j-cubes", cubes), ("k-lorenz", lorenz), ("l-moire", moire), ("m-contours", contours),
                 ("n-galaxy", galaxy), ("o-lissajous", lissajous)]:
    path = out / f"{name}.png"
    Image.fromarray(fn(), "L").save(path, optimize=True)
    print(path)
