#!/usr/bin/env python3
"""Generate the "dorado" wallpapers into rotation/ (hyprpaper cycles that folder), and the new-tab sky for Firefox: plates
of a night atlas, drawn in brass and parchment on ink. All kept dim on purpose, so windows and text stay comfortable
over them. Star positions are J2000 values of the bright stars, the astrolabe's plate is computed for latitude 43.26 N
(Bilbao) and the orrery uses mean longitudes for the eclipse of 12 Aug 2026; the faint dust behind is random.
Needs pycairo, numpy and Pillow. Run: python3 astrolabio.py"""
import math
import os
import random
from pathlib import Path

import cairo

HERE = Path(__file__).parent
FONTS = HERE.parent / "fonts"
OUT = HERE / "rotation"

W, H = 1920, 1200
INK, INK2 = (0x0d, 0x11, 0x1a), (0x19, 0x20, 0x30)
BRASS, GOLD, PARCH, MUTED, LINE = (0xd6, 0xb1, 0x6a), (0xe6, 0xcb, 0x82), (0xe4, 0xdc, 0xc8), (0x85, 0x8b, 0x9a), (0x33, 0x3c, 0x50)
TAU = 2 * math.pi

# name: (RA hours, Dec degrees, magnitude)
S = {
    "Dubhe": (11.06, 61.75, 1.8), "Merak": (11.03, 56.38, 2.4), "Phecda": (11.90, 53.69, 2.4), "Megrez": (12.26, 57.03, 3.3),
    "Alioth": (12.90, 55.96, 1.8), "Mizar": (13.40, 54.93, 2.2), "Alkaid": (13.79, 49.31, 1.9), "Muscida": (8.50, 60.72, 3.4),
    "um23": (9.52, 63.06, 3.7), "umUps": (9.85, 59.04, 3.8), "umTheta": (9.55, 51.68, 3.2), "Talitha": (8.99, 48.04, 3.1),
    "umKappa": (9.06, 47.16, 3.6), "umLam": (10.28, 42.91, 3.4), "umMu": (10.37, 41.50, 3.0), "umChi": (11.77, 47.78, 3.7),
    "umPsi": (11.16, 44.50, 3.0), "umNu": (11.31, 33.09, 3.5), "umXi": (11.30, 31.53, 3.8),
    "Polaris": (2.53, 89.26, 2.0), "Yildun": (17.54, 86.59, 4.4), "miEps": (16.77, 82.04, 4.2), "miZeta": (15.73, 77.79, 4.3),
    "Kochab": (14.85, 74.16, 2.1), "Pherkad": (15.35, 71.83, 3.0), "miEta": (16.29, 75.76, 5.0),
    "Segin": (1.91, 63.67, 3.4), "Ruchbah": (1.43, 60.24, 2.7), "casGamma": (0.95, 60.72, 2.5), "Schedar": (0.68, 56.54, 2.2), "Caph": (0.15, 59.15, 2.3),
    "Alderamin": (21.31, 62.59, 2.5), "Alfirk": (21.48, 70.56, 3.2), "Errai": (23.66, 77.63, 3.2), "cepIota": (22.83, 66.20, 3.5), "cepZeta": (22.18, 58.20, 3.4),
    "Eltanin": (17.94, 51.49, 2.2), "Rastaban": (17.51, 52.30, 2.8), "draXi": (17.89, 56.87, 3.7), "draNu": (17.54, 55.18, 4.9), "draDelta": (19.21, 67.66, 3.1),
    "draChi": (18.35, 72.73, 3.6), "draZeta": (17.15, 65.71, 3.2), "draEta": (16.40, 61.51, 2.7), "draTheta": (16.03, 58.57, 4.0), "draIota": (15.42, 58.97, 3.3),
    "Thuban": (14.07, 64.38, 3.6), "draKappa": (12.56, 69.79, 3.9), "draLam": (11.52, 69.33, 3.8),
    "Deneb": (20.69, 45.28, 1.3), "Sadr": (20.37, 40.26, 2.2), "Gienah": (20.77, 33.97, 2.5), "cygDelta": (19.75, 45.13, 2.9), "Albireo": (19.51, 27.96, 3.1),
    "Vega": (18.62, 38.78, 0.0), "lyrZeta": (18.75, 37.61, 4.4), "Sheliak": (18.83, 33.36, 3.5), "Sulafat": (18.98, 32.69, 3.2), "lyrDelta": (18.91, 36.90, 4.3),
    "Capella": (5.28, 46.00, 0.1), "Menkalinan": (5.99, 44.95, 1.9), "aurTheta": (6.00, 37.21, 2.6), "Elnath": (5.44, 28.61, 1.7), "aurIota": (4.95, 33.17, 2.7),
    "Arcturus": (14.26, 19.18, -0.1), "Izar": (14.75, 27.07, 2.4), "Nekkar": (15.03, 40.39, 3.5), "booGamma": (14.53, 38.31, 3.0), "booEta": (13.91, 18.40, 2.7),
    "Castor": (7.58, 31.89, 1.6), "Pollux": (7.76, 28.03, 1.1), "Mirfak": (3.41, 49.86, 1.8), "Algol": (3.14, 40.96, 2.1),
    "Markab": (23.08, 15.21, 2.5), "Scheat": (23.06, 28.08, 2.4), "Algenib": (0.22, 15.18, 2.8), "Alpheratz": (0.14, 29.09, 2.1),
    "Mirach": (1.16, 35.62, 2.1), "Almach": (2.06, 42.33, 2.1), "andDelta": (0.66, 30.86, 3.3),
    "Regulus": (10.14, 11.97, 1.4), "Denebola": (11.82, 14.57, 2.1), "Algieba": (10.33, 19.84, 2.1), "Zosma": (11.24, 20.52, 2.6), "Chertan": (11.24, 15.43, 3.3),
    "leoEta": (10.12, 16.76, 3.5), "Adhafera": (10.28, 23.42, 3.4), "Rasalas": (9.88, 26.01, 3.9), "leoEps": (9.76, 23.77, 3.0),
    "Aldebaran": (4.60, 16.51, 0.9), "Pleyades": (3.79, 24.11, 2.9),
    "Betelgeuse": (5.92, 7.41, 0.5), "Rigel": (5.24, -8.20, 0.1), "Bellatrix": (5.42, 6.35, 1.6), "Mintaka": (5.53, -0.30, 2.2), "Alnilam": (5.60, -1.20, 1.7),
    "Alnitak": (5.68, -1.94, 1.8), "Saiph": (5.80, -9.67, 2.1), "Meissa": (5.59, 9.93, 3.5), "oriIota": (5.59, -5.91, 2.8), "oriTheta": (5.59, -5.39, 4.7),
    "pi1": (4.91, 10.15, 4.7), "pi2": (4.84, 8.90, 4.4), "pi3": (4.83, 6.96, 3.2), "pi4": (4.85, 5.61, 3.7), "pi5": (4.90, 2.44, 3.7), "pi6": (4.98, 1.71, 4.5),
    "oriMu": (6.04, 9.65, 4.1), "oriNu": (6.12, 14.77, 4.4), "oriXi": (6.20, 14.21, 4.4), "chi1": (5.91, 20.28, 4.4), "chi2": (6.06, 20.14, 4.6),
}
UMA = [("Alkaid", "Mizar"), ("Mizar", "Alioth"), ("Alioth", "Megrez"), ("Megrez", "Phecda"), ("Phecda", "Merak"), ("Merak", "Dubhe"), ("Dubhe", "Megrez"),
       ("Dubhe", "um23"), ("um23", "Muscida"), ("Muscida", "umUps"), ("umUps", "Dubhe"), ("umUps", "umTheta"), ("umTheta", "Talitha"), ("umTheta", "umKappa"),
       ("Phecda", "umChi"), ("umChi", "umPsi"), ("umPsi", "umLam"), ("umLam", "umMu"), ("umChi", "umNu"), ("umNu", "umXi")]
