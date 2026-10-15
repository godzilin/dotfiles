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
W, H, X0, Y0 = 32, 32, 3, 1  # skull drawn at 2x so it dominates; thin bones cross behind it, ends at the corners

skull = {(X0 + 2 * c + dx, Y0 + 2 * r + dy) for r, row in enumerate(SKULL) for c, ch in enumerate(row) if ch == "X"
         for dx in (0, 1) for dy in (0, 1)}
# a one-pixel gap around the skull so the bones read as going behind it
halo = {(x + dx, y + dy) for x, y in skull for dx in (-1, 0, 1) for dy in (-1, 0, 1)}


def near_segment(px, py, ax, ay, bx, by, r):
    t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
    return math.hypot(px - ax - t * (bx - ax), py - ay - t * (by - ay)) <= r


bones = set()
for (ax, ay), (bx, by) in [((1, 4), (W - 2, H - 2)), ((W - 2, 4), (1, H - 2))]:
    nx, ny = (by - ay), -(bx - ax)
    n = math.hypot(nx, ny)
    for x in range(W):
        for y in range(H):
            knobs = any(math.hypot(x - ex - s * 0.9 * nx / n, y - ey - s * 0.9 * ny / n) <= 1.1
                        for ex, ey in ((ax, ay), (bx, by)) for s in (-1, 1))
            if near_segment(x + 0.5, y + 0.5, ax + 0.5, ay + 0.5, bx + 0.5, by + 0.5, 0.6) or knobs:
                bones.add((x, y))
# nothing of the bones may show through the eyes, nose or teeth: hide them behind the skull's whole outline
solid = {(x, y) for y in range(H) for xs in [[x for x, yy in skull if yy == y]] if xs for x in range(min(xs), max(xs) + 1)}
bones -= halo | solid


def pixel(x, y):
    if (x, y) in skull:
        return 1 + min((y - Y0) * 4 // (2 * len(SKULL)), 3)  # stripe colours top to bottom
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
lines += ["", "$6       COMPUTAH · TYPE II"]
open("skull.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
