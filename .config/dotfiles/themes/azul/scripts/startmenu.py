#!/usr/bin/env python3
"""Windows 98 Start menu for the "azul" theme (GTK3 + gtk-layer-shell, drawn by the Chicago95 GTK theme).
  startmenu.py menu      -> the Start menu, anchored above the Start button (startmenu.sh toggles it)
  startmenu.py run       -> "Ejecutar" dialog
  startmenu.py shutdown  -> "Apagar el sistema" dialog
Programas is built from the installed .desktop files, grouped by their main category."""
import os
import subprocess
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gdk, Gio, GLib, Gtk, GtkLayerShell, PangoCairo  # noqa: E402

TASKBAR = 34  # height of the waybar taskbar the menu sits on
HOME = os.path.expanduser("~")
USER = (subprocess.run(["getent", "passwd", os.environ.get("USER", "")], capture_output=True, text=True)
        .stdout.split(":")[4:5] or [""])[0].split(",")[0] or os.environ.get("USER", "")

CSS = b"""
window.start-overlay { background: transparent; }
.start-panel { background: #c0c0c0; border-style: solid; border-width: 1px 2px 2px 1px;
               border-color: #dfdfdf #000000 #000000 #dfdfdf; padding: 1px; }
.start-inner { border-style: solid; border-width: 1px; border-color: #ffffff #808080 #808080 #ffffff; }
button.start-item { background: #c0c0c0; background-image: none; border: none; border-radius: 0; box-shadow: none;
                    padding: 3px 6px 3px 4px; min-height: 30px; outline: none; }
button.start-item.small { padding: 2px 6px 2px 4px; min-height: 18px; }
button.start-item:hover, button.start-item:focus, button.start-item.open { background: #000080; }
button.start-item label { color: #000000; font-size: 16px; }
button.start-item.small label { font-size: 13px; }
button.start-item:hover label, button.start-item:focus label, button.start-item.open label { color: #ffffff; }
button.start-item:disabled label { color: #808080; }
.start-sep { min-height: 2px; margin: 2px 2px; border-top: 1px solid #808080; border-bottom: 1px solid #ffffff; }
"""

CATEGORIES = [  # (freedesktop main category, folder name, icon)
    ("Utility", "Accesorios", "applications-accessories"),
    ("Development", "Programación", "applications-development"),
    ("Education", "Educación", "applications-science"),
    ("Game", "Juegos", "applications-games"),
    ("Graphics", "Gráficos", "applications-graphics"),
    ("Network", "Internet", "applications-internet"),
    ("AudioVideo", "Multimedia", "applications-multimedia"),
    ("Office", "Oficina", "applications-office"),
    ("Science", "Ciencia", "applications-science"),
    ("Settings", "Configuración", "preferences-desktop"),
    ("System", "Herramientas del sistema", "applications-system"),
]
HOVER_MS = 250  # how long the pointer rests on a folder before it opens, as in Windows


