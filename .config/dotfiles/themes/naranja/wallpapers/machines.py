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


def tape_deck():
    """Front panel of a cassette deck: tape window, twin VU meters and the transport keys."""
    x0, y0, w, h = 360, 330, 1200, 540
    art = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="{BG}" stroke="{LINE}" stroke-width="2"/>',
           f'<rect x="{x0 + 40}" y="{y0 + 40}" width="520" height="300" rx="10" fill="{BG0}" stroke="{FAINT}" stroke-width="2"/>']
    for cx in (x0 + 190, x0 + 410):  # reels seen through the window
        art += [f'<circle cx="{cx}" cy="{y0 + 190}" r="62" fill="none" stroke="{MUTED}" stroke-width="2"/>',
                f'<circle cx="{cx}" cy="{y0 + 190}" r="18" fill="none" stroke="{AMBER}" stroke-width="3"/>']
    for i, name in enumerate(("L", "R")):  # VU meters
        mx, my = x0 + 620 + i * 280, y0 + 40
        art += [f'<rect x="{mx}" y="{my}" width="250" height="150" rx="8" fill="{BG0}" stroke="{FAINT}" stroke-width="2"/>',
                f'<path d="M{mx + 30},{my + 110} A110,110 0 0 1 {mx + 220},{my + 110}" fill="none" stroke="{LINE}" stroke-width="2"/>',
                f'<path d="M{mx + 180},{my + 62} A110,110 0 0 1 {mx + 220},{my + 110}" fill="none" stroke="{RED}" stroke-width="4"/>']
        a = math.radians(-58 + i * 12)
        art += [f'<line x1="{mx + 125}" y1="{my + 140}" x2="{mx + 125 + 115 * math.sin(a):.1f}" y2="{my + 140 - 115 * math.cos(a):.1f}" stroke="{AMBER}" stroke-width="2"/>',
                label(mx + 125, my + 132, f"VU · {name}", 11, FAINT, "middle")]
    keys = ["REW", "PLAY", "FF", "STOP", "REC", "EJECT"]
    for i, key in enumerate(keys):
        kx = x0 + 620 + i * 90
        fill = AMBER if key == "PLAY" else BG0
        art += [f'<rect x="{kx}" y="{y0 + 230}" width="78" height="56" rx="6" fill="{fill}" stroke="{LINE}" stroke-width="2"/>',
                label(kx + 39, y0 + 310, key, 11, MUTED, "middle")]
    art += [label(x0 + 40, y0 + h - 60, "STEREO CASSETTE DECK", 16, TEXT),
            label(x0 + 40, y0 + h - 34, "DOLBY B NR · METAL · AUTO REVERSE", 11, FAINT)]
    art += [f'<rect x="{x0 + w - 360 + i * 82}" y="{y0 + h - 70}" width="70" height="8" fill="{c}"/>' for i, c in enumerate(STRIPES)]
    return art


def waveform():
    """A recorded take: mirrored waveform bars, louder in the middle, with a playhead."""
    rnd = random.Random(7)
    n, x0, cy = 150, 160, 600
    step = (W - 2 * x0) / n
    art = [f'<line x1="{x0}" y1="{cy}" x2="{W - x0}" y2="{cy}" stroke="{LINE}"/>']
    play = int(n * 0.62)
    for i in range(n):
        env = math.sin(math.pi * i / n) ** 0.8
        hgt = 20 + 260 * env * (0.35 + 0.65 * rnd.random())
        color = STRIPES[min(int(hgt / 75), 3)] if i < play else LINE
        art.append(f'<rect x="{x0 + i * step:.1f}" y="{cy - hgt / 2:.1f}" width="{step * 0.55:.1f}" height="{hgt:.1f}" rx="2" fill="{color}"/>')
    px = x0 + play * step - step * 0.2
    art += [f'<line x1="{px:.1f}" y1="{cy - 220}" x2="{px:.1f}" y2="{cy + 220}" stroke="{TEXT}" stroke-width="1.5"/>',
            label(px + 10, cy - 205, "02:47", 13, TEXT), label(W - x0, cy + 250, "04:31", 13, FAINT, "end"),
            label(x0, cy + 250, "TAKE 03 · 48 KHZ · 24 BIT", 13, FAINT)]
    return art


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


