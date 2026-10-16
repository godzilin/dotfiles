#!/usr/bin/env python3
"""Wallpaper selector popup (opened from the waybar wallpaper button).
Thumbnails of the active theme's rotation/ folder: click one to pin it, or go back to the random rotation.
Looks: the theme's popups/media.css plus popups/wallpaper.css when it exists; texts from theme.json "wallpaper".
Esc closes; a click outside closes it too (hypr/binds.lua)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf, GLib, Gtk  # noqa: E402

GLib.set_prgname("nostromo-wallpaper")  # Wayland app_id, matched by the window rule

THEME = Path("~/.config/dotfiles/themes/current").expanduser()
NAME = os.readlink(THEME)
ROTATION = THEME.resolve() / "wallpapers" / "rotation"
SCRIPT = Path("~/.config/hypr/scripts/wallpaper.sh").expanduser()
CACHE = Path("~/.cache/nostromo").expanduser()
THUMBS = CACHE / "thumbs" / NAME
TW, TH, COLS = 160, 100, 3
IMAGES = (".jpg", ".jpeg", ".png", ".webp")


def pinned():
    try:
        return (CACHE / f"wallpaper-{NAME}").read_text().strip()
    except OSError:
        return ""


def thumb(src):
    """Cached thumbnail; rebuilt when the wallpaper is newer (the generators rewrite rotation/)."""
    out = THUMBS / (src.stem + ".png")
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        THUMBS.mkdir(parents=True, exist_ok=True)
        pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(src), TW * 2, -1, True)  # cover-crop to TW x TH
        h = min(pix.get_height(), pix.get_width() * TH // TW)
        pix = pix.new_subpixbuf(0, (pix.get_height() - h) // 2, pix.get_width(), h)
        pix.scale_simple(TW, TH, GdkPixbuf.InterpType.BILINEAR).savev(str(out), "png", [], [])
    return GdkPixbuf.Pixbuf.new_from_file(str(out))


class Popup(Gtk.Window):
    def __init__(self):
        super().__init__(title="Fondos")
        theme = json.loads((THEME / "theme.json").read_text())
        texts = {"title": "FONDOS", "random": "Aleatorio"} | theme.get("wallpaper", {})
        for css in ("media.css", "wallpaper.css"):
            path = THEME / "popups" / css
            if path.exists():
                provider = Gtk.CssProvider()
                provider.load_from_path(str(path))
                Gtk.StyleContext.add_provider_for_screen(self.get_screen(), provider,
                                                         Gtk.STYLE_PROVIDER_PRIORITY_USER)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=18)
        self.add(root)
        head = Gtk.Box(spacing=6)
        dot = Gtk.Label(label="▮"); dot.get_style_context().add_class("head-dot")
        self.files = sorted(p for p in ROTATION.iterdir() if p.suffix.lower() in IMAGES)
        title = Gtk.Label(label=f"{texts['title']} · {len(self.files)}", xalign=0)
        title.get_style_context().add_class("head")
        self.random = Gtk.Button(label=texts["random"])
        self.random.get_style_context().add_class("random")
        self.random.connect("clicked", lambda *_: self.choose("random"))
        head.pack_start(dot, False, False, 0); head.pack_start(title, True, True, 0)
        head.pack_end(self.random, False, False, 0)
        root.pack_start(head, False, False, 0)
        stripes = Gtk.Box(homogeneous=True)
        for i in range(1, 5):
            bar = Gtk.Box(); bar.set_size_request(-1, 3); bar.get_style_context().add_class(f"stripe-{i}")
            stripes.pack_start(bar, True, True, 0)
        root.pack_start(stripes, False, False, 0)

        grid = Gtk.FlowBox(max_children_per_line=COLS, min_children_per_line=COLS, homogeneous=True,
                           selection_mode=Gtk.SelectionMode.NONE, row_spacing=8, column_spacing=8)
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        scroll.add(grid)
        root.pack_start(scroll, True, True, 0)
        self.buttons, self.pending = {}, []
        for f in self.files:
            b = Gtk.Button(tooltip_text=f.stem, relief=Gtk.ReliefStyle.NONE)
            b.get_style_context().add_class("thumb")
            img = Gtk.Image(); img.set_size_request(TW, TH)
            b.add(img)
            b.connect("clicked", lambda _b, f=f: self.choose(str(f)))
            grid.add(b)
            self.buttons[str(f)] = b
            self.pending.append((f, img))
        self.mark(pinned())
        GLib.idle_add(self.load_next)  # thumbnails fill in without blocking the window

        self.connect("key-press-event", lambda _w, e: e.keyval == 0xff1b and Gtk.main_quit())
        self.connect("destroy", Gtk.main_quit)

    def load_next(self):
        if not self.pending:
            return False
        f, img = self.pending.pop(0)
        try:
            img.set_from_pixbuf(thumb(f))
        except GLib.Error:
            img.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        return True

    def mark(self, now):
        for path, b in [*self.buttons.items(), ("", self.random)]:
            ctx = b.get_style_context()
            ctx.add_class("on") if path == (now if now in self.buttons else "") else ctx.remove_class("on")

    def choose(self, what):
        subprocess.Popen([str(SCRIPT), "set", what], start_new_session=True)
        self.mark(what)


if __name__ == "__main__":
    win = Popup()
    win.show_all()
    if "--shot" in sys.argv:  # close by itself, for screenshots
        GLib.timeout_add_seconds(4, Gtk.main_quit)
    Gtk.main()