ORI = [("Betelgeuse", "Alnitak"), ("Bellatrix", "Mintaka"), ("Mintaka", "Alnilam"), ("Alnilam", "Alnitak"), ("Alnitak", "Saiph"), ("Mintaka", "Rigel"),
       ("Betelgeuse", "Bellatrix"), ("Bellatrix", "Meissa"), ("Betelgeuse", "Meissa"), ("Bellatrix", "pi3"), ("pi1", "pi2"), ("pi2", "pi3"), ("pi3", "pi4"), ("pi4", "pi5"), ("pi5", "pi6"),
       ("Betelgeuse", "oriMu"), ("oriMu", "oriNu"), ("oriNu", "chi2"), ("chi2", "chi1"), ("oriNu", "oriXi"), ("oriIota", "oriTheta")]
FIGURES = [
    ("URSA MAIOR", UMA[:7]), ("URSA MINOR", [("Polaris", "Yildun"), ("Yildun", "miEps"), ("miEps", "miZeta"), ("miZeta", "Kochab"), ("Kochab", "Pherkad"), ("Pherkad", "miEta"), ("miEta", "miZeta")]),
    ("CASSIOPEIA", [("Segin", "Ruchbah"), ("Ruchbah", "casGamma"), ("casGamma", "Schedar"), ("Schedar", "Caph")]),
    ("CEPHEUS", [("Alderamin", "Alfirk"), ("Alfirk", "Errai"), ("Errai", "cepIota"), ("cepIota", "Alfirk"), ("cepIota", "cepZeta"), ("cepZeta", "Alderamin")]),
    ("DRACO", [("Eltanin", "Rastaban"), ("Rastaban", "draNu"), ("draNu", "draXi"), ("draXi", "Eltanin"), ("draXi", "draDelta"), ("draDelta", "draChi"), ("draChi", "draZeta"), ("draZeta", "draEta"),
               ("draEta", "draTheta"), ("draTheta", "draIota"), ("draIota", "Thuban"), ("Thuban", "draKappa"), ("draKappa", "draLam")]),
    ("CYGNUS", [("Deneb", "Sadr"), ("Sadr", "Albireo"), ("cygDelta", "Sadr"), ("Sadr", "Gienah")]),
    ("LYRA", [("Vega", "lyrZeta"), ("lyrZeta", "lyrDelta"), ("lyrDelta", "Sulafat"), ("Sulafat", "Sheliak"), ("Sheliak", "lyrZeta")]),
    ("AURIGA", [("Capella", "Menkalinan"), ("Menkalinan", "aurTheta"), ("aurTheta", "Elnath"), ("Elnath", "aurIota"), ("aurIota", "Capella")]),
    ("BOOTES", [("Arcturus", "Izar"), ("Izar", "Nekkar"), ("Nekkar", "booGamma"), ("booGamma", "Arcturus"), ("Arcturus", "booEta")]),
    ("ANDROMEDA", [("Alpheratz", "andDelta"), ("andDelta", "Mirach"), ("Mirach", "Almach")]),
    ("PEGASUS", [("Markab", "Scheat"), ("Scheat", "Alpheratz"), ("Alpheratz", "Algenib"), ("Algenib", "Markab")]),
    ("LEO", [("Regulus", "leoEta"), ("leoEta", "Algieba"), ("Algieba", "Adhafera"), ("Adhafera", "Rasalas"), ("Rasalas", "leoEps"), ("Algieba", "Zosma"), ("Zosma", "Denebola"), ("Denebola", "Chertan"), ("Chertan", "Regulus"), ("Zosma", "Chertan")]),
    ("GEMINI", [("Castor", "Pollux")]),
]


