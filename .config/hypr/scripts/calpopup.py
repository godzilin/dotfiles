#!/usr/bin/env python3
"""Nostromo calendar popup (named calpopup.py so it does not shadow the stdlib calendar module) (opened from the waybar clock).
Month grid, year progress, moon phase and upcoming events from khal (iCloud via vdirsyncer).
Keys: left/right or h/l change month, t today, q/Esc close."""
import calendar
import datetime as dt
import math
import shutil
import subprocess
import sys
import termios
import tty

MONTHS = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
          "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
WEEKDAYS = ["LU", "MA", "MI", "JU", "VI", "SA", "DO"]
DAY_NAMES = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
MOON = [("●", "LUNA NUEVA"), ("◔", "CRECIENTE"), ("◑", "CUARTO CRECIENTE"), ("◕", "GIBOSA CRECIENTE"),
        ("○", "LUNA LLENA"), ("◕", "GIBOSA MENGUANTE"), ("◐", "CUARTO MENGUANTE"), ("◔", "MENGUANTE")]


def rgb(hex_color, text, bold=False):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"\033[{'1;' if bold else ''}38;2;{r};{g};{b}m{text}\033[0m"


AMBER, TEXT, SUB, MUTED, FAINT, LINE, RED = "#e9a23b", "#e8dfc8", "#b3a891", "#857c69", "#4a4438", "#3d382d", "#c8553d"
STRIPES = ["#e0c36a", "#e9a23b", "#d9652b", "#c8553d"]


def moon_phase(day):
    """Fraction of the synodic month since a known new moon (2000-01-06 18:14 UTC)."""
    days = (dt.datetime.combine(day, dt.time(12)) - dt.datetime(2000, 1, 6, 18, 14)).total_seconds() / 86400
    return (days % 29.530588853) / 29.530588853


def events(start, days):
    """[(date, 'HH:MM' or '', title)] from khal; empty if khal is not set up yet."""
    try:
        out = subprocess.run(
            ["khal", "list", "--day-format", "", "--format", "{start-date}\t{start-time}\t{title}",
             start.isoformat(), f"{days}d"], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    found = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            try:
                found.append((dt.date.fromisoformat(parts[0]), parts[1], parts[2]))
            except ValueError:
                pass
    return found


def render(year, month, today):
    first = dt.date(year, month, 1)
    month_events = events(first, calendar.monthrange(year, month)[1])
    busy = {d for d, _, _ in month_events}
    out = []

    out.append("  " + rgb(AMBER, MONTHS[month - 1], True) + rgb(SUB, f" {year}")
               + rgb(MUTED, f"   SEM {today.isocalendar().week:02d} · DÍA {today.timetuple().tm_yday:03d}".rjust(33 - len(MONTHS[month - 1]) - 5)))
    out.append("  " + "".join(rgb(c, "━" * 9) for c in STRIPES))
    out.append("")
    out.append("  " + "  ".join(rgb(MUTED if i < 5 else FAINT, w) for i, w in enumerate(WEEKDAYS)))
    for week in calendar.Calendar(0).monthdatescalendar(year, month):
        cells = []
        for d in week:
            label = f"{d.day:2d}"
            if d.month != month:
                cell = rgb("#2f2b23", label)
            elif d == today:
                cell = f"\033[1;48;2;233;162;59;38;2;18;17;16m{label}\033[0m"
            else:
                cell = rgb(TEXT if d.weekday() < 5 else MUTED, label)
            mark = rgb(AMBER, "·") if d in busy and d.month == month else " "
            cells.append(cell + mark)
        out.append("  " + " ".join(cells))
    out.append("")

    # Year progress and moon
    year_len = 366 if calendar.isleap(today.year) else 365
    pct = today.timetuple().tm_yday / year_len
    filled = round(pct * 24)
    out.append("  " + rgb(MUTED, "AÑO  ") + rgb(AMBER, "▮" * filled) + rgb(LINE, "▯" * (24 - filled)) + rgb(SUB, f" {pct:4.0%}"))
    phase = moon_phase(today)
    icon, name = MOON[int((phase * 8) + 0.5) % 8]
    lit = (1 - math.cos(2 * math.pi * phase)) / 2
    out.append("  " + rgb(MUTED, "LUNA ") + rgb(TEXT, icon) + rgb(SUB, f"  {name} · {lit:.0%}"))
    out.append("")

    # Upcoming events (always from today, whatever month is shown)
    out.append("  " + rgb(MUTED, "PRÓXIMO") + rgb(LINE, " " + "─" * 28))
    upcoming = events(today, 14)
    if upcoming:
        for d, time, title in upcoming[:6]:
            when = "HOY" if d == today else "MAÑ" if d == today + dt.timedelta(1) else f"{DAY_NAMES[d.weekday()]} {d.day:02d}"
            out.append("  " + rgb(AMBER if d == today else SUB, f"{when:<6}") + rgb(MUTED, f"{time or 'TODO':>5}  ") + rgb(TEXT, title[:22]))
    elif shutil.which("khal") and subprocess.run(["khal", "printcalendars"], capture_output=True).stdout.strip():
        out.append("  " + rgb(FAINT, "NADA EN 14 DÍAS"))
    else:
        out.append("  " + rgb(FAINT, "SIN CALENDARIO · ver README"))
    out.append("")
    out.append("  " + rgb(FAINT, "← → MES   T HOY   ESC CERRAR"))
    return "\n".join(out)


def read_key():
    ch = sys.stdin.read(1)
    if ch == "\033":
        seq = sys.stdin.read(2) if select_ready() else ""
        return {"[D": "left", "[C": "right"}.get(seq, "esc")
    return ch


def select_ready():
    import select
    return bool(select.select([sys.stdin], [], [], 0.05)[0])


def main():
    today = dt.date.today()
    year, month = today.year, today.month
    old = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    sys.stdout.write("\033[?25l")  # hide cursor
    try:
        while True:
            sys.stdout.write("\033[H\033[2J" + render(year, month, today))
            sys.stdout.flush()
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
        print(render(dt.date.today().year, dt.date.today().month, dt.date.today()))
    else:
        main()
