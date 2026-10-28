#!/usr/bin/env python3
"""Weather popup of the "blanco" theme (opened by hypr/scripts/weather.sh): the Weather app's look, white text on a
sky that follows the hour and the conditions, big temperature, the next hours in a row and seven days with range bars.
Data and icons come from the shared hypr/scripts/weather.py (Open-Meteo cache). Keys: r refresh, Esc close."""
import datetime as dt
import os
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
import weather  # noqa: E402  (load, wmo)

DAYS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
COMPASS = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
# sky gradients (top, bottom) for the background
SKY = {"day": ("#4f9ae8", "#2a6cc4"), "cloud": ("#7d8fa3", "#4f6075"), "rain": ("#5d6d80", "#36434f"),
       "night": ("#1f2f52", "#0c1528")}

CSS = """
window {{ background-image: linear-gradient(to bottom, {top}, {bottom}); }}
* {{ font-family: "Inter", "Symbols Nerd Font", sans-serif; color: #ffffff; }}
.place {{ font-size: 15pt; font-weight: 600; }}
.temp {{ font-size: 44pt; font-weight: 300; }}
.desc {{ font-size: 11pt; font-weight: 500; }}
.hilo {{ font-size: 10.5pt; font-weight: 500; }}
.card {{ background: rgba(255, 255, 255, 0.14); border-radius: 12px; padding: 10px 12px; }}
.card-title {{ font-size: 8.5pt; font-weight: 600; color: rgba(255, 255, 255, 0.65); }}
.hour {{ font-size: 9.5pt; font-weight: 500; }}
.hour-icon {{ font-size: 14pt; }}
.rain {{ font-size: 8pt; color: #9fd3ff; font-weight: 600; }}
.day {{ font-size: 10.5pt; font-weight: 500; }}
.lo {{ font-size: 10.5pt; color: rgba(255, 255, 255, 0.6); }}
.hi {{ font-size: 10.5pt; font-weight: 600; }}
.track {{ background: rgba(0, 0, 0, 0.18); border-radius: 3px; min-height: 5px; }}
.range {{ border-radius: 3px; min-height: 5px; background-image: linear-gradient(to right, #8fd3ff, #ffd36b, #ff9f4a); }}
.detail-key {{ font-size: 8.5pt; color: rgba(255, 255, 255, 0.65); font-weight: 600; }}
.detail {{ font-size: 11pt; font-weight: 500; }}
.offline {{ font-size: 11pt; }}
"""


def label(text, cls, xalign=0.5):
    w = Gtk.Label(label=text, xalign=xalign)
    w.get_style_context().add_class(cls)
    return w


def card(title):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    box.get_style_context().add_class("card")
    box.pack_start(label(title, "card-title", xalign=0), False, False, 0)
    return box


