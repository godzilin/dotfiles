#!/usr/bin/env python3
"""Nostromo weather (Open-Meteo, no API key).
  weather.py bar    -> waybar JSON: icon + temperature (refreshes the cache when older than 10 min)
  weather.py popup  -> full view in the terminal popup (r refresh, Esc/q close)
Location: ~/.config/nostromo/weather.conf ("lat lon Name"), created from the IP on first run. Kept out of git."""
import datetime as dt
import json
import os
import shutil
import sys
import termios
import time
import tty
import urllib.parse
import urllib.request

CONF = os.path.expanduser("~/.config/nostromo/weather.conf")
CACHE = os.path.expanduser("~/.cache/nostromo/weather.json")
MAX_AGE = 600

AMBER, TEXT, SUB, MUTED, FAINT, LINE = "#e9a23b", "#e8dfc8", "#b3a891", "#857c69", "#4a4438", "#3d382d"
BLUE, YELLOW, ORANGE, RED = "#7b93a8", "#e0c36a", "#d9652b", "#c8553d"
STRIPES = [YELLOW, AMBER, ORANGE, RED]
DAYS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
COMPASS = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]

# WMO weather code -> (day icon, night icon, description)
SUN, MOON, PARTLY, PARTLY_N, CLOUD, FOG = "󰖙", "󰖔", "󰖕", "󰼱", "󰖐", "󰖑"
WMO = {0: (SUN, MOON, "DESPEJADO"), 1: (PARTLY, PARTLY_N, "POCO NUBOSO"), 2: (PARTLY, PARTLY_N, "PARCIALMENTE NUBOSO"),
       3: (CLOUD, CLOUD, "NUBLADO"), 45: (FOG, FOG, "NIEBLA"), 48: (FOG, FOG, "NIEBLA CON ESCARCHA")}
for c in (51, 53, 55, 56, 57):
    WMO[c] = ("󰖗", "󰖗", "LLOVIZNA")
for c in (61, 63, 66, 80, 81):
    WMO[c] = ("󰖗", "󰖗", "LLUVIA")
for c in (65, 67, 82):
    WMO[c] = ("󰖖", "󰖖", "LLUVIA FUERTE")
for c in (71, 73, 77, 85):
    WMO[c] = ("󰖘", "󰖘", "NIEVE")
for c in (75, 86):
    WMO[c] = ("󰼶", "󰼶", "NEVADA FUERTE")
WMO[95] = ("󰖓", "󰖓", "TORMENTA")
WMO[96] = WMO[99] = ("󰖒", "󰖒", "TORMENTA CON GRANIZO")


def wmo(code, day=True):
    icon_day, icon_night, desc = WMO.get(code, (CLOUD, CLOUD, "—"))
    return (icon_day if day else icon_night), desc


def location():
    try:
        lat, lon, name = open(CONF).read().split(maxsplit=2)
        return float(lat), float(lon), name.strip()
    except (OSError, ValueError):
        pass
    with urllib.request.urlopen("https://ipinfo.io/json", timeout=5) as r:
        info = json.load(r)
    lat, lon = info["loc"].split(",")
    os.makedirs(os.path.dirname(CONF), exist_ok=True)
    with open(CONF, "w") as f:
        f.write(f"{lat} {lon} {info.get('city', '')}\n")
    return float(lat), float(lon), info.get("city", "")


def fetch():
    lat, lon, name = location()
    query = urllib.parse.urlencode({
        "latitude": lat, "longitude": lon, "timezone": "auto", "wind_speed_unit": "kmh",
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,is_day,"
                   "wind_speed_10m,wind_direction_10m,wind_gusts_10m,pressure_msl,precipitation",
        "hourly": "temperature_2m,precipitation_probability,weather_code,is_day",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
                 "sunrise,sunset,uv_index_max",
        "forecast_days": 7, "forecast_hours": 13,
    })
    with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?{query}", timeout=10) as r:
        data = json.load(r)
    data["place"] = name
    data["fetched"] = time.time()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE + ".tmp", "w") as f:
        json.dump(data, f)
    os.replace(CACHE + ".tmp", CACHE)
    return data


def load(refresh=False):
    try:
        data = json.load(open(CACHE))
        if not refresh and time.time() - data.get("fetched", 0) < MAX_AGE:
            return data
    except (OSError, ValueError):
        data = None
    try:
        return fetch()
    except OSError:
        return data  # offline: keep showing the last forecast


def bar():
    data = load()
    if not data:
        print(json.dumps({"text": "󰖐 --°", "class": "offline", "tooltip": "Sin datos del tiempo"}))
        return
    cur = data["current"]
    icon, desc = wmo(cur["weather_code"], cur["is_day"])
    print(json.dumps({"text": f"{icon} {round(cur['temperature_2m'])}°",
                      "tooltip": f"{data['place']} · {desc.capitalize()}", "class": "ok"}))


def rgb(color, text, bold=False):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return f"\033[{'1;' if bold else ''}38;2;{r};{g};{b}m{text}\033[0m"


def temp_color(t):
    return BLUE if t < 8 else SUB if t < 16 else YELLOW if t < 24 else ORANGE if t < 31 else RED


