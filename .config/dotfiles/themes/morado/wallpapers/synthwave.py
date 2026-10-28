#!/usr/bin/env python3
"""Generate the "morado" wallpapers into rotation/ (hyprpaper cycles that folder): synthwave, 1986. A violet night,
a striped sun sinking into a neon grid, palms, a city, chrome letters, a VHS screen, a tunnel and the Arch logo in
neon. Neon lines get a soft glow (a blurred copy underneath). Fonts come from the theme's fonts/ (Orbitron, Share
Tech Mono). Needs numpy, Pillow and rsvg-convert (for the Arch logo). Run: python3 synthwave.py"""
import io
import math
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1200
HERE = Path(__file__).parent
FONTS = HERE.parent / "fonts"
OUT = HERE / "rotation"

NIGHT, VIOLET, MAGENTA, PINK, ORANGE, YELLOW, CYAN = \
    (11, 2, 23), (38, 16, 75), (255, 42, 157), (255, 124, 194), (255, 138, 61), (255, 211, 25), (45, 226, 230)
HORIZON = int(H * 0.58)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def vgrad(top, bottom, h=H, w=W):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top, float)[None, None, :]
    b = np.array(bottom, float)[None, None, :]
    return np.broadcast_to(a + (b - a) * t, (h, w, 3)).astype(np.uint8)


def sky():
    """Night violet at the top warming to magenta at the horizon, darker below it."""
    img = np.zeros((H, W, 3), np.uint8)
    img[:HORIZON] = vgrad(NIGHT, (110, 18, 110), HORIZON)
    img[HORIZON:] = vgrad((24, 4, 44), NIGHT, H - HORIZON)
    return Image.fromarray(img)


def stars(img, n=260, seed=1, top=HORIZON):
    d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    for _ in range(n):
        x, y = rng.randrange(W), rng.randrange(top)
        c = rng.choice([(255, 255, 255), PINK, CYAN])
        r = rng.choice([0, 0, 0, 1])
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)


