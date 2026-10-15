#!/usr/bin/env python3
"""Draw logo.txt for fastfetch: a red sun crossed by a black diagonal bar, in half-block characters.
$1 is red, $2 black (colours set in config.jsonc). Run: python3 make_logo.py"""
import math
from pathlib import Path

COLS, ROWS = 30, 15  # each row is two pixels tall
PX_H = ROWS * 2


def pixel(x, y):
    """0 paper, 1 red, 2 black (black overprints red)."""
    px, py = x + 0.5, y + 0.5
    # bar from bottom-left to top-right, 3.2 px thick
    ax, ay, bx, by = 1, PX_H - 3, COLS - 1, 3
    t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
    if math.hypot(px - (ax + t * (bx - ax)), py - (ay + t * (by - ay))) < 1.7:
        return 2
    if math.hypot(px - 12, py - 14) < 11.5:
        return 1
    if 22 <= px <= 28 and 22 <= py <= 25:  # a small black block, bottom right
        return 2
    return 0


lines = []
for r in range(ROWS):
    out, cur = "", None
    for c in range(COLS):
        top, bot = pixel(c, 2 * r), pixel(c, 2 * r + 1)
        if top == bot == 0:
            ch, col = " ", cur
        elif top and bot:
            ch, col = "█", max(top, bot) if top != bot else top
        elif top:
            ch, col = "▀", top
        else:
            ch, col = "▄", bot
        if col != cur and ch != " ":
            out += f"${col}"
            cur = col
        out += ch
    lines.append(out.rstrip())
Path(__file__).with_name("logo.txt").write_text("\n".join(lines) + "\n")
print("\n".join(l.replace("$1", "").replace("$2", "") for l in lines))