def rgb(c, a=1.0):
    return c[0] / 255, c[1] / 255, c[2] / 255, a


def sheet(cx=W / 2, cy=H / 2):
    """A new ink sheet: a little lighter around (cx, cy), like the sky near a dome's slit."""
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, 1250)
    g.add_color_stop_rgb(0, *rgb(INK2)[:3])
    g.add_color_stop_rgb(1, *rgb(INK)[:3])
    c.set_source(g)
    c.paint()
    return s, c


def dust(c, n, seed):
    r = random.Random(seed)
    for _ in range(n):
        m = r.random() ** 3
        c.set_source_rgba(*rgb(PARCH, 0.10 + 0.35 * m))
        c.arc(r.uniform(0, W), r.uniform(0, H), 0.5 + 0.8 * m, 0, TAU)
        c.fill()


def star(c, x, y, mag, colour=PARCH):
    r = max(0.9, 4.2 - 0.85 * mag)
    g = cairo.RadialGradient(x, y, 0, x, y, r * 4)
    g.add_color_stop_rgba(0, *rgb(colour, 0.28))
    g.add_color_stop_rgba(1, *rgb(colour, 0))
    c.set_source(g)
    c.arc(x, y, r * 4, 0, TAU)
    c.fill()
    c.set_source_rgba(*rgb(colour, 0.92))
    c.arc(x, y, r, 0, TAU)
    c.fill()


