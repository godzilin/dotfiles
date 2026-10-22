#!/usr/bin/env python3
"""Generate the Fósforo wallpapers into rotation/ (hyprpaper cycles that folder). Run: python3 fosforo.py
Green phosphor on black: every piece glows (blurred copy under the sharp one) and sits under CRT scanlines."""
import math
import random
import subprocess
from pathlib import Path

W, H = 1920, 1200
PHOS, TEXT, MUTED, LINE, FAINT = "#33ff4d", "#a6ffad", "#3f9147", "#1a3a1d", "#0b170b"
FONT = 'font-family="&apos;3270 Nerd Font Mono&apos;"'  # quoted: a family starting with a digit is not a CSS identifier


def screen(art, status):
    """Black screen, glow filter, scanlines, a status line at the bottom like the 3270 operator area."""
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<defs>',
        '<filter id="glow" x="-10%" y="-10%" width="120%" height="120%">'
        '<feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect y="2" width="4" height="2" fill="#000" opacity="0.45"/></pattern>',
        '<radialGradient id="vignette"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.75"/></radialGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="#020402"/>',
        '<g filter="url(#glow)">', *art,
        f'<line x1="96" y1="{H - 120}" x2="{W - 96}" y2="{H - 120}" stroke="{LINE}" stroke-width="2"/>',
        f'<text x="96" y="{H - 86}" {FONT} font-size="22" fill="{MUTED}">{status}</text>',
        f'<text x="{W - 96}" y="{H - 86}" {FONT} font-size="22" fill="{MUTED}" text-anchor="end">THINKPAD P14S · CACHYOS · HYPRLAND</text>',
        '</g>',
        f'<rect width="{W}" height="{H}" fill="url(#scan)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>',
        '</svg>',
    ])


def ready():
    """An empty session: a header line and a big READY with the block cursor."""
    return [f'<text x="96" y="150" {FONT} font-size="26" fill="{MUTED}">SYSTEM FOSFORO  ·  SESSION 01  ·  LU 3279-S2B</text>',
            f'<text x="96" y="660" {FONT} font-size="260" fill="{PHOS}">READY█</text>']


def hexdump():
    """This script's own bytes as a hexdump, one row picked out in bright phosphor."""
    data, art = Path(__file__).read_bytes(), []
    for row in range(32):
        chunk = data[row * 16:(row + 1) * 16]
        hexes = " ".join(f"{b:02X}" for b in chunk)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        line = f"{row * 16:08X}  {hexes:<47}  |{text}|".replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        art.append(f'<text x="96" y="{150 + row * 29}" {FONT} font-size="30" xml:space="preserve" '
                   f'fill="{TEXT if row == 17 else MUTED}" opacity="{1 if row == 17 else 0.55}">{line}</text>')
    return art


def scope():
    """Oscilloscope graticule with a 3:4 Lissajous figure."""
    x0, y0, w, h = 460, 200, 1000, 760
    art = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{LINE}" stroke-width="2"/>']
    art += [f'<line x1="{x0 + w * i / 10}" y1="{y0}" x2="{x0 + w * i / 10}" y2="{y0 + h}" stroke="{FAINT}" stroke-width="2"/>' for i in range(1, 10)]
    art += [f'<line x1="{x0}" y1="{y0 + h * i / 8}" x2="{x0 + w}" y2="{y0 + h * i / 8}" stroke="{FAINT}" stroke-width="2"/>' for i in range(1, 8)]
    pts = " ".join(f"{x0 + w / 2 + 400 * math.sin(3 * t + math.pi / 2):.1f},{y0 + h / 2 + 300 * math.sin(4 * t):.1f}"
                   for t in (i * 2 * math.pi / 900 for i in range(901)))
    art.append(f'<polyline points="{pts}" fill="none" stroke="{PHOS}" stroke-width="3"/>')
    art.append(f'<text x="{x0}" y="{y0 - 24}" {FONT} font-size="22" fill="{MUTED}">CH1 2V/DIV   CH2 2V/DIV   X-Y</text>')
    return art


