#!/usr/bin/env python3
"""Generate the "cian" wallpapers into rotation/ (hyprpaper cycles that folder): blueprint sheets. Prussian blue paper
with a squared grid, a white border and a title block in the corner, and on each sheet one part drawn in white lines
with centre lines and dimensions: a gear, a UR3e robot arm, a ThinkPad, the Arch logo with its construction lines, a
bolt and a workshop floor plan. Lettering in B612 (the theme's fonts/). Needs numpy, Pillow and rsvg-convert.
Run: python3 plano.py"""
import io
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1200
HERE = Path(__file__).parent
OUT = HERE / "rotation"
PAPER, INK, SOFT, FAINT = (16, 53, 102), (243, 248, 254), (195, 214, 238), (88, 132, 189)
BOLD = ImageFont.truetype(str(HERE.parent / "fonts/b612-latin-700-normal.ttf"), 22)
SMALL = ImageFont.truetype(str(HERE.parent / "fonts/b612-mono-latin-400-normal.ttf"), 17)
TINY = ImageFont.truetype(str(HERE.parent / "fonts/b612-mono-latin-400-normal.ttf"), 14)


def sheet(title, scale="1:1", number=1):
    """Blue paper with a slight mottling, the squared grid, the double border and the title block."""
    rng = np.random.default_rng(number)
    base = np.array(PAPER, float)[None, None, :] + rng.normal(0, 2.2, (H, W, 1))
    shade = (np.linspace(-6, 6, W)[None, :, None] + np.linspace(-4, 4, H)[:, None, None])
    img = Image.fromarray(np.clip(base + shade, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 24):
        d.line([(x, 0), (x, H)], fill=(30, 70, 122) if x % 120 else (40, 84, 138), width=1)
    for y in range(0, H, 24):
        d.line([(0, y), (W, y)], fill=(30, 70, 122) if y % 120 else (40, 84, 138), width=1)
    d.rectangle([40, 40, W - 40, H - 40], outline=INK, width=3)
    d.rectangle([52, 52, W - 52, H - 52], outline=SOFT, width=1)
    # title block in the bottom-right corner: four ruled rows
    x0, y0 = W - 52 - 560, H - 52 - 150
    d.rectangle([x0, y0, W - 52, H - 52], fill=PAPER, outline=INK, width=2)
    for y in (y0 + 50, y0 + 100):
        d.line([(x0, y), (W - 52, y)], fill=INK, width=1)
    d.line([(x0 + 280, y0 + 100), (x0 + 280, H - 52)], fill=INK, width=1)
    d.text((x0 + 16, y0 + 14), title, font=BOLD, fill=INK)
    d.text((x0 + 16, y0 + 64), "LINUX  ·  ARCH  ·  CACHYOS", font=SMALL, fill=SOFT)
    d.text((x0 + 16, y0 + 114), f"ESCALA {scale}", font=SMALL, fill=SOFT)
    d.text((x0 + 296, y0 + 114), f"HOJA {number} DE 7", font=SMALL, fill=SOFT)
    return img, d


def centre(d, x, y, r):
    """Dash-dot centre lines through a point, a little longer than the feature (radius r)."""
    for (ax, ay, bx, by) in ((x - r - 30, y, x + r + 30, y), (x, y - r - 30, x, y + r + 30)):
        n = int(math.hypot(bx - ax, by - ay) // 22)
        for i in range(n):
            t0, t1 = i / n, (i + 0.6) / n
            d.line([(ax + (bx - ax) * t0, ay + (by - ay) * t0), (ax + (bx - ax) * t1, ay + (by - ay) * t1)], fill=SOFT, width=1)


def arrow(d, x, y, ang, size=14):
    a1, a2 = ang + 2.7, ang - 2.7
    d.polygon([(x, y), (x + size * math.cos(a1), y + size * math.sin(a1)), (x + size * math.cos(a2), y + size * math.sin(a2))], fill=INK)


def dim(d, a, b, text, off=40):
    """A linear dimension between points a and b, drawn off to one side with extension lines and arrows."""
    (ax, ay), (bx, by) = a, b
    ang = math.atan2(by - ay, bx - ax)
    nx, ny = -math.sin(ang) * off, math.cos(ang) * off
    pa, pb = (ax + nx, ay + ny), (bx + nx, by + ny)
    d.line([a, (pa[0] + nx * 0.2, pa[1] + ny * 0.2)], fill=SOFT, width=1)
    d.line([b, (pb[0] + nx * 0.2, pb[1] + ny * 0.2)], fill=SOFT, width=1)
    d.line([pa, pb], fill=INK, width=1)
    arrow(d, *pa, ang)
    arrow(d, *pb, ang + math.pi)
    mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
    tw = d.textlength(text, font=SMALL)
    d.rectangle([mx - tw / 2 - 6, my - 12, mx + tw / 2 + 6, my + 12], fill=PAPER)
    d.text((mx, my), text, font=SMALL, fill=INK, anchor="mm")


def label(d, x, y, text, tx, ty):
    """A leader line from a point on the part to a note."""
    d.line([(x, y), (tx, ty)], fill=SOFT, width=1)
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=INK)
    d.text((tx + (8 if tx > x else -8), ty), text, font=SMALL, fill=INK, anchor="lm" if tx > x else "rm")


def save(img, name):
    OUT.mkdir(exist_ok=True)
    img.save(OUT / f"{name}.png", optimize=True)
    print(OUT / f"{name}.png")


# 1: the blank sheet
img, d = sheet("HOJA EN BLANCO", "—", 1)
save(img, "a-hoja")

# 2: a spur gear, 24 teeth
img, d = sheet("RUEDA DENTADA  Z=24  m=12", "1:1", 2)
cx, cy, rp, z = 760, 560, 300, 24
pts = []
for i in range(z * 4):
    a = i / (z * 4) * 2 * math.pi
    r = rp + 22 if i % 4 in (1, 2) else rp - 26
    pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
d.polygon(pts, outline=INK, width=3)
for r, w in ((rp, 1), (90, 3), (40, 3)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK if w > 1 else SOFT, width=w)
d.rectangle([cx - 10, cy - 52, cx + 10, cy - 40], fill=PAPER, outline=INK, width=2)  # keyway
centre(d, cx, cy, rp + 22)
dim(d, (cx - rp - 22, cy + rp + 70), (cx + rp + 22, cy + rp + 70), "Ø 644", 20)
label(d, cx + 64, cy - 64, "Ø 180  CHAVETERO 20", 1250, 300)
label(d, cx + rp * 0.7, cy + rp * 0.7, "Ø PRIMITIVO 600", 1250, 820)
save(img, "b-engranaje")

# 3: UR3e robot arm, side view (link lengths in mm from Universal Robots' data: 151.9, 243.65, 213, 112.35, 85.35)
img, d = sheet("BRAZO UR3e  ·  ALZADO", "1:1.4", 3)
s = 1.6
base = (520, 930)
d.rectangle([base[0] - 70, base[1], base[0] + 70, base[1] + 40], outline=INK, width=3)
j1 = (base[0], base[1] - 151.9 * s)
j2 = (j1[0] + 243.65 * s * math.cos(math.radians(-35)), j1[1] + 243.65 * s * math.sin(math.radians(-35)))
j3 = (j2[0] + 213 * s * math.cos(math.radians(15)), j2[1] + 213 * s * math.sin(math.radians(15)))
j4 = (j3[0], j3[1] + 112.35 * s)
tool = (j4[0] + 85.35 * s, j4[1])
for a, b in ((base, j1), (j1, j2), (j2, j3), (j3, j4), (j4, tool)):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    nx, ny = -math.sin(ang) * 26, math.cos(ang) * 26
    d.polygon([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], outline=INK, width=3)
for j in (j1, j2, j3, j4):
    d.ellipse([j[0] - 40, j[1] - 40, j[0] + 40, j[1] + 40], fill=PAPER, outline=INK, width=3)
    centre(d, *j, 40)
d.rectangle([tool[0], tool[1] - 30, tool[0] + 40, tool[1] + 30], outline=INK, width=3)
dim(d, j1, j2, "243.65", -60)
dim(d, j2, j3, "213", -60)
dim(d, base, j1, "151.9", 110)
label(d, *j3, "MUÑECA 1", 1500, 380)
label(d, tool[0] + 40, tool[1], "TCP", 1500, 620)
save(img, "c-brazo-ur3e")

# 4: ThinkPad, plan view
img, d = sheet("THINKPAD P14s  ·  PLANTA", "1:1.6", 4)
x0, y0, w, h = 420, 230, 990, 700
d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 26, outline=INK, width=3)
d.rounded_rectangle([x0 + 60, y0 + 70, x0 + w - 60, y0 + 420], 10, outline=SOFT, width=2)
for row in range(5):
    for col in range(14):
        kx, ky = x0 + 95 + col * 58, y0 + 100 + row * 58
        d.rectangle([kx, ky, kx + 48, ky + 48], outline=INK, width=1)
