#!/usr/bin/env python3
"""Nostromo calendar popup (named calpopup.py so it does not shadow the stdlib calendar module) (opened from the waybar clock).
Month grid, year progress and upcoming events from khal (iCloud via vdirsyncer).
Keys: left/right or h/l change month, t today, q/Esc close.
Events come from a cache file so the popup opens instantly; khal refreshes it in the background."""
import calendar
import datetime as dt
import os
import select
import shutil
import subprocess
import sys
import termios
import threading
import tty

MONTHS = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
          "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
WEEKDAYS = ["LU", "MA", "MI", "JU", "VI", "SA", "DO"]
DAY_NAMES = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
def rgb(hex_color, text, bold=False):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"\033[{'1;' if bold else ''}38;2;{r};{g};{b}m{text}\033[0m"


AMBER, TEXT, SUB, MUTED, FAINT, LINE, RED = "#e9a23b", "#e8dfc8", "#b3a891", "#857c69", "#4a4438", "#3d382d", "#c8553d"
STRIPES = ["#e0c36a", "#e9a23b", "#d9652b", "#c8553d"]


CACHE = os.path.expanduser("~/.cache/calpopup.tsv")
EVENTS = []  # [(date, 'HH:MM' or '', title)] for roughly a year either side of today
KHAL_OK = True


def parse(text):
    found = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            try:
                found.append((dt.date.fromisoformat(parts[0]), parts[1], parts[2]))
            except ValueError:
                pass
    return found


def load_cache():
    global EVENTS
    try:
        with open(CACHE) as f:
            EVENTS = parse(f.read())
    except OSError:
        pass


def refresh(done):
    """Ask khal for two years of events (~1 s), update the cache, then signal a redraw."""
    global EVENTS, KHAL_OK
    start = dt.date.today().replace(day=1) - dt.timedelta(days=365)
    try:
        out = subprocess.run(
            ["khal", "list", "--day-format", "", "--format", "{start-date}\t{start-time}\t{title}",
             start.isoformat(), "760d"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        KHAL_OK = False
    else:
        KHAL_OK = out.returncode == 0
        if KHAL_OK:
            EVENTS = parse(out.stdout)
            os.makedirs(os.path.dirname(CACHE), exist_ok=True)
            with open(CACHE, "w") as f:
                f.write(out.stdout)
    done.set()


def render(year, month, today):
    width = max(shutil.get_terminal_size().columns - 4, 28)  # everything stretches to the window
    cell = width // 7
    width = cell * 7
    busy = {d for d, _, _ in EVENTS if d.year == year and d.month == month}
    out = []

    title = rgb(AMBER, "󰯇 " + MONTHS[month - 1], True) + rgb(SUB, f" {year}")
    info = f"SEM {today.isocalendar().week:02d} · DÍA {today.timetuple().tm_yday:03d}"
    out.append("  " + title + " " * (width - len(MONTHS[month - 1]) - 7 - len(info)) + rgb(MUTED, info))
    out.append("  " + "".join(rgb(c, "━" * (width // 4 + (i < width % 4))) for i, c in enumerate(STRIPES)))
    out.append("  " + "".join(rgb(MUTED if i < 5 else FAINT, w.rjust(cell - 2) + "  ") for i, w in enumerate(WEEKDAYS)))
    for week in calendar.Calendar(0).monthdatescalendar(year, month):
        cells = []
        for d in week:
            label = f"{d.day:2d}"
            if d.month != month:
                num = rgb("#2f2b23", label)
            elif d == today:
                num = f"\033[1;48;2;233;162;59;38;2;18;17;16m{label}\033[0m"
            else:
                num = rgb(TEXT if d.weekday() < 5 else MUTED, label)
            mark = rgb(AMBER, "·") if d in busy and d.month == month else " "
            cells.append(" " * (cell - 4) + num + mark + " ")
        out.append("  " + "".join(cells))
    out.append("")

    # Year progress
    year_len = 366 if calendar.isleap(today.year) else 365
    pct = today.timetuple().tm_yday / year_len
    bar = width - 10
    filled = round(pct * bar)
    out.append("  " + rgb(MUTED, "AÑO  ") + rgb(AMBER, "▮" * filled) + rgb(LINE, "▯" * (bar - filled)) + rgb(SUB, f"{pct:5.0%}"))
    out.append("")

    # Upcoming events (always from today, whatever month is shown)
    out.append("  " + rgb(MUTED, "PRÓXIMO") + rgb(LINE, " " + "─" * (width - 8)))
    upcoming = [e for e in EVENTS if today <= e[0] < today + dt.timedelta(days=14)]
    if upcoming:
        for d, time, name in upcoming[:4]:
            when = "HOY" if d == today else "MAÑ" if d == today + dt.timedelta(1) else f"{DAY_NAMES[d.weekday()]} {d.day:02d}"
            out.append("  " + rgb(AMBER if d == today else SUB, f"{when:<6}") + rgb(MUTED, f"{time or 'TODO':>5}  ") + rgb(TEXT, name[:width - 13]))
    elif KHAL_OK:
        out.append("  " + rgb(FAINT, "NADA EN 14 DÍAS"))
    else:
        out.append("  " + rgb(FAINT, "SIN CALENDARIO · ver README"))
    out.append("  " + rgb(FAINT, "← → MES   T HOY   ESC CERRAR"))
    return "\n".join(out)


def read_key():
    # os.read, not sys.stdin.read: Python's buffer would swallow the rest of an arrow-key sequence
    data = os.read(sys.stdin.fileno(), 8).decode(errors="ignore")
    return {"\x1b[D": "left", "\x1b[C": "right", "\x1b": "esc"}.get(data, data)


def main():
    today = dt.date.today()
    year, month = today.year, today.month
    old = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    sys.stdout.write("\033[?25l")  # hide cursor
    try:
        load_cache()
        refreshed = threading.Event()
        threading.Thread(target=refresh, args=(refreshed,), daemon=True).start()
        while True:
            sys.stdout.write("\033[H\033[2J" + render(year, month, today))
            sys.stdout.flush()
            # wait for a key, but redraw as soon as khal's fresh events arrive
            while not select.select([sys.stdin], [], [], 0.1)[0] and not refreshed.is_set():
                pass
            if refreshed.is_set():
                refreshed.clear()
                continue
            key = read_key()
            if key in ("q", "esc"):
                break
            if key in ("left", "h"):
                year, month = (year - 1, 12) if month == 1 else (year, month - 1)
            elif key in ("right", "l"):
                year, month = (year + 1, 1) if month == 12 else (year, month + 1)
            elif key == "t":
                year, month = today.year, today.month
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        sys.stdout.write("\033[?25h")


if __name__ == "__main__":
    if "--print" in sys.argv:  # non-interactive check
        refresh(threading.Event())
        print(render(dt.date.today().year, dt.date.today().month, dt.date.today()))
    else:
        main()
