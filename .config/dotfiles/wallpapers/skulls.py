"""Skull wallpapers for nostromo.py: the skull is the house mark, drawn here in ten cassette-futurism takes."""
import math

W, H = 1920, 1200
BG, BG0 = "#1a1814", "#121110"
GRID, LINE, MUTED, FAINT, TEXT = "#2a2620", "#3d382d", "#857c69", "#4a4438", "#e8dfc8"
YELLOW, AMBER, ORANGE, RED = "#e0c36a", "#e9a23b", "#d9652b", "#c8553d"
STRIPES = [YELLOW, AMBER, ORANGE, RED]
FONT = 'font-family="IBM Plex Mono" letter-spacing="3"'

# Vector skull, ~100 units wide, origin at the middle of the cranium
HEAD = ("M-46,10 A48,48 0 1 1 46,10 L46,30 Q46,40 36,42 L30,43 L30,62 Q30,66 26,66 "
        "L-26,66 Q-30,66 -30,62 L-30,43 L-36,42 Q-46,40 -46,30 Z")
NOSE = "M0,27 L-6,38 L6,38 Z"

# 13 x 14 pixel skull for the dot-matrix / pixel takes
PIXELS = """
....XXXXX....
..XXXXXXXXX..
.XXXXXXXXXXX.
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XX...XXX...XX
XX...XXX...XX
XX...XXX...XX
XXXXXX.XXXXXX
.XXXX...XXXX.
..XXXXXXXXX..
..X.X.X.X.X..
..XXXXXXXXX..
...XXXXXXX...
""".split()


def skull(cx, cy, size, stroke=AMBER, fill="none", width=2.0, eyes=None):
    """Outline (or filled) skull centred on (cx, cy), `size` px wide."""
    k = size / 100
    eyes = eyes or (BG0 if fill != "none" else "none")
    teeth = "".join(f"M{x},50 V66 " for x in (-15, -5, 5, 15))
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({k:.4f})" stroke="{stroke}" '
            f'stroke-width="{width / k:.3f}" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="{HEAD}" fill="{fill}"/>'
            f'<ellipse cx="-19" cy="12" rx="12" ry="11" fill="{eyes}"/>'
            f'<ellipse cx="19" cy="12" rx="12" ry="11" fill="{eyes}"/>'
            f'<path d="{NOSE}" fill="{eyes}"/>'
            f'<path d="M-30,50 H30 {teeth}" fill="none"/></g>')


def pixel_cells():
    return [(c, r) for r, row in enumerate(PIXELS) for c, ch in enumerate(row) if ch == "X"]


def stripes_h(y0, x1=-20, x2=W + 20):
    return [f'<line x1="{x1}" y1="{y0 + i * 17}" x2="{x2}" y2="{y0 + i * 17}" stroke="{c}" stroke-width="10"/>'
            for i, c in enumerate(STRIPES)]


def skull_stripes():
    """Big outline skull standing on the four tape stripes."""
    return [*stripes_h(820), skull(1280, 560, 520, AMBER, BG, 3)]


