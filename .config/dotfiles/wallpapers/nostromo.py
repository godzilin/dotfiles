#!/usr/bin/env python3
"""Generate the Nostromo wallpapers into rotation/ (hyprpaper cycles that folder). Run: python3 nostromo.py"""
import math
import subprocess
from pathlib import Path

import skulls
from skulls import skull

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
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>',
        f'<pattern id="dots" width="48" height="48" patternUnits="userSpaceOnUse"><circle cx="24" cy="24" r="1.2" fill="{GRID}"/></pattern>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
        *art,
        *marks,
        skull(104, 96, 17, STRIPES[1], "none", 1.4),  # house mark
        f'<text x="124" y="104" {FONT} font-size="15" font-weight="600" fill="{MUTED}">THINKPAD P14S GEN 5</text>',
        f'<line x1="96" y1="122" x2="840" y2="122" stroke="{FAINT}" stroke-width="1"/>',
        f'<text x="96" y="146" {FONT} font-size="12" fill="{FAINT}">RYZEN 7 PRO 8840HS · RADEON 780M · 32 GB · 1 TB NVME · CACHYOS · HYPRLAND</text>',
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


def vu():
    """VU meter: arc scale with ticks, red zone at the top end, needle resting near 0 dB."""
    cx, cy, r = W / 2, 880, 520
    def at(deg, rad):  # point on the dial; 0 deg points straight up
        a = math.radians(deg - 90)
        return cx + rad * math.cos(a), cy + rad * math.sin(a)
    art = [f'<rect x="{cx - 640}" y="{cy - 640}" width="1280" height="760" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>']
    for i in range(21):
        deg = -50 + i * 5
        color = STRIPES[3] if deg > 25 else MUTED
        (x1, y1), (x2, y2) = at(deg, r), at(deg, r + (34 if i % 5 == 0 else 18))
        art.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{3 if i % 5 == 0 else 2}"/>')
    (ax, ay), (bx, by) = at(-50, r - 14), at(25, r - 14)
    (rx, ry) = at(50, r - 14)
    art += [f'<path d="M{ax:.1f},{ay:.1f} A{r - 14},{r - 14} 0 0 1 {bx:.1f},{by:.1f}" fill="none" stroke="{LINE}" stroke-width="2"/>',
            f'<path d="M{bx:.1f},{by:.1f} A{r - 14},{r - 14} 0 0 1 {rx:.1f},{ry:.1f}" fill="none" stroke="{STRIPES[3]}" stroke-width="6"/>']
    nx, ny = at(14, r + 20)
    art += [f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{STRIPES[1]}" stroke-width="3"/>',
            f'<circle cx="{cx}" cy="{cy}" r="16" fill="{STRIPES[1]}"/>',
            f'<text x="{cx}" y="{cy - 200}" {FONT} font-size="44" fill="{MUTED}" text-anchor="middle">VU</text>']
    for i, color in enumerate(STRIPES):
        y = cy + 60 + i * STEP
        art.append(f'<line x1="{cx - 640}" y1="{y}" x2="{cx + 640}" y2="{y}" stroke="{color}" stroke-width="{STRIPE_W}"/>')
    return art


def horizon():
    """Striped sun setting behind a perspective grid floor."""
    hy, cx, r = 760, W / 2, 300
    art = ['<clipPath id="sky"><rect width="1920" height="760"/></clipPath>', '<g clip-path="url(#sky)">']
    bands = [(STRIPES[0], 0), (STRIPES[1], 1), (STRIPES[2], 2), (STRIPES[3], 3)]
    for color, i in bands:  # sun cut into four bands with growing gaps, like the stripes
        top, bottom = hy - r + i * r / 4 + i * 6, hy - r + (i + 1) * r / 4
        art.append(f'<clipPath id="b{i}"><rect x="0" y="{top:.1f}" width="{W}" height="{bottom - top:.1f}"/></clipPath>'
                   f'<circle cx="{cx}" cy="{hy}" r="{r}" fill="{color}" clip-path="url(#b{i})"/>')
    art.append('</g>')
    art.append(f'<line x1="0" y1="{hy}" x2="{W}" y2="{hy}" stroke="{STRIPES[1]}" stroke-width="2"/>')
    art += [f'<line x1="{cx}" y1="{hy}" x2="{cx + k * 260}" y2="{H}" stroke="{LINE}" stroke-width="1.5"/>' for k in range(-12, 13)]
    art += [f'<line x1="0" y1="{hy + d:.1f}" x2="{W}" y2="{hy + d:.1f}" stroke="{LINE}" stroke-width="1.5"/>'
            for d in (440 * (0.62 ** n) for n in range(9))]
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


def spectrum():
    """Graphic equalizer: columns of segments, colored by height like the stripes."""
    cols, seg_w, seg_h, gap = 32, 34, 14, 6
    x0, base = (W - cols * (seg_w + gap)) / 2, 900
    art = []
    for c in range(cols):
        t = c / (cols - 1)
        level = int(4 + 18 * math.exp(-((t - 0.3) ** 2) / 0.05) + 7 * math.exp(-((t - 0.75) ** 2) / 0.01) + 3 * math.sin(c * 1.7) ** 2)
        for s in range(26):
            y = base - s * (seg_h + gap)
            color = (STRIPES[0] if s < 10 else STRIPES[1] if s < 17 else STRIPES[2] if s < 22 else STRIPES[3]) if s < level else GRID
            art.append(f'<rect x="{x0 + c * (seg_w + gap):.1f}" y="{y}" width="{seg_w}" height="{seg_h}" rx="2" fill="{color}"/>')
    art.append(f'<line x1="{x0 - 20}" y1="{base + seg_h + 16}" x2="{W - x0 + 20}" y2="{base + seg_h + 16}" stroke="{LINE}" stroke-width="2"/>')
    for i, hz in enumerate(["31", "63", "125", "250", "500", "1K", "2K", "4K", "8K", "16K"]):
        x = x0 + (i + 0.5) * (cols * (seg_w + gap)) / 10
        art.append(f'<text x="{x:.1f}" y="{base + 60}" {FONT} font-size="12" fill="{FAINT}" text-anchor="middle">{hz}</text>')
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
    art += [f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px - 60:.1f}" y2="{py + 90:.1f}" stroke="{MUTED}"/>',
            f'<text x="{px - 66:.1f}" y="{py + 110:.1f}" {FONT} font-size="12" fill="{MUTED}" text-anchor="end">USCSS · 180924609</text>']
    return art


out = Path(__file__).with_name("rotation")
out.mkdir(exist_ok=True)
for name, art, model, side in [("a-stripes", stripes(), "MOD. N-1200", "SIDE A"),
                               ("b-reels", reels(), "MOD. R-0090", "SIDE B"),
                               ("c-scope", scope(), "MOD. O-0440", "SIDE A"),
                               ("d-vu", vu(), "MOD. V-0020", "SIDE B"),
                               ("e-horizon", horizon(), "MOD. H-1979", "SIDE A"),
                               ("f-radar", radar(), "MOD. M-0426", "SIDE B"),
                               ("g-spectrum", spectrum(), "MOD. E-1016", "SIDE A"),
                               ("h-orbit", orbit(), "MOD. L-0426", "SIDE B"),
                               *((n, f(), m, sd) for n, f, m, sd in skulls.ALL)]:
    png = out / f"{name}.png"
    subprocess.run(["rsvg-convert", "-o", png], input=frame(art, model, side).encode(), check=True)
    print(png)
