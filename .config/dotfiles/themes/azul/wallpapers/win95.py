#!/usr/bin/env python3
"""Generate the "azul" wallpapers into rotation/: the Windows 95/98 desktop classics, drawn from scratch
(teal desktop, setup clouds, setup gradient, 8x8 desktop patterns, a sandstone tile). Run: python3 win95.py"""
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 1920, 1200
OUT = Path(__file__).resolve().with_name("rotation")
rng = np.random.default_rng(95)


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)


def save(img, name):
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(OUT / f"{name}.png", optimize=True)
    print("wrote", name)


def noise(octaves, base=6, persistence=0.55):
    """Fractal value noise in 0..1 (bilinear-upsampled random grids)."""
    acc = np.zeros((H, W), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        gw, gh = base * 2 ** o + 1, int(base * 2 ** o * H / W) + 2
        grid = Image.fromarray((rng.random((gh, gw)) * 255).astype(np.uint8))
        acc += amp * np.asarray(grid.resize((W, H), Image.BICUBIC), np.float32) / 255
        total += amp
        amp *= persistence
    return acc / total


def bayer_quantize(img, levels):
    """Ordered dithering to a few levels per channel, like a 256-colour VGA mode."""
    b = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - 0.5
    t = np.tile(b, (H // 4 + 1, W // 4 + 1))[:H, :W][..., None]
    step = 255 / (levels - 1)
    return np.round(img / step + t) * step


def pattern(rows, fg, bg, scale=2):
    """Windows 3.1/95 desktop pattern: an 8x8 bitmap tiled over the desktop colour."""
    bits = np.array([[int(c) for c in f"{r:08b}"] for r in rows], np.float32)
    tile = np.kron(bits, np.ones((scale, scale), np.float32))
    m = np.tile(tile, (H // tile.shape[0] + 1, W // tile.shape[1] + 1))[:H, :W][..., None]
    return hexc(fg) * m + hexc(bg) * (1 - m)


OUT.mkdir(exist_ok=True)
for f in OUT.glob("*"):
    f.unlink()

# The default Windows 95 desktop
save(np.broadcast_to(hexc("#008080"), (H, W, 3)), "a-teal")

# Setup / boot clouds: soft white clouds over a blue sky
v = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
sky = hexc("#3a6fd8") * (1 - v) + hexc("#8fb7f0") * v
n = noise(7, base=12, persistence=0.6)
clouds = np.clip((n - 0.5) * 3.2, 0, 1) ** 1.2
shade = np.clip(1 - (noise(5, base=9) - 0.5) * 0.6, 0.7, 1.1)
cloud_col = hexc("#ffffff")[None, None, :] * shade[..., None] * 0.97
img = sky * (1 - clouds[..., None]) + cloud_col * clouds[..., None]
save(bayer_quantize(img, 32), "b-clouds")

# Setup screen: blue fading to black, dithered like 1995 hardware
img = hexc("#0000ff") * (1 - v) + hexc("#000000") * v
save(bayer_quantize(np.broadcast_to(img, (H, W, 3)).copy(), 8), "c-setup")

# Desktop patterns over teal (Weave, Boxes, Diamonds) and Pinstripe on grey
save(pattern([0x88, 0x54, 0x22, 0x45, 0x88, 0x15, 0x22, 0x51], "#000000", "#008080"), "d-weave")
save(pattern([0xFF, 0x81, 0xBD, 0xA5, 0xA5, 0xBD, 0x81, 0xFF], "#004040", "#008080"), "e-boxes")
save(pattern([0x10, 0x28, 0x44, 0x82, 0x44, 0x28, 0x10, 0x00], "#000080", "#008080"), "f-diamonds")
save(pattern([0x01] * 8, "#808080", "#c0c0c0", scale=3), "g-pinstripe")

# Sandstone ("Arenisca") tile: warm speckled noise, tiled 128 px like the original
tile_h = tile_w = 128
fine = rng.random((tile_h, tile_w)).astype(np.float32)
blot = np.asarray(Image.fromarray((rng.random((8, 8)) * 255).astype(np.uint8)).resize((tile_w, tile_h), Image.BICUBIC),
                  np.float32) / 255
t = 0.55 * fine + 0.45 * blot
tile = hexc("#a08868") * (1 - t[..., None]) + hexc("#d8c8a8") * t[..., None]
img = np.tile(tile, (H // tile_h + 1, W // tile_w + 1, 1))[:H, :W]
save(img, "h-sandstone")