def text(c, x, y, s, size, colour=MUTED, a=1.0, face="Alegreya Sans", slant=cairo.FONT_SLANT_NORMAL, anchor=0.5, spacing=0.0):
    c.select_font_face(face, slant, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    w = sum(c.text_extents(ch).x_advance + spacing for ch in s)
    px = x - w * anchor
    c.set_source_rgba(*rgb(colour, a))
    for ch in s:
        c.move_to(px, y)
        c.show_text(ch)
        px += c.text_extents(ch).x_advance + spacing


def radial_text(c, cx, cy, r, ang, s, size, colour=MUTED, a=1.0, face="Alegreya Sans"):
    """Text centred at angle ang on a circle, its feet towards the centre."""
    c.save()
    c.translate(cx + r * math.cos(ang), cy + r * math.sin(ang))
    c.rotate(ang + math.pi / 2)
    text(c, 0, 0, s, size, colour, a, face)
    c.restore()


def plate(c, number, title, sub=""):
    """The atlas caption in the bottom-right corner."""
    text(c, W - 56, H - 74, f"LÁMINA {number}", 13, BRASS, 0.8, spacing=2.5, anchor=1)
    text(c, W - 56, H - 48, title, 25, PARCH, 0.75, "Alegreya", cairo.FONT_SLANT_ITALIC, anchor=1)
    if sub:
        text(c, W - 56, H - 26, sub, 13, MUTED, 0.85, anchor=1)


def limb(c, cx, cy, r, colour=BRASS, a=0.55, step=1, inward=True):
    """A graduated circle, 360 degrees, the signature of the theme."""
    c.set_line_width(1)
    sign = -1 if inward else 1
    for d in range(0, 360, step):
        length = 14 if d % 30 == 0 else 9 if d % 10 == 0 else 6 if d % 5 == 0 else 3.5
        t = math.radians(d)
        c.move_to(cx + r * math.cos(t), cy + r * math.sin(t))
        c.line_to(cx + (r + sign * length) * math.cos(t), cy + (r + sign * length) * math.sin(t))
    c.set_source_rgba(*rgb(colour, a))
    c.stroke()


def ring(c, cx, cy, r, colour=BRASS, a=0.5, w=1.0):
    c.new_path()  # or arc() joins the circle to whatever text left as the current point
    c.set_line_width(w)
    c.set_source_rgba(*rgb(colour, a))
    c.arc(cx, cy, r, 0, TAU)
    c.stroke()


def finish(s, name):
    """A touch of grain so the dark gradients don't band, then JPEG."""
    a = np.ndarray((H, W, 4), np.uint8, s.get_data()).copy()[:, :, [2, 1, 0]]
    noise = np.random.default_rng(len(name)).normal(0, 1.4, (H, W, 1))
    img = Image.fromarray(np.clip(a + noise, 0, 255).astype(np.uint8))
    OUT.mkdir(exist_ok=True)
    img.save(OUT / name, quality=92, subsampling=0)
    return img


def planisferio():
    s, c = sheet()
    dust(c, 900, 1)
    cx, cy, R = W / 2, H / 2, 545
    rad = lambda dec: (90 - dec) / 100 * R * 0.97  # down to dec -10
    pos = lambda st: (cx + rad(S[st][1]) * math.cos(S[st][0] * TAU / 24), cy + rad(S[st][1]) * math.sin(S[st][0] * TAU / 24))
    for dec in (80, 60, 40, 20, 0):
        ring(c, cx, cy, rad(dec), LINE, 0.9)
    c.set_line_width(1)
    c.set_source_rgba(*rgb(LINE, 0.75))
    for h in range(24):
        t = h * TAU / 24
        c.move_to(cx + rad(80) * math.cos(t), cy + rad(80) * math.sin(t))
        c.line_to(cx + rad(0) * math.cos(t), cy + rad(0) * math.sin(t))
    c.stroke()
    # ecliptic: tan(dec) = sin(RA) tan(obliquity)
    c.set_source_rgba(*rgb(BRASS, 0.45))
    c.set_dash([7, 6])
    for i in range(361):
        ra = math.radians(i)
        r = rad(math.degrees(math.atan(math.sin(ra) * math.tan(math.radians(23.44)))))
        c.line_to(cx + r * math.cos(ra), cy + r * math.sin(ra))
    c.stroke()
    c.set_dash([])
    for name, lines in FIGURES:
        c.set_line_width(1)
        c.set_source_rgba(*rgb(BRASS, 0.6))
        for a, b in lines:
            c.move_to(*pos(a))
            c.line_to(*pos(b))
        c.stroke()
        pts = [pos(n) for ln in lines for n in ln]
        px, py = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        text(c, px, py + 24, name, 12, MUTED, 0.95, spacing=2)
    for st, (ra, dec, mag) in S.items():
        if dec > -10 and not st.startswith("um") and rad(dec) < R:
            star(c, *pos(st), mag)
    ring(c, cx, cy, R, BRASS, 0.6)
    ring(c, cx, cy, R + 34, BRASS, 0.6)
    limb(c, cx, cy, R + 34, a=0.5)
    for h in range(24):
        radial_text(c, cx, cy, R + 8, h * TAU / 24, f"{h}h", 13, MUTED, 0.95)
    plate(c, "I", "Planisferio boreal", "Polo norte, ascensiones rectas y eclíptica")
    finish(s, "a-planisferio.jpg")


def tympan(c, cx, cy, R, phi):
    """The fixed part of the instrument for latitude phi (radians): limb, hours and plate. Returns the radii of the
    equator and of the Tropic of Cancer; instrumento.py draws the moving rete over this."""
    eps = math.radians(23.44)
    re = R / math.tan((math.pi / 2 + eps) / 2)  # the Tropic of Capricorn is the plate's edge
    rcancer = re * math.tan((math.pi / 2 - eps) / 2)
    for r_, a, w in ((R + 92, 0.7, 2.2), (R + 88, 0.4, 1), (R + 50, 0.5, 1)):
        ring(c, cx, cy, r_, BRASS, a, w)
    limb(c, cx, cy, R + 88, a=0.6)
    for h in range(24):
        n = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"][h % 12]
        radial_text(c, cx, cy, R + 58, h * TAU / 24 - math.pi / 2, n, 19, BRASS, 0.85, "Alegreya")
    # the climate: horizon-side almucantars and azimuths, clipped to the plate and to the sky above the horizon
    c.save()
    c.arc(cx, cy, R, 0, TAU)
    c.clip()
    ring(c, cx, cy, re, LINE, 1)
    ring(c, cx, cy, rcancer, LINE, 1)
    c.set_line_width(1)
    c.set_source_rgba(*rgb(LINE, 1))
    c.move_to(cx - R, cy); c.line_to(cx + R, cy); c.move_to(cx, cy - R); c.line_to(cx, cy + R); c.stroke()
    alm = lambda a: (re * math.cos(phi) / (math.sin(phi) + math.sin(a)), re * math.cos(a) / (math.sin(phi) + math.sin(a)))
    yc0, r0 = alm(0)
    c.save()
    c.arc(cx, cy - yc0, r0, 0, TAU)  # above the horizon
    c.clip()
    yz = re * math.tan((math.pi / 2 - phi) / 2)
    yn = -re / math.tan((math.pi / 2 - phi) / 2)
    ym, half = (yz + yn) / 2, (yz - yn) / 2
    for az in range(-80, 90, 10):
        t = math.radians(az)
        ring(c, cx + half * math.tan(t), cy - ym, half / math.cos(t), LINE, 0.8, 0.8)
    c.restore()
    for d in range(0, 88, 6):
        yc, r_ = alm(math.radians(d))
        ring(c, cx, cy - yc, r_, BRASS if d == 0 else (0x5a, 0x63, 0x78), 0.75 if d == 0 else 0.7, 1.3 if d == 0 else 0.9)
    c.restore()
    return re, rcancer


def astrolabio():
    s, c = sheet()
    dust(c, 500, 2)
    cx, cy, R = W / 2, H / 2, 480
    re, rcancer = tympan(c, cx, cy, R, math.radians(43.26))
    # the rete in brass, over the plate: ecliptic, its zodiac scale and the star pointers
    ec = (R - rcancer) / 2, (R + rcancer) / 2
    ecx, ecy = cx, cy - ec[0]
    ring(c, cx, cy, R - 1, BRASS, 0.85, 2.4)
    ring(c, ecx, ecy, ec[1], BRASS, 0.85, 2.4)
    ring(c, ecx, ecy, ec[1] - 20, BRASS, 0.5, 1)
    limb(c, ecx, ecy, ec[1], a=0.55, step=2)
    c.set_line_width(1.8)
    c.set_source_rgba(*rgb(BRASS, 0.75))
    for t_ in (-1.1, -0.2, 0.75, 1.75, 2.75, 3.75, 4.7):
        c.move_to(ecx + (ec[1] - 20) * math.cos(t_), ecy + (ec[1] - 20) * math.sin(t_))
        c.line_to(cx + 70 * math.cos(t_), cy + 70 * math.sin(t_))
    c.stroke()
    for st in ("Vega", "Arcturus", "Capella", "Deneb", "Regulus", "Aldebaran", "Betelgeuse", "Rigel", "Pollux", "Dubhe", "Altair"):
        if st == "Altair":
            ra, dec = 19.85, 8.87
        else:
            ra, dec = S[st][:2]
        t, r_ = ra * TAU / 24 + 0.55, re * math.tan((math.pi / 2 - math.radians(dec)) / 2)
        px, py = cx + r_ * math.cos(t), cy + r_ * math.sin(t)
        foot = (px - 34 * math.cos(t - 0.45), py - 34 * math.sin(t - 0.45))
        c.move_to(px, py)
        c.curve_to(foot[0] + 8 * math.cos(t + 1.2), foot[1] + 8 * math.sin(t + 1.2), foot[0], foot[1], foot[0] - 12 * math.cos(t), foot[1] - 12 * math.sin(t))
        c.set_line_width(2.4)
        c.set_source_rgba(*rgb(BRASS, 0.8))
        c.stroke()
        star(c, px, py, 2.4, GOLD)
    for r_ in (70, 26):
        ring(c, cx, cy, r_, BRASS, 0.7, 1.5)
    # the rule across the face
    t = math.radians(-58)
    dx, dy = math.cos(t), math.sin(t)
    nx, ny = -dy, dx
    c.move_to(cx - (R + 40) * dx + 8 * nx, cy - (R + 40) * dy + 8 * ny)
    c.line_to(cx + (R + 40) * dx + 2 * nx, cy + (R + 40) * dy + 2 * ny)
    c.line_to(cx + (R + 40) * dx - 2 * nx, cy + (R + 40) * dy - 2 * ny)
    c.line_to(cx - (R + 40) * dx - 8 * nx, cy - (R + 40) * dy - 8 * ny)
    c.close_path()
    c.set_source_rgba(*rgb((0x8a, 0x70, 0x42), 0.8))
    c.fill()
    c.arc(cx, cy, 9, 0, TAU)
    c.set_source_rgba(*rgb(BRASS, 0.95))
    c.fill()
    plate(c, "II", "Astrolabio planisférico", "Tímpano para 43° 16′ N")
    finish(s, "b-astrolabio.jpg")


def moon_disc(c, x, y, r, age, seed):
    """age 0..1 of the synodic month. Lit limb plus an elliptical terminator, with a few dark seas clipped to the lit part."""
    c.set_source_rgba(*rgb((0x22, 0x29, 0x3a), 1))
    c.arc(x, y, r, 0, TAU)
    c.fill()
    k = math.cos(age * TAU)  # 1 new, 0 quarter, -1 full
    waxing = age < 0.5
    side = 1 if waxing else -1
    c.save()
    c.translate(x, y)
    c.new_path()
    if abs(k) > 0.995 and k > 0:
        c.restore()
        ring(c, x, y, r, BRASS, 0.4)
        return
    c.arc(0, 0, r, -math.pi / 2, math.pi / 2) if side > 0 else c.arc_negative(0, 0, r, -math.pi / 2, math.pi / 2)
    # back along the terminator
    n = 80
    for i in range(n + 1):
        t = math.pi / 2 - i * math.pi / n
        c.line_to(side * k * r * math.cos(t), r * math.sin(t))
    c.close_path()
    c.clip()
    g = cairo.RadialGradient(-r * 0.2, -r * 0.2, r * 0.1, 0, 0, r * 1.1)
    g.add_color_stop_rgb(0, *rgb((0xd8, 0xcf, 0xb6))[:3])
    g.add_color_stop_rgb(1, *rgb((0x9c, 0x93, 0x7d))[:3])
    c.set_source(g)
    c.paint()
    rr = random.Random(7)
    for _ in range(11):
        mx, my, mr = rr.uniform(-.65, .55) * r, rr.uniform(-.6, .5) * r, rr.uniform(.12, .34) * r
        sea = cairo.RadialGradient(mx, my, 0, mx, my, mr)
        sea.add_color_stop_rgba(0, *rgb((0x6c, 0x68, 0x62), 0.42))
        sea.add_color_stop_rgba(0.65, *rgb((0x6c, 0x68, 0x62), 0.30))
        sea.add_color_stop_rgba(1, *rgb((0x6c, 0x68, 0x62), 0))
        c.set_source(sea)
        c.arc(mx, my, mr, 0, TAU)
        c.fill()
    c.restore()


def fases():
    s, c = sheet(W / 2, 950)
    dust(c, 700, 3)
    n = 13
    cx, cy, R = W / 2, 1500, 1160  # a wide arc over the bottom of the screen
    ring(c, cx, cy, R, BRASS, 0.35)
    limb(c, cx, cy, R + 74, a=0.38, step=1)
    names = {0: "Nueva", 3: "Cuarto creciente", 6: "Llena", 9: "Cuarto menguante", 12: "Nueva"}
    for i in range(n):
        t = -math.pi / 2 + math.radians((i - 6) * 7.2)
        x, y = cx + R * math.cos(t), cy + R * math.sin(t)
        moon_disc(c, x, y, 54, i / 12, i)
        if i in names:
            text(c, x, y + 92, names[i], 15, MUTED, 1, "Alegreya", cairo.FONT_SLANT_ITALIC)
    plate(c, "III", "Las fases de la Luna", "Mes sinódico de 29,53 días")
    finish(s, "c-fases.jpg")


def orrery():
    s, c = sheet(460, H / 2)
    dust(c, 700, 4)
    cx, cy = 460, H / 2
    d = 9720.2  # days from J2000 to 12 Aug 2026
    planets = [("Mercurio", 252.25, 4.0923344, 4), ("Venus", 181.98, 1.6021302, 6), ("Tierra", 100.46, 0.9856474, 6.5), ("Marte", 355.45, 0.5240208, 5),
               ("Júpiter", 34.40, 0.0830853, 13), ("Saturno", 49.94, 0.0334443, 11), ("Urano", 313.23, 0.0117281, 8), ("Neptuno", 304.88, 0.0059810, 8)]
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, 150)
    g.add_color_stop_rgba(0, *rgb(GOLD, 0.65))
    g.add_color_stop_rgba(0.14, *rgb(BRASS, 0.3))
    g.add_color_stop_rgba(1, *rgb(BRASS, 0))
    c.set_source(g)
    c.arc(cx, cy, 150, 0, TAU)
    c.fill()
    c.set_source_rgba(*rgb(GOLD, 0.95))
    c.arc(cx, cy, 15, 0, TAU)
    c.fill()
    for i, (name, l0, rate, size) in enumerate(planets):
        r = 110 + i * 136
        ring(c, cx, cy, r, BRASS if i % 4 == 3 else LINE, 0.5 if i % 4 == 3 else 1)
        t = -math.radians((l0 + rate * d) % 360)
        x, y = cx + r * math.cos(t), cy + r * math.sin(t)
        if name == "Saturno":
            c.save(); c.translate(x, y); c.rotate(-0.4); c.scale(1, 0.32)
            ring(c, 0, 0, size + 9, PARCH, 0.75, 2)
            c.restore()
        c.set_source_rgba(*rgb(PARCH if name != "Marte" else (0xc9, 0x86, 0x6c), 0.92))
        c.arc(x, y, size, 0, TAU)
        c.fill()
        if name == "Tierra":
            ring(c, x, y, 17, MUTED, 0.8)
            c.set_source_rgba(*rgb(PARCH, 0.9))
            c.arc(x + 17 * math.cos(t + math.pi), y + 17 * math.sin(t + math.pi), 2.2, 0, TAU)
            c.fill()
        text(c, x, y + size + 22, name, 15, MUTED, 1, "Alegreya", cairo.FONT_SLANT_ITALIC)
    limb(c, cx, cy, 1090, a=0.3)
    plate(c, "IV", "Sistema del mundo", "Posiciones del 12 de agosto de 2026; distancias sin escala")
    finish(s, "d-sistema.jpg")