def skull_dots():
    """Dot-matrix skull: lit dots coloured in stripe bands, unlit dots faint."""
    cell, x0, y0 = 46, W / 2 - 13 * 46 / 2 + 23, 300
    lit = set(pixel_cells())
    art = []
    for r in range(14):
        color = STRIPES[min(r * 4 // 14, 3)]
        for c in range(13):
            x, y = x0 + c * cell, y0 + r * cell
            art.append(f'<circle cx="{x:.1f}" cy="{y}" r="{15 if (c, r) in lit else 3}" '
                       f'fill="{color if (c, r) in lit else LINE}"/>')
    return art


def skull_pixel():
    """Chunky pixel skull with an end-of-tape message."""
    cell, gap, x0, y0 = 38, 5, 1160, 300
    art = [f'<rect x="{x0 + c * cell}" y="{y0 + r * cell}" width="{cell - gap}" height="{cell - gap}" '
           f'fill="{STRIPES[min(c * 4 // 13, 3)]}"/>' for c, r in pixel_cells()]
    art += [f'<text x="{x0}" y="{y0 + 14 * cell + 70}" {FONT} font-size="28" font-weight="600" fill="{TEXT}">END OF SIDE A</text>',
            f'<text x="{x0}" y="{y0 + 14 * cell + 104}" {FONT} font-size="14" fill="{MUTED}">PLEASE TURN THE TAPE OVER ▮</text>']
    return art


def skull_blueprint():
    """Engineering drawing of the skull: construction lines, dimensions and callouts."""
    cx, cy, size = 960, 560, 500
    k = size / 100
    art = [f'<line x1="{cx}" y1="200" x2="{cx}" y2="980" stroke="{LINE}" stroke-dasharray="14 6 3 6"/>',
           f'<line x1="560" y1="{cy + 12 * k}" x2="1360" y2="{cy + 12 * k}" stroke="{LINE}" stroke-dasharray="14 6 3 6"/>',
           f'<circle cx="{cx}" cy="{cy - 10 * k}" r="{48 * k}" fill="none" stroke="{GRID}" stroke-width="2"/>',
           skull(cx, cy, size, AMBER, "none", 2)]
    # width dimension under the jaw, height dimension on the right
    yb, xr = cy + 66 * k + 60, cx + 46 * k + 70
    art += [f'<path d="M{cx - 46 * k},{yb} H{cx + 46 * k} M{cx - 46 * k},{yb - 10} v20 M{cx + 46 * k},{yb - 10} v20" stroke="{MUTED}"/>',
            f'<text x="{cx}" y="{yb + 28}" {FONT} font-size="13" fill="{MUTED}" text-anchor="middle">460</text>',
            f'<path d="M{xr},{cy - 58 * k} V{cy + 66 * k} M{xr - 10},{cy - 58 * k} h20 M{xr - 10},{cy + 66 * k} h20" stroke="{MUTED}"/>',
            f'<text x="{xr + 16}" y="{cy + 8 * k}" {FONT} font-size="13" fill="{MUTED}">620</text>']
    for (px, py), (tx, ty), label in [((-19, 12), (-150, -40), "ORB. L"), ((19, 12), (150, -40), "ORB. R"),
                                      ((0, 33), (-150, 45), "NASAL"), ((10, 58), (150, 70), "MAXILLA"),
                                      ((30, -40), (150, -80), "CRANIUM")]:
        x, y, lx, ly = cx + px * k, cy + py * k, cx + tx * 2.2, cy + ty * k  # labels sit just outside the skull
        anchor = "end" if tx < 0 else "start"
        art += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{AMBER}"/>',
                f'<polyline points="{x:.1f},{y:.1f} {lx:.1f},{ly:.1f} {lx + (-40 if tx < 0 else 40):.1f},{ly:.1f}" fill="none" stroke="{FAINT}"/>',
                f'<text x="{lx + (-48 if tx < 0 else 48):.1f}" y="{ly + 5:.1f}" {FONT} font-size="13" fill="{MUTED}" text-anchor="{anchor}">{label}</text>']
    return art


def skull_badge():
    """Round badge: crossbones, skull and MEMENTO MORI running round the rim."""
    cx, cy, r = 960, 600, 300
    bone = lambda a: (f'<g transform="rotate({a} {cx} {cy + 40})"><line x1="{cx - 260}" y1="{cy + 40}" x2="{cx + 260}" y2="{cy + 40}" '
                      f'stroke="{LINE}" stroke-width="22" stroke-linecap="round"/>'
                      + "".join(f'<circle cx="{cx + s * 262}" cy="{cy + 40 + d * 14}" r="18" fill="{LINE}"/>' for s in (-1, 1) for d in (-1, 1)) + '</g>')
    text = "MEMENTO MORI · COMPUTAH · TYPE II · " * 2  # letters spaced evenly round the circle
    return [f'<circle cx="{cx}" cy="{cy}" r="{r + 70}" fill="none" stroke="{LINE}" stroke-width="2"/>',
            f'<circle cx="{cx}" cy="{cy}" r="{r + 10}" fill="none" stroke="{FAINT}" stroke-width="1"/>',
            # rsvg has no textPath: place each letter round the rim by hand
            *(f'<text x="{cx}" y="{cy - r - 32}" font-family="IBM Plex Mono" font-size="18" fill="{MUTED}" text-anchor="middle" '
              f'transform="rotate({n * 360 / len(text):.2f} {cx} {cy})">{ch}</text>' for n, ch in enumerate(text)),
            bone(35), bone(-35), skull(cx, cy - 30, 300, AMBER, BG, 3)]


def skull_ecg():
    """Heart monitor: a few beats, then the line goes flat and ends in a skull."""
    x0, y0, w, h = 300, 360, 1320, 480
    art = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="none" stroke="{LINE}" stroke-width="2"/>']
    art += [f'<line x1="{x0 + i * w / 22:.1f}" y1="{y0}" x2="{x0 + i * w / 22:.1f}" y2="{y0 + h}" stroke="{GRID}"/>' for i in range(1, 22)]
    art += [f'<line x1="{x0}" y1="{y0 + i * h / 8}" x2="{x0 + w}" y2="{y0 + h * i / 8}" stroke="{GRID}"/>' for i in range(1, 8)]
    base = y0 + h / 2
    pts, x = [(x0, base)], x0
    for beat, amp in enumerate((1, 0.85, 0.6, 0.3)):  # fading beats
        x += 120
        pts += [(x, base), (x + 15, base - 25 * amp), (x + 30, base), (x + 42, base + 20 * amp),
                (x + 55, base - 170 * amp), (x + 70, base + 60 * amp), (x + 82, base), (x + 120, base - 30 * amp), (x + 150, base)]
        x += 150
    pts.append((x0 + w - 220, base))
    line = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return art + [f'<polyline points="{line}" fill="none" stroke="{AMBER}" stroke-width="7" opacity="0.15"/>',
                  f'<polyline points="{line}" fill="none" stroke="{AMBER}" stroke-width="2.5"/>',
                  skull(x0 + w - 140, base - 10, 120, RED, BG, 2.5),
                  f'<text x="{x0 + w - 24}" y="{y0 + 40}" {FONT} font-size="14" fill="{RED}" text-anchor="end">ASYSTOLE · 0 BPM</text>',
                  f'<text x="{x0 + 24}" y="{y0 + 40}" {FONT} font-size="14" fill="{MUTED}">CREW VITALS · KANE, G.</text>']


def skull_tape():
    """A cassette whose label is the skull, reels in the window below."""
    x0, y0, w, h = 560, 300, 800, 520
    art = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="28" fill="{BG}" stroke="{LINE}" stroke-width="3"/>',
           f'<rect x="{x0 + 50}" y="{y0 + 50}" width="{w - 100}" height="{h - 190}" rx="10" fill="{BG0}" stroke="{FAINT}" stroke-width="2"/>']
    art += [f'<rect x="{x0 + 50}" y="{y0 + 70 + i * 22}" width="{w - 100}" height="12" fill="{c}"/>' for i, c in enumerate(STRIPES)]
    art += [skull(x0 + w / 2, y0 + 230, 110, AMBER, BG0, 2.5),
            f'<text x="{x0 + 80}" y="{y0 + 205}" {FONT} font-size="20" font-weight="600" fill="{TEXT}">MEMENTO</text>',
            f'<text x="{x0 + w - 80}" y="{y0 + 205}" {FONT} font-size="20" font-weight="600" fill="{TEXT}" text-anchor="end">MORI</text>',
            f'<text x="{x0 + 80}" y="{y0 + 240}" {FONT} font-size="13" fill="{MUTED}">SIDE A</text>',
            f'<text x="{x0 + w - 80}" y="{y0 + 240}" {FONT} font-size="13" fill="{MUTED}" text-anchor="end">C-90</text>']
    wy = y0 + h - 95
    art.append(f'<rect x="{x0 + 220}" y="{wy - 40}" width="{w - 440}" height="80" rx="40" fill="none" stroke="{FAINT}" stroke-width="2"/>')
    for rx in (x0 + 290, x0 + w - 290):
        art += [f'<circle cx="{rx}" cy="{wy}" r="28" fill="none" stroke="{MUTED}" stroke-width="2"/>']
        art += [f'<line x1="{rx}" y1="{wy}" x2="{rx + 18 * math.cos(math.radians(a)):.1f}" y2="{wy + 18 * math.sin(math.radians(a)):.1f}" stroke="{MUTED}" stroke-width="3"/>'
                for a in (90, 210, 330)]
    art += [f'<circle cx="{x0 + cx}" cy="{y0 + h - 22}" r="7" fill="none" stroke="{FAINT}" stroke-width="2"/>' for cx in (120, w - 120)]
    return art


