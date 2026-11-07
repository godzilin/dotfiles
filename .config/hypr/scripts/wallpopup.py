#!/usr/bin/env python3
"""Wallpaper selector popup (opened from the waybar wallpaper button).
Thumbnails of the active theme's rotation/ folder: click one to pin it, or go back to the random rotation.
A theme with "wallpaper_engine": true in theme.json (camaleon) gets a second tab with the Wallpaper Engine wallpapers its
daemon can draw (~/.cache/nostromo/<theme>-we.json); "Rotar" then rotates through the visible tab only (<theme>-modo).
A right click on one of those opens a menu: leave it out of "Rotar" or bring it back (<theme>-we-fuera; it can still be
pinned), hide it (<theme>-we-ocultos) or, for a Workshop one, open its Steam page to unsubscribe (and hide it).
Hidden ones wait in the "Ocultos" tab: a click there brings one back.
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
OUT = CACHE / f"{NAME}-we-fuera"
HIDDEN = CACHE / f"{NAME}-we-ocultos"
THUMBS = CACHE / "thumbs" / NAME
TW, TH, COLS = 160, 100, 3
IMAGES = (".jpg", ".jpeg", ".png", ".webp")


def pinned():
    try:
        return (CACHE / f"wallpaper-{NAME}").read_text().strip()
    except OSError:
        return ""


def mode():
    """Source the theme's daemon rotates through: "we" or "img" (only with "wallpaper_engine")."""
    try:
        return (CACHE / f"{NAME}-modo").read_text().strip()
    except OSError:
        return "we"


def hidden_ones():
    try:
        return set(HIDDEN.read_text().splitlines())
    except OSError:
        return set()


def out_of_rotation():
    try:
        return set(OUT.read_text().splitlines())
    except OSError:
        return set()