def constelacion(fname, number, title, sub, lines, centre, scale, labels, extras=()):
    s, c = sheet()
    dust(c, 1000, len(fname))
    ra0, dec0 = centre
    cosd = math.cos(math.radians(dec0))
    pos = lambda st: (W / 2 + 130 - (S[st][0] - ra0) * 15 * cosd * scale, H / 2 - (S[st][1] - dec0) * scale)
    c.set_line_width(1)
    c.set_source_rgba(*rgb(LINE, 0.6))
    for i in range(-8, 9):  # right-ascension and declination grid every 5 degrees
        c.move_to(W / 2 + 130 + i * 5 * scale * cosd * 2, 0); c.line_to(W / 2 + 130 + i * 5 * scale * cosd * 2, H)
        c.move_to(0, H / 2 + i * 5 * scale); c.line_to(W, H / 2 + i * 5 * scale)
    c.stroke()
    c.set_line_width(1.2)
    c.set_source_rgba(*rgb(BRASS, 0.55))
    for a, b in lines:
        ax, ay, bx, by = *pos(a), *pos(b)
        d = math.hypot(bx - ax, by - ay) or 1
        ux, uy = (bx - ax) / d, (by - ay) / d
        c.move_to(ax + ux * 11, ay + uy * 11)  # lines stop short of the stars, as in old atlases
        c.line_to(bx - ux * 11, by - uy * 11)
    c.stroke()
    for st in {n for ln in lines for n in ln} | set(extras):
        star(c, *pos(st), S[st][2])
    for st, (label, dx, dy, big) in labels.items():
        x, y = pos(st)
        text(c, x + dx, y + dy, label, 20 if big else 15, BRASS if big else MUTED, 0.95 if big else 1, "Alegreya", cairo.FONT_SLANT_ITALIC, anchor=0 if dx >= 0 else 1)
    plate(c, number, title, sub)
    finish(s, fname)