def glow(img, draw_fn, blur=8):
    """Draw neon with draw_fn(draw) twice: blurred underneath for the halo, sharp on top."""
    layer = Image.new("RGB", img.size, (0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    halo = layer.filter(ImageFilter.GaussianBlur(blur))
    img = ImageChops.add(img, halo)
    return ImageChops.lighter(img, layer)


def grid(img, color=MAGENTA, spacing=110, rows=18):
    """Perspective floor: lines fanning out from the vanishing point, rows squeezing towards the horizon."""
    def lines(d):
        cx = W / 2
        for k in range(-24, 25):
            d.line([(cx + k * 8, HORIZON), (cx + k * spacing * 2.2, H)], fill=color, width=2)
        for i in range(1, rows):
            y = HORIZON + (H - HORIZON) * (i / rows) ** 2.2
            d.line([(0, y), (W, y)], fill=color, width=2)
        d.line([(0, HORIZON), (W, HORIZON)], fill=PINK, width=3)
    return glow(img, lines, 6)


def sun(img, cx=W // 2, cy=HORIZON - 40, r=300):
    """The striped sun: yellow to magenta top to bottom, with gaps that widen towards its base, cut by the horizon."""
    s = Image.new("RGB", (2 * r, 2 * r))
    s.paste(Image.fromarray(vgrad(YELLOW, MAGENTA, 2 * r, 2 * r)))
    mask = Image.new("L", (2 * r, 2 * r), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    for i in range(9):  # stripes from just above the middle down, wider and wider
        y = r * 0.45 + i * r * 0.12
        d.rectangle([0, y, 2 * r, y + 3 + i * 2.6], fill=0)
    halo = Image.new("RGB", img.size, (0, 0, 0))
    ImageDraw.Draw(halo).ellipse([cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40], fill=(120, 20, 90))
    img = ImageChops.add(img, halo.filter(ImageFilter.GaussianBlur(60)))
    img.paste(s, (cx - r, cy - r), mask)
    # the horizon swallows the bottom of the sun
    img.paste(Image.fromarray(vgrad((24, 4, 44), NIGHT, H - HORIZON)), (0, HORIZON))
    return img


def mountains(img, seed=3, color=CYAN):
    rng = random.Random(seed)
    pts, x = [(0, HORIZON)], 0
    while x < W:
        x += rng.randint(60, 160)
        pts.append((x, HORIZON - rng.randint(40, 230)))
    pts.append((W, HORIZON))
    ImageDraw.Draw(img).polygon(pts, fill=(18, 5, 40))

    def edges(d):
        d.line(pts, fill=color, width=2)
        for (x1, y1) in pts[1:-1]:
            d.line([(x1, y1), (x1 + rng.randint(-60, 60), HORIZON)], fill=(20, 110, 130), width=1)
    return glow(img, edges, 5)


def palm(d, x, base, h, lean=0.0, color=(8, 1, 18)):
    """A palm silhouette: a curved trunk and fronds hanging from the crown."""
    top = (x + lean * h, base - h)
    for t in np.linspace(0, 1, 40):
        px = x + lean * h * t ** 2
        py = base - h * t
        w = 14 - 8 * t
        d.ellipse([px - w, py - w, px + w, py + w], fill=color)
    for a in range(0, 360, 36):
        ang = math.radians(a)
        pts = []
        for t in np.linspace(0, 1, 18):
            pts.append((top[0] + math.cos(ang) * 190 * t, top[1] + math.sin(ang) * 70 * t + 120 * t * t))
        d.line(pts, fill=color, width=14)


def chrome_text(img, text, size, y):
    """Chrome lettering: a vertical gradient (sky blue, white, dark horizon line, sunset) through the glyphs."""
    f = font("orbitron-latin-900-normal.ttf", size)
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    bw = md.textlength(text, font=f)
    x = (W - bw) / 2
    md.text((x, y), text, font=f, fill=255)
    box = mask.getbbox()
    h = box[3] - box[1]
    g = np.zeros((H, W, 3), np.uint8)
    top, mid = box[1], box[1] + h // 2
    g[top:mid] = vgrad((120, 200, 255), (255, 255, 255), mid - top)
    g[mid:box[3]] = vgrad((60, 20, 90), (255, 160, 220), box[3] - mid)
    outline = mask.filter(ImageFilter.MaxFilter(9))
    img = glow(img, lambda d: d.bitmap((0, 0), outline, fill=MAGENTA), 10)
    img.paste(Image.fromarray(g), (0, 0), mask)
    return img


def arch_logo(size):
    svg = HERE.parent / "icons/archlinux.svg"
    png = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), str(svg)], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).split()[-1]


def save(img, name):
    OUT.mkdir(exist_ok=True)
    img.save(OUT / f"{name}.png", optimize=True)
    print(OUT / f"{name}.png")


# a: the classic sunset over the grid, wireframe mountains
img = sky(); stars(img); img = sun(img); img = mountains(img); img = grid(img); save(img, "a-atardecer")

# b: only the grid running to the horizon under the stars, cyan
img = sky(); stars(img, 500, 7); img = grid(img, CYAN, 90, 22); save(img, "b-rejilla")

# c: palms against the sun
img = sky(); stars(img, 150, 4); img = sun(img, W // 2 + 260, HORIZON - 20, 330); img = grid(img)
d = ImageDraw.Draw(img)
palm(d, 330, H, 760, 0.22); palm(d, 520, H, 600, -0.18); palm(d, 1650, H, 700, -0.25)
save(img, "c-palmeras")

# d: a city of towers with lit windows
img = sky(); stars(img, 200, 9); img = sun(img, W // 2, HORIZON - 120, 260)
d = ImageDraw.Draw(img)
rng = random.Random(5)
x = 0
while x < W:
    w, h = rng.randint(70, 160), rng.randint(180, 620)
    d.rectangle([x, HORIZON + 60 - h, x + w, H], fill=(10, 2, 24))
    for wy in range(HORIZON + 80 - h, H, 22):
        for wx in range(x + 10, x + w - 10, 18):
            if rng.random() < 0.28:
                d.rectangle([wx, wy, wx + 8, wy + 10], fill=rng.choice([CYAN, PINK, YELLOW]))
    x += w + rng.randint(4, 20)
save(img, "d-ciudad")

# e: chrome LINUX over the sunset, the year in neon script below
img = sky(); stars(img, 300, 11); img = sun(img, W // 2, HORIZON + 40, 360); img = grid(img)
img = chrome_text(img, "LINUX", 260, 300)
f = font("orbitron-latin-700-normal.ttf", 64)
img = glow(img, lambda d: d.text((W / 2, 640), "ARCH 1986", font=f, fill=CYAN, anchor="mm"), 8)
save(img, "e-cromo")

# f: a VHS screen: blue tape, PLAY, the counter and tracking noise
img = Image.fromarray(vgrad((20, 30, 120), (10, 10, 60)))
d = ImageDraw.Draw(img)
rng = random.Random(2)
for _ in range(90):
    y = rng.randrange(H)
    d.line([(0, y), (W, y)], fill=(40, 60, 170), width=rng.choice([1, 1, 2]))
for y in range(H - 140, H - 100, 3):
    d.line([(rng.randrange(-200, 0), y), (W, y)], fill=(200, 200, 230), width=1)
f = font("share-tech-mono-latin-400-normal.ttf", 84)
img = glow(img, lambda d: (d.text((120, 120), "PLAY", font=f, fill=(255, 255, 255)),
                           d.polygon([(370, 140), (370, 200), (420, 170)], fill=(255, 255, 255)),
                           d.text((120, 230), "SP  0:19:86", font=f, fill=(255, 255, 255)),
                           d.text((W - 120, 120), "CH 03", font=f, fill=(255, 255, 255), anchor="ra")), 4)
save(img, "f-vhs")

# g: a tunnel of neon frames shrinking to the centre
img = Image.new("RGB", (W, H), NIGHT)
def tunnel(d):
    for i in range(26):
        k = 0.82 ** i
        w, h = W * k, H * k
        c = MAGENTA if i % 2 else CYAN
        d.rectangle([W / 2 - w / 2, H / 2 - h / 2, W / 2 + w / 2, H / 2 + h / 2], outline=c, width=max(1, int(5 * k) + 1))
img = glow(img, tunnel, 7); save(img, "g-tunel")

# h: the Arch logo as a neon sign over the grid
img = sky(); stars(img, 400, 13); img = grid(img)
logo = arch_logo(560)
edge = logo.filter(ImageFilter.FIND_EDGES).point(lambda a: 255 if a > 40 else 0).filter(ImageFilter.MaxFilter(5))
pos = (W // 2 - 280, HORIZON - 640)
img = glow(img, lambda d: d.bitmap(pos, edge, fill=CYAN), 12)
img = glow(img, lambda d: d.bitmap((pos[0] + 6, pos[1] + 6), edge, fill=MAGENTA), 6)
save(img, "h-arch-neon")
