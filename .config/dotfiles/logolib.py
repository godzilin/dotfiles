"""Shared by the themes' fastfetch/make_logo.py: paint big, shrink, pack into truecolor half blocks (one text cell holds
two pixels, foreground above and background below), for a "file-raw" logo. Needs rsvg-convert (librsvg), Pillow and numpy."""
import io
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

PX_W, PX_H = 9, 11  # screen size of one half-block pixel in alacritty: not square, so paint in screen proportions
ARCH_SVG = Path(__file__).parent / "themes/dorado/icons/archlinux.svg"


def size(cols, rows2, k=3):
    """Canvas that keeps circles round once shrunk to cols x rows2 half-block pixels."""
    return cols * PX_W * k, rows2 * PX_H * k


def arch(height):
    """The Arch logo as an L mask cropped to its shape, height pixels tall."""
    png = subprocess.run(["rsvg-convert", "-h", str(height * 2), str(ARCH_SVG)], capture_output=True, check=True).stdout
    a = Image.open(io.BytesIO(png)).convert("RGBA").split()[-1]
    a = a.crop(a.getbbox())
    return a.resize((round(a.width * height / a.height), height), Image.LANCZOS)


def blocks(img, cols, rows2, bg, cut=110, resample=Image.BOX):
    """Lines of ANSI half blocks. Pixels under alpha cut stay empty (the terminal shows through); soft edges above it are
    blended on bg, the terminal's background."""
    px = np.asarray(img.convert("RGBA").resize((cols, rows2), resample)).astype(float)
    alpha = px[:, :, 3:] / 255
    rgb = (px[:, :, :3] * alpha + np.array(bg, float) * (1 - alpha)).round().astype(int)
    on = px[:, :, 3] >= cut

    def cell(c, r):
        top, low = on[r, c], on[r + 1, c]
        fg = lambda p: "\x1b[38;2;%d;%d;%dm" % tuple(p)
        back = lambda p: "\x1b[48;2;%d;%d;%dm" % tuple(p)
        if top and low:
            return fg(rgb[r, c]) + back(rgb[r + 1, c]) + "▀\x1b[0m"
        if top:
            return fg(rgb[r, c]) + "▀\x1b[0m"
        if low:
            return fg(rgb[r + 1, c]) + "▄\x1b[0m"
        return " "

    return ["".join(cell(c, r) for c in range(cols)).rstrip() for r in range(0, rows2, 2)]


def write(path, lines):
    Path(path).write_text("\n".join(lines) + "\n")