def eclipse():
    s, c = sheet()
    dust(c, 900, 6)
    finish_a = np.ndarray((H, W, 4), np.uint8, s.get_data())
    cx, cy, R = W * 0.5, H * 0.46, 150
    y, x = np.mgrid[0:H, 0:W]
    dx, dy = x - cx, y - cy
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    rng = np.random.default_rng(12)
    streams = sum(rng.uniform(.25, 1) * np.cos(th * k + rng.uniform(0, TAU)) for k in rng.integers(3, 90, 46)) / 12
    length = 0.5 + 0.34 * np.clip(streams, -1, 1) + 0.36 * np.abs(np.cos(th))  # solar-minimum-ish: longer towards the equator
    corona = np.exp(-(r - R) / (R * length * 1.15)) * (r > R)
    corona = np.clip(corona * 0.5, 0, 1)[:, :, None]  # dim: it has to sit behind windows
    base = finish_a[:, :, :3].astype(float)
    tint = np.array(PARCH[::-1], float)
    out = base * (1 - corona) + tint * corona
    finish_a[:, :, :3] = np.clip(out, 0, 255).astype(np.uint8)
    s.mark_dirty()
    c.set_source_rgb(*rgb(INK)[:3])
    c.arc(cx, cy, R, 0, TAU)
    c.fill()
    ring(c, cx, cy, R + 0.5, PARCH, 0.8, 1.5)
    # Baily's bead
    t = math.radians(-38)
    bx, by = cx + R * math.cos(t), cy + R * math.sin(t)
    g = cairo.RadialGradient(bx, by, 0, bx, by, 42)
    g.add_color_stop_rgba(0, *rgb(PARCH, 0.85))
    g.add_color_stop_rgba(0.2, *rgb(GOLD, 0.35))
    g.add_color_stop_rgba(1, *rgb(GOLD, 0))
    c.set_source(g)
    c.arc(bx, by, 42, 0, TAU)
    c.fill()
    limb(c, cx, cy, 520, a=0.28)
    plate(c, "V", "Eclipse total de Sol", "12 de agosto de 2026")
    finish(s, "e-eclipse.jpg")


