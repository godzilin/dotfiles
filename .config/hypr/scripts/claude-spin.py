#!/usr/bin/env python3
"""Modulo custom/claude de waybar: gira el asterisco de Claude mientras alguna sesion piensa."""
import json, os, sys, time
D = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "claude-estado")
F = "·✢✳✶✻✽✻✶✳✢"
MAX = 1200  # shortcut: una sesion muerta sin Stop deja de contar a los 20 min; un Bash mas largo sin otra llamada tambien


def activas():
    try:
        return sum(time.time() - e.stat().st_mtime < MAX for e in os.scandir(D))
    except FileNotFoundError:
        return 0


def sale(t, c, tip):
    print(json.dumps({"text": t, "class": c, "tooltip": tip}), flush=True)


i, prev = 0, None
while True:
    n = activas()
    if n:
        sale(F[i % len(F)], "pensando", f"Claude pensando ({n})"); i += 1; time.sleep(.13); prev = 1
    else:
        if prev != 0:
            sale("✻", "parado", "Claude en espera"); prev = 0
        time.sleep(.5)