def render(data):
    width = max(shutil.get_terminal_size().columns - 4, 36)
    if not data:
        return "\n  " + rgb(MUTED, "SIN DATOS · ¿HAY CONEXIÓN?")
    cur, daily, hourly = data["current"], data["daily"], data["hourly"]
    icon, desc = wmo(cur["weather_code"], cur["is_day"])
    updated = dt.datetime.fromtimestamp(data["fetched"]).strftime("%H:%M")
    out = []
    head = data["place"].upper()
    stamp = f"ACT {updated}"
    out.append("  " + rgb(AMBER, head, True) + " " * (width - len(head) - len(stamp)) + rgb(FAINT, stamp))
    out.append("  " + "".join(rgb(c, "━" * (width // 4 + (i < width % 4))) for i, c in enumerate(STRIPES)))
    t = round(cur["temperature_2m"])
    out.append("")
    out.append("  " + rgb(AMBER, icon) + "  " + rgb(temp_color(t), f"{t}°", True) + "  " + rgb(TEXT, desc))
    out.append("     " + rgb(MUTED, f"SENSACIÓN {round(cur['apparent_temperature'])}° · "
                                    f"MÁX {round(daily['temperature_2m_max'][0])}° · MÍN {round(daily['temperature_2m_min'][0])}°"))
    out.append("")

    wind_dir = COMPASS[round(cur["wind_direction_10m"] / 45) % 8]
    sunrise = daily["sunrise"][0][11:16]
    sunset = daily["sunset"][0][11:16]
    rows = [("HUMEDAD", f"{cur['relative_humidity_2m']}%", "VIENTO", f"{round(cur['wind_speed_10m'])} km/h {wind_dir}"),
            ("PRESIÓN", f"{round(cur['pressure_msl'])} hPa", "RACHAS", f"{round(cur['wind_gusts_10m'])} km/h"),
            ("UV", f"{daily['uv_index_max'][0]:.0f}", "LLUVIA", f"{daily['precipitation_probability_max'][0] or 0}%"),
            ("AMANECE", sunrise, "ANOCHECE", sunset)]
    half = width // 2
    for k1, v1, k2, v2 in rows:
        out.append("  " + rgb(MUTED, f"{k1:<9}") + rgb(TEXT, f"{v1:<{half - 9}}") + rgb(MUTED, f"{k2:<9}") + rgb(TEXT, v2))
    out.append("")

    # Next 12 hours: one column per hour (icon, temperature, rain chance)
    out.append("  " + rgb(MUTED, "PRÓXIMAS HORAS") + rgb(LINE, " " + "─" * (width - 15)))
    hours = list(zip(hourly["time"], hourly["temperature_2m"], hourly["precipitation_probability"],
                     hourly["weather_code"], hourly["is_day"]))[1:13]
    col = max(width // max(len(hours), 1), 4)
    hours = hours[: width // col]
    out.append("  " + "".join(rgb(FAINT, h[0][11:13].rjust(col - 1) + " ") for h in hours))
    out.append("  " + "".join(rgb(SUB, wmo(h[3], h[4])[0].rjust(col - 1) + " ") for h in hours))
    out.append("  " + "".join(rgb(temp_color(h[1]), f"{round(h[1])}°".rjust(col - 1) + " ") for h in hours))
    out.append("  " + "".join(rgb(BLUE if (h[2] or 0) >= 30 else FAINT, f"{h[2] or 0}%".rjust(col - 1) + " ") for h in hours))
    out.append("")

    # 7 days: min..max drawn on a shared scale, like a range bar
    out.append("  " + rgb(MUTED, "7 DÍAS") + rgb(LINE, " " + "─" * (width - 7)))
    lo, hi = min(daily["temperature_2m_min"]), max(daily["temperature_2m_max"])
    span = max(hi - lo, 1)
    bar_w = width - 26
    for i, day in enumerate(daily["time"]):
        d = dt.date.fromisoformat(day)
        name = "HOY" if i == 0 else DAYS[d.weekday()]
        tmin, tmax = daily["temperature_2m_min"][i], daily["temperature_2m_max"][i]
        a = round((tmin - lo) / span * bar_w)
        b = max(round((tmax - lo) / span * bar_w), a + 1)
        rng = rgb(LINE, "─" * a) + rgb(temp_color(tmax), "━" * (b - a)) + rgb(LINE, "─" * (bar_w - b))
        rain = daily["precipitation_probability_max"][i] or 0
        out.append("  " + rgb(AMBER if i == 0 else SUB, f"{name:<4}") + rgb(SUB, wmo(daily["weather_code"][i])[0]) + "  "
                   + rgb(MUTED, f"{round(tmin):>3}° ") + rng + rgb(TEXT, f" {round(tmax):>2}°")
                   + rgb(BLUE if rain >= 30 else FAINT, f" {rain:>3}%"))
    out.append("  " + rgb(FAINT, "R ACTUALIZAR   ESC CERRAR"))
    return "\n".join(out)


def popup():
    data = load()
    old = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    sys.stdout.write("\033[?25l")
    try:
        while True:
            sys.stdout.write("\033[H\033[2J" + render(data))
            sys.stdout.flush()
            key = os.read(sys.stdin.fileno(), 8).decode(errors="ignore")
            if key in ("q", "\x1b"):
                break
            if key == "r":
                data = load(refresh=True)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        sys.stdout.write("\033[?25h")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "bar"
    if mode == "bar":
        bar()
    elif mode == "print":
        print(render(load()))
    else:
        popup()
