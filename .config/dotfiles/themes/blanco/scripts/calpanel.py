#!/usr/bin/env python3
"""Calendar popup of the "blanco" theme (opened from the clock by hypr/scripts/calendar.sh; not called calendar.py,
which would shadow the stdlib module calpopup imports): the month view of the Calendar app in a light panel,
today in a red circle, a dot under days with events and the next two weeks below.
Events come from the shared popup's khal cache (hypr/scripts/calpopup.py), refreshed in the background.
Keys: left/right change month, t today, Esc close."""
import datetime as dt
import os
import sys
import threading

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

sys.path.insert(0, os.path.expanduser("~/.config/hypr/scripts"))
import calpopup  # noqa: E402  (events: load_cache, refresh, EVENTS, KHAL_OK)

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
          "noviembre", "diciembre"]
WEEKDAYS = ["L", "M", "X", "J", "V", "S", "D"]
DAY_NAMES = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]

CSS = b"""
window { background: #ffffff; }
* { font-family: "Inter", sans-serif; color: #1d1d1f; }
.month { font-size: 17pt; font-weight: 700; }
.year { font-size: 17pt; font-weight: 400; color: #8e8e93; }
button.nav { background: #f2f2f7; border: none; border-radius: 7px; box-shadow: none; padding: 2px 10px; min-height: 0; }
button.nav:hover { background: #e5e5ea; }
button.nav label { font-size: 10.5pt; font-weight: 600; }
.weekday { font-size: 9pt; font-weight: 600; color: #8e8e93; }
.weekday.weekend { color: #aeaeb2; }
.day { font-size: 11pt; min-width: 28px; min-height: 28px; border-radius: 999px; }
.day.weekend { color: #8e8e93; }
.day.other { color: #c7c7cc; }
.day.today { background: #ff3b30; color: #ffffff; font-weight: 700; }
.dot { font-size: 5pt; color: #8e8e93; margin-top: -2px; margin-bottom: 2px; }
.dot.empty { color: transparent; }
separator { background: #e5e5ea; min-height: 1px; }
.section { font-size: 9pt; font-weight: 600; color: #8e8e93; }
.event-bar { background: #007aff; min-width: 3px; border-radius: 2px; }
.event-bar.today { background: #ff3b30; }
.event { font-size: 10.5pt; font-weight: 500; }
.when { font-size: 9.5pt; color: #8e8e93; }
.empty-list { font-size: 10pt; color: #8e8e93; }
"""


def label(text, *classes, xalign=0.5):
    w = Gtk.Label(label=text, xalign=xalign)
    for c in classes:
        w.get_style_context().add_class(c)
    return w


class Calendar(Gtk.Window):
    def __init__(self):
        super().__init__(title="Calendario")
        self.today = dt.date.today()
        self.year, self.month = self.today.year, self.today.month
        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=16)
        self.add(self.root)
        self.connect("key-press-event", self.on_key)
        self.connect("destroy", Gtk.main_quit)

        calpopup.load_cache()
        self.draw()
        done = threading.Event()
        threading.Thread(target=lambda: (calpopup.refresh(done), GLib.idle_add(self.draw)), daemon=True).start()

    def move(self, months):
        m = self.year * 12 + self.month - 1 + months
        self.year, self.month = divmod(m, 12)
        self.month += 1
        self.draw()

    def on_key(self, _w, e):
        name = Gdk.keyval_name(e.keyval)
        if name in ("Escape", "q"):
            Gtk.main_quit()
        elif name == "Left":
            self.move(-1)
        elif name == "Right":
            self.move(1)
        elif name == "t":
            self.year, self.month = self.today.year, self.today.month
            self.draw()

    def draw(self):
        for child in self.root.get_children():
            self.root.remove(child)
        busy = {d for d, _, _ in calpopup.EVENTS}

        head = Gtk.Box(spacing=6)
        head.pack_start(label(MONTHS[self.month - 1].capitalize(), "month", xalign=0), False, False, 0)
        head.pack_start(label(str(self.year), "year", xalign=0), False, False, 0)
        for text, step in (("›", 1), ("Hoy", 0), ("‹", -1)):
            b = Gtk.Button(label=text)
            b.get_style_context().add_class("nav")
            b.connect("clicked", lambda _b, s=step: self.move(s) if s else self.go_today())
            head.pack_end(b, False, False, 0)
        self.root.pack_start(head, False, False, 0)

        grid = Gtk.Grid(column_homogeneous=True, row_spacing=0, column_spacing=0)
        for i, w in enumerate(WEEKDAYS):
            grid.attach(label(w, "weekday", *(["weekend"] if i >= 5 else [])), i, 0, 1, 1)
        first = dt.date(self.year, self.month, 1)
        start = first - dt.timedelta(days=first.weekday())
        weeks = ((self.month_end() - start).days // 7) + 1  # only the weeks this month touches
        for k in range(7 * weeks):
            d = start + dt.timedelta(days=k)
            cls = ["day"]
            if d.month != self.month:
                cls.append("other")
            elif d == self.today:
                cls.append("today")
            elif d.weekday() >= 5:
                cls.append("weekend")
            cell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            num = label(str(d.day), *cls)
            num.set_halign(Gtk.Align.CENTER)
            cell.pack_start(num, False, False, 0)
            cell.pack_start(label("●", "dot", *([] if d in busy and d.month == self.month else ["empty"])), False, False, 0)
            grid.attach(cell, k % 7, 1 + k // 7, 1, 1)
        self.root.pack_start(grid, False, False, 0)

        self.root.pack_start(Gtk.Separator(), False, False, 2)
        self.root.pack_start(label("Próximos", "section", xalign=0), False, False, 0)
        upcoming = [e for e in calpopup.EVENTS if self.today <= e[0] < self.today + dt.timedelta(days=14)][:4]
        for d, time, name in upcoming:
            when = "Hoy" if d == self.today else "Mañana" if d == self.today + dt.timedelta(1) \
                else f"{DAY_NAMES[d.weekday()]} {d.day}"
            row = Gtk.Box(spacing=8)
            row.pack_start(label("", "event-bar", *(["today"] if d == self.today else [])), False, False, 0)
            text = label(name, "event", xalign=0)
            text.set_ellipsize(3)  # Pango.EllipsizeMode.END
            row.pack_start(text, True, True, 0)
            row.pack_end(label(f"{when}  {time or 'todo el día'}", "when", xalign=1), False, False, 0)
            self.root.pack_start(row, False, False, 0)
        if not upcoming:
            msg = "Nada en las próximas dos semanas" if calpopup.KHAL_OK else "Sin calendario (ver README)"
            self.root.pack_start(label(msg, "empty-list", xalign=0), False, False, 0)
        self.root.show_all()
        return False

    def month_end(self):
        nxt = dt.date(self.year + self.month // 12, self.month % 12 + 1, 1)
        return nxt - dt.timedelta(days=1)

    def go_today(self):
        self.year, self.month = self.today.year, self.today.month
        self.draw()


if __name__ == "__main__":
    GLib.set_prgname("nostromo-calendar")  # Wayland app_id: the window rules in look.lua place it under the clock
    Calendar().show_all()
    Gtk.main()