def spawn(*argv):
    subprocess.Popen(argv, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def css():
    p = Gtk.CssProvider()
    p.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


# A menu is a list of entries: None (separator) or (label, icon, target), where target is a callable (run it and
# close), a list (a submenu) or None (a greyed-out line). icon is an icon name or a Gio.Icon.

def programs_menu():
    groups = {}
    for app in Gio.AppInfo.get_all():
        if not app.should_show() or not app.get_id():
            continue
        cats = (app.get_categories() or "").split(";")
        key = next((c for c, _, _ in CATEGORIES if c in cats or (c == "AudioVideo" and {"Audio", "Video"} & set(cats))),
                   "Other")
        groups.setdefault(key, []).append(app)
    folders = [(name, icon, groups.pop(c)) for c, name, icon in CATEGORIES if c in groups]
    if "Other" in groups:
        folders.append(("Otros", "applications-other", groups.pop("Other")))
    return [(name, icon, [(a.get_display_name(), a.get_icon() or "application-x-executable",
                           lambda a=a: spawn("gtk-launch", a.get_id()))
                          for a in sorted(apps, key=lambda a: a.get_display_name().lower())])
            for name, icon, apps in folders]


def documents_menu():
    items = [i for i in Gtk.RecentManager.get_default().get_items() if i.exists()]
    items.sort(key=lambda i: i.get_modified(), reverse=True)
    recent = [(i.get_display_name(), i.get_gicon(), lambda u=i.get_uri(): spawn("xdg-open", u)) for i in items[:12]]
    return [("Mis documentos", "folder-documents", lambda: spawn("xdg-open", os.path.join(HOME, "Documents"))),
            None] + (recent or [("(Vacío)", None, None)])


def settings_menu():
    return [(label, icon, lambda a=argv: spawn(*a)) for label, icon, argv in [
        ("Panel de control", "preferences-system", ["systemsettings"]),
        ("Pantalla", "preferences-desktop-display", ["systemsettings", "kcm_kscreen"]),
        ("Red", "network-workgroup", ["systemsettings", "kcm_networkmanagement"]),
        ("Sonido", "audio-volume-high", ["pavucontrol"]),
        ("Bluetooth", "bluetooth-active", ["systemsettings", "kcm_bluetooth"]),
    ]]


def search_menu():
    return [("Archivos o carpetas...", "system-search", lambda: spawn("thunar", HOME)),
            ("Programas...", "applications-other", lambda: spawn("fuzzel"))]


class Banner(Gtk.DrawingArea):
    """The vertical "Linux98" strip on the left of the menu."""

    def __init__(self):
        super().__init__()
        self.set_size_request(22, -1)
        self.connect("draw", self.draw)

    def draw(self, _w, cr):
        h = self.get_allocated_height()
        import cairo
        g = cairo.LinearGradient(0, 0, 0, h)
        g.add_color_stop_rgb(0, 0, 0, 0)
        g.add_color_stop_rgb(1, 0x10 / 255, 0x84 / 255, 0xd0 / 255)
        cr.set_source(g)
        cr.paint()
        cr.translate(4, h - 6)
        cr.rotate(-3.14159265 / 2)
        layout = PangoCairo.create_layout(cr)
        layout.set_markup("<span font_family='Arial' weight='heavy' size='13pt' foreground='#ffffff'>Linux</span>"
                          "<span font_family='Arial' size='13pt' foreground='#c0c0c0'>98</span>", -1)
        PangoCairo.show_layout(cr, layout)


class StartMenu(Gtk.Window):
    """One full-screen transparent overlay surface holding the menu and every open submenu as plain widgets.
    No xdg_popup grabs (with one open, Hyprland sends all pointer events to the popup, so GTK menus could neither
    switch folders on hover nor tell a click on another folder from a click outside): here a click on the empty
    area closes everything, and the exclusive keyboard makes Esc and the arrows work without clicking first."""

    def __init__(self):
        super().__init__()
        self.get_style_context().add_class("start-overlay")
        visual = self.get_screen().get_rgba_visual()
        if visual is not None:
            self.set_visual(visual)
        self.set_app_paintable(True)
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "win95-start")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self, edge, True)
        GtkLayerShell.set_exclusive_zone(self, -1)  # cover the taskbar too: clicking it also closes the menu
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)

        self.layers = Gtk.Overlay()
        catcher = Gtk.EventBox(visible_window=False)  # the empty area: a click there closes the menu
        catcher.connect("button-press-event", lambda *_: Gtk.main_quit())
        self.layers.add(catcher)
        self.add(self.layers)
        self.levels = []  # open submenus: (panel, folder button that opened it)
        self.pending = None  # hover timer

        main = self.panel([
            ("_Programas", "applications-other", programs_menu()),
            ("_Documentos", "folder-documents", documents_menu()),
            ("_Configuración", "control-center2", settings_menu()),
            ("_Buscar", "system-search", search_menu()),
            ("Ay_uda", "help", lambda: spawn("xdg-open", os.path.join(HOME, ".config/hypr/README.md"))),
            ("_Ejecutar...", "system-run", lambda: spawn(sys.executable, __file__, "run")),
            None,
            (f"Cerrar la _sesión de {USER}...", "system-log-out", lambda: spawn(sys.executable, __file__, "logout")),
            ("_Apagar el sistema...", "system-shutdown", lambda: spawn(sys.executable, __file__, "shutdown")),
        ], level=0, banner=True)
        main.set_halign(Gtk.Align.START)
        main.set_valign(Gtk.Align.END)
        main.set_margin_start(2)
        main.set_margin_bottom(TASKBAR - 2)
        self.layers.add_overlay(main)

        self.connect("key-press-event", self.key)
        self.connect("destroy", Gtk.main_quit)

    def panel(self, entries, level, banner=False):
        """A bevelled box of items; long lists wrap into columns like Windows does."""
        outer = Gtk.Box(); outer.get_style_context().add_class("start-panel")
        inner = Gtk.Box(); inner.get_style_context().add_class("start-inner")
        outer.add(inner)
        if banner:
            inner.pack_start(Banner(), False, False, 0)
        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        inner.pack_start(grid, True, True, 0)
        screen_h = Gdk.Display.get_default().get_monitor(0).get_geometry().height
        rows = max(1, (screen_h - TASKBAR - 20) // 24)
        for n, entry in enumerate(entries):
            if entry is None:
                w = Gtk.Box(); w.get_style_context().add_class("start-sep")
            else:
                w = self.item(*entry, level=level, small=not banner)
            grid.attach(w, n // rows, n % rows, 1, 1)
        stop = Gtk.EventBox(visible_window=False)  # presses on borders, banner and separators must not reach the catcher
        stop.connect("button-press-event", lambda *_: True)
        stop.add(outer)
        stop.show_all()
        return stop

    def item(self, label, icon, target, level, small):
        b = Gtk.Button(relief=Gtk.ReliefStyle.NONE)
        b.get_style_context().add_class("start-item")
        if small:
            b.get_style_context().add_class("small")
        box = Gtk.Box(spacing=6 if small else 10)
        size = 16 if small else 32
        if icon is not None:
            img = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.MENU) if isinstance(icon, Gio.Icon) \
                else Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DND)
            img.set_pixel_size(size)
            box.pack_start(img, False, False, 0)
        else:
            box.pack_start(Gtk.Box(width_request=size), False, False, 0)
        lab = Gtk.Label(xalign=0, use_underline=not small, label=label)
        lab.set_size_request(150 if not small else 120, -1)
        box.pack_start(lab, True, True, 0)
        b.add(box)
        b.folder = isinstance(target, list)
        if b.folder:
            box.pack_end(Gtk.Label(label="▸"), False, False, 0)
            b.connect("clicked", lambda w: self.open(w, target, level + 1))
        elif target is None:
            b.set_sensitive(False)
        else:
            b.connect("clicked", lambda *_: (target(), Gtk.main_quit()))
        b.connect("enter-notify-event", lambda w, _e: self.hover(w, target, level))
        b.connect("leave-notify-event", lambda *_: self.cancel_hover())
        return b

    def hover(self, button, target, level):
        self.cancel_hover()
        self.pending = GLib.timeout_add(HOVER_MS, self.hovered, button, target, level)

    def cancel_hover(self):
        if self.pending:
            GLib.source_remove(self.pending)
            self.pending = None

    def hovered(self, button, target, level):
        self.pending = None
        if button.folder:
            self.open(button, target, level + 1)
        else:
            self.close_from(level)  # resting on a plain item closes the deeper submenus
        return False

    def open(self, button, entries, level):
        """Show entries as submenu number `level` next to button (no-op if it is already the one open there)."""
        if len(self.levels) >= level and self.levels[level - 1][1] is button:
            return
        self.close_from(level - 1)
        panel = self.panel(entries, level)
        x, y = button.translate_coordinates(self.layers, 0, 0)
        _, nat = panel.get_preferred_size()
        width, height = self.layers.get_allocated_width(), self.layers.get_allocated_height()
        x = min(x + button.get_allocated_width() - 2, width - nat.width)
        y = max(0, min(y - 3, height - TASKBAR - nat.height))  # grow upwards when it does not fit
        panel.set_halign(Gtk.Align.START)
        panel.set_valign(Gtk.Align.START)
        panel.set_margin_start(x)
        panel.set_margin_top(y)
        self.layers.add_overlay(panel)
        button.get_style_context().add_class("open")
        self.levels.append((panel, button))

    def close_from(self, level):
        """Close the submenus deeper than `level` (0 = all of them)."""
        while len(self.levels) > level:
            panel, button = self.levels.pop()
            button.get_style_context().remove_class("open")
            panel.destroy()

    def key(self, _w, e):
        focus = self.get_focus()
        if e.keyval == Gdk.KEY_Escape:
            if not self.levels:
                Gtk.main_quit()
            else:
                _, button = self.levels[-1]
                self.close_from(len(self.levels) - 1)
                button.grab_focus()
        elif e.keyval in (Gdk.KEY_Right, Gdk.KEY_KP_Right) and getattr(focus, "folder", False):
            focus.clicked()
            self.levels[-1][0].child_focus(Gtk.DirectionType.TAB_FORWARD)
        elif e.keyval in (Gdk.KEY_Left, Gdk.KEY_KP_Left) and self.levels:
            _, button = self.levels[-1]
            self.close_from(len(self.levels) - 1)
            button.grab_focus()
        elif e.keyval in (Gdk.KEY_Up, Gdk.KEY_Down) and not isinstance(focus, Gtk.Button):
            self.layers.child_focus(Gtk.DirectionType.TAB_FORWARD)
        else:
            return False
        return True


