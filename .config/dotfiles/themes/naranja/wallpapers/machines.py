"""Ten more wallpapers for nostromo.py: tape decks, scopes, disks and other machines. No skulls."""
import math
import random

W, H = 1920, 1200
BG, BG0 = "#1a1814", "#121110"
GRID, LINE, MUTED, FAINT, TEXT = "#2a2620", "#3d382d", "#857c69", "#4a4438", "#e8dfc8"
YELLOW, AMBER, ORANGE, RED = "#e0c36a", "#e9a23b", "#d9652b", "#c8553d"
STRIPES = [YELLOW, AMBER, ORANGE, RED]
FONT = 'font-family="IBM Plex Mono" letter-spacing="3"'


def label(x, y, text, size=13, fill=MUTED, anchor="start"):
    return f'<text x="{x:.1f}" y="{y:.1f}" {FONT} font-size="{size}" fill="{fill}" text-anchor="{anchor}">{text}</text>'


def contours():
    """Topographic map: wobbly contour rings round two peaks, one contour in amber."""
    art = []
    for (cx, cy, rings, seed) in ((1250, 560, 14, 1), (620, 760, 9, 2)):
        rnd = random.Random(seed)
        phases = [rnd.uniform(0, 2 * math.pi) for _ in range(3)]
        for k in range(1, rings + 1):
            r = k * 34
            pts = []
            for a in range(0, 361, 4):
                t = math.radians(a)
                wob = 1 + 0.12 * math.sin(3 * t + phases[0]) + 0.07 * math.sin(5 * t + phases[1] + k * 0.2)
                pts.append(f"{cx + r * wob * math.cos(t) * 1.3:.1f},{cy + r * wob * math.sin(t):.1f}")
            color, width = (AMBER, 2) if (seed, k) == (1, 6) else (LINE, 1.3)
            art.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{width}"/>')
    art += [f'<circle cx="1250" cy="560" r="5" fill="{AMBER}"/>', label(1266, 552, "▲ 1 482 M", 13, TEXT),
            label(636, 752, "▲ 905 M", 13, MUTED)]
    return art


def lissajous():
    """Lissajous figure 3:2 on a round scope tube."""
    cx, cy, r = W / 2, H / 2 + 20, 330
    art = [f'<circle cx="{cx}" cy="{cy}" r="{r + 40}" fill="{BG0}" stroke="{LINE}" stroke-width="3"/>']
    art += [f'<line x1="{cx - r}" y1="{cy + k * r / 4}" x2="{cx + r}" y2="{cy + k * r / 4}" stroke="{GRID}"/>' for k in range(-3, 4)]
    art += [f'<line x1="{cx + k * r / 4}" y1="{cy - r}" x2="{cx + k * r / 4}" y2="{cy + r}" stroke="{GRID}"/>' for k in range(-3, 4)]
    pts = " ".join(f"{cx + 270 * math.sin(3 * t + math.pi / 4):.1f},{cy + 270 * math.sin(2 * t):.1f}"
                   for t in (i * 2 * math.pi / 720 for i in range(721)))
    art += [f'<polyline points="{pts}" fill="none" stroke="{AMBER}" stroke-width="8" opacity="0.12"/>',
            f'<polyline points="{pts}" fill="none" stroke="{AMBER}" stroke-width="2"/>',
            label(cx - r - 40, cy + r + 90, "X · 3 HZ", 13, MUTED), label(cx + r + 40, cy + r + 90, "Y · 2 HZ", 13, MUTED, "end")]
    return art


def circuit():
    """Circuit board traces running between pads, with one chip in the middle."""
    rnd = random.Random(11)
    art = []
    chip_x, chip_y, cw, ch = 860, 480, 200, 240
    for i in range(10):
        for side in (-1, 1):
            y = chip_y + 20 + i * 22
            x = chip_x if side < 0 else chip_x + cw
            path = f"M{x},{y} h{side * 40}"
            dx = side * rnd.randint(80, 360)
            dy = rnd.choice((-1, 1)) * rnd.randint(30, 260)
            path += f" l{side * abs(dy)},{dy} h{dx}"
            color = AMBER if (i, side) in ((3, 1), (7, -1)) else LINE
            art.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>')
            ex = x + side * 40 + side * abs(dy) + dx
            art.append(f'<circle cx="{ex}" cy="{y + dy}" r="7" fill="{BG0}" stroke="{color}" stroke-width="3"/>')
    art += [f'<rect x="{chip_x}" y="{chip_y}" width="{cw}" height="{ch}" rx="6" fill="{BG0}" stroke="{MUTED}" stroke-width="2"/>',
            label(chip_x + cw / 2, chip_y + ch / 2 - 6, "MOS", 18, TEXT, "middle"),
            label(chip_x + cw / 2, chip_y + ch / 2 + 20, "6502", 14, MUTED, "middle")]
    return art


def telemetry():
    """Flight telemetry: three traces on a shared time axis, readouts on the right."""
    x0, y0, w = 220, 300, 1300
    rnd = random.Random(5)
    art = []
    for row, (name, color, unit) in enumerate((("ALT", AMBER, "KM"), ("VEL", ORANGE, "M/S"), ("TEMP", YELLOW, "°C"))):
        top = y0 + row * 210
        art += [f'<line x1="{x0}" y1="{top + 160}" x2="{x0 + w}" y2="{top + 160}" stroke="{LINE}"/>',
                label(x0, top + 10, name, 13, MUTED)]
        v, pts = 0.5, []
        for i in range(0, w + 1, 10):
            v = min(max(v + rnd.uniform(-0.06, 0.07) + (0.004 if row == 0 else 0), 0.05), 0.95)
            pts.append(f"{x0 + i},{top + 160 - v * 130:.1f}")
        art.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2"/>')
        art.append(label(x0 + w + 40, top + 100, f"{v * 100:05.1f}", 34, TEXT))
        art.append(label(x0 + w + 40, top + 128, unit, 12, FAINT))
    art += [label(x0 + i * w / 6, y0 + 3 * 210 - 20, f"T+{i * 10:02d}", 11, FAINT) for i in range(7)]
    return art


def constellation():
    """Star chart: faint field, one constellation joined up and named."""
    rnd = random.Random(9)
    art = [f'<circle cx="{rnd.uniform(100, W - 100):.0f}" cy="{rnd.uniform(200, H - 100):.0f}" r="{rnd.choice((1, 1, 1.5, 2))}" fill="{FAINT}"/>'
           for _ in range(260)]
    stars = [(700, 420), (840, 380), (980, 450), (1120, 400), (1240, 520), (1180, 680), (1020, 720), (960, 580)]
    art.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in stars)} {stars[2][0]},{stars[2][1]}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    for i, (x, y) in enumerate(stars):
        r = 7 if i in (1, 4) else 4.5
        art += [f'<circle cx="{x}" cy="{y}" r="{r + 8}" fill="{AMBER}" opacity="0.12"/>',
                f'<circle cx="{x}" cy="{y}" r="{r}" fill="{AMBER if i in (1, 4) else TEXT}"/>']
    art += [label(1262, 512, "ZETA II", 13, AMBER), label(700, 790, "ZETA RETICULI · 39 LY", 13, MUTED)]
    return art


ALL = [("n03-contours", contours, "MOD. T-1482", "SIDE A"),
       ("n06-lissajous", lissajous, "MOD. X-0032", "SIDE B"),
       ("n08-circuit", circuit, "MOD. C-6502", "SIDE B"),
       ("n09-telemetry", telemetry, "MOD. M-0310", "SIDE A"),
       ("n10-constellation", constellation, "MOD. Z-0039", "SIDE B")]