def circumpolar():
    s, c = sheet(W * 0.55, 330)
    px, py = W * 0.55, 360  # the celestial pole
    r = random.Random(8)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(1500):
        rad = 18 + r.random() ** 0.7 * 1300
        a0 = r.uniform(0, TAU)
        m = r.random() ** 2.6
        col = r.choice((PARCH, PARCH, BRASS, GOLD, (0x8f, 0xab, 0xd0)))
        c.set_line_width(0.7 + 1.1 * m)
        c.set_source_rgba(*rgb(col, 0.10 + 0.5 * m))
        c.arc(px, py, rad, a0, a0 + 0.62)  # about 2 h 20 of exposure
        c.stroke()
    # the hill and the dome, cut out in ink
    c.move_to(0, H)
    pts = [(0, 1010), (240, 975), (520, 1000), (800, 1040), (1150, 1050), (1390, 1040), (1640, 1012), (1920, 1040)]
    c.line_to(*pts[0])
    for a, b in zip(pts, pts[1:]):
        mx = (a[0] + b[0]) / 2
        c.curve_to(mx, a[1], mx, b[1], *b)
    c.line_to(W, H)
    c.close_path()
    c.set_source_rgb(*rgb((8, 10, 15))[:3])
    c.fill()
    dx, dy, dr = 430, 930, 100  # base centre on the ridge
    c.rectangle(dx - dr - 6, dy, 2 * dr + 12, 100)
    c.fill()
    c.arc(dx, dy, dr, math.pi, 0)
    c.fill()
    c.save()
    c.translate(dx, dy)
    c.rotate(0.45)
    c.rectangle(-9, -dr - 2, 18, 58)  # the dome's slit, a little sky through it
    c.set_source_rgba(*rgb(BRASS, 0.5))
    c.fill()
    c.restore()
    plate(c, "VI", "Estrellas circumpolares", "Dos horas de exposición hacia el polo")
    finish(s, "f-circumpolar.jpg")


