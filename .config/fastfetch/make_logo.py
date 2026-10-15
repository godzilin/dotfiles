#!/usr/bin/env python3
"""Draw the fastfetch logo into skull.txt from the same vector skull as the wallpapers.
The SVG is rasterised small and packed into half-block characters, so curves stay round. Run: python3 make_logo.py"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.expanduser("~/.config/dotfiles/wallpapers"))
from skulls import HEAD, NOSE  # noqa: E402

COLS, ROWS = 30, 26  # wide and short: same height as the info column
X0, Y0, UW, UH = -50, -60, 100, 128  # skull units shown

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{COLS * 8}" height="{ROWS * 8}" viewBox="{X0} {Y0} {UW} {UH}" preserveAspectRatio="none">'
       f'<rect x="{X0}" y="{Y0}" width="{UW}" height="{UH}" fill="black"/>'
       f'<path d="{HEAD}" fill="white"/>'
       '<ellipse cx="-19" cy="12" rx="13" ry="12" fill="black"/><ellipse cx="19" cy="12" rx="13" ry="12" fill="black"/>'
       f'<path d="{NOSE}" fill="black" transform="scale(1.3) translate(0,-6)"/>'
       + "".join(f'<path d="M{x},46 V64" stroke="black" stroke-width="3.2"/>' for x in (-15, -5, 5, 15))
       + '</svg>')
png = subprocess.run(["rsvg-convert"], input=svg.encode(), capture_output=True, check=True).stdout
# area-average down to the pixel grid, one grey byte per pixel
grey = subprocess.run(["magick", "png:-", "-colorspace", "gray", "-filter", "box", "-resize", f"{COLS}x{ROWS}!", "gray:-"],
                      input=png, capture_output=True, check=True).stdout
lit = [[grey[r * COLS + c] > 110 for c in range(COLS)] for r in range(ROWS)]

lines = []
for r in range(0, ROWS, 2):
    band = 1 + min(r * 4 // ROWS, 3)  # tape-stripe colours, top to bottom
    row = "".join("█" if a and b else "▀" if a else "▄" if b else " " for a, b in zip(lit[r], lit[r + 1]))
    if row.strip():
        lines.append(f"${band}{row.rstrip()}")
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "skull.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
