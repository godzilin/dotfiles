#!/usr/bin/env python3
"""Phase of the Moon for the "dorado" theme, by mean synodic month (good to about half a day, plenty for a bar).
  luna.py          waybar JSON: phase glyph (Nerd Font weather set), tooltip with the phase and the next full and new moon
  luna.py --texto  one line of plain text, for hyprlock
  luna.py --test   self-check against known new and full moons"""
import json
import math
import sys
from datetime import datetime, timedelta, timezone

SYNODIC = 29.530588853
EPOCH = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)  # a new moon
NAMES = ((0.033, "Luna nueva"), (0.217, "Luna creciente"), (0.283, "Cuarto creciente"), (0.467, "Gibosa creciente"), (0.533, "Luna llena"),
         (0.717, "Gibosa menguante"), (0.783, "Cuarto menguante"), (0.967, "Luna menguante"), (1.0, "Luna nueva"))


def age(when):
    """Fraction of the synodic month: 0 new, 0.5 full."""
    return ((when - EPOCH).total_seconds() / 86400 / SYNODIC) % 1


def illumination(a):
    return (1 - math.cos(a * 2 * math.pi)) / 2


def name(a):
    return next(n for limit, n in NAMES if a < limit)


def glyph(a):
    return chr(0xE38D + round(a * 28) % 28)  # nf-weather-moon_new ... moon_waning_crescent_6: 28 steps


def next_at(when, target):
    days = ((target - age(when)) % 1) * SYNODIC
    return when + timedelta(days=days)


def test():
    for y, m, d, h, want in ((2026, 8, 12, 17, 0.0), (2026, 11, 9, 7, 0.0), (2025, 3, 14, 6, 0.5), (2026, 11, 24, 14, 0.5)):
        got = age(datetime(y, m, d, h, tzinfo=timezone.utc))
        off = abs((got - want + 0.5) % 1 - 0.5) * SYNODIC
        assert off < 0.75, (y, m, d, off)
    assert name(0.0) == name(0.99) == "Luna nueva" and name(0.5) == "Luna llena" and name(0.25) == "Cuarto creciente"
    assert glyph(0.0) == chr(0xE38D) and glyph(0.5) == chr(0xE39B) and glyph(0.999) == chr(0xE38D)
    assert illumination(0.5) == 1 and illumination(0.0) == 0
    print("ok")


def main():
    if "--test" in sys.argv:
        return test()
    now = datetime.now(timezone.utc)
    a = age(now)
    pct = round(illumination(a) * 100)
    if "--texto" in sys.argv:
        return print(f"{name(a)}  ·  {pct} %")
    fmt = lambda d: d.astimezone().strftime("%d/%m")
    print(json.dumps({
        "text": glyph(a),
        "tooltip": f"{name(a)}, {pct} % iluminada\nLlena el {fmt(next_at(now, 0.5))}  ·  Nueva el {fmt(next_at(now, 0.0))}",
        "class": "llena" if 0.467 <= a < 0.533 else "nueva" if a < 0.033 or a >= 0.967 else "",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