d.ellipse([x0 + w / 2 - 8, y0 + 300, x0 + w / 2 + 8, y0 + 316], fill=(255, 122, 102))  # TrackPoint
d.rectangle([x0 + w / 2 - 170, y0 + 450, x0 + w / 2 + 170, y0 + 650], outline=INK, width=2)
for k in (-1, 0, 1):
    d.rectangle([x0 + w / 2 + k * 70 - 30, y0 + 430, x0 + w / 2 + k * 70 + 30, y0 + 446], outline=SOFT, width=1)
dim(d, (x0, y0 + h), (x0 + w, y0 + h), "316.6", 60)
dim(d, (x0 + w, y0), (x0 + w, y0 + h), "224.1", 60)
label(d, x0 + w / 2, y0 + 308, "TRACKPOINT", 1560, 300)
save(img, "d-thinkpad")

# 5: the Arch logo with its construction lines
img, d = sheet("LOGO ARCH  ·  TRAZADO", "2:1", 5)
svg = HERE.parent / "icons/archlinux.svg"
png = subprocess.run(["rsvg-convert", "-w", "720", "-h", "720", str(svg)], capture_output=True, check=True).stdout
a = Image.open(io.BytesIO(png)).split()[-1]
edge = a.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(3))
ox, oy = 600, 210
img.paste(INK, (ox, oy), edge)
d = ImageDraw.Draw(img)
apex, left, right = (ox + 342, oy + 18), (ox, oy + 702), (ox + 720, oy + 702)
for p, q in ((apex, left), (apex, right), (left, right)):
    d.line([p, q], fill=FAINT, width=1)
