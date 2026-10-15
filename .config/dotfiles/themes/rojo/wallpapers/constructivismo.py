#!/usr/bin/env python3
"""Generate the "rojo" wallpapers into rotation/: constructivist poster compositions (Lissitzky, Rodchenko, Klutsis,
Shukhov) drawn from scratch. Two inks, red and black, on newsprint: each sheet is drawn as two masks, the inks get a
worn texture and the red plate is printed a few pixels off register, like a 1920s press. Run: python3 constructivismo.py"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1200
SS = 2  # supersampling for smooth edges
OUT = Path(__file__).resolve().with_name("rotation")
FONTS = Path(__file__).resolve().parent.parent / "fonts"
PAPER, INK, RED = (239, 230, 210), (20, 20, 20), (212, 42, 30)
rng = np.random.default_rng(1925)


def font(name, px):
    return ImageFont.truetype(str(FONTS / name), px * SS)


RUSSO = "russo-one-400-normal.ttf"
OSWALD = "oswald-700-normal.ttf"


class Sheet:
    """Two plates (red, black) drawn in supersampled coordinates of the final W x H canvas."""

    def __init__(self):
        self.red = Image.new("L", (W * SS, H * SS), 0)
        self.ink = Image.new("L", (W * SS, H * SS), 0)

    def d(self, plate):
        return ImageDraw.Draw(self.red if plate == "red" else self.ink)

    @staticmethod
    def pts(points):
        return [(x * SS, y * SS) for x, y in points]

    def poly(self, plate, points, erase=False):
        self.d(plate).polygon(self.pts(points), fill=0 if erase else 255)

    def rect(self, plate, cx, cy, w, h, angle=0, erase=False):
        a = math.radians(angle)
        c, s = math.cos(a), math.sin(a)
        corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        self.poly(plate, [(cx + x * c - y * s, cy + x * s + y * c) for x, y in corners], erase)

    def circle(self, plate, cx, cy, r, erase=False):
        self.d(plate).ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=0 if erase else 255)

    def ring(self, plate, cx, cy, r, width):
        self.d(plate).ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], outline=255, width=width * SS)

    def line(self, plate, x0, y0, x1, y1, width):
        self.d(plate).line([(x0 * SS, y0 * SS), (x1 * SS, y1 * SS)], fill=255, width=max(1, int(width * SS)))

    def text(self, plate, txt, x, y, px, fontname=RUSSO, angle=0, anchor="la", spacing=0, erase=False):
        """Text rotated by `angle` degrees (counter-clockwise), anchored at (x, y)."""
        f = font(fontname, px)
        box = f.getbbox(txt, anchor=anchor)
        tw = box[2] - box[0] + spacing * SS * len(txt)
        layer = Image.new("L", (tw + 40 * SS, box[3] - box[1] + 40 * SS), 0)
        dr = ImageDraw.Draw(layer)
        cx = 20 * SS
        for ch in txt:
            dr.text((cx, 20 * SS - box[1]), ch, font=f, fill=255)
            cx += f.getlength(ch) + spacing * SS
        rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
        target = self.red if plate == "red" else self.ink
        ox, oy = int(x * SS - rot.width / 2), int(y * SS - rot.height / 2)
        if erase:
            hole = Image.new("L", target.size, 0)
            hole.paste(rot, (ox, oy))
            target.paste(ImageChops.subtract(target, hole))
        else:
            patch = Image.new("L", target.size, 0)
            patch.paste(rot, (ox, oy))
            target.paste(ImageChops.lighter(target, patch))

    def halftone(self, plate, cx, cy, r, spacing=14, angle=15, light_dir=(-0.6, -0.8)):
        """Dot screen inside a circle, dots growing away from the light: a printed sphere."""
        dr = self.d(plate)
        a = math.radians(angle)
        n = int(r / spacing) + 2
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x = cx + (i * math.cos(a) - j * math.sin(a)) * spacing
                y = cy + (i * math.sin(a) + j * math.cos(a)) * spacing
                dx, dy = (x - cx) / r, (y - cy) / r
                if dx * dx + dy * dy > 1:
                    continue
                shade = 0.5 - 0.5 * (dx * light_dir[0] + dy * light_dir[1])
                rr = spacing * 0.55 * shade
                if rr > 0.6:
                    dr.ellipse([(x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS], fill=255)

    def render(self, name, register=(3, 2)):
        red = np.asarray(self.red.resize((W, H), Image.LANCZOS), np.float32) / 255
        ink = np.asarray(self.ink.resize((W, H), Image.LANCZOS), np.float32) / 255
        red = np.roll(red, register, axis=(1, 0))  # the red plate is a little off register
        # Newsprint: warm base, fine grain, a few fibres, darker towards the edges
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        vign = 1 - 0.07 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        grain = rng.normal(0, 5, (H, W)).astype(np.float32)
        blotch = np.asarray(Image.fromarray((rng.random((24, 38)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC),
                            np.float32) / 255 - 0.5
        paper = (np.array(PAPER, np.float32)[None, None] * vign[..., None] + grain[..., None] + 10 * blotch[..., None])
        # Worn ink: the plates don't cover evenly
        wear = np.asarray(Image.fromarray((rng.random((H // 3, W // 3)) * 255).astype(np.uint8))
                          .resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
        red_cov = np.clip(red * (0.86 + 0.18 * wear), 0, 1)[..., None]
        ink_cov = np.clip(ink * (0.9 + 0.12 * wear), 0, 1)[..., None]
        img = paper * (1 - red_cov) + np.array(RED, np.float32) * red_cov
        img = img * (1 - ink_cov) + np.array(INK, np.float32) * ink_cov  # black overprints red
        Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(OUT / f"{name}.jpg", quality=92, subsampling=0)
        print("wrote", name)


def cuna():
    """Lissitzky: a red wedge from the white field drives into a white circle cut out of the black field."""
    s = Sheet()
    s.poly("ink", [(1920, 0), (1920, 1200), (900, 1200), (1260, 0)])  # black field on the right, cut diagonally
    s.circle("ink", 1390, 620, 280, erase=True)  # white circle in the black
    s.poly("red", [(90, 820), (1380, 590), (1388, 660)])  # the wedge, its tip inside the circle
    s.circle("red", 520, 330, 130)
    for cx, cy, w, h, a in [(300, 980, 260, 26, -10), (840, 170, 120, 120, 20), (1660, 1080, 200, 28, -40)]:
        s.rect("red", cx, cy, w, h, a)
    for cx, cy, w, h, a in [(250, 560, 420, 10, -10), (1020, 1040, 160, 40, 28)]:
        s.rect("ink", cx, cy, w, h, a)
    s.rect("ink", 1660, 300, 240, 22, -40, erase=True)  # splinters of white in the black
    s.rect("ink", 1720, 900, 140, 18, 25, erase=True)
    s.text("ink", "CUÑA", 470, 1090, 74, spacing=6)
    s.text("red", "№ 1", 1720, 160, 40, OSWALD)
    s.render("a-cuna")


def torre():
    """Shukhov radio tower: stacked hyperboloid lattice sections under a red sun."""
    s = Sheet()
    s.circle("red", 1300, 330, 260)
    base_y, x0 = 1200, 1180
    widths = [300, 240, 190, 150, 115, 85]
    y = base_y
    for k, wb in enumerate(widths):
        h = 190 - k * 14
        wt = wb * 0.62
        n = 22
        for i in range(n):
            t = i / n
            # straight generators twisted between the bottom and top rings make the hyperboloid
            xb = x0 + wb * math.cos(math.pi * 2 * t) * 1.0
            xt = x0 + wt * math.cos(math.pi * 2 * t + 1.1)
            s.line("ink", xb, y, xt, y - h, 3)
            xb2 = x0 + wb * math.cos(math.pi * 2 * t)
            xt2 = x0 + wt * math.cos(math.pi * 2 * t - 1.1)
            s.line("ink", xb2, y, xt2, y - h, 3)
        s.rect("ink", x0, y - h, wt * 2 + 16, 8)
        y -= h
        if k + 1 < len(widths):
            widths[k + 1] = min(widths[k + 1], wt)
    s.rect("ink", x0, y - 60, 6, 120)
    for r in (60, 110, 160):
        s.d("red").arc([(x0 - r) * SS, (y - 60 - r) * SS, (x0 + r) * SS, (y - 60 + r) * SS], 200, 340, fill=255, width=6 * SS)
    s.rect("red", 360, 600, 120, 1100, -8)
    s.text("ink", "RADIO", 360, 600, 120, angle=82, spacing=10)
    s.text("ink", "ONDAS · SEÑAL · DISTANCIA", 520, 1110, 30, OSWALD, spacing=4)
    s.render("b-torre")


def rayos():
    """Klutsis: rays fanning out of a corner, a black band carrying the word across."""
    s = Sheet()
    ox, oy = -120, 1320
    for i in range(14):
        a0 = math.radians(-8 - i * 6.4)
        a1 = a0 - math.radians(3.2)
        R = 3200
        s.poly("red", [(ox, oy), (ox + R * math.cos(a0), oy + R * math.sin(a0)), (ox + R * math.cos(a1), oy + R * math.sin(a1))])
    s.rect("ink", 1000, 640, 2600, 210, -24)
    s.rect("red", 1000, 640, 2600, 210, -24, erase=True)  # the band hides the rays, so the letters read as paper
    s.text("ink", "ENERGÍA", 1060, 610, 150, angle=24, spacing=14, erase=True)
    s.circle("ink", 1620, 230, 120)
    s.ring("red", 1620, 230, 175, 14)
    s.render("c-rayos")


def megafono():
    """Rodchenko: a cone of sound spreading from the left with the shout written along it."""
    s = Sheet()
    s.poly("red", [(70, 560), (1920, 40), (1920, 1140), (70, 700)])
    s.rect("ink", 70, 630, 120, 260)
    s.circle("ink", 30, 630, 70)
    s.text("ink", "¡CONSTRUIR!", 1080, 330, 150, angle=15, spacing=8)
    s.text("ink", "MÁQUINAS · RITMO · FUTURO", 1220, 860, 70, OSWALD, angle=-17, spacing=6)
    s.rect("ink", 1500, 600, 600, 12, 0)
    s.render("d-megafono")


def circulos():
    """Suprematist echo: printed spheres, rings and crossing bars."""
    s = Sheet()
    s.halftone("ink", 640, 600, 360, spacing=16)
    s.circle("red", 1230, 420, 210)
    s.ring("ink", 1230, 420, 300, 10)
    s.rect("ink", 1100, 760, 1500, 46, -18)
    s.rect("red", 1240, 860, 1100, 18, -18)
    s.rect("ink", 1560, 300, 40, 640, 18)
    s.text("red", "1925", 1600, 1040, 110, angle=0, spacing=10)
    s.render("e-circulos")


def tipografia():
    """Pure typography: a huge numeral, a vertical red slab with the word, ink rules."""
    s = Sheet()
    s.text("ink", "04", 760, 640, 820, OSWALD, angle=0)
    s.rect("red", 1440, 600, 300, 1300)
    s.text("ink", "TRABAJO", 1440, 600, 170, angle=90, spacing=12)
    for y in (140, 170, 200):
        s.rect("ink", 380, y, 600, 8)
    s.text("red", "EL TALLER DEL FUTURO", 380, 1080, 44, OSWALD, spacing=6)
    s.render("f-tipografia")


def fabrica():
    """Factory: chimneys and sheds in black, red smoke bands driven by the wind."""
    s = Sheet()
    ground = 900
    s.rect("ink", W / 2, (ground + H) / 2 + 2, W + 20, H - ground + 4)
    for x, w, h in [(260, 70, 520), (420, 90, 640), (1180, 80, 560), (1340, 60, 470)]:
        s.poly("ink", [(x - w / 2, ground), (x + w / 2, ground), (x + w * 0.38, ground - h), (x - w * 0.38, ground - h)])
    for x in range(560, 1100, 180):  # saw-tooth shed roofs
        s.poly("ink", [(x, ground), (x, ground - 150), (x + 180, ground - 60), (x + 180, ground)])
    for i, (x, h) in enumerate([(420, 640), (1180, 560)]):
        for k in range(3):
            y0 = ground - h - 40 - k * 70
            s.rect("red", x + 380 + k * 60, y0 - k * 30, 760, 34, -14 - i * 4)
    s.circle("red", 1640, 260, 150)
    s.text("ink", "PRODUCCIÓN", 1450, 1050, 92, angle=0, spacing=10, erase=True)
    s.render("g-fabrica")


OUT.mkdir(exist_ok=True)
for f in OUT.glob("*"):
    f.unlink()
for fn in (cuna, torre, rayos, megafono, circulos, tipografia, fabrica):
    fn()
