#!/usr/bin/env python3
"""Generate the "azul" wallpapers into rotation/: the Windows 95/98 desktop classics, drawn from scratch
(teal desktop, setup clouds, setup gradient, 8x8 desktop patterns, tiles like Red Blocks or Straw Mat,
and the screensavers: 3D Pipes, Starfield, Mystify, Plus! Space). Run: python3 win95.py"""
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

# ---- More classics: Windows 95/98 tiled wallpapers and Plus! / screensaver scenes ----
from PIL import ImageDraw  # noqa: E402
import math  # noqa: E402


def tiled(tile):
    th, tw = tile.shape[:2]
    return np.tile(tile, (H // th + 1, W // tw + 1, 1))[:H, :W]


def bevel_tile(w, h, face, light, dark, edge=3):
    """A raised block: light top/left, dark bottom/right, like every Win95 button."""
    t = np.broadcast_to(hexc(face), (h, w, 3)).copy()
    t[:edge, :] = hexc(light)
    t[:, :edge] = hexc(light)
    t[-edge:, :] = hexc(dark)
    t[:, -edge:] = hexc(dark)
    return t


# Twill: diagonal weave, black on grey
save(pattern([0x0F, 0x87, 0xC3, 0xE1, 0xF0, 0x78, 0x3C, 0x1E][::-1], "#000000", "#c0c0c0", scale=3), "i-twill")

# Red Blocks: staggered bevelled bricks
brick = bevel_tile(96, 32, "#a01818", "#e05050", "#500808")
row2 = np.roll(brick, 48, axis=1)
save(tiled(np.concatenate([brick, row2])), "j-redblocks")

# Bubbles: shaded spheres over deep blue
img = Image.fromarray(np.broadcast_to(hexc("#000060"), (H, W, 3)).astype(np.uint8))
d = ImageDraw.Draw(img)
for _ in range(90):
    x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(12, 70)
    for k in range(int(r), 0, -2):  # light from the top left
        t = k / r
        c = (hexc("#2060ff") * t + hexc("#c0e0ff") * (1 - t)).astype(int)
        off = (r - k) * 0.35
        d.ellipse([x - k - off, y - k - off, x + k - off, y + k - off], fill=tuple(c))
save(bayer_quantize(np.asarray(img, np.float32), 16), "k-bubbles")

# Circles: concentric rings tiled, teal on teal
yy, xx = np.mgrid[0:64, 0:64]
rr = np.hypot(xx - 31.5, yy - 31.5)
m = ((rr // 4) % 2 == 0)[..., None] & (rr < 30)[..., None]
save(tiled(np.where(m, hexc("#00a0a0"), hexc("#006060"))), "l-circles")

# Blue Rivets: brushed steel plates with a rivet in each corner
plate = 80
t = np.asarray(Image.fromarray((rng.random((plate, plate)) * 255).astype(np.uint8)).resize((plate, plate * 4)).resize((plate, plate)),
               np.float32)[..., None] / 255
tile = hexc("#203880") * (1 - t * 0.4) + hexc("#5070c0") * t * 0.4
tile = tile.copy()
tile[:2] = hexc("#7090e0"); tile[:, :2] = hexc("#7090e0"); tile[-2:] = hexc("#101830"); tile[:, -2:] = hexc("#101830")
ry, rx = np.mgrid[0:plate, 0:plate]
for cx, cy in [(10, 10), (plate - 11, 10), (10, plate - 11), (plate - 11, plate - 11)]:
    dist = np.hypot(rx - cx, ry - cy)
    shade = np.clip(1 - ((rx - cx) + (ry - cy)) / 8, 0.2, 1.6)[..., None]
    tile = np.where((dist < 4)[..., None], hexc("#8090b0") * shade, tile)
save(tiled(tile), "m-rivets")

# Waves: layered sine bands in VGA blues
y = np.arange(H, dtype=np.float32)[:, None]
x = np.arange(W, dtype=np.float32)[None, :]
band = (y + 22 * np.sin(x / 90) + 10 * np.sin(x / 31 + y / 70)) / 36
cols = np.array([hexc(c) for c in ["#000080", "#0000a8", "#0040c0", "#0080c0", "#00a8c0", "#0080c0", "#0040c0", "#0000a8"]])
save(cols[np.floor(band).astype(int) % len(cols)], "n-waves")

# Straw Mat: woven over-under strips
s = 16
a = np.zeros((s * 2, s * 2, 3), np.float32)
grad = np.linspace(0.75, 1.15, s, dtype=np.float32)
a[:s, :s] = hexc("#c8b070") * grad[None, :, None]
a[s:, s:] = hexc("#c8b070") * grad[None, :, None]
a[:s, s:] = hexc("#b09858") * grad[:, None, None]
a[s:, :s] = hexc("#b09858") * grad[:, None, None]
save(tiled(a), "o-strawmat")

# Tiles: glazed bathroom tiles with grout
save(tiled(np.pad(bevel_tile(58, 58, "#4080a0", "#80c0e0", "#204860", edge=4), ((1, 1), (1, 1), (0, 0)),
                 constant_values=200)), "p-tiles")

# Carved Stone: embossed grey noise
n = noise(6, base=20, persistence=0.6)
emb = (np.roll(n, 2, axis=(0, 1)) - n) * 6
save(np.broadcast_to(hexc("#909090"), (H, W, 3)) * (0.85 + emb[..., None]), "q-carvedstone")

# Screensavers on black: 3D Pipes, Starfield, Mystify
img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)
step = 60
for pipe in range(7):
    col = hexc(["#ff4040", "#40ff40", "#4080ff", "#ffff40", "#ff40ff", "#40ffff", "#ffa040"][pipe])
    x, y = rng.integers(2, W // step - 2) * step, rng.integers(2, H // step - 2) * step
    dx, dy = 1, 0
    for _ in range(40):
        if rng.random() < 0.35:
            dx, dy = (0, rng.choice([-1, 1])) if dx else (rng.choice([-1, 1]), 0)
        nx, ny = x + dx * step * rng.integers(1, 4), y + dy * step * rng.integers(1, 4)
        if not (step <= nx <= W - step and step <= ny <= H - step):
            dx, dy = -dx, -dy
            continue
        for k in range(9, 0, -1):  # a tube: dark edges, bright core
            c = tuple((col * (0.35 + 0.65 * (1 - k / 9))).astype(int))
            d.line([(x, y), (nx, ny)], fill=c, width=k * 2)
        for k in range(12, 0, -1):  # ball joint
            c = tuple((col * (0.3 + 0.7 * (1 - k / 12)) + 30 * (1 - k / 12)).clip(0, 255).astype(int))
            d.ellipse([nx - k - (12 - k) * 0.3, ny - k - (12 - k) * 0.3, nx + k - (12 - k) * 0.3, ny + k - (12 - k) * 0.3], fill=c)
        x, y = nx, ny
save(np.asarray(img, np.float32), "r-pipes")

img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)
cx, cy = W / 2, H / 2
for _ in range(900):
    a, r = rng.uniform(0, math.tau), rng.uniform(10, 1100) ** 1.0
    ln = r * 0.06
    b = int(min(255, 60 + r / 4))
    d.line([(cx + math.cos(a) * r, cy + math.sin(a) * r), (cx + math.cos(a) * (r + ln), cy + math.sin(a) * (r + ln))],
           fill=(b, b, b), width=1 if r < 500 else 2)
save(np.asarray(img, np.float32), "s-starfield")

img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)
for col in [(255, 0, 255), (0, 255, 255)]:
    pts = rng.uniform([0, 0], [W, H], (4, 2))
    vel = rng.uniform(-40, 40, (4, 2))
    for k in range(14):
        d.polygon([tuple(p) for p in pts], outline=col)
        pts = pts + vel
        for p, v in zip(pts, vel):
            for i, lim in enumerate((W, H)):
                if not 0 <= p[i] <= lim:
                    v[i] = -v[i]
save(np.asarray(img, np.float32), "t-mystify")

# Plus! Space: dithered planet with rings over stars
v = np.zeros((H, W, 3), np.float32)
stars = rng.random((H, W)) > 0.9985
v[stars] = 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
px, py, pr = W * 0.62, H * 0.55, 300
dist = np.hypot(xx - px, yy - py)
light = np.clip(((px - xx) * 0.6 + (py - yy) * 0.8) / pr + 0.6, 0.05, 1.2)
bands = 0.85 + 0.15 * np.sin((yy - py) / 18 + noise(4, base=8) * 4)
planet = (hexc("#c08040") * bands[..., None] * light[..., None])
v = np.where((dist < pr)[..., None], planet, v)
ring = np.abs(((xx - px) / 2.6) ** 2 + ((yy - py) * 2.2) ** 2 - (pr * 0.62) ** 2 * 1.0) < pr * 90
behind = (yy < py) & (dist < pr)
v = np.where((ring & ~behind)[..., None], hexc("#d0c0a0") * 0.8, v)
save(bayer_quantize(v, 8), "u-space")