def sunburst():
    """Seventies sunburst: stripe-coloured rays fanning out of the bottom-right corner, kept short of the labels."""
    art, cx, cy, r = [], W, H, 1150
    for i in range(12):
        a1 = math.radians(-178 + i * 7.2)
        a2 = a1 + math.radians(3.4)
        color = STRIPES[i % 4] if 2 <= i <= 9 else LINE
        art.append(f'<path d="M{cx},{cy} L{cx + r * math.cos(a1):.1f},{cy + r * math.sin(a1):.1f} '
                   f'L{cx + r * math.cos(a2):.1f},{cy + r * math.sin(a2):.1f} Z" fill="{color}" opacity="0.8"/>')
    art.append(f'<circle cx="{cx}" cy="{cy}" r="360" fill="{BG0}" stroke="{LINE}" stroke-width="2"/>')
    return art


def punch_card():
    """An 80-column punch card with a few rows punched."""
    x0, y0, w, h = 300, 360, 1320, 560
    rnd = random.Random(3)
    art = [f'<path d="M{x0 + 40},{y0} H{x0 + w} V{y0 + h} H{x0} V{y0 + 40} Z" fill="{BG}" stroke="{LINE}" stroke-width="2"/>']
    cols, rows = 80, 12
    cw, rh = (w - 80) / cols, (h - 110) / rows
    for c in range(cols):
        holes = rnd.sample(range(rows), rnd.choice((0, 1, 1, 2, 3)))
        for r in range(rows):
            x, y = x0 + 40 + c * cw, y0 + 70 + r * rh
            if r in holes:
                art.append(f'<rect x="{x + cw * 0.2:.1f}" y="{y + rh * 0.15:.1f}" width="{cw * 0.6:.1f}" height="{rh * 0.65:.1f}" fill="{AMBER if c < 32 else BG0}"/>')
            elif c % 10 == 0:
                art.append(label(x + cw / 2, y + rh * 0.7, str((r + 2) % 10 if r > 1 else ""), 9, FAINT, "middle"))
    art += [label(x0 + 60, y0 + 44, "IBM 5081 · FORTRAN STATEMENT", 13, MUTED),
            label(x0 + w - 30, y0 + 44, "CARD 0042", 13, FAINT, "end")]
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


def floppy():
    """A 3.5-inch floppy disk, label written in marker."""
    x0, y0, s = 760, 300, 400
    k = s / 90
    art = [f'<path d="M{x0},{y0} H{x0 + 84 * k} L{x0 + 90 * k},{y0 + 6 * k} V{y0 + 94 * k} H{x0} Z" fill="{BG}" stroke="{LINE}" stroke-width="3"/>',
           f'<rect x="{x0 + 20 * k}" y="{y0}" width="{46 * k}" height="{30 * k}" fill="{FAINT}"/>',
           f'<rect x="{x0 + 50 * k}" y="{y0 + 4 * k}" width="{10 * k}" height="{22 * k}" fill="{BG0}"/>',
           f'<rect x="{x0 + 10 * k}" y="{y0 + 42 * k}" width="{70 * k}" height="{48 * k}" rx="4" fill="{TEXT}" opacity="0.92"/>']
    art += [f'<rect x="{x0 + 10 * k}" y="{y0 + 42 * k + i * 9}" width="{70 * k}" height="7" fill="{c}"/>' for i, c in enumerate(STRIPES)]
    art += [f'<text x="{x0 + 16 * k}" y="{y0 + 66 * k}" font-family="IBM Plex Mono" font-size="34" font-weight="600" fill="{BG0}">BACKUP</text>',
            f'<text x="{x0 + 16 * k}" y="{y0 + 78 * k}" font-family="IBM Plex Mono" font-size="20" fill="{FAINT}">DISK 2 OF 7 · 1.44 MB</text>',
            f'<rect x="{x0 + 4 * k}" y="{y0 + 86 * k}" width="{4 * k}" height="{4 * k}" fill="{BG0}"/>']
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


ALL = [("n01-tape-deck", tape_deck, "MOD. D-0600", "SIDE A"),
       ("n02-waveform", waveform, "MOD. W-0048", "SIDE B"),
       ("n03-contours", contours, "MOD. T-1482", "SIDE A"),
       ("n04-sunburst", sunburst, "MOD. S-1977", "SIDE B"),
       ("n05-punch-card", punch_card, "MOD. P-5081", "SIDE A"),
       ("n06-lissajous", lissajous, "MOD. X-0032", "SIDE B"),
       ("n07-floppy", floppy, "MOD. F-0144", "SIDE A"),
       ("n08-circuit", circuit, "MOD. C-6502", "SIDE B"),
       ("n09-telemetry", telemetry, "MOD. M-0310", "SIDE A"),
       ("n10-constellation", constellation, "MOD. Z-0039", "SIDE B")]
