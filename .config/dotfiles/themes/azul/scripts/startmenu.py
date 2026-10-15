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
.start-panel { background: #c0c0c0; border-style: solid; border-width: 1px 2px 2px 1px;
               border-color: #dfdfdf #000000 #000000 #dfdfdf; padding: 1px; }
.start-inner { border-style: solid; border-width: 1px; border-color: #ffffff #808080 #808080 #ffffff; }
button.start-item { background: #c0c0c0; background-image: none; border: none; border-radius: 0; box-shadow: none;
                    padding: 3px 6px 3px 4px; min-height: 30px; outline: none; }
button.start-item:hover, button.start-item.open { background: #000080; }
button.start-item label { color: #000000; font-size: 16px; }
button.start-item:hover label, button.start-item.open label { color: #ffffff; }
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


def spawn(*argv):
    subprocess.Popen(argv, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def css():
    p = Gtk.CssProvider()
    p.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def menu_item(label, icon=None, action=None, submenu=None):
    item = Gtk.MenuItem()
    box = Gtk.Box(spacing=6)
    if icon is not None:
        img = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.MENU) if isinstance(icon, Gio.Icon) \
            else Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        img.set_pixel_size(16)
        box.pack_start(img, False, False, 0)
    box.pack_start(Gtk.Label(label=label, xalign=0), True, True, 0)
    item.add(box)
    if submenu is not None:
        item.set_submenu(submenu)
    if action is not None:
        item.connect("activate", lambda *_: (action(), Gtk.main_quit()))
    return item


def programs_menu():
    groups = {}
    for app in Gio.AppInfo.get_all():
        if not app.should_show() or not isinstance(app, Gio.DesktopAppInfo):
            continue
        cats = (app.get_categories() or "").split(";")
        key = next((c for c, _, _ in CATEGORIES if c in cats or (c == "AudioVideo" and {"Audio", "Video"} & set(cats))),
                   "Other")
        groups.setdefault(key, []).append(app)
    menu = Gtk.Menu()
    folders = [(name, icon, groups.pop(c)) for c, name, icon in CATEGORIES if c in groups]
    if "Other" in groups:
        folders.append(("Otros", "applications-other", groups.pop("Other")))
    for name, icon, apps in folders:
        sub = Gtk.Menu()
        for app in sorted(apps, key=lambda a: a.get_display_name().lower()):
            sub.append(menu_item(app.get_display_name(), app.get_icon() or "application-x-executable",
                                 lambda a=app: spawn("gtk-launch", a.get_id())))
        menu.append(menu_item(name, icon, submenu=sub))
    return menu


def documents_menu():
    menu = Gtk.Menu()
    menu.append(menu_item("Mis documentos", "folder-documents", lambda: spawn("xdg-open", os.path.join(HOME, "Documents"))))
    menu.append(Gtk.SeparatorMenuItem())
    items = [i for i in Gtk.RecentManager.get_default().get_items() if i.exists()]
    items.sort(key=lambda i: i.get_modified(), reverse=True)
    for info in items[:12]:
        menu.append(menu_item(info.get_display_name(), info.get_gicon(), lambda u=info.get_uri(): spawn("xdg-open", u)))
    if not items:
        empty = menu_item("(Vacío)")
        empty.set_sensitive(False)
        menu.append(empty)
    return menu


def settings_menu():
    menu = Gtk.Menu()
    for label, icon, argv in [
        ("Panel de control", "preferences-system", ["systemsettings"]),
        ("Pantalla", "preferences-desktop-display", ["systemsettings", "kcm_kscreen"]),
        ("Red", "network-workgroup", ["systemsettings", "kcm_networkmanagement"]),
        ("Sonido", "audio-volume-high", ["pavucontrol"]),
        ("Bluetooth", "bluetooth-active", ["systemsettings", "kcm_bluetooth"]),
    ]:
        menu.append(menu_item(label, icon, lambda a=argv: spawn(*a)))
    return menu


def search_menu():
    menu = Gtk.Menu()
    menu.append(menu_item("Archivos o carpetas...", "system-search", lambda: spawn("thunar", HOME)))
    menu.append(menu_item("Programas...", "applications-other", lambda: spawn("fuzzel")))
    return menu


class Banner(Gtk.DrawingArea):
    """The vertical "Windows98" strip on the left of the menu."""

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
        layout.set_markup("<span font_family='Arial' weight='heavy' size='13pt' foreground='#ffffff'>Windows</span>"
                          "<span font_family='Arial' size='13pt' foreground='#c0c0c0'>98</span>", -1)
        PangoCairo.show_layout(cr, layout)


class StartMenu(Gtk.Window):
    def __init__(self):
        super().__init__()
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "win95-start")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, TASKBAR - 2)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, 2)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        self.open_menu = None

        outer = Gtk.Box(); outer.get_style_context().add_class("start-panel")
        inner = Gtk.Box(); inner.get_style_context().add_class("start-inner")
        outer.add(inner)
        inner.pack_start(Banner(), False, False, 0)
        items = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        inner.pack_start(items, True, True, 0)
        self.add(outer)

        entries = [
            ("_Programas", "applications-other", programs_menu),
            ("_Documentos", "folder-documents", documents_menu),
            ("_Configuración", "control-center2", settings_menu),
            ("_Buscar", "system-search", search_menu),
            ("Ay_uda", "help", lambda: spawn("xdg-open", os.path.join(HOME, ".config/hypr/README.md"))),
            ("_Ejecutar...", "system-run", lambda: spawn(sys.executable, __file__, "run")),
            None,
            (f"Cerrar la _sesión de {USER}...", "system-log-out", lambda: spawn(sys.executable, __file__, "logout")),
            ("_Apagar el sistema...", "system-shutdown", lambda: spawn(sys.executable, __file__, "shutdown")),
        ]
        for entry in entries:
            if entry is None:
                sep = Gtk.Box(); sep.get_style_context().add_class("start-sep")
                items.pack_start(sep, False, False, 0)
                continue
            label, icon, target = entry
            items.pack_start(self.item(label, icon, target), False, False, 0)

        self.connect("key-press-event", lambda _w, e: e.keyval == Gdk.KEY_Escape and Gtk.main_quit())
        self.connect("focus-out-event", lambda *_: GLib.timeout_add(150, self.maybe_close))
        self.connect("destroy", Gtk.main_quit)

    def item(self, label, icon, target):
        b = Gtk.Button(relief=Gtk.ReliefStyle.NONE)
        b.get_style_context().add_class("start-item")
        box = Gtk.Box(spacing=10)
        img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DND)
        img.set_pixel_size(32)
        box.pack_start(img, False, False, 0)
        lab = Gtk.Label(xalign=0, use_underline=True, label=label)
        lab.set_size_request(150, -1)
        box.pack_start(lab, True, True, 0)
        builds_menu = target in (programs_menu, documents_menu, settings_menu, search_menu)
        if builds_menu:
            box.pack_end(Gtk.Label(label="▸"), False, False, 0)
            b.connect("clicked", lambda w: self.popup(w, target()))
            b.connect("enter-notify-event", lambda w, _e: GLib.timeout_add(250, self.hover_popup, w, target))
        else:
            b.connect("clicked", lambda *_: (target(), Gtk.main_quit()))
        b.add(box)
        return b

    def hover_popup(self, w, target):
        if w.get_state_flags() & Gtk.StateFlags.PRELIGHT and (self.open_menu is None or self.open_menu[0] is not w):
            self.popup(w, target())
        return False

    def popup(self, widget, menu):
        if self.open_menu:
            self.open_menu[1].popdown()
        menu.show_all()
        widget.get_style_context().add_class("open")
        menu.connect("deactivate", lambda *_: (widget.get_style_context().remove_class("open"),
                                               setattr(self, "open_menu", None)))
        self.open_menu = (widget, menu)
        menu.popup_at_widget(widget, Gdk.Gravity.NORTH_EAST, Gdk.Gravity.NORTH_WEST, None)

    def maybe_close(self):
        if self.open_menu is None and not self.is_active():
            Gtk.main_quit()
        return False


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
