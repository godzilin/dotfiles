#!/usr/bin/env python3
"""Rain falling on the desktop of the "morado" theme: a transparent layer over the wallpaper and under the windows.
It only draws while the active workspace is empty, so it costs nothing while working.
  lluvia.py          the daemon (theme.json "daemons")
  lluvia.py --test   self-check"""
import json
import random
import subprocess
import sys

W, H = 1920, 1200
DROPS, FPS = 140, 20
SLANT = 0.14  # same angle as the wallpaper's rain


def new_drop(rng, anywhere=False):
    depth = rng.uniform(0.35, 1.0)  # far drops are slower, shorter and fainter
    return [rng.uniform(0, W + 120), rng.uniform(-H, H) if anywhere else rng.uniform(-200, -20), depth]


def step(drops, rng):
    for d in drops:
        speed = 34 * d[2]
        d[1] += speed
        d[0] -= speed * SLANT
        if d[1] > H:
            d[:] = new_drop(rng)


def empty_workspace():
    out = subprocess.run(["hyprctl", "activeworkspace", "-j"], capture_output=True, text=True).stdout
    return json.loads(out or "{}").get("windows", 1) == 0


def daemon():
    import cairo
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GLib, Gtk, GtkLayerShell as Shell

    rng = random.Random()
    drops = [new_drop(rng, True) for _ in range(DROPS)]
    state = {"on": True}

    win = Gtk.Window()
    Shell.init_for_window(win)
    Shell.set_layer(win, Shell.Layer.BOTTOM)  # hyprpaper restarts on the background layer and would land on top
    Shell.set_namespace(win, "lluvia")
    for edge in (Shell.Edge.TOP, Shell.Edge.BOTTOM, Shell.Edge.LEFT, Shell.Edge.RIGHT):
        Shell.set_anchor(win, edge, True)
    Shell.set_exclusive_zone(win, -1)
    win.set_app_paintable(True)
    win.set_visual(win.get_screen().get_rgba_visual())

    def draw(_, c):
        c.set_operator(cairo.OPERATOR_CLEAR)
        c.paint()
        c.set_operator(cairo.OPERATOR_OVER)
        if not state["on"]:
            return
        c.set_line_width(1)
        for x, y, depth in drops:
            length = 46 * depth
            c.set_source_rgba(0.77, 0.73, 0.86, 0.34 * depth)
            c.move_to(x, y)
            c.line_to(x - length * SLANT, y + length)
            c.stroke()

    def tick():
        if state["on"]:
            step(drops, rng)
            win.queue_draw()
        return True

    def check():
        on = empty_workspace()
        if on != state["on"]:
            state["on"] = on
            win.queue_draw()  # clears the last frame when it stops
        return True

    win.connect("draw", draw)
    win.connect("realize", lambda w: w.get_window().input_shape_combine_region(cairo.Region(), 0, 0))
    GLib.timeout_add(1000 // FPS, tick)
    GLib.timeout_add_seconds(1, check)
    win.show_all()
    Gtk.main()


def test():
    rng = random.Random(1)
    drops = [new_drop(rng, True) for _ in range(DROPS)]
    start = [d[:] for d in drops]
    for _ in range(300):
        step(drops, rng)
    assert all(d[1] <= H + 40 for d in drops) and drops != start
    d = [10.0, 10.0, 1.0]
    step([d], rng)
    assert d[1] > 10 and d[0] < 10, "falls down and to the left"
    print("ok")


if __name__ == "__main__":
    test() if sys.argv[1:] == ["--test"] else daemon()
