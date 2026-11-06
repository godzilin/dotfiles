#!/usr/bin/env python3
"""Write logo.txt: the Arch logo as a glossy gel gumdrop in the six stripes of the 1977 rainbow, standing on a white
shelf with its reflection under it. Run: python3 make_logo.py"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

COLS, ROWS2 = 46, 42
W, H = L.size(COLS, ROWS2)
STRIPES = [(97, 187, 70), (253, 184, 39), (245, 130, 31), (224, 58, 62), (150, 61, 151), (0, 157, 220)]

mask = L.arch(H * 74 // 100)
mw, mh = mask.size
stripe = np.array(STRIPES, float)[(np.arange(mh) * 6 // mh)]
body = np.repeat(stripe[:, None, :], mw, axis=1)
# depth: darker towards the rim, like a lens of coloured glass
inner = np.asarray(mask.filter(ImageFilter.GaussianBlur(mh / 22)), float) / 255
body *= (0.62 + 0.38 * np.clip((inner - 0.5) * 2, 0, 1))[:, :, None]
gem = Image.fromarray(body.clip(0, 255).astype(np.uint8)).convert("RGBA")
gem.putalpha(mask)
# gloss: a white crescent over the top half, cut to the shape
gloss = Image.new("L", mask.size, 0)
ImageDraw.Draw(gloss).ellipse([-mw * 0.3, -mh * 0.85, mw * 1.3, mh * 0.34], fill=105)
gloss = ImageChops.multiply(gloss.filter(ImageFilter.GaussianBlur(mh / 60)), mask.filter(ImageFilter.MinFilter(9)))
gem.alpha_composite(Image.merge("RGBA", (*[Image.new("L", mask.size, 255)] * 3, gloss)))

img = Image.new("RGBA", (W, H), (255, 255, 255, 0))
x, y = (W - mw) // 2, H * 3 // 100
img.alpha_composite(gem, (x, y))
# the reflection fades out on the shelf
ref = gem.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, mw, H - y - mh))
ramp = np.linspace(0.30, 0, ref.height)[:, None]
r = np.asarray(ref).astype(float)
r[:, :, 3] *= ramp
img.alpha_composite(Image.fromarray(r.astype(np.uint8)), (x, y + mh))
L.write(HERE / "logo.txt", L.blocks(img, COLS, ROWS2, (255, 255, 255), cut=14))
