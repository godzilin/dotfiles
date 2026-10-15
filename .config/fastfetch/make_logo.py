#!/usr/bin/env python3
"""Draw the fastfetch logo (skull and crossbones) into skull.txt. Run: python3 make_logo.py"""
import math

SKULL = """
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
W, H, X0, Y0 = 29, 24, 8, 0  # canvas and where the skull sits (bones cross under the jaw)

skull = {(X0 + c, Y0 + r) for r, row in enumerate(SKULL) for c, ch in enumerate(row) if ch == "X"}
# a one-pixel gap around the skull so the bones read as going behind it
halo = {(x + dx, y + dy) for x, y in skull for dx in (-1, 0, 1) for dy in (-1, 0, 1)}


def near_segment(px, py, ax, ay, bx, by, r):
    t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
    return math.hypot(px - ax - t * (bx - ax), py - ay - t * (by - ay)) <= r


bones = set()
for (ax, ay), (bx, by) in [((3, 11), (W - 4, H - 2)), ((W - 4, 11), (3, H - 2))]:
    nx, ny = (by - ay), -(bx - ax)
    n = math.hypot(nx, ny)
    for x in range(W):
        for y in range(H):
            knobs = any(math.hypot(x - ex - s * 1.3 * nx / n, y - ey - s * 1.3 * ny / n) <= 1.5
                        for ex, ey in ((ax, ay), (bx, by)) for s in (-1, 1))
            if near_segment(x + 0.5, y + 0.5, ax + 0.5, ay + 0.5, bx + 0.5, by + 0.5, 0.95) or knobs:
                bones.add((x, y))
bones -= halo


def pixel(x, y):
    if (x, y) in skull:
        return 1 + min((y - Y0) * 4 // len(SKULL), 3)  # stripe colours top to bottom
    return 5 if (x, y) in bones else 0


lines = []
for y in range(0, H, 2):
    out, colour = "", None
    for x in range(W):
        top, bot = pixel(x, y), pixel(x, y + 1)
        char = "█" if top and bot else "▀" if top else "▄" if bot else " "
        c = top or bot
        if c and c != colour:
            out += f"${c}"
            colour = c
        out += char
    lines.append(out.rstrip())
lines += ["", "$6     COMPUTAH · TYPE II"]
open("skull.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
