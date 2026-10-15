#!/usr/bin/env python3
"""Terminal intro: the skull logo scans in top to bottom like a CRT (~0.4 s), then the cursor
goes back up so fastfetch draws over it in the very same place."""
import json
import os
import re
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
conf = json.loads(re.sub(r"^\s*//.*$", "", open(os.path.join(here, "config.jsonc")).read(), flags=re.M))
colours = {k: f"\033[{v}m" for k, v in conf["logo"]["color"].items()}
pad = conf["logo"]["padding"]
lines = open(os.path.join(here, "skull.txt")).read().rstrip("\n").split("\n")

out = sys.stdout
out.write("\033[?25l" + "\n" * pad.get("top", 0))
for line in lines:
    # the scanline: draw the row bright cream first, then in its real colour
    plain = re.sub(r"\$\d", "", line)
    out.write(" " * pad.get("left", 0) + "\033[38;2;232;223;200m" + plain + "\r")
    out.flush()
    time.sleep(0.012)
    out.write(" " * pad.get("left", 0) + re.sub(r"\$(\d)", lambda m: colours.get(m.group(1), ""), line) + "\033[0m\n")
    out.flush()
    time.sleep(0.012)
out.write(f"\033[{len(lines) + pad.get('top', 0)}A\r\033[?25h")
out.flush()
