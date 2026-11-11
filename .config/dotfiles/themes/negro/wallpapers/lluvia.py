#!/usr/bin/env python3
"""Frames of falling katakana for the lock screen (hypr/hyprlock.conf cycles them, one per second): transparent PNGs,
columns with a bright head and a fading green trail, each at its own speed. The loop is seamless: 52 rows, speeds 1 or 2.
Needs Pillow and noto-cjk. Run: python3 lluvia.py"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).parent / "lluvia"
W, H, ROW, PITCH = 800, 1144, 22, 17
ROWS = H // ROW  # 52
COLS = W // PITCH
CHARS = [chr(c) for c in range(0xFF71, 0xFF9E)] + list("0123456789")
FONT = ImageFont.truetype("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", 20, index=0)
GREEN = (51, 255, 77)
rng = random.Random(5)

cols = []
for c in range(COLS):
    cols.append({
        "off": rng.randrange(ROWS), "speed": rng.choice([1, 1, 2]), "len": rng.randrange(8, 30),
        "gain": rng.choice([0.5, 0.7, 1.0, 1.0]), "gap": rng.random() < 0.2,
        "chars": [rng.choice(CHARS) for _ in range(ROWS)],
    })

OUT.mkdir(exist_ok=True)
for k in range(ROWS):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for c, col in enumerate(cols):
        if col["gap"] and (k // 13 + c) % 2:  # some columns pause: their rain has passed
            continue
        head = (col["off"] + col["speed"] * k) % ROWS
        for i in range(col["len"]):
            r = (head - i) % ROWS
            if rng.random() < 0.03:
                col["chars"][r] = rng.choice(CHARS)
            f = (1 - i / col["len"]) ** 1.6 * col["gain"]
            colr = (200, 255, 210) if i == 0 else tuple(int(v * f) for v in GREEN)
            alpha = 255 if i == 0 else int(255 * min(1, f * 1.4))
            d.text((c * PITCH, r * ROW), col["chars"][r], font=FONT, fill=colr + (alpha,))
    glow = img.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(glow, img)
    img.save(OUT / f"{k:02d}.png", optimize=True)
