#!/usr/bin/env python3
"""Write logo.txt: a 3270 display on its stand, drawn only with text, as that terminal could. The Arch logo fills the screen
in shade characters, dimmer towards the foot as if the phosphor were still fading. $1 frame, $2 bright, $3 dim (config.jsonc).
Run: python3 make_logo.py"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import logolib as L  # noqa: E402

IN_W, IN_H = 36, 13
m = L.arch(IN_H * 20)
m = np.asarray(m.resize((int(IN_H * 2.45), IN_H), Image.BOX), float) / 255
left = (IN_W - m.shape[1]) // 2
rows = []
for y in range(IN_H):
    fade = 1 - 0.55 * y / IN_H
    line = ""
    for x in range(IN_W):
        v = m[y, x - left] * fade if 0 <= x - left < m.shape[1] else 0
        line += " " if v < 0.12 else "$3░" if v < 0.3 else "$3▒" if v < 0.5 else "$2▓" if v < 0.72 else "$2█"
    rows.append(line)
out = ["$1┌" + "─" * (IN_W + 2) + "┐",
       "$1│ $2ARCH LINUX" + " " * (IN_W - 15) + "READY $1│"]
out += [f"$1│ {r} $1│" for r in rows]
out += ["$1│ $2> fastfetch_" + " " * (IN_W - 12) + " $1│",
        "$1└" + "─" * ((IN_W + 2) // 2 - 1) + "┬┬" + "─" * ((IN_W + 2) // 2 - 1) + "┘",
        " " * ((IN_W + 4) // 2 - 7) + "$1═══════╧╧═══════"]
(HERE / "logo.txt").write_text("\n".join(out) + "\n")