def skull_pattern():
    """Wallpaper-paper of small outline skulls; one of them is lit."""
    art = []
    for r in range(8):  # stops above the bottom label
        for c in range(15):
            x, y = 120 + c * 120 + (60 if r % 2 else 0), 240 + r * 110
            if (r, c) == (4, 9):
                art.append(skull(x, y, 56, AMBER, AMBER, 2, eyes=BG0))
            elif x < W - 60:
                art.append(skull(x, y, 56, LINE, "none", 1.5))
    return art


def skull_horizon():
    """The striped sun is a skull, setting behind the perspective grid."""
    hy, cx = 780, W / 2
    art = ['<clipPath id="sky"><rect width="1920" height="780"/></clipPath>', '<g clip-path="url(#sky)">']
    for i, color in enumerate(STRIPES):
        top = hy - 420 + i * 105 + i * 8
        art.append(f'<clipPath id="kb{i}"><rect x="0" y="{top}" width="{W}" height="{105 - 8}"/></clipPath>'
                   f'<g clip-path="url(#kb{i})">{skull(cx, hy - 250, 520, color, color, 1, eyes=BG)}</g>')
    art += ['</g>', f'<line x1="0" y1="{hy}" x2="{W}" y2="{hy}" stroke="{AMBER}" stroke-width="2"/>']
    art += [f'<line x1="{cx}" y1="{hy}" x2="{cx + k * 260}" y2="{H}" stroke="{LINE}" stroke-width="1.5"/>' for k in range(-12, 13)]
    art += [f'<line x1="0" y1="{hy + d:.1f}" x2="{W}" y2="{hy + d:.1f}" stroke="{LINE}" stroke-width="1.5"/>'
            for d in (420 * (0.62 ** n) for n in range(9))]
    return art