def dialog(title, icon, text):
    d = Gtk.Dialog(title=title)
    d.set_resizable(False)
    area = d.get_content_area()
    area.set_border_width(10)
    row = Gtk.Box(spacing=14)
    img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
    img.set_pixel_size(32)
    img.set_valign(Gtk.Align.START)
    row.pack_start(img, False, False, 0)
    body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    body.pack_start(Gtk.Label(label=text, xalign=0, wrap=True, max_width_chars=44), False, False, 0)
    row.pack_start(body, True, True, 0)
    area.pack_start(row, True, True, 0)
    return d, body


def run_dialog():
    d, body = dialog("Ejecutar", "system-run",
                     "Escriba el nombre de un programa, carpeta, documento o recurso de Internet, y se abrirá.")
    line = Gtk.Box(spacing=8)
    line.pack_start(Gtk.Label(label="_Abrir:", use_underline=True), False, False, 0)
    entry = Gtk.Entry(activates_default=True, width_chars=34)
    line.pack_start(entry, True, True, 0)
    body.pack_start(line, False, False, 0)
    d.add_button("Aceptar", Gtk.ResponseType.OK)
    d.add_button("Cancelar", Gtk.ResponseType.CANCEL)
    d.set_default_response(Gtk.ResponseType.OK)
    d.show_all()
    if d.run() == Gtk.ResponseType.OK and entry.get_text().strip():
        cmd = entry.get_text().strip()
        if "://" in cmd or os.path.exists(os.path.expanduser(cmd)):
            spawn("xdg-open", os.path.expanduser(cmd))
        else:
            spawn("sh", "-c", cmd)


