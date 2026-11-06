#!/usr/bin/env python3
"""Generate the Nostromo wallpapers into rotation/ (hyprpaper cycles that folder). Run: python3 nostromo.py"""
import math
import subprocess
from pathlib import Path

import machines

W, H = 1920, 1200
BG_TOP, BG_BOTTOM = "#1a1814", "#121110"
GRID, LINE, MUTED, FAINT = "#2a2620", "#3d382d", "#857c69", "#4a4438"
STRIPES = ["#e0c36a", "#e9a23b", "#d9652b", "#c8553d"]  # yellow, amber, orange, red
STRIPE_W, STEP = 10, 17  # stripe thickness, distance between stripe centers
FONT = 'font-family="IBM Plex Mono" letter-spacing="3"'


def frame(art):
    """A flat warm ground and one drawing: no grid, marks or lettering."""
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        *(a for a in art if "<text" not in a),
        '</svg>',
    ])


def stripes():
    """Parallel stripes: horizontal from the left edge, then a 45 degree turn to the top edge."""
    corner_x, corner_y, bend = 1220, 860, math.tan(math.radians(22.5))
    art = []
    for i, color in enumerate(STRIPES):
        d = i * STEP
        cx, cy = corner_x + d * bend, corner_y + d
        art.append(f'<polyline points="-20,{cy:.1f} {cx:.1f},{cy:.1f} {cx + cy + 20:.1f},-20" fill="none" '
                   f'stroke="{color}" stroke-width="{STRIPE_W}" stroke-linejoin="miter"/>')
    return art


def scope():
    """Oscilloscope: graticule box with a decaying amber sine trace and stripes on the right."""
    x0, y0, w, h = 560, 330, 1000, 560
    art = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="none" stroke="{LINE}" stroke-width="2"/>']
    art += [f'<line x1="{x0 + w * i / 10}" y1="{y0}" x2="{x0 + w * i / 10}" y2="{y0 + h}" stroke="{GRID}"/>' for i in range(1, 10)]
    art += [f'<line x1="{x0}" y1="{y0 + h * i / 8}" x2="{x0 + w}" y2="{y0 + h * i / 8}" stroke="{GRID}"/>' for i in range(1, 8)]
    pts = " ".join(f"{x0 + t:.1f},{y0 + h / 2 - 200 * math.exp(-t / 450) * math.sin(t / 38):.1f}" for t in range(0, w + 1, 4))
    art += [f'<polyline points="{pts}" fill="none" stroke="{STRIPES[1]}" stroke-width="6" opacity="0.18"/>',
            f'<polyline points="{pts}" fill="none" stroke="{STRIPES[1]}" stroke-width="2"/>']
    for i, color in enumerate(STRIPES):
        x = W - 280 + i * STEP
        art.append(f'<line x1="{x}" y1="-20" x2="{x}" y2="{H - 150}" stroke="{color}" stroke-width="{STRIPE_W}"/>')
    return art


def radar():
    """Motion-tracker sweep: range rings, crosshair, a fading sweep wedge and a few blips."""
    cx, cy = W / 2, H / 2 + 20
    art = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE if r < 400 else MUTED}" stroke-width="{1.5 if r < 400 else 2}"/>'
           for r in (100, 200, 300, 400)]
    art += [f'<line x1="{cx - 420}" y1="{cy}" x2="{cx + 420}" y2="{cy}" stroke="{LINE}"/>',
            f'<line x1="{cx}" y1="{cy - 420}" x2="{cx}" y2="{cy + 420}" stroke="{LINE}"/>']
    for deg in range(0, 360, 10):
        a = math.radians(deg)
        art.append(f'<line x1="{cx + 400 * math.cos(a):.1f}" y1="{cy + 400 * math.sin(a):.1f}" '
                   f'x2="{cx + (414 if deg % 30 else 424) * math.cos(a):.1f}" y2="{cy + (414 if deg % 30 else 424) * math.sin(a):.1f}" stroke="{MUTED}" stroke-width="2"/>')
    for k in range(24):  # sweep: thin wedges fading out behind the leading edge at -40 deg
        a1, a2 = math.radians(-40 - k * 2.5), math.radians(-40 - (k + 1) * 2.5)
        art.append(f'<path d="M{cx},{cy} L{cx + 400 * math.cos(a1):.1f},{cy + 400 * math.sin(a1):.1f} '
                   f'A400,400 0 0 0 {cx + 400 * math.cos(a2):.1f},{cy + 400 * math.sin(a2):.1f} Z" fill="{STRIPES[1]}" opacity="{0.22 * (1 - k / 24):.3f}"/>')
    a = math.radians(-40)
    art.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + 400 * math.cos(a):.1f}" y2="{cy + 400 * math.sin(a):.1f}" stroke="{STRIPES[1]}" stroke-width="2.5"/>')
    for bx, by, color in [(150, -170, STRIPES[0]), (250, -60, STRIPES[2]), (-120, 230, STRIPES[3])]:
        art += [f'<circle cx="{cx + bx}" cy="{cy + by}" r="14" fill="{color}" opacity="0.25"/>',
                f'<circle cx="{cx + bx}" cy="{cy + by}" r="6" fill="{color}"/>']
    return art


def orbit():
    """Navigation plot: a planet with tilted orbits and a ship marker on the outer one."""
    cx, cy = W / 2 + 120, H / 2 + 40
    art = [f'<g transform="rotate(-18 {cx} {cy})">']
    for rx, ry, color, width in [(260, 90, LINE, 1.5), (430, 150, LINE, 1.5), (640, 225, MUTED, 2)]:
        art.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{"6 8" if rx == 430 else "none"}"/>')
    art += [f'<circle cx="{cx + 640 * math.cos(2.4):.1f}" cy="{cy + 225 * math.sin(2.4):.1f}" r="9" fill="{STRIPES[1]}"/>',
            f'<circle cx="{cx + 430 * math.cos(-0.5):.1f}" cy="{cy + 150 * math.sin(-0.5):.1f}" r="5" fill="{STRIPES[0]}"/>', '</g>']
    for i, color in enumerate(STRIPES):  # planet: concentric rings shrinking inward
        art.append(f'<circle cx="{cx}" cy="{cy}" r="{120 - i * 22}" fill="{color}"/>')
    art.append(f'<circle cx="{cx}" cy="{cy}" r="{120 - 4 * 22}" fill="{BG_BOTTOM}"/>')
    sx, sy = cx + 640 * math.cos(2.4), cy + 225 * math.sin(2.4)
    a = math.radians(-18)  # ship position after the group rotation, for its callout
    px, py = cx + (sx - cx) * math.cos(a) - (sy - cy) * math.sin(a), cy + (sx - cx) * math.sin(a) + (sy - cy) * math.cos(a)
    return art


out = Path(__file__).with_name("rotation")
out.mkdir(exist_ok=True)
for name, art in [("a-stripes", stripes()), ("c-scope", scope()), ("f-radar", radar()), ("h-orbit", orbit()),
                  *((n, f()) for n, f in machines.ALL)]:
    png = out / f"{name}.png"
    subprocess.run(["rsvg-convert", "-o", png], input=frame(art).encode(), check=True)
    print(png)
