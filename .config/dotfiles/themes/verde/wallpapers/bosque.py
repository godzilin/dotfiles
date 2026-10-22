#!/usr/bin/env python3
"""Generate the "verde" (Bosque) wallpapers into rotation/ (hyprpaper cycles that folder). Run: python3 bosque.py
Everything is procedural (Pillow + numpy) and seeded, so the same files come out every time."""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1200
SS = 2  # supersampling for smooth edges
OUT = Path(__file__).resolve().parent / "rotation"

# Palette (theme.json)
NIGHT, BG, BG1, BG2, LINE = "#0f140f", "#151c15", "#1d261c", "#263224", "#34432f"
MUTED, SUB, TEXT = "#7f8f72", "#aab89a", "#e4e6d0"
MOSS, SUN, BARK, BERRY, FERN, STREAM, SKY = "#9cc26b", "#e3c56e", "#c9894b", "#c0624a", "#7fae6e", "#6aa39a", "#7f9fb5"


def rgb(h):
    if isinstance(h, tuple):
        return h[:3]
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def gradient(top, bottom, w=W * SS, h=H * SS, power=1.0):
    t = np.linspace(0, 1, h)[:, None, None] ** power
    a, b = np.array(rgb(top)), np.array(rgb(bottom))
    arr = (a + (b - a) * t) * np.ones((1, w, 1))
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def ridge(rng, base, amp, w=W * SS, octaves=5, rough=0.55):
    """Height (y in px) of a hill line for every x: a few random sines, like 1D fractal noise."""
    x = np.arange(w)
    y = np.full(w, float(base))
    a, f = amp, 1.0 / w * 2
    for _ in range(octaves):
        y += a * np.sin(x * f * math.tau + rng.uniform(0, math.tau))
        a *= rough
        f *= 2.1
    return y


def pine(draw, x, ground, h, color, rng):
    """A fir: stacked, slightly ragged triangles over a short trunk."""
    tiers = max(3, int(h / (14 * SS)))
    w = h * rng.uniform(0.28, 0.36)
    draw.rectangle([x - h * 0.02, ground - h * 0.12, x + h * 0.02, ground], fill=color)
    for i in range(tiers):
        t = i / tiers
        top = ground - h * (0.12 + 0.88 * (t + 1 / tiers))
        bottom = ground - h * (0.08 + 0.88 * t)
        half = w * (1 - t) * 0.55 + w * 0.1
        jitter = rng.uniform(-0.08, 0.08) * half
        draw.polygon([(x, top), (x + half + jitter, bottom), (x - half + jitter, bottom)], fill=color)