def shutdown_dialog():
    d, body = dialog("Apagar el sistema", "system-shutdown", "¿Está seguro de que desea:")
    options = [("_Apagar el equipo", ["systemctl", "poweroff"]),
               ("_Reiniciar el equipo", ["systemctl", "reboot"]),
               ("_Suspender el equipo", ["systemctl", "suspend"]),
               ("_Cerrar todos los programas e iniciar la sesión como otro usuario",
                ["hyprctl", "dispatch", "hl.dsp.exit()"])]
    group = None
    radios = []
    for label, argv in options:
        r = Gtk.RadioButton.new_with_mnemonic_from_widget(group, label)
        group = group or r
        radios.append((r, argv))
        body.pack_start(r, False, False, 0)
    d.add_button("_Sí", Gtk.ResponseType.YES)
    d.add_button("_No", Gtk.ResponseType.NO)
    d.set_default_response(Gtk.ResponseType.YES)
    d.show_all()
    if d.run() == Gtk.ResponseType.YES:
        spawn(*next(argv for r, argv in radios if r.get_active()))


def logout_dialog():
    d, _ = dialog("Cerrar sesión", "system-log-out", "¿Está seguro de que desea cerrar la sesión?")
    d.add_button("_Sí", Gtk.ResponseType.YES)
    d.add_button("_No", Gtk.ResponseType.NO)
    d.show_all()
    if d.run() == Gtk.ResponseType.YES:
        spawn("hyprctl", "dispatch", "hl.dsp.exit()")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "menu"
    GLib.set_prgname("win95-start" if mode == "menu" else "win95-dialog")  # Wayland app_id for the window rules
    css()
    if mode == "menu":
        w = StartMenu()
        w.show_all()
        Gtk.main()
    else:
        {"run": run_dialog, "shutdown": shutdown_dialog, "logout": logout_dialog}[mode]()


if __name__ == "__main__":
    main()