d.ellipse([ox + 285, oy + 420, ox + 435, oy + 570], outline=FAINT, width=1)
centre(d, ox + 360, oy + 495, 75)
dim(d, left, right, "720", 70)
dim(d, apex, left, "773", -70)
label(d, ox + 360, oy + 420, "ARCO R75", 1500, 420)
save(img, "e-arch")

# 6: a hex bolt M24, side view with its thread
img, d = sheet("TORNILLO  M24 × 160  DIN 931", "1:1", 6)
hx, hy = 420, 600
d.rectangle([hx, hy - 120, hx + 150, hy + 120], outline=INK, width=3)
for y in (hy - 60, hy + 60):
    d.line([(hx, y), (hx + 150, y)], fill=INK, width=2)
sx0, sx1 = hx + 150, hx + 1050
d.rectangle([sx0, hy - 72, sx1, hy + 72], outline=INK, width=3)
for x in range(sx0 + 330, sx1, 26):
    d.line([(x, hy - 72), (x + 13, hy + 72)], fill=SOFT, width=1)
d.line([(sx0 + 330, hy - 58), (sx1, hy - 58)], fill=SOFT, width=1)
d.line([(sx0 + 330, hy + 58), (sx1, hy + 58)], fill=SOFT, width=1)
centre(d, (hx + sx1) / 2, hy, (sx1 - hx) / 2)
dim(d, (sx0, hy + 72), (sx1, hy + 72), "160", 90)
dim(d, (sx0 + 330, hy - 72), (sx1, hy - 72), "ROSCA 54", -70)
dim(d, (hx, hy - 120), (hx, hy + 120), "36", 70)
save(img, "f-tornillo")

# 7: a workshop floor plan with doors and dimensions
img, d = sheet("TALLER  ·  PLANTA BAJA", "1:50", 7)
x0, y0 = 300, 200
walls = [(x0, y0, x0 + 1100, y0 + 760)]
d.rectangle(walls[0], outline=INK, width=8)
d.line([(x0 + 620, y0), (x0 + 620, y0 + 420)], fill=INK, width=5)
d.line([(x0, y0 + 420), (x0 + 400, y0 + 420)], fill=INK, width=5)
d.line([(x0 + 500, y0 + 420), (x0 + 1100, y0 + 420)], fill=INK, width=5)
for (px, py, r, start) in ((x0 + 400, y0 + 420, 100, 270), (x0 + 620, y0 + 300, 90, 90)):
    d.arc([px - r, py - r, px + r, py + r], start, start + 90, fill=SOFT, width=2)
d.rectangle([x0 + 700, y0 + 520, x0 + 1050, y0 + 600], outline=SOFT, width=2)   # workbench
d.rectangle([x0 + 60, y0 + 480, x0 + 260, y0 + 700], outline=SOFT, width=2)    # rack
for (tx, ty, t) in ((x0 + 310, y0 + 200, "ESTUDIO"), (x0 + 860, y0 + 200, "ALMACÉN"), (x0 + 550, y0 + 640, "TALLER")):
    d.text((tx, ty), t, font=BOLD, fill=INK, anchor="mm")
d.text((x0 + 875, y0 + 560), "BANCO", font=TINY, fill=SOFT, anchor="mm")
d.text((x0 + 160, y0 + 590), "ESTANTE", font=TINY, fill=SOFT, anchor="mm")
dim(d, (x0, y0 + 760), (x0 + 1100, y0 + 760), "11.00", 60)
dim(d, (x0 + 1100, y0), (x0 + 1100, y0 + 760), "7.60", 60)
save(img, "g-taller")
