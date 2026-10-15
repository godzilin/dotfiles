#!/usr/bin/env python3
"""Generate the Nostromo wallpapers into rotation/ (hyprpaper cycles that folder). Run: python3 nostromo.py"""
import math
import subprocess
from pathlib import Path

W, H = 1920, 1200
BG_TOP, BG_BOTTOM = "#1a1814", "#121110"
GRID, LINE, MUTED, FAINT = "#2a2620", "#3d382d", "#857c69", "#4a4438"
STRIPES = ["#e0c36a", "#e9a23b", "#d9652b", "#c8553d"]  # yellow, amber, orange, red
STRIPE_W, STEP = 10, 17  # stripe thickness, distance between stripe centers
FONT = 'font-family="IBM Plex Mono" letter-spacing="3"'


def frame(art, model, side):
    """Shared background, corner marks and labels around one piece of art."""
    marks = [f'<path d="M{x-8},{y} h16 M{x},{y-8} v16" stroke="{FAINT}" stroke-width="1.5"/>'
             for x, y in [(64, 64), (W - 64, 64), (64, H - 64), (W - 64, H - 64)]]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>',
        f'<pattern id="dots" width="48" height="48" patternUnits="userSpaceOnUse"><circle cx="24" cy="24" r="1.2" fill="{GRID}"/></pattern>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
        *art,
        *marks,
        # One <text> with a tspan so the subtitle always starts after the name, whatever its length
        f'<text x="96" y="104" {FONT} font-size="15" font-weight="600" fill="{STRIPES[1]}">COMPUTAH'
        f'<tspan dx="28" font-weight="400" fill="{MUTED}">PERSONAL COMPUTING SYSTEM</tspan></text>',
        f'<line x1="96" y1="122" x2="620" y2="122" stroke="{FAINT}" stroke-width="1"/>',
        f'<text x="96" y="146" {FONT} font-size="12" fill="{FAINT}">HYPRLAND · ARCH/CACHYOS · LENOVO THINKPAD</text>',
        f'<text x="{W-96}" y="{H-92}" {FONT} font-size="12" fill="{FAINT}" text-anchor="end">{model} · {side} · TYPE II · 90 MIN</text>',
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


def reels():
    """Two tape reels in outline joined by the tape, stripes along the bottom label."""
    art, cy, r = [], 600, 190
    for cx in (W / 2 - 330, W / 2 + 330):
        art += [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="2"/>',
                f'<circle cx="{cx}" cy="{cy}" r="{r - 70}" fill="none" stroke="{GRID}" stroke-width="40"/>',
                f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{STRIPES[1]}" stroke-width="3"/>']
        art += [f'<line x1="{cx + 34 * math.cos(a):.1f}" y1="{cy + 34 * math.sin(a):.1f}" '
                f'x2="{cx + 52 * math.cos(a):.1f}" y2="{cy + 52 * math.sin(a):.1f}" stroke="{STRIPES[1]}" stroke-width="3"/>'
                for a in (math.radians(d) for d in (90, 210, 330))]
    art.append(f'<line x1="{W/2 - 330}" y1="{cy + r}" x2="{W/2 + 330}" y2="{cy + r}" stroke="{LINE}" stroke-width="2"/>')
    for i, color in enumerate(STRIPES):
        y = 900 + i * STEP
        art.append(f'<line x1="-20" y1="{y}" x2="{W + 20}" y2="{y}" stroke="{color}" stroke-width="{STRIPE_W}"/>')
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


out = Path(__file__).with_name("rotation")
out.mkdir(exist_ok=True)
for name, art, model, side in [("a-stripes", stripes(), "MOD. N-1200", "SIDE A"),
                               ("b-reels", reels(), "MOD. R-0090", "SIDE B"),
                               ("c-scope", scope(), "MOD. O-0440", "SIDE A")]:
    png = out / f"{name}.png"
    subprocess.run(["rsvg-convert", "-o", png], input=frame(art, model, side).encode(), check=True)
    print(png)
