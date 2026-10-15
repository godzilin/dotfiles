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

sonoma_hills("a-sonoma-dawn", ("#bcd6f2", "#f6e7da"),
             [("#9fd0b8", "#5fa98e"), ("#6db58f", "#2f7f63"), ("#3f8f72", "#1d5a46"), ("#2a6e57", "#123b2f")], 0.4)
sonoma_hills("b-sonoma-dusk", ("#f2c7b8", "#fbe9d6"),
             [("#f0a58f", "#d97862"), ("#d97a7a", "#a94f61"), ("#a45878", "#6e3557"), ("#6b3a62", "#3c1f3a")], 2.0)
sonoma_hills("c-sonoma-lake", ("#d9ecfb", "#eef6fb"),
             [("#a9cdea", "#7fb0dc"), ("#7aa8d6", "#4c80bd"), ("#4f7fbd", "#2c5797"), ("#2e5793", "#16315e")], 4.1)
ventura("d-ventura-orange", ("#fde3c8", [(0.2, 0.2, 0.9, "#ffd0a1"), (0.85, 0.8, 0.8, "#ffb38a")]),
        [("#ffb15e", "#f26b2a"), ("#ff8a3d", "#d9481f"), ("#ffc178", "#f08a3c")], 0.8)
ventura("e-ventura-blue", ("#dcecff", [(0.1, 0.9, 0.9, "#c4dcff"), (0.9, 0.1, 0.8, "#e6efff")]),
        [("#7fb6ff", "#2f6fe0"), ("#5a96f5", "#1f4fc2"), ("#a9cdff", "#5a8de8")], 2.4)
finish(blobs("#f4ecf7", [(0.15, 0.25, 1.0, "#c9b6f2"), (0.8, 0.3, 0.9, "#f7b7d2"), (0.5, 0.9, 1.0, "#a8d8f0"),
                         (0.95, 0.95, 0.7, "#fbd9b0")], soft=0.42), "f-monterey-pastel")
finish(blobs("#e9f3ee", [(0.1, 0.8, 1.0, "#bfe3cf"), (0.7, 0.2, 1.1, "#d3e9f7"), (0.95, 0.85, 0.8, "#f3e6c4")],
             soft=0.45), "g-big-sur-mist")