def skull_radar():
    """Motion tracker with one unknown contact, drawn as a skull."""
    cx, cy = W / 2, H / 2 + 20
    art = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE if r < 400 else MUTED}" stroke-width="{1.5 if r < 400 else 2}"/>'
           for r in (100, 200, 300, 400)]
    art += [f'<line x1="{cx - 420}" y1="{cy}" x2="{cx + 420}" y2="{cy}" stroke="{LINE}"/>',
            f'<line x1="{cx}" y1="{cy - 420}" x2="{cx}" y2="{cy + 420}" stroke="{LINE}"/>']
    for k in range(24):
        a1, a2 = math.radians(-60 - k * 2.5), math.radians(-60 - (k + 1) * 2.5)
        art.append(f'<path d="M{cx},{cy} L{cx + 400 * math.cos(a1):.1f},{cy + 400 * math.sin(a1):.1f} '
                   f'A400,400 0 0 0 {cx + 400 * math.cos(a2):.1f},{cy + 400 * math.sin(a2):.1f} Z" fill="{AMBER}" opacity="{0.2 * (1 - k / 24):.3f}"/>')
    sx, sy = cx + 190, cy - 230
    art += [f'<circle cx="{sx}" cy="{sy + 5}" r="46" fill="{RED}" opacity="0.15"/>', skull(sx, sy, 56, RED, BG, 2),
            f'<line x1="{sx + 40}" y1="{sy - 30}" x2="{sx + 120}" y2="{sy - 90}" stroke="{MUTED}"/>',
            f'<text x="{sx + 128}" y="{sy - 92}" {FONT} font-size="13" fill="{RED}">UNKNOWN LIFEFORM · 7 M</text>']
    return art


ALL = [("s01-skull-stripes", skull_stripes, "MOD. K-0001", "SIDE A"),
       ("s02-skull-dots", skull_dots, "MOD. K-0013", "SIDE B"),
       ("s03-skull-pixel", skull_pixel, "MOD. K-0008", "SIDE A"),
       ("s04-skull-blueprint", skull_blueprint, "MOD. K-0460", "SIDE B"),
       ("s05-skull-badge", skull_badge, "MOD. K-1979", "SIDE A"),
       ("s06-skull-ecg", skull_ecg, "MOD. K-0000", "SIDE B"),
       ("s07-skull-tape", skull_tape, "MOD. K-0090", "SIDE A"),
       ("s08-skull-pattern", skull_pattern, "MOD. K-0135", "SIDE B"),
       ("s09-skull-horizon", skull_horizon, "MOD. K-1984", "SIDE A"),
       ("s10-skull-radar", skull_radar, "MOD. K-0426", "SIDE B")]
