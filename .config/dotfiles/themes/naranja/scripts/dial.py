#!/usr/bin/env python3
"""The tuning dial in the bar: the hours are the frequencies and the needle is the time of day."""
import json
import sys
from datetime import datetime

COLS = 72  # 3 columns per hour
NEEDLE = "#f28c28"


def scale():
    """Top row: 00 04 08... above their tick."""
    row = [" "] * (COLS + 2)
    for hour in range(0, 25, 4):
        row[hour * 3:hour * 3 + 2] = f"{hour:02d}"
    return "".join(row)


def ticks(minutes):
    needle = min(minutes * COLS // 1440, COLS)
    row = ["|" if i % 12 == 0 else "'" if i % 3 == 0 else "." for i in range(COLS + 1)]
    return "".join(row[:needle]) + f"<span color='{NEEDLE}' weight='bold'>|</span>" + "".join(row[needle + 1:])


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        assert ticks(0).startswith(f"<span color='{NEEDLE}'")
        assert ticks(1439).count("span") == 2 and ticks(720).split("<")[0].endswith(".")
        assert len(scale()) == COLS + 2 and scale().startswith("00")
        print("ok")
    else:
        now = datetime.now()
        print(json.dumps({"text": f"{scale()}\n{ticks(now.hour * 60 + now.minute)}", "tooltip": False}))