def thumb(src, key=None):
    """Cached thumbnail; rebuilt when the wallpaper is newer (the generators rewrite rotation/)."""
    out = THUMBS / ((key or src.stem) + ".png")
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
        tabs = json.loads((THEME / "theme.json").read_text()).get("wallpaper_engine")  # counts go on the tabs
        title = Gtk.Label(label=texts["title"] if tabs else f"{texts['title']} · {len(self.files)}", xalign=0)
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

        self.buttons, self.pending = {}, []
        images = [(str(f), f, f.stem, None) for f in self.files]
        self.we = []
        if theme.get("wallpaper_engine"):
            try:
                self.we = json.loads((CACHE / f"{NAME}-we.json").read_text())
            except (OSError, ValueError):
                pass
        if theme.get("wallpaper_engine"):
            self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
            self.stack.add_titled(self.grid(images), "img", f"Imágenes · {len(images)}")
            hidden = hidden_ones()
            self.lowres = {w["folder"] for w in self.we if w.get("lowres")}  # never rotated: they look pixelated
            we = [(w["folder"], Path(w["preview"]), w["title"], "we-" + Path(w["folder"]).name) for w in self.we]
            self.stack.add_titled(self.grid([e for e in we if e[0] not in hidden], "we"), "we", "")
            self.stack.add_titled(self.grid([e for e in we if e[0] in hidden], "hidden"), "hidden", "")
            self.retitle()
            switch = Gtk.StackSwitcher(stack=self.stack, halign=Gtk.Align.START)
            switch.get_style_context().add_class("tabs")
            root.pack_start(switch, False, False, 0)
            root.pack_start(self.stack, True, True, 0)
            now = pinned()
            self.stack.show_all()
            self.stack.set_visible_child_name("we" if now in {w["folder"] for w in self.we} or (not now and mode() == "we") else "img")
            self.stack.connect("notify::visible-child-name", lambda *_: self.mark(pinned()))
        else:
            self.stack = None
            root.pack_start(self.grid(images), True, True, 0)
        self.mark(pinned())
        GLib.idle_add(self.load_next)  # thumbnails fill in without blocking the window

        self.connect("key-press-event", lambda _w, e: e.keyval == 0xff1b and Gtk.main_quit())
        self.connect("destroy", Gtk.main_quit)

    def grid(self, entries, kind="img"):
        """Scrolled grid of (pin value, image, tooltip, thumbnail cache key); kind is img, we or hidden."""
        grid = Gtk.FlowBox(max_children_per_line=COLS, min_children_per_line=COLS, homogeneous=True,
                           selection_mode=Gtk.SelectionMode.NONE, row_spacing=8, column_spacing=8)
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        scroll.add(grid)
        self.flows = getattr(self, "flows", {}) | {kind: grid}
        for entry in entries:
            self.add_thumb(kind, entry)
        return scroll

    def add_thumb(self, kind, entry):
        value, f, tip, key = entry
        b = Gtk.Button(tooltip_text=tip, relief=Gtk.ReliefStyle.NONE)
        b.get_style_context().add_class("thumb")
        img = Gtk.Image(); img.set_size_request(TW, TH)
        b.add(img)
        if kind == "hidden":
            b.set_tooltip_text(f"{tip}\nclic: volver a mostrarlo")
            b.connect("clicked", lambda b: self.unhide(b, entry))
        else:
            b.connect("clicked", lambda _b: self.choose(value))
            self.buttons[value] = b
        if kind == "we":
            low = value in getattr(self, "lowres", ())
            b.set_tooltip_text(f"{tip}\n" + ("baja resolución: se verá pixelado, no entra en Rotar\n" if low else "")
                               + "clic derecho: más opciones")
            b.connect("button-press-event", lambda b, e: e.button == 3 and self.menu(b, e, entry))
            if low:
                b.get_style_context().add_class("lowres")
            if value in out_of_rotation():
                b.get_style_context().add_class("off")
        self.flows[kind].add(b)
        b.show_all()
        self.pending.append((f, img, key))
        if len(self.pending) == 1 and getattr(self, "loaded", False):
            GLib.idle_add(self.load_next)  # moved between tabs after the first load finished

    def retitle(self):
        for kind, label in (("we", "Wallpaper Engine"), ("hidden", "Ocultos")):
            n = len(self.flows[kind].get_children())
            self.stack.child_set_property(self.stack.get_child_by_name(kind), "title", f"{label} · {n}")

    def unhide(self, button, entry):
        HIDDEN.write_text("".join(f"{v}\n" for v in sorted(hidden_ones() - {entry[0]})))
        button.get_parent().destroy()
        self.add_thumb("we", entry)
        self.retitle()

    def load_next(self):
        if not self.pending:
            self.loaded = True
            return False
        f, img, key = self.pending.pop(0)
        try:
            img.set_from_pixbuf(thumb(f, key))
        except GLib.Error:
            img.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        return True

    def menu(self, button, event, entry):
        value = entry[0]
        m = Gtk.Menu()
        items = [] if value in getattr(self, "lowres", ()) else [  # low resolution: never in "Rotar" anyway
            ("Meter en Rotar" if value in out_of_rotation() else "Quitar de Rotar", lambda: self.toggle_out(button, value))]
        items.append(("Ocultar", lambda: self.hide(button, entry)))
        if "/workshop/content/" in value:  # deleting the folder is useless: Steam downloads it again while subscribed
            items.append(("Desuscribirse en Steam", lambda: (subprocess.Popen(
                ["steam", f"steam://url/CommunityFilePage/{Path(value).name}"], start_new_session=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), self.hide(button, entry))))
        for label, action in items:
            it = Gtk.MenuItem(label=label)
            it.connect("activate", lambda _i, a=action: a())
            m.append(it)
        m.show_all()
        m.attach_to_widget(button)
        m.popup_at_pointer(event)
        return True

    def hide(self, button, entry):
        with HIDDEN.open("a") as f:
            f.write(f"{entry[0]}\n")
        self.buttons.pop(entry[0], None)
        button.get_parent().destroy()  # the FlowBoxChild around it
        self.add_thumb("hidden", entry)
        self.retitle()

    def toggle_out(self, button, value):
        out = out_of_rotation() ^ {value}
        OUT.write_text("".join(f"{v}\n" for v in sorted(out)))
        ctx = button.get_style_context()
        ctx.add_class("off") if value in out else ctx.remove_class("off")
        return True

    def mark(self, now):
        rotating_here = not self.stack or self.stack.get_visible_child_name() == mode()
        for path, b in [*self.buttons.items(), ("", self.random)]:
            on = path == now if path else (now not in self.buttons and rotating_here)
            ctx = b.get_style_context()
            ctx.add_class("on") if on else ctx.remove_class("on")

    def choose(self, what):
        if what == "random" and self.stack:
            (CACHE / f"{NAME}-modo").write_text(self.stack.get_visible_child_name() + "\n")
        subprocess.Popen([str(SCRIPT), "set", what], start_new_session=True)
        self.mark("" if what == "random" else what)


if __name__ == "__main__":
    win = Popup()
    win.show_all()
    if "--shot" in sys.argv:  # close by itself, for screenshots
        GLib.timeout_add_seconds(4, Gtk.main_quit)
    Gtk.main()
