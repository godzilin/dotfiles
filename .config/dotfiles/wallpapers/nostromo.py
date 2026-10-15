#!/usr/bin/env python3
"""Generate the Nostromo wallpaper: python3 nostromo.py && rsvg-convert nostromo.svg -o nostromo.png"""
import math
from pathlib import Path

W, H = 1920, 1200
BG_TOP, BG_BOTTOM = "#1a1814", "#121110"
GRID, MUTED, FAINT = "#2a2620", "#857c69", "#4a4438"
STRIPES = ["#e0c36a", "#e9a23b", "#d9652b", "#c8553d"]  # yellow, amber, orange, red

STRIPE_W, STEP = 10, 17           # stripe thickness, distance between stripe centers
CORNER_X, CORNER_Y = 1220, 860    # where the first stripe bends up at 45 degrees
BEND = math.tan(math.radians(22.5))

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs>',
    f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>',
    f'<pattern id="dots" width="48" height="48" patternUnits="userSpaceOnUse"><circle cx="24" cy="24" r="1.2" fill="{GRID}"/></pattern>',
    '</defs>',
    f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
    f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
]

# Parallel stripes: horizontal from the left edge, then a 45 degree turn to the top edge
for i, color in enumerate(STRIPES):
    d = i * STEP
    cx, cy = CORNER_X + d * BEND, CORNER_Y + d
    end_x = cx + cy + 20
    parts.append(
        f'<polyline points="-20,{cy:.1f} {cx:.1f},{cy:.1f} {end_x:.1f},-20" fill="none" '
        f'stroke="{color}" stroke-width="{STRIPE_W}" stroke-linejoin="miter"/>'
    )

# Corner registration marks
for x, y in [(64, 64), (W - 64, 64), (64, H - 64), (W - 64, H - 64)]:
    parts.append(f'<path d="M{x-8},{y} h16 M{x},{y-8} v16" stroke="{FAINT}" stroke-width="1.5"/>')

font = 'font-family="IBM Plex Mono" letter-spacing="3"'
parts += [
    f'<text x="96" y="104" {font} font-size="15" font-weight="600" fill="{STRIPES[1]}">COMPUTAH</text>',
    f'<text x="180" y="104" {font} font-size="15" fill="{MUTED}">PERSONAL COMPUTING SYSTEM</text>',
    f'<line x1="96" y1="122" x2="560" y2="122" stroke="{FAINT}" stroke-width="1"/>',
    f'<text x="96" y="146" {font} font-size="12" fill="{FAINT}">HYPRLAND · ARCH/CACHYOS · LENOVO THINKPAD</text>',
    f'<text x="{W-96}" y="{H-92}" {font} font-size="12" fill="{FAINT}" text-anchor="end">MOD. N-1200 · SIDE A · TYPE II · 90 MIN</text>',
    '</svg>',
]

out = Path(__file__).with_name("nostromo.svg")
out.write_text("\n".join(parts))
print(out)
