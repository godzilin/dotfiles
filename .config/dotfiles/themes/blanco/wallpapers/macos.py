#!/usr/bin/env python3
"""Generate the "blanco" wallpapers into rotation/: soft macOS-style abstracts
(Sonoma hills, Ventura ribbons, Monterey/Big Sur colour fields). Run: python3 macos.py"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

W, H = 2560, 1600
OUT = Path(__file__).resolve().with_name("rotation")
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u, v = xx / W, yy / H


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)


def vgrad(top, bottom, t=None):
    t = v if t is None else t
    return hexc(top) * (1 - t[..., None]) + hexc(bottom) * t[..., None]


def blobs(base, spots, soft=0.35):
    """Mesh-gradient look: coloured gaussian spots over a base colour."""
    img = np.broadcast_to(hexc(base), (H, W, 3)).copy()
    for cx, cy, r, col in spots:
        d2 = ((u - cx) * W / H) ** 2 + (v - cy) ** 2
        a = np.exp(-d2 / (2 * (r * soft) ** 2))[..., None]
        img = img * (1 - a) + hexc(col) * a
    return img


def layer(img, edge, top, bottom, shadow=0.18, depth=0.35):
    """Fill below the curve edge(x) (in 0..1 of height) with a gradient, soft shadow on top of the edge."""
    e = edge[None, :]
    mask = np.clip((v - e) * H / 1.5, 0, 1)  # 1.5 px antialias
    sh = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28))
    sh = np.asarray(sh, np.float32)[..., None] / 255
    img = img * (1 - shadow * sh * (1 - mask[..., None]))  # shadow above the edge (the layer casts upward)
    t = np.clip((v - e) / depth, 0, 1)
    fill = vgrad(top, bottom, t)
    return img * (1 - mask[..., None]) + fill * mask[..., None]


def wave(base, amps, phase):
    x = np.linspace(0, 1, W, dtype=np.float32)
    y = np.full(W, base, np.float32)
    for k, (a, f) in enumerate(amps):
        y += a * np.sin(2 * np.pi * f * x + phase + k * 1.7)
    return y


def ribbon(img, center, width, col_a, col_b, phase):
    """Ventura-like folded ribbon: crisp band whose width twists; front and back faces in two tones, soft shadow."""
    x = np.linspace(0, 1, W, dtype=np.float32)
    tw = np.sin(2 * np.pi * 0.9 * x + phase)  # twist: sign = which face shows
    half = width * (0.12 + 0.88 * np.abs(tw)) / 2
    top, bot = (center - half)[None, :], (center + half)[None, :]
    mask = np.clip((v - top) * H / 1.5, 0, 1) * np.clip((bot - v) * H / 1.5, 0, 1)
    sh = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(36))
    sh = np.roll(np.asarray(sh, np.float32), 24, axis=0)[..., None] / 255
    img = img * (1 - 0.22 * sh)
    across = np.clip((v - top) / np.maximum(bot - top, 1e-4), 0, 1)  # 0 at top edge, 1 at bottom
    face = (tw > 0)[None, :, None]
    light = 1.08 - 0.25 * np.abs(across - 0.3)[..., None]  # lit near the upper edge, like a curved surface
    col = np.where(face, hexc(col_a), hexc(col_b)) * light
    m = mask[..., None]
    return img * (1 - m) + col * m


def finish(img, name, grain=2.2):
    img = img + rng.normal(0, grain, img.shape[:2])[..., None]  # a little grain kills banding
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(OUT / f"{name}.jpg", quality=93, subsampling=0)
    print("wrote", name)


def sonoma_hills(name, sky, hills, phase):
    img = vgrad(*sky)
    for i, (top, bottom) in enumerate(hills):
        edge = wave(0.38 + i * 0.13, [(0.05, 0.6), (0.025, 1.3), (0.01, 2.9)], phase + i * 2.1)
        img = layer(img, edge, top, bottom)
    finish(img, name)


def ventura(name, bg, ribbons, phase):
    img = blobs(*bg)
    for i, (a, b) in enumerate(ribbons):
        c = wave(0.25 + i * 0.2, [(0.12, 0.45), (0.04, 1.1)], phase + i * 1.3)
        img = ribbon(img, c, 0.16 + 0.03 * i, a, b, phase + i * 0.9)
    finish(img, name)


OUT.mkdir(exist_ok=True)
for f in OUT.glob("*"):
    f.unlink()

sonoma_hills("a-colinas-alba", ("#bcd6f2", "#f6e7da"),
             [("#9fd0b8", "#5fa98e"), ("#6db58f", "#2f7f63"), ("#3f8f72", "#1d5a46"), ("#2a6e57", "#123b2f")], 0.4)
sonoma_hills("b-colinas-ocaso", ("#f2c7b8", "#fbe9d6"),
             [("#f0a58f", "#d97862"), ("#d97a7a", "#a94f61"), ("#a45878", "#6e3557"), ("#6b3a62", "#3c1f3a")], 2.0)
sonoma_hills("c-colinas-lago", ("#d9ecfb", "#eef6fb"),
             [("#a9cdea", "#7fb0dc"), ("#7aa8d6", "#4c80bd"), ("#4f7fbd", "#2c5797"), ("#2e5793", "#16315e")], 4.1)
ventura("d-cintas-naranja", ("#fde3c8", [(0.2, 0.2, 0.9, "#ffd0a1"), (0.85, 0.8, 0.8, "#ffb38a")]),
        [("#ffb15e", "#f26b2a"), ("#ff8a3d", "#d9481f"), ("#ffc178", "#f08a3c")], 0.8)
ventura("e-cintas-azules", ("#dcecff", [(0.1, 0.9, 0.9, "#c4dcff"), (0.9, 0.1, 0.8, "#e6efff")]),
        [("#7fb6ff", "#2f6fe0"), ("#5a96f5", "#1f4fc2"), ("#a9cdff", "#5a8de8")], 2.4)
finish(blobs("#f4ecf7", [(0.15, 0.25, 1.0, "#c9b6f2"), (0.8, 0.3, 0.9, "#f7b7d2"), (0.5, 0.9, 1.0, "#a8d8f0"),
                         (0.95, 0.95, 0.7, "#fbd9b0")], soft=0.42), "f-pastel")
finish(blobs("#e9f3ee", [(0.1, 0.8, 1.0, "#bfe3cf"), (0.7, 0.2, 1.1, "#d3e9f7"), (0.95, 0.85, 0.8, "#f3e6c4")],
             soft=0.45), "g-bruma")


# ---------------------------------------------------------------------------
# More eras: classic Mac OS, Aqua, the big-cat/photo years, modern macOS, iOS, iPod/iMac colours.
# Stylised re-creations only (no logos); named <year>-<what> so they sort by era.

X = u * W / H  # horizontal coordinate in screen-height units (keeps circles round)
x1 = np.linspace(0, 1, W, dtype=np.float32)


def blur(img, r):
    return np.asarray(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)),
                      np.float32)


def glow(img, a, col):
    """Screen-blend a colour with strength a (H,W) in 0..1."""
    a = np.clip(a, 0, 1)[..., None]
    return 255 - (255 - img) * (1 - a * hexc(col) / 255)


def stars(img, n, seed, top=1.0):
    r = np.random.default_rng(seed)
    s = np.zeros((H, W), np.uint8)
    ys = np.minimum((r.uniform(0, top, n) ** 1.3 * H).astype(int), H - 1)  # denser near the top
    s[ys, r.integers(0, W, n)] = (255 * r.uniform(0.2, 1, n) ** 2).astype(np.uint8)
    a = np.asarray(Image.fromarray(s).filter(ImageFilter.GaussianBlur(0.9)), np.float32) / 255 * 4
    return glow(img, a, "#ffffff")


def noise1d(n, seed):
    pts = np.random.default_rng(seed).uniform(0, 1, n + 1)
    return np.interp(np.linspace(0, n, W), np.arange(n + 1), pts).astype(np.float32)


def ridge(seed, base, amp, octaves=8):
    """Fractal mountain skyline, y in 0..1 of height."""
    r = np.random.default_rng(seed)
    y = np.full(W, base, np.float32)
    for k in range(octaves):
        n = 2 * 2 ** k
        y += amp * 0.55 ** k * np.interp(x1 * n, np.arange(n + 1), r.uniform(-1, 1, n + 1))
    return y


def palette(t, stops):
    pos = [p for p, _ in stops]
    cols = np.array([hexc(c) for _, c in stops])
    return np.stack([np.interp(t, pos, cols[:, i]) for i in range(3)], -1).astype(np.float32)


def solid(col):
    return np.broadcast_to(hexc(col), (H, W, 3)).copy()


# --- classic Mac OS (1984-2001) ---

def pattern(rows, scale, *cols):
    """1-bit/indexed desktop pattern, each pattern pixel drawn as scale x scale."""
    t = np.array([[int(c) for c in r] for r in rows])
    big = np.tile(t, (H // (t.shape[0] * scale) + 1, W // (t.shape[1] * scale) + 1))
    big = np.repeat(np.repeat(big, scale, 0), scale, 1)[:H, :W]
    return np.array([hexc(c) for c in cols])[big]


def imac(name, cols, rib=12):
    """iMac G3 translucent plastic: ribbed, lit through the middle of each colour, glossy top."""
    n = len(cols)
    k = np.minimum((u * n).astype(int), n - 1)
    f = u * n - k
    lit = 0.78 + 0.34 * np.sin(np.pi * f) ** 0.6 - 0.2 * v
    img = np.array([hexc(c) for c in cols])[k] * (lit * (1 + 0.05 * np.sin(2 * np.pi * xx / rib)))[..., None]
    finish(glow(img, 0.5 * np.exp(-((v - 0.1) / 0.07) ** 2) * np.sin(np.pi * f) ** 2, "#ffffff"), name)


finish(pattern(["10", "01"], 8, "#f4f4ef", "#2a2a2c"), "1984-gnu", grain=0)
finish(pattern(["00010000", "00111000", "01111100", "11111110", "01111100", "00111000", "00010000", "00000000"],
               6, "#7474c4", "#9d9de6"), "1991-linux-0.01", grain=0)
finish(pattern(["22222221"] + ["20000001"] * 6 + ["11111111"], 4, "#c6c6c6", "#999999", "#e4e4e4"),
       "1996-tux", grain=0)
img = blobs("#2d5bb8", [(0.15, 0.1, 0.9, "#5f93e6"), (0.9, 0.95, 0.9, "#132e78")], soft=0.45)
for i in range(4):
    img = glow(img, 0.22 * np.exp(-((np.hypot(X - 1.3, v - 1.1) - 0.5 - 0.22 * i) / 0.05) ** 2), "#b3d0ff")
finish(img, "1993-debian")
imac("1998-kde-1.0", ["#0098b8"])
imac("1999-gnome-1.0", ["#2a5fbf", "#e2445f", "#6fc23a", "#6a3f9e", "#f2862b"])
img = vgrad("#f4ede0", "#e8dfcc")
for i, c in enumerate(["#61bb46", "#fdb827", "#f5821f", "#e03a3e", "#963d97", "#009ddc"]):
    img[(v >= 0.36 + i * 0.05) & (v < 0.41 + i * 0.05)] = hexc(c)
finish(img, "1978-bsd")

# --- Aqua (2001-2007) ---

img = blobs("#0b3a8f", [(0.2, 0.2, 1.0, "#2a7fe0"), (0.85, 0.9, 0.9, "#0a2466"), (0.7, 0.3, 0.8, "#3fa0ff")], soft=0.45)
for i in range(5):
    c = wave(0.3 + 0.1 * i, [(0.12, 0.4), (0.03, 1.3)], 0.7 * i)[None, :]
    img = glow(img, 0.18 * np.exp(-((v - c) / (0.015 + 0.02 * i)) ** 2) + 0.5 * np.exp(-((v - c) / 0.002) ** 2),
               "#dff0ff")
finish(img, "2001-linux-2.4")
img = vgrad("#f6f6f6", "#e2e2e2") * np.where((yy // 4) % 2 == 0, 1.0, 0.955)[..., None]
img = glow(img, 0.45 * np.exp(-((X - 1.35) ** 2 + (v - 0.9) ** 2) / 0.12), "#6fa8ff")
finish(img, "1994-linux-1.0", grain=0)


def brushed(win=160, seed=5):
    n = np.random.default_rng(seed).normal(0, 1, (H, W + win)).astype(np.float32)
    c = np.cumsum(n, axis=1)
    return (c[:, win:] - c[:, :-win]) / np.sqrt(win) + np.random.default_rng(seed + 1).normal(0, 0.6, (H, 1))


gray = 150 + 50 * np.exp(-((X - 0.8) ** 2 + (v - 0.35) ** 2) / 0.5) + 8 * brushed()
finish(gray[..., None] * np.array([1.0, 1.01, 1.03], np.float32), "2003-fedora-core-1", grain=0.8)

th = np.radians(-18)
along, across = X * np.cos(th) + v * np.sin(th), -X * np.sin(th) + v * np.cos(th)
img = blobs("#0e3b8c", [(0.2, 0.8, 0.9, "#061a4f"), (0.8, 0.2, 0.9, "#2b6fd6")], soft=0.45)
r = np.random.default_rng(3)
for _ in range(18):
    p0, w, a0, ln, s = r.uniform(across.min(), across.max()), r.uniform(0.002, 0.03), r.uniform(0, 1.6), \
        r.uniform(0.3, 0.9), r.uniform(0.15, 0.5)
    img = glow(img, s * np.exp(-((across - p0) / w) ** 2) * np.exp(-((along - a0) / ln) ** 2), "#9ccaff")
finish(img, "2002-arch-0.1")

rr, ang = np.hypot(X - 1.9, v - 1.3), np.arctan2(v - 1.3, X - 1.9)
img = vgrad("#2a86e8", "#0c3486")
for k in range(9):
    d = rr - 0.55 - 0.12 * k - 0.025 * np.sin(5 * ang + k)
    img = glow(img, 0.35 * np.exp(-(d / (0.01 + 0.006 * k)) ** 2) + 0.12 * np.exp(-(d / 0.08) ** 2), "#bfe6ff")
finish(img, "2005-git")


def aurora(name, sky, curtains, seed):
    img = vgrad(*sky)
    for i, (base, low, high, s) in enumerate(curtains):
        d = v - wave(base, [(0.08, 0.5), (0.03, 1.4), (0.01, 3.1)], seed + i * 1.9)[None, :]
        rays = (0.3 + 0.7 * noise1d(400, seed + i) ** 2) * (0.4 + 0.6 * noise1d(5, seed + 50 + i))
        inten = np.where(d < 0, np.exp(d / 0.12), np.exp(-(d / 0.012) ** 2)) * rays[None, :] * s
        up = np.clip(-d / 0.32, 0, 1)[..., None]
        col = hexc(low) * (1 - up) + hexc(high) * up
        img = 255 - (255 - img) * (1 - inten[..., None] * col / 255)
    finish(stars(blur(img, 1.5), 2500, seed, top=0.8), name)


aurora("2004-ubuntu", ("#05040f", "#1a0f3a"),
       [(0.55, "#ff4fd8", "#5b2bd9", 0.8), (0.62, "#c44dff", "#2b3fd9", 0.6), (0.48, "#ff7ad9", "#7a2bd9", 0.45)], 2)
aurora("2010-systemd", ("#03081a", "#0f2a5a"),
       [(0.58, "#7fd7ff", "#6b4dff", 0.75), (0.5, "#b98cff", "#2b5bd9", 0.55), (0.66, "#9ff0ff", "#3b6bff", 0.4)], 7)

# --- galaxy and photo years (2011-2019), redrawn as flat landscapes ---

img = blobs("#02030a", [(0.3, 0.7, 0.8, "#0b0f2a"), (0.8, 0.2, 0.7, "#140a24")], soft=0.4)
th = np.radians(-32)
gx, gy = X - 0.55 * W / H, v - 0.5
xr, yr = gx * np.cos(th) + gy * np.sin(th), (-gx * np.sin(th) + gy * np.cos(th)) / 0.33
R, phi = np.hypot(xr, yr), np.arctan2(yr, xr)
arm = 0.5 + 0.5 * np.cos(2 * phi - 7 * np.log(R + 0.02))
dust = 1 - 0.55 * np.exp(-((arm - 0.05) / 0.12) ** 2) * np.exp(-R / 0.3)
img = glow(img, np.exp(-R / 0.16) * (0.45 + 0.55 * arm ** 2) * dust * 0.9, "#a9bfff")
img = glow(img, np.exp(-(R / 0.035) ** 2) + 0.6 * np.exp(-R / 0.05), "#fff1d0")
finish(stars(blur(img, 1.2), 4000, 11), "2011-linux-3.0")

img = vgrad("#b9c9d6", "#e8edf0")
foamtex = blur(np.random.default_rng(4).uniform(0, 255, (H, W, 1)).repeat(3, 2), 3)[..., 0] / 255
for i, (a, b) in enumerate([("#3e7a8f", "#16384a"), ("#2c5f75", "#0e2a3a"), ("#1f4b5f", "#0a1e2a")]):
    e = wave(0.45 + 0.13 * i, [(0.04, 0.35), (0.015, 1.2), (0.006, 3)], 1.1 * i)
    if i == 0:
        e = e - 0.2 * np.exp(-((x1 - 0.35) / 0.12) ** 2)  # the big set wave
    img = layer(img, e, a, b, shadow=0.2, depth=0.3)
    dd = v - e[None, :]
    img = glow(img, (dd > 0) * np.exp(-np.clip(dd, 0, None) / 0.018) * np.clip(foamtex * 3 - 1, 0, 1), "#f4f8fa")
finish(img, "2012-raspberry-pi")


def scene(sky, layers, n_stars=0, seed=0, shadow=0.1, depth=0.4):
    img = vgrad(*sky)
    if n_stars:
        img = stars(img, n_stars, seed, top=0.6)
    for e, a, b in layers:
        img = layer(img, e, a, b, shadow=shadow, depth=depth)
    return img


dx = x1 - 0.63
dome = np.where(dx < 0, 0.5 + 0.5 * np.cos(np.pi * np.clip(dx / 0.16, -1, 0)), np.clip(1 - dx / 0.02, 0, 1) ** 0.5)
finish(scene(("#2c3e74", "#f2a07b"), [(ridge(11, 0.52, 0.08), "#8f86b8", "#a99bc0"),
                                       (ridge(12, 0.62, 0.05) - 0.24 * dome, "#564a7b", "#564a7b"),
                                       (ridge(13, 0.8, 0.05), "#2c2547", "#17132a")]), "2015-linux-4.0")
wall = 0.78 - 0.55 * np.clip((x1 - 0.3) / 0.25, 0, 1) ** 0.7 + ridge(21, 0, 0.02)
finish(scene(("#0b1430", "#4b4a86"), [(ridge(20, 0.6, 0.05), "#3b3b6e", "#2c2c58"), (wall, "#6c6aa0", "#2a2850"),
                                       (ridge(22, 0.9, 0.025, octaves=10), "#120f22", "#07060f")],
             n_stars=1500, seed=3, depth=0.7), "2016-flatpak")
mist = [("#a9bad3", "#b8c6db"), ("#8a9dbd", "#9aabc6"), ("#6b80a5", "#7a8eb1"), ("#4c6189", "#596e95"),
        ("#2f3e5e", "#26324d")]
finish(scene(("#d8e4ef", "#f4efe6"), [(ridge(30 + i, 0.42 + 0.1 * i, 0.07), a, b) for i, (a, b) in enumerate(mist)],
             shadow=0.05), "2008-kde-4")

h = 0.62
img = scene(("#7fb3dd", "#e3eef3"), [(ridge(41, 0.36, 0.12), "#eef2f6", "#93a6bd"),
                                      (np.minimum(ridge(42, 0.52, 0.05), h - 0.005), "#6b7f62", "#3b4a3a")])
src = np.clip(2 * int(h * H) - np.arange(int(h * H), H), 0, H - 1)
img[int(h * H):] = blur(img[src] * np.array([0.72, 0.84, 0.95], np.float32), 3)[: H - int(h * H)]
img[int(h * H):int(h * H) + 3] *= 0.6
finish(img, "2017-arch-x86-64")


def dunes(name, sky, sands, n_stars=0):
    img = vgrad(*sky)
    if n_stars:
        img = stars(img, n_stars, 9, top=0.5)
    for i, (a, b) in enumerate(sands):
        e = 0.48 + 0.12 * i + 0.07 * np.abs(np.sin(np.pi * (1.3 + 0.4 * i) * x1 + 1.7 * i)) - 0.07
        e = e + 0.015 * np.sin(2 * np.pi * 2.3 * x1 + i)
        img = layer(img, e, a, b, shadow=0.3, depth=0.3)
        dd = v - e[None, :]
        img = glow(img, 0.25 * (dd > 0) * np.exp(-np.clip(dd, 0, None) / 0.004), a)  # sunlit crest
    finish(img, name)


dunes("2019-linux-5.0", ("#a8c4dc", "#f3dcc0"),
      [("#f0c58e", "#c98a52"), ("#e6ad74", "#b06e3e"), ("#d89a62", "#93552c")])
dunes("2007-kvm", ("#0c1633", "#3a4f7a"),
      [("#4d5f8a", "#2b3658"), ("#3d4c75", "#212a47"), ("#2f3b60", "#161d33")], n_stars=1800)

h = 0.62
img = np.where((v < h)[..., None], vgrad("#5f84b8", "#f0c7a6", np.clip(v / h, 0, 1)),
               vgrad("#6f8fb5", "#1d3556", np.clip((v - h) / (1 - h), 0, 1)))
img = glow(img, (v > h) * np.exp(-((X - 1.0) / 0.08) ** 2) * np.exp(-(v - h) / 0.2)
           * (0.4 + 0.6 * noise1d(300, 5)[None, :]), "#ffd9b0")
bump = np.clip(np.sin(np.pi * (x1 - 0.12) / 0.66), 0, 1) ** 0.7 * (x1 > 0.12) * (x1 < 0.78)
e = h - 0.17 * bump * (1 + 0.25 * ridge(51, 0, 1, octaves=6))
m = (np.clip((v - e[None, :]) * H / 1.5, 0, 1) * (v < h) * (bump > 0)[None, :])[..., None]
img = img * (1 - m) + vgrad("#4a5d82", "#26344f") * m
finish(img, "2020-pipewire")

# --- modern macOS (2020-2025) ---


def flow(name, sky, layers, tilt=0.0, amp=0.09, phase=0.0):
    img = vgrad(*sky)
    for i, (a, b) in enumerate(layers):
        e = wave(0.25 + 0.17 * i, [(amp, 0.45), (amp * 0.4, 1.1)], phase + i * 1.4) + tilt * (x1 - 0.5)
        img = layer(img, e, a, b, shadow=0.25, depth=0.45)
    finish(img, name)


flow("2022-steam-deck", ("#ffcf9a", "#ff9f7a"),
     [("#ff8a6a", "#e8557a"), ("#d94f8f", "#9a3da6"), ("#8a3fbf", "#4b39b5"), ("#3c3fc0", "#1b1f6e")])
flow("2022-hyprland", ("#1c1033", "#2e1748"),
     [("#5b2a7a", "#3a1f66"), ("#3f2b8c", "#251a5e"), ("#25307a", "#141c4a"), ("#121a3f", "#070b1f")], phase=1.0)
flow("2022-rust-en-linux", ("#a7d8ff", "#c9b8ff"),
     [("#6fb6ff", "#4a7ff0"), ("#7f6ff5", "#5a3fd6"), ("#c86fe6", "#8a3fc4"), ("#4a2fa8", "#1f155e")],
     tilt=-0.35, amp=0.07, phase=2.2)
ventura("2024-preempt-rt", ("#150f12", [(0.2, 0.8, 0.9, "#2a1508"), (0.9, 0.2, 0.8, "#1f0f1a")]),
        [("#ff9b45", "#c4421a"), ("#ff7a2d", "#a8320f"), ("#ffb35e", "#d9661f")], 1.6)

R, ang = np.hypot(X - 0.8, v - 0.62), np.arctan2(v - 0.62, X - 0.8)
t = 0.5 + 0.5 * np.cos(2 * ang + 7 * R)
c = np.exp(-(R / 0.12) ** 2)  # glowing core hides the swirl's singular centre
t = t * (1 - c) + c
img = palette(t, [(0, "#120a3a"), (0.35, "#3b1f8f"), (0.6, "#c2338f"), (0.8, "#ff5a5a"), (1, "#ffb38a")])
finish(blur(img * (0.55 + 0.45 * np.exp(-R / 0.9))[..., None], 2), "2024-valve-y-arch")


def rbox(cx, cy, hw, hh, rad):
    px, py = np.abs(X - cx) - hw + rad, np.abs(v - cy) - hh + rad
    return np.hypot(np.maximum(px, 0), np.maximum(py, 0)) + np.minimum(np.maximum(px, py), 0) - rad


def glass(img, d, k=0.05):
    """Liquid Glass lens: refract the background near the edge, lift it, add a lit rim and a soft shadow."""
    gy, gx = np.gradient(d)
    nrm = np.hypot(gx, gy) + 1e-9
    gx, gy = gx / nrm, gy / nrm
    img = img * (1 - 0.2 * (d > 0) * np.exp(-np.clip(d - 0.01, 0, None) / 0.03))[..., None]
    t = np.clip(-d / 0.06, 0, 1)
    shift = (1 - t) ** 2 * k * H
    sx = np.clip(xx + gx * shift, 0, W - 1).astype(int)
    sy = np.clip(yy + gy * shift, 0, H - 1).astype(int)
    inside = np.clip(-d * H / 1.5, 0, 1)[..., None]
    img = img * (1 - inside) + (img[sy, sx] * 1.04 + 10) * inside
    rim = np.exp(-(d / 0.003) ** 2) * (0.35 + 0.65 * np.clip(-(gx + gy) / 1.4, 0, 1))
    return glow(img, rim * 0.8, "#ffffff")


img = blobs("#1257c9", [(0.15, 0.2, 0.9, "#2fc6f2"), (0.85, 0.75, 1.0, "#6b4ff0"), (0.55, 0.15, 0.6, "#37e0c4"),
                        (0.4, 0.9, 0.8, "#1b2f9e")], soft=0.42)
img = layer(img, wave(0.55, [(0.08, 0.5), (0.03, 1.2)], 0.3), "#3ab0ff", "#2a3fd0", shadow=0.15, depth=0.5)
for cx, cy, hw, hh, rad in [(0.45, 0.32, 0.22, 0.22, 0.22), (1.05, 0.6, 0.34, 0.12, 0.12),
                            (0.7, 0.8, 0.14, 0.14, 0.06)]:
    img = glass(img, rbox(cx, cy, hw, hh, rad))
finish(img, "2025-linux-6.14")

# --- iOS ---

img = blobs("#f3d9e6", [(0.1, 0.1, 1, "#a7c7f2"), (0.9, 0.2, 0.9, "#f6c1a8"), (0.5, 0.9, 1, "#c9a9e8"),
                        (0.2, 0.8, 0.7, "#9fe0d6")], soft=0.5)
r = np.random.default_rng(8)
for _ in range(30):
    cx, cy, rad = r.uniform(0, W / H), r.uniform(0, 1), r.uniform(0.02, 0.12)
    img = glow(img, np.clip((rad - np.hypot(X - cx, v - cy)) / 0.006, 0, 1) * r.uniform(0.08, 0.25), "#ffffff")
finish(blur(img, 3), "2013-steam-linux")


def shapes(name, bg, circles):
    img = vgrad(*bg)
    for cx, cy, rad, col in circles:
        d = np.hypot(X - cx * W / H, v - cy)
        ds = np.hypot(X - cx * W / H, v - cy - 0.012)
        img = img * (1 - 0.25 * (ds > rad) * np.exp(-np.clip(ds - rad, 0, None) / 0.03))[..., None]
        m = np.clip((rad - d) * H / 1.5, 0, 1)[..., None]
        shade = (1.08 - 0.22 * np.clip((v - cy + rad) / (2 * rad), 0, 1))[..., None]
        img = img * (1 - m) + hexc(col) * shade * m
    finish(img, name)


shapes("2021-linux-30-anos", ("#f2ece4", "#e6ddd2"),
       [(0.2, 0.85, 0.45, "#e8a07a"), (0.75, 0.15, 0.38, "#7fb3c4"), (0.95, 0.8, 0.3, "#2f4a6b"),
        (0.5, 0.45, 0.18, "#f2c46b"), (0.1, 0.1, 0.22, "#c87a8a")])
shapes("2021-cachyos", ("#141821", "#0b0d12"),
       [(0.2, 0.85, 0.45, "#9a4f3a"), (0.75, 0.15, 0.38, "#2f6b80"), (0.95, 0.8, 0.3, "#1c2c48"),
        (0.5, 0.45, 0.18, "#b8892f"), (0.1, 0.1, 0.22, "#7a3a52")])
finish(blobs("#07070f", [(0.2, 0.3, 0.9, "#3a1f9e"), (0.8, 0.2, 0.8, "#c2338f"), (0.6, 0.85, 0.9, "#ff7a3d"),
                         (0.1, 0.9, 0.6, "#1f6fd1")], soft=0.38), "2024-plasma-6")

img = vgrad("#040406", "#0b0b10")
for k, col in enumerate(["#ff3b30", "#ff9500", "#ffcc00", "#34c759", "#30b0c7", "#007aff", "#5856d6", "#af52de"]):
    c = wave(0.5 + (k - 3.5) * 0.025, [(0.16, 0.45), (0.05, 1.15)], 0.6 + k * 0.12)[None, :]
    img = img + hexc(col) * (0.9 * np.exp(-((v - c) / 0.0025) ** 2) + 0.25 * np.exp(-((v - c) / 0.03) ** 2))[..., None]
finish(img, "2018-proton")

# --- iPod and iMac colours ---

cols = ["#c9c9cf", "#2b2b2e", "#8b5bd6", "#2f8fe0", "#4dbb4d", "#f2d33a", "#f39a2b", "#f06aa6", "#e0303a"]
k = np.minimum((u * len(cols)).astype(int), len(cols) - 1)
f = u * len(cols) - k
sheen = (0.85 + 0.25 * np.exp(-((v - 0.3) / 0.35) ** 2)) * (1 - 0.25 * np.exp(-f / 0.01) - 0.25 * np.exp(-(1 - f) / 0.01))
finish(np.array([hexc(c) for c in cols])[k] * sheen[..., None] + 4 * brushed(seed=8)[..., None], "2008-android")

th = np.radians(25)
s = X * np.cos(th) + v * np.sin(th)
s = (s - s.min()) / (s.max() - s.min()) * 7
k = np.minimum(s.astype(int), 6)
f = (s - k)[..., None]
pairs = [("#d7ecd6", "#7bbf8a"), ("#fbe9b0", "#efc551"), ("#fdd5b8", "#f39a5f"), ("#f8c9cb", "#e7656d"),
         ("#e2d2f2", "#a786d6"), ("#cfe3f6", "#5d9be0"), ("#eceef1", "#b9bfc8")]
light, dark = np.array([hexc(a) for a, _ in pairs]), np.array([hexc(b) for _, b in pairs])
finish(blur(light[k] * (1 - f) + dark[k] * f, 1.5), "2022-linux-6.0")
