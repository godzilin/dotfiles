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


ALL = [("n06-lissajous", lissajous)]
