#!/usr/bin/env python3
"""Two analogue VU meters on the desktop of the "naranja" theme, driven by whatever is playing (the default sink's monitor).
A layer under the windows that lets clicks through; with nothing playing the needles rest and it stops redrawing.
  vumetro.py                 the daemon (theme.json "daemons")
  vumetro.py --png FILE      one frame to a file
  vumetro.py --test          self-check"""
import math
import subprocess
import sys
import threading
import time

import cairo
import numpy as np

W, H, GAP = 250, 150, 14
MARGIN_RIGHT, MARGIN_BOTTOM = 32, 92  # clear of the bar, which an exclusive zone of -1 ignores
RATE, CHUNK = 8000, 2 * 2 * 400  # 50 ms of s16le stereo
DB_MIN, DB_MAX = -20.0, 3.0
SPAN = math.radians(74)  # sweep of the needle
OFFSET = 18.0  # dB between digital full scale and the meter's 0 VU


def level(samples):
    """Position 0..1 of the needle for one channel of s16 samples."""
    rms = math.sqrt(float(np.mean(np.square(samples.astype(np.float64))))) / 32768 if len(samples) else 0
    if rms < 1e-5:
        return 0.0
    return min(1.0, max(0.0, (20 * math.log10(rms) + OFFSET - DB_MIN) / (DB_MAX - DB_MIN)))


def needle_angle(pos):
    return -SPAN / 2 + SPAN * pos


def meter(ctx, x, pos):
    ctx.save()
    ctx.translate(x, 0)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(0.08, 0.06, 0.05)
    ctx.fill()
    face = cairo.RadialGradient(W / 2, H * 0.9, 30, W / 2, H * 0.9, W * 0.8)
    face.add_color_stop_rgb(0, 0.98, 0.80, 0.48)
    face.add_color_stop_rgb(1, 0.72, 0.47, 0.20)
    ctx.rectangle(5, 5, W - 10, H - 10)
    ctx.set_source(face)
    ctx.fill()

    cx, cy, r = W / 2, H + 42, 158
    ink = (0.13, 0.09, 0.06)
    red = (0.70, 0.12, 0.08)
    zero = (0 - DB_MIN) / (DB_MAX - DB_MIN)
    for part, colour, width in ((0, ink, 1.5), (1, red, 5)):
        a, b = (0, zero) if part == 0 else (zero, 1)
        ctx.set_source_rgb(*colour)
        ctx.set_line_width(width)
        ctx.arc(cx, cy, r, needle_angle(a) - math.pi / 2, needle_angle(b) - math.pi / 2)
        ctx.stroke()
    ctx.select_font_face("Michroma")
    ctx.set_font_size(9)
    for db in (-20, -10, -7, -5, -3, -2, -1, 0, 1, 2, 3):
        p = (db - DB_MIN) / (DB_MAX - DB_MIN)
        a = needle_angle(p)
        ctx.set_source_rgb(*(red if db > 0 else ink))
        ctx.set_line_width(1.5)
        ctx.move_to(cx + (r + 1) * math.sin(a), cy - (r + 1) * math.cos(a))
        ctx.line_to(cx + (r + 9) * math.sin(a), cy - (r + 9) * math.cos(a))
        ctx.stroke()
        if db in (-20, -10, -5, 0, 3):
            label = str(abs(db))
            ext = ctx.text_extents(label)
            ctx.move_to(cx + (r + 19) * math.sin(a) - ext.width / 2, cy - (r + 19) * math.cos(a) + 4)
            ctx.show_text(label)
    ctx.set_source_rgb(*ink)
    ctx.set_font_size(15)
    ext = ctx.text_extents("VU")
    ctx.move_to(W / 2 - ext.width / 2, H - 48)
    ctx.show_text("VU")

    a = needle_angle(pos)
    ctx.set_source_rgb(0.1, 0.07, 0.05)
    ctx.set_line_width(2)
    ctx.move_to(cx, cy)
    ctx.line_to(cx + (r + 8) * math.sin(a), cy - (r + 8) * math.cos(a))
    ctx.stroke()
    ctx.rectangle(5, H - 22, W - 10, 17)  # the bakelite strip that hides the pivot
    ctx.set_source_rgb(0.08, 0.06, 0.05)
    ctx.fill()
    ctx.restore()


def frame(ctx, left, right):
    meter(ctx, 0, left)
    meter(ctx, W + GAP, right)


class Listener(threading.Thread):
    """Latest level of each channel; respawns parec if the audio server restarts."""
    daemon = True
    left = right = 0.0

    def run(self):
        cmd = ["parec", "-d", "@DEFAULT_MONITOR@", "--format=s16le", f"--rate={RATE}", "--channels=2", "--latency-msec=50"]
        while True:
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as p:
                while chunk := p.stdout.read(CHUNK):
                    s = np.frombuffer(chunk, dtype=np.int16)
                    self.left, self.right = level(s[::2]), level(s[1::2])
            self.left = self.right = 0.0
            time.sleep(2)


def daemon():
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GLib, Gtk, GtkLayerShell as Shell

    win = Gtk.Window()
    Shell.init_for_window(win)
    Shell.set_layer(win, Shell.Layer.BOTTOM)  # hyprpaper restarts on the background layer and would land on top
    Shell.set_namespace(win, "vumetro")
    Shell.set_anchor(win, Shell.Edge.RIGHT, True)
    Shell.set_anchor(win, Shell.Edge.BOTTOM, True)
    Shell.set_margin(win, Shell.Edge.RIGHT, MARGIN_RIGHT)
    Shell.set_margin(win, Shell.Edge.BOTTOM, MARGIN_BOTTOM)
    Shell.set_exclusive_zone(win, -1)
    win.set_size_request(2 * W + GAP, H)
    win.set_app_paintable(True)

    listener = Listener()
    listener.start()
    needles = [0.0, 0.0]

    def tick():
        target = listener.left, listener.right
        moved = False
        for i in (0, 1):
            step = (target[i] - needles[i]) * 0.3  # the slow swing of a real movement
            if abs(step) > 0.001:
                needles[i] += step
                moved = True
        if moved:
            win.queue_draw()
        return True

    def draw(_, ctx):
        frame(ctx, *needles)

    win.connect("draw", draw)
    win.connect("realize", lambda w: w.get_window().input_shape_combine_region(cairo.Region(), 0, 0))
    GLib.timeout_add(33, tick)
    win.show_all()
    Gtk.main()


def test():
    silence = np.zeros(400, dtype=np.int16)
    assert level(silence) == 0
    full = np.full(400, 32767, dtype=np.int16)
    assert level(full) == 1
    zero_vu = np.full(400, int(32768 * 10 ** (-OFFSET / 20)), dtype=np.int16)
    assert abs(level(zero_vu) - (0 - DB_MIN) / (DB_MAX - DB_MIN)) < 0.01
    assert needle_angle(0) < 0 < needle_angle(1)
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        test()
    elif sys.argv[1:2] == ["--png"]:
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 2 * W + GAP, H)
        frame(cairo.Context(surface), 0.45, 0.8)
        surface.write_to_png(sys.argv[2])
    else:
        daemon()