class Weather(Gtk.Window):
    def __init__(self):
        super().__init__(title="Tiempo")
        self.css = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=16)
        self.add(self.root)
        self.connect("key-press-event", self.on_key)
        self.connect("destroy", Gtk.main_quit)
        self.draw(weather.load())

    def on_key(self, _w, e):
        name = Gdk.keyval_name(e.keyval)
        if name in ("Escape", "q"):
            Gtk.main_quit()
        elif name == "r":
            self.draw(weather.load(refresh=True))

    def draw(self, data):
        for child in self.root.get_children():
            self.root.remove(child)
        if not data:
            self.css.load_from_data(CSS.format(top=SKY["cloud"][0], bottom=SKY["cloud"][1]).encode())
            self.root.pack_start(label("Sin datos del tiempo. ¿Hay conexión?", "offline"), True, True, 0)
            self.root.show_all()
            return
        cur, daily, hourly = data["current"], data["daily"], data["hourly"]
        code = cur["weather_code"]
        sky = "night" if not cur["is_day"] else "rain" if code >= 51 else "cloud" if code >= 3 else "day"
        self.css.load_from_data(CSS.format(top=SKY[sky][0], bottom=SKY[sky][1]).encode())

        icon, desc = weather.wmo(code, cur["is_day"])
        head = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        head.pack_start(label(data["place"] or "Aquí", "place"), False, False, 0)
        head.pack_start(label(f"{round(cur['temperature_2m'])}°", "temp"), False, False, 0)
        head.pack_start(label(f"{icon}  {desc.capitalize()}", "desc"), False, False, 0)
        head.pack_start(label(f"Máx.: {round(daily['temperature_2m_max'][0])}°   "
                              f"Mín.: {round(daily['temperature_2m_min'][0])}°", "hilo"), False, False, 0)
        self.root.pack_start(head, False, False, 4)

        hours = card("PRÓXIMAS HORAS")
        row = Gtk.Box(homogeneous=True, spacing=0)
        items = list(zip(hourly["time"], hourly["temperature_2m"], hourly["precipitation_probability"],
                         hourly["weather_code"], hourly["is_day"]))[1:8]
        for i, (t, temp, rain, c, day) in enumerate(items):
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            col.pack_start(label(t[11:13], "hour"), False, False, 0)
            col.pack_start(label(weather.wmo(c, day)[0], "hour-icon"), False, False, 0)
            col.pack_start(label(f"{rain}%" if (rain or 0) >= 30 else " ", "rain"), False, False, 0)
            col.pack_start(label(f"{round(temp)}°", "hour"), False, False, 0)
            row.pack_start(col, True, True, 0)
        hours.pack_start(row, False, False, 0)
        self.root.pack_start(hours, False, False, 0)

        days = card("PRÓXIMOS 7 DÍAS")
        lo, hi = min(daily["temperature_2m_min"]), max(daily["temperature_2m_max"])
        span = max(hi - lo, 1)
        for i, day in enumerate(daily["time"]):
            d = dt.date.fromisoformat(day)
            tmin, tmax = daily["temperature_2m_min"][i], daily["temperature_2m_max"][i]
            line = Gtk.Box(spacing=8)
            name = label("Hoy" if i == 0 else DAYS[d.weekday()].capitalize(), "day", xalign=0)
            name.set_size_request(40, -1)
            line.pack_start(name, False, False, 0)
            line.pack_start(label(weather.wmo(daily["weather_code"][i])[0], "hour-icon"), False, False, 0)
            low = label(f"{round(tmin)}°", "lo", xalign=1)
            low.set_size_request(34, -1)
            line.pack_start(low, False, False, 0)
            # range bar: the track is the week's span, the coloured part this day's min..max
            track = Gtk.Box()
            track.get_style_context().add_class("track")
            track.set_valign(Gtk.Align.CENTER)
            width = 150
            a = round((tmin - lo) / span * width)
            b = max(round((tmax - lo) / span * width), a + 6)
            fill = Gtk.Box()
            fill.get_style_context().add_class("range")
            fill.set_size_request(b - a, 5)
            pad = Gtk.Box()
            pad.set_size_request(a, 5)
            track.pack_start(pad, False, False, 0)
            track.pack_start(fill, False, False, 0)
            track.set_size_request(width, 5)
            line.pack_start(track, True, True, 0)
            high = label(f"{round(tmax)}°", "hi", xalign=1)
            high.set_size_request(34, -1)
            line.pack_start(high, False, False, 0)
            days.pack_start(line, False, False, 0)
        self.root.pack_start(days, False, False, 0)

        details = Gtk.Grid(column_homogeneous=True, column_spacing=8, row_spacing=8)
        wind = f"{round(cur['wind_speed_10m'])} km/h {COMPASS[round(cur['wind_direction_10m'] / 45) % 8]}"
        for i, (k, v) in enumerate([("SENSACIÓN", f"{round(cur['apparent_temperature'])}°"),
                                    ("HUMEDAD", f"{cur['relative_humidity_2m']}%"), ("VIENTO", wind),
                                    ("ÍNDICE UV", f"{daily['uv_index_max'][0]:.0f}"),
                                    ("AMANECER", daily["sunrise"][0][11:16]), ("ATARDECER", daily["sunset"][0][11:16])]):
            cell = card(k)
            cell.pack_start(label(v, "detail", xalign=0), False, False, 0)
            details.attach(cell, i % 3, i // 3, 1, 1)
        self.root.pack_start(details, False, False, 0)
        self.root.show_all()


if __name__ == "__main__":
    GLib.set_prgname("nostromo-weather")  # Wayland app_id: the window rules in look.lua place it under the bar
    Weather().show_all()
    Gtk.main()
