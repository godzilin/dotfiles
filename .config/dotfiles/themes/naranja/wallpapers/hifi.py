#!/usr/bin/env python3
"""Plain surfaces of a 1970s receiver, no drawing and no text: walnut, speaker cloth, black brushed aluminium."""
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 1920, 1200
OUT = Path(__file__).resolve().parent / "rotation"
rng = np.random.default_rng(1974)


def stretched(sx, sy):
    """Smooth noise 0..1, stretched by sx/sy cells."""
    small = rng.random((H // sy + 2, W // sx + 2))
    img = Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255


def tint(v, dark, light):
    v = np.clip(v, 0, 1)[..., None]
    return Image.fromarray((np.array(dark) * (1 - v) + np.array(light) * v).astype(np.uint8))


def walnut():
    bend = stretched(700, 90) * 60
    y = np.arange(H, dtype=np.float32)[:, None] + bend
    rings = 0.5 + 0.5 * np.sin(y / 11 + stretched(500, 40) * 9)
    return tint(rings ** 2.2 * 0.5 + stretched(240, 2) * 0.5, (22, 14, 9), (70, 43, 26))


def cloth():
    x, y = np.meshgrid(np.arange(W), np.arange(H))
    weave = (np.sin(x * np.pi / 2) * np.sin(y * np.pi / 2) + 1) / 2
    return tint(weave * 0.6 + stretched(300, 300) * 0.25, (17, 13, 11), (52, 41, 33))


def brushed():
    return tint(stretched(420, 1) * 0.7 + 0.1, (15, 13, 12), (44, 40, 37))


OUT.mkdir(exist_ok=True)
for name, make in (("a-nogal", walnut), ("b-rejilla", cloth), ("c-aluminio", brushed)):
    make().save(OUT / f"{name}.jpg", quality=88)