def radar():
    """PPI radar: range rings, a sweep fading behind the beam and a few contacts."""
    cx, cy, r = W / 2, 560, 440
    art = [f'<circle cx="{cx}" cy="{cy}" r="{r * k / 4}" fill="none" stroke="{LINE}" stroke-width="2"/>' for k in range(1, 5)]
    art += [f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(math.radians(a)):.1f}" y2="{cy + r * math.sin(math.radians(a)):.1f}" '
            f'stroke="{FAINT}" stroke-width="2"/>' for a in range(0, 360, 30)]
    beam = -60
    for i in range(40):  # trail: thin wedges getting dimmer away from the beam
        a1, a2 = math.radians(beam - i * 1.5), math.radians(beam - (i + 1) * 1.5)
        art.append(f'<path d="M{cx},{cy} L{cx + r * math.cos(a1):.1f},{cy + r * math.sin(a1):.1f} '
                   f'A{r},{r} 0 0 0 {cx + r * math.cos(a2):.1f},{cy + r * math.sin(a2):.1f} Z" fill="{PHOS}" opacity="{0.35 * (1 - i / 40):.3f}"/>')
    art.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(math.radians(beam)):.1f}" '
               f'y2="{cy + r * math.sin(math.radians(beam)):.1f}" stroke="{TEXT}" stroke-width="3"/>')
    for d, a, label in [(0.62, -75, "TGT 01"), (0.35, 40, "TGT 02"), (0.85, 160, "TGT 03"), (0.5, 230, "TGT 04")]:
        x, y = cx + r * d * math.cos(math.radians(a)), cy + r * d * math.sin(math.radians(a))
        art += [f'<rect x="{x - 6:.1f}" y="{y - 6:.1f}" width="12" height="12" fill="{TEXT}"/>',
                f'<text x="{x + 16:.1f}" y="{y + 7:.1f}" {FONT} font-size="20" fill="{MUTED}">{label}</text>']
    return art


def terrain():
    """Vector terrain like an old arcade: perspective floor and a wireframe mountain range."""
    hy, cx = 700, W / 2
    art = [f'<line x1="0" y1="{hy}" x2="{W}" y2="{hy}" stroke="{PHOS}" stroke-width="2"/>']
    art += [f'<line x1="{cx}" y1="{hy}" x2="{cx + k * 220}" y2="{H}" stroke="{LINE}" stroke-width="2"/>' for k in range(-14, 15)]
    art += [f'<line x1="0" y1="{hy + d:.1f}" x2="{W}" y2="{hy + d:.1f}" stroke="{LINE}" stroke-width="2"/>'
            for d in (500 * (0.6 ** n) for n in range(9))]
    rnd = random.Random(3270)
    x, pts = -20, []
    while x < W + 40:
        pts.append((x, hy - rnd.choice([40, 90, 160, 240, 330]) * (0.6 + 0.4 * math.sin(x / 300) ** 2)))
        x += rnd.randint(80, 180)
    art.append(f'<polyline points="{" ".join(f"{px:.0f},{py:.0f}" for px, py in pts)}" fill="none" stroke="{PHOS}" stroke-width="3"/>')
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):  # a ridge line down from each peak to the next valley
        art.append(f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{(ax + bx) / 2:.0f}" y2="{hy}" stroke="{MUTED}" stroke-width="2"/>')
    return art


out = Path(__file__).with_name("rotation")
out.mkdir(exist_ok=True)
for name, art, status in [("a-ready", ready(), "READY"), ("b-hexdump", hexdump(), "DUMP FOSFORO.PY"),
                          ("c-scope", scope(), "SCOPE  X-Y  3:4"), ("d-radar", radar(), "PPI  RANGE 40 NM"),
                          ("e-terrain", terrain(), "VECTOR  SECTOR 7")]:
    png = out / f"{name}.png"
    subprocess.run(["rsvg-convert", "-o", png], input=screen(art, status).encode(), check=True)
    print(png)