def arch():
    # on-curve points of the outline in icons/archlinux.svg (24 units), a few extra along the long edges
    P = [(11.39, .605), (8.635, 7.132), (11.558, 9.686), (8.306, 7.826), (4.15, 15.6), (0, 23.395), (9.021, 19.533), (8.853, 17.871), (9.75, 14.9), (11.54, 13.898),
         (13.3, 15.0), (14.018, 18.307), (13.872, 19.55), (22.786, 23.394), (20.857, 19.824), (16.924, 17.111), (20.061, 18.345), (15.75, 9.7)]
    P = [(x / 24, y / 24) for x, y in P]
    s, c = sheet()
    dust(c, 1000, 9)
    cx, cy, size = W / 2, H / 2 - 20, 720
    pts = [(cx + (x - .5) * size, cy + (y - .5) * size) for x, y in P]
    ring(c, cx, cy + 30, 480, LINE, 1)
    limb(c, cx, cy + 30, 480, a=0.45)
    c.set_line_width(1.2)
    c.set_source_rgba(*rgb(BRASS, 0.6))
    for a, b in zip(pts, pts[1:] + pts[:1]):
        d = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        c.move_to(a[0] + ux * 10, a[1] + uy * 10)
        c.line_to(b[0] - ux * 10, b[1] - uy * 10)
    c.stroke()
    mags = [0.2, 2.6, 3.4, 2.8, 3.2, 0.6, 2.4, 3.4, 3.2, 2.2, 3.2, 3.4, 2.4, 0.6, 3.2, 3.4, 2.8, 3.0]
    for p, m in zip(pts, mags):
        star(c, *p, m)
    text(c, pts[0][0] + 22, pts[0][1] + 6, "α Archis", 20, BRASS, 0.95, "Alegreya", cairo.FONT_SLANT_ITALIC, anchor=0)
    plate(c, "VII", "Arcus Linuxianus", "Constelación moderna, rolling release")
    finish(s, "g-arch.jpg")


if __name__ == "__main__":
    # cairo finds fonts through fontconfig: add fonts/ so this works whichever theme is active
    import tempfile
    conf = tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False)
    conf.write(f"<fontconfig><include>/etc/fonts/fonts.conf</include><dir>{FONTS}</dir></fontconfig>")
    conf.close()
    os.environ["FONTCONFIG_FILE"] = conf.name
    import numpy as np  # not at the top: instrumento.py imports this module and only needs the drawing helpers
    from PIL import Image

    planisferio()
    astrolabio()
    fases()
    orrery()
    constelacion("h-orion.jpg", "VIII", "Orión, el cazador", "Ascensión recta 5h 30m, declinación 0°", ORI, (5.55, 4.0), 31,
                 {"Betelgeuse": ("Betelgeuse", -20, 8, True), "Rigel": ("Rigel", 20, 8, True), "Bellatrix": ("Bellatrix", 18, 6, False), "Saiph": ("Saiph", 16, 8, False),
                  "Alnilam": ("Alnilam", -16, -6, False), "Alnitak": ("Alnitak", -16, 12, False), "Mintaka": ("Mintaka", 16, -4, False), "oriIota": ("La Espada", 16, 8, False),
                  "pi3": ("El Escudo", 16, 6, False), "oriNu": ("La Maza", -14, -6, False)})
    constelacion("i-osa-mayor.jpg", "IX", "La Osa Mayor", "Ascensión recta 11h, declinación +50°", UMA, (11.0, 50.0), 21,
                 {"Dubhe": ("Dubhe", 14, -12, True), "Merak": ("Merak", 16, 8, False), "Phecda": ("Phecda", 14, 22, False), "Megrez": ("Megrez", 0, -16, False),
                  "Alioth": ("Alioth", -14, -12, False), "Mizar": ("Mizar", -14, -12, False), "Alkaid": ("Alkaid", -16, 8, True)})
    eclipse()
    circumpolar()
    arch()
    Image.open(OUT / "a-planisferio.jpg").crop((360, 60, 1560, 1140)).resize((1000, 900), Image.LANCZOS) \
        .save(HERE.parent / "firefox/chrome/cielo.jpg", quality=80)