def forest_layer(img, rng, base, amp, color, tree_h, density, haze=None):
    """A hill line covered in firs, filled down to the bottom of the picture."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = ridge(rng, base, amp)
    w = img.size[0]
    d.polygon([(0, img.size[1])] + [(x, y[x]) for x in range(0, w, 4)] + [(w - 1, y[-1]), (w - 1, img.size[1])], fill=color)
    x = 0
    while x < w:
        h = tree_h * rng.uniform(0.6, 1.25)
        pine(d, x, y[int(x)] + tree_h * 0.1, h, color, rng)
        x += tree_h * rng.uniform(0.12, 0.5) / density
    img.alpha_composite(layer)
    if haze is not None:  # mist rising from the valley behind the next layer
        img.alpha_composite(mist(img.size, base - amp * 0.2, img.size[1] * 0.18, haze))
    return y


def mist(size, y, spread, color, alpha=150):
    w, h = size
    t = np.clip((np.arange(h) - (y - spread)) / (2 * spread), 0, 1)
    a = (np.sin(t * math.pi) ** 2 * alpha).astype(np.uint8)
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = rgb(color)
    arr[..., 3] = a[:, None]
    return Image.fromarray(arr, "RGBA")


def glow(size, points, color, radius, strength=1.0):
    """Soft light dots (fireflies, sun): blurred discs, added on top."""
    layer = Image.new("RGBA", size, rgb(color) + (0,))  # transparent in the same colour, so the blur has no dark fringe
    d = ImageDraw.Draw(layer)
    for x, y, r in points:
        d.ellipse([x - r, y - r, x + r, y + r], fill=rgb(color) + (round(255 * strength),))
    halo = layer.filter(ImageFilter.GaussianBlur(radius))
    out = Image.alpha_composite(halo, halo)
    return Image.alpha_composite(out, layer)


def grain(img, amount=6, seed=0):
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    noise = np.random.default_rng(seed).normal(0, amount, arr.shape[:2])[..., None]
    return Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8), "RGB")


def save(img, name, seed):
    img = img.convert("RGB").resize((W, H), Image.LANCZOS)
    grain(img, 4, seed).save(OUT / name, optimize=True)
    print("wrote", name)


def niebla():
    """Fir ridges dissolving into mist at dusk, the far ones paler."""
    rng = random.Random(3)
    img = gradient(mix(SUN, BG2, 0.55), BG, power=0.9).convert("RGBA")
    img.alpha_composite(glow(img.size, [(W * SS * 0.68, H * SS * 0.36, 90 * SS)], mix(SUN, TEXT, 0.4), 80 * SS, 0.8))
    layers = [(0.42, 50, mix(SUB, BG2, 0.35), 40), (0.52, 60, mix(MUTED, BG2, 0.45), 60), (0.62, 70, mix(FERN, BG1, 0.6), 90),
              (0.74, 70, mix(FERN, BG, 0.78), 130), (0.88, 60, NIGHT, 190)]
    for i, (base, amp, color, th) in enumerate(layers):
        haze = mix(SUN, SUB, 0.5) if i < len(layers) - 1 else None
        forest_layer(img, rng, H * SS * base, amp * SS, color, th * SS, 1.0 + i * 0.2, haze)
    save(img, "a-niebla.png", 1)


def luciernagas():
    """Night in the forest: trunks, ferns at their feet and fireflies."""
    rng = random.Random(7)
    img = gradient(BG1, NIGHT, power=0.7).convert("RGBA")
    d = ImageDraw.Draw(img)
    for depth, color in [(0.35, mix(BG2, BG1, 0.3)), (0.6, BG1), (1.0, NIGHT)]:
        for _ in range(int(9 * depth) + 4):
            x = rng.uniform(0, W * SS)
            w = rng.uniform(18, 46) * SS * depth
            lean = rng.uniform(-30, 30) * SS
            d.polygon([(x - w / 2 + lean, 0), (x + w / 2 + lean, 0), (x + w * 0.65, H * SS), (x - w * 0.65, H * SS)], fill=color)
    forest_layer(img, rng, H * SS * 0.9, 18 * SS, NIGHT, 60 * SS, 2.0)
    for _ in range(26):  # ferns along the forest floor
        fern(ImageDraw.Draw(img), rng.uniform(0, W * SS), H * SS * rng.uniform(0.93, 1.02), rng.uniform(140, 260) * SS,
             math.radians(rng.uniform(-150, -30)), mix(BG2, NIGHT, 0.4), rng, detail=False)
    flies = [(rng.uniform(0, W * SS), rng.uniform(H * SS * 0.25, H * SS * 0.95), rng.uniform(2, 4.5) * SS) for _ in range(70)]
    img.alpha_composite(glow(img.size, flies, mix(SUN, MOSS, 0.4), 9 * SS))
    save(img, "b-luciernagas.png", 2)


def fern(draw, x, y, length, angle, color, rng, detail=True, width=None):
    """A frond: a curving stem with pairs of leaflets that shrink toward the tip (and their own lobes)."""
    steps = 30
    width = width or max(1, length / 90)
    pts = []
    bend = rng.uniform(-0.9, 0.9) / steps
    a = angle
    px, py = x, y
    for i in range(steps + 1):
        pts.append((px, py, a))
        px += math.cos(a) * length / steps
        py += math.sin(a) * length / steps
        a += bend
    draw.line([(p[0], p[1]) for p in pts], fill=color, width=round(width))
    for i, (px, py, a) in enumerate(pts[2:-1], start=2):
        t = i / steps
        leaf = length * 0.32 * (1 - t) ** 0.8 * (0.4 + 0.6 * min(1, t * 4))
        for side in (-1, 1):
            la = a + side * math.radians(62)
            if detail and leaf > 18:
                fern(draw, px, py, leaf, la, color, rng, detail=False, width=max(1, width * 0.6))
            else:
                ex, ey = px + math.cos(la) * leaf, py + math.sin(la) * leaf
                nx, ny = math.cos(la + math.pi / 2) * leaf * 0.18, math.sin(la + math.pi / 2) * leaf * 0.18
                draw.polygon([(px, py), ((px + ex) / 2 + nx, (py + ey) / 2 + ny), (ex, ey), ((px + ex) / 2 - nx, (py + ey) / 2 - ny)],
                             fill=color)


def helechos():
    """Botanical plate: big fern fronds in moss greens on the dark ground."""
    rng = random.Random(11)
    img = gradient(BG, NIGHT).convert("RGBA")
    for color, n, scale in [(BG2, 7, 1.15), (mix(FERN, BG1, 0.55), 5, 1.0), (FERN, 3, 0.85), (MOSS, 2, 0.7)]:
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for _ in range(n):
            x = rng.choice([rng.uniform(-0.05, 0.35), rng.uniform(0.65, 1.05)]) * W * SS
            fern(d, x, H * SS * rng.uniform(1.0, 1.1), rng.uniform(700, 1050) * SS * scale,
                 math.radians(rng.uniform(-115, -65) + (25 if x < W * SS / 2 else -25)), rgb(color) + (255,), rng)
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.6 * SS)))
    save(img, "c-helechos.png", 3)


def smooth_noise(rng, w, h, cells, octaves=4):
    out = np.zeros((h, w))
    amp = 1.0
    for o in range(octaves):
        n = cells * 2 ** o
        small = Image.fromarray((rng.random((n, int(n * w / h) + 1)) * 255).astype(np.uint8))
        out += amp * np.asarray(small.resize((w, h), Image.BICUBIC), float) / 255
        amp *= 0.5
    return (out - out.min()) / (out.max() - out.min())


def curvas():
    """Topographic map of a wooded valley: contour lines, every fifth one stronger, and a stream."""
    rng = np.random.default_rng(5)
    w, h = W * SS, H * SS
    z = smooth_noise(rng, w, h, 3)
    levels = 28
    q = np.floor(z * levels)
    edge = (np.diff(q, axis=0, prepend=q[:1]) != 0) | (np.diff(q, axis=1, prepend=q[:, :1]) != 0)
    major = edge & (q % 5 == 0)
    base = np.asarray(gradient(BG1, BG, w, h)).astype(float)
    tint = np.array(rgb(FERN), float)
    base = base + (tint - base) * (z[..., None] * 0.18)  # higher ground a bit greener
    img = base.copy()
    img[edge] = img[edge] * 0.35 + np.array(rgb(MUTED)) * 0.65
    img[major] = np.array(rgb(MOSS))
    im = Image.fromarray(img.astype(np.uint8), "RGB").filter(ImageFilter.MaxFilter(3))
    d = ImageDraw.Draw(im)
    pts, y = [], h * 0.15  # the stream runs downhill through the low ground
    x = w * 0.12
    while y < h:
        pts.append((x, y))
        x += math.sin(y / (140 * SS)) * 18 * SS + 6 * SS
        y += 12 * SS
    d.line(pts, fill=rgb(STREAM), width=5 * SS, joint="curve")
    save(im, "d-curvas.png", 4)


def lago():
    """A still mountain lake: fir ridge at sunset and its rippled reflection."""
    rng = random.Random(21)
    w, h = W * SS, H * SS
    horizon = int(h * 0.6)
    sky = gradient(mix(BARK, SUN, 0.5), mix(SUN, TEXT, 0.35), w, horizon, power=1.2).convert("RGBA")
    sky.alpha_composite(glow(sky.size, [(w * 0.3, horizon * 0.86, 70 * SS)], mix(SUN, TEXT, 0.6), 60 * SS, 0.9))
    forest_layer(sky, rng, horizon * 0.72, 60 * SS, mix(BARK, BG2, 0.55), 70 * SS, 1.0, mix(SUN, TEXT, 0.3))
    forest_layer(sky, rng, horizon * 0.88, 40 * SS, mix(FERN, NIGHT, 0.75), 120 * SS, 1.4)
    top = sky.crop((0, 0, w, horizon))
    refl = np.asarray(top.transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")).copy()
    for row in range(refl.shape[0]):  # ripples grow toward the viewer
        shift = int(math.sin(row / (3.0 * SS) + row * 0.002) * (1 + row / refl.shape[0] * 10) * SS)
        refl[row] = np.roll(refl[row], shift, axis=0)
    water = Image.fromarray((refl * 0.62 + np.array(rgb(STREAM)) * 0.08).astype(np.uint8)).resize((w, h - horizon))
    img = Image.new("RGB", (w, h))
    img.paste(top.convert("RGB"), (0, 0))
    img.paste(water, (0, horizon))
    d = ImageDraw.Draw(img)
    r2 = random.Random(4)
    for _ in range(60):  # glints on the water
        y = r2.uniform(horizon + 10 * SS, h)
        x = r2.uniform(0, w)
        ln = r2.uniform(20, 90) * SS * (y - horizon) / (h - horizon)
        d.line([(x, y), (x + ln, y)], fill=mix(SUN, TEXT, 0.5), width=SS)
    save(img, "e-lago.png", 5)


def leaf(d, x, y, size, angle, color, vein):
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((t, math.sin(t * math.pi) * 0.32 * (1 - t * 0.3)))
    outline = [(t, s) for t, s in pts] + [(t, -s) for t, s in reversed(pts)]
    ca, sa = math.cos(angle), math.sin(angle)
    tr = lambda u, v: (x + (u * ca - v * sa) * size, y + (u * sa + v * ca) * size)
    d.polygon([tr(u, v) for u, v in outline], fill=color)
    d.line([tr(-0.12, 0), tr(0.95, 0)], fill=vein, width=max(1, round(size / 60)))
    for k in range(1, 6):
        u = k / 6.5
        for s in (-1, 1):
            d.line([tr(u, 0), tr(u + 0.12, s * 0.2 * math.sin(u * math.pi))], fill=vein, width=max(1, round(size / 90)))


def hojas():
    """Leaves drifting down a dark stream: greens with a few autumn ones."""
    rng = random.Random(33)
    img = gradient(mix(STREAM, BG, 0.75), NIGHT).convert("RGBA")
    for blur, n, (lo, hi) in [(6, 30, (60, 110)), (2, 22, (110, 180)), (0, 12, (180, 280))]:
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for _ in range(n):
            c = rng.choices([MOSS, FERN, SUN, BARK, BERRY, mix(FERN, BG, 0.4)], [5, 5, 2, 2, 1, 4])[0]
            dim = {6: 0.55, 2: 0.25, 0: 0.0}[blur]
            col = mix(c, BG, dim)
            leaf(d, rng.uniform(-50, W * SS), rng.uniform(-50, H * SS), rng.uniform(lo, hi) * SS, rng.uniform(0, math.tau),
                 col + (255,), mix(col, NIGHT, 0.35) + (255,))
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur * SS)) if blur else layer)
    save(img, "f-hojas.png", 6)


def amanecer():
    """Morning over rolling hills: rays of sun through the haze, birch-pale light."""
    rng = random.Random(42)
    w, h = W * SS, H * SS
    img = gradient(mix(SKY, TEXT, 0.55), mix(SUN, TEXT, 0.5), power=1.4).convert("RGBA")
    sun = (w * 0.76, h * 0.42)
    rays = Image.new("RGBA", img.size, rgb(TEXT) + (0,))
    d = ImageDraw.Draw(rays)
    for k in range(14):
        a = math.radians(95 + k * 13 + rng.uniform(-4, 4))
        spread = math.radians(rng.uniform(2, 4))
        far = w * 1.5
        d.polygon([sun, (sun[0] + math.cos(a - spread) * far, sun[1] + math.sin(a - spread) * far),
                   (sun[0] + math.cos(a + spread) * far, sun[1] + math.sin(a + spread) * far)], fill=rgb(TEXT) + (60,))
    img.alpha_composite(rays.filter(ImageFilter.GaussianBlur(14 * SS)))
    img.alpha_composite(glow(img.size, [(sun[0], sun[1], 60 * SS)], mix(SUN, TEXT, 0.7), 70 * SS))
    hills = [(0.55, 40, mix(SKY, TEXT, 0.25), False), (0.63, 50, mix(SKY, FERN, 0.45), True), (0.72, 60, mix(FERN, MOSS, 0.3), True),
             (0.82, 70, mix(FERN, BG2, 0.55), True), (0.93, 50, mix(FERN, BG, 0.8), True)]
    for i, (base, amp, color, trees) in enumerate(hills):
        if trees:
            forest_layer(img, rng, h * base, amp * SS, color, (40 + i * 22) * SS, 0.35 + i * 0.15, mix(TEXT, SUN, 0.3))
        else:
            layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            y = ridge(rng, h * base, amp * SS, octaves=3)
            ImageDraw.Draw(layer).polygon([(0, h)] + [(x, y[x]) for x in range(0, w, 4)] + [(w - 1, h)], fill=color)
            img.alpha_composite(layer)
    save(img, "g-amanecer.png", 7)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for scene in (niebla, luciernagas, helechos, curvas, lago, hojas, amanecer):
        scene()
