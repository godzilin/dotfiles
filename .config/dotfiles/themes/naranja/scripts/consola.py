#!/usr/bin/env python3
"""The bridge console of the "naranja" theme: a layer under the windows, shown while the 0-consola.png plate is the pinned
wallpaper. The laptop is the ship: real CPU, temperature, memory, disk, battery and network as its systems, uptime as the
mission clock, a log of what actually changed, and a wireframe of the hull that turns a step at a time, as a plotter would.
  consola.py                   the daemon (theme.json "daemons")
  consola.py --png FILE        one frame to a file
  consola.py --test            self-check"""
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

import cairo

W, H = 1920, 1200
TICK = 3  # seconds between redraws
PIN = Path.home() / ".cache/nostromo/wallpaper-naranja"
PLATE = "0-consola.png"
STENCIL, MONO = "Saira Stencil One", "BlexMono Nerd Font"
BG0, BG1, LINE, MUTED, SUB, TEXT = "121110", "24211b", "3d382d", "857c69", "b3a891", "e8dfc8"
AMBER, YELLOW, ORANGE, RED = "e9a23b", "e0c36a", "d9652b", "c8553d"
STRIPES = (YELLOW, AMBER, ORANGE, RED)
LEFT, RIGHT, PANEL_W = 56, 1484, 380


def rgb(h, a=1.0):
    return int(h[:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:], 16) / 255, a


def text(c, x, y, s, size, colour=SUB, a=1.0, face=MONO, anchor=0.0):
    c.select_font_face(face)
    c.set_font_size(size)
    c.move_to(x - c.text_extents(s).x_advance * anchor, y)
    c.set_source_rgba(*rgb(colour, a))
    c.show_text(s)


def hazard(c, x, y, w, h):
    c.save()
    c.rectangle(x, y, w, h)
    c.clip()
    c.set_source_rgba(*rgb(YELLOW, 0.75))
    for k in range(int(x - h), int(x + w + h), 2 * int(h)):
        c.move_to(k, y + h)
        c.line_to(k + h, y)
        c.line_to(k + 2 * h, y)
        c.line_to(k + h, y + h)
        c.close_path()
    c.fill()
    c.restore()


def panel(c, x, y, h, title):
    c.set_line_width(1)
    c.set_source_rgba(*rgb(LINE))
    c.rectangle(x + 0.5, y + 0.5, PANEL_W, h)
    c.stroke()
    c.set_source_rgba(*rgb(BG1))
    c.rectangle(x + 1, y + 1, PANEL_W - 1, 30)
    c.fill()
    text(c, x + 14, y + 23, title, 18, AMBER, face=STENCIL)
    for i, ink in enumerate(STRIPES):
        c.set_source_rgba(*rgb(ink))
        c.rectangle(x + PANEL_W - 54 + i * 11, y + 10, 8, 12)
        c.fill()


def fixed():
    """Everything that never moves, as a surface."""
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    c.set_source_rgba(*rgb(BG0))
    c.paint()
    c.set_line_width(1)
    c.set_source_rgba(*rgb(LINE, 0.28))
    for x in range(0, W, 48):
        c.move_to(x + 0.5, 0)
        c.line_to(x + 0.5, H)
    for y in range(0, H, 48):
        c.move_to(0, y + 0.5)
        c.line_to(W, y + 0.5)
    c.stroke()
    text(c, LEFT, 104, "NOSTROMO", 46, TEXT, face=STENCIL)
    text(c, LEFT + 268, 92, "GZ-01", 16, AMBER)
    text(c, LEFT + 268, 110, "HEAVY HAULER", 13, MUTED)
    for i, ink in enumerate(STRIPES):  # the theme's four stripes run the width of the console
        c.set_source_rgba(*rgb(ink, 0.9))
        c.rectangle(LEFT, 120 + i * 4, W - 2 * LEFT, 3)
        c.fill()
    panel(c, LEFT, 160, 300, "REACTOR")
    panel(c, LEFT, 484, 180, "LIFE SUPPORT")
    panel(c, LEFT, 688, 180, "CARGO HOLD")
    panel(c, RIGHT, 160, 300, "POWER CELLS")
    panel(c, RIGHT, 484, 384, "COMMS")
    text(c, W / 2, 880, "HULL PLAN  1:400", 13, MUTED, anchor=0.5)
    hazard(c, LEFT, 900, W - 2 * LEFT, 14)
    text(c, LEFT, 952, "MISSION ELAPSED", 13, MUTED)
    text(c, 760, 952, "SHIP LOG", 13, MUTED)
    return s


# ---- telemetry: nothing here is invented ------------------------------------------------------------------------------


def read(path, default=""):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return default


def hwmon(name, leaf):
    for d in Path("/sys/class/hwmon").glob("hwmon*"):
        if read(d / "name") == name:
            return read(d / leaf)
    return ""


def cpu_times(stat):
    fields = [int(v) for v in stat.splitlines()[0].split()[1:]]
    return sum(fields), fields[3] + fields[4]


def percent(before, after):
    total = after[0] - before[0]
    return 100 * (total - (after[1] - before[1])) / total if total > 0 else 0.0


def net_bytes(dev):
    """(iface, rx, tx) of the busiest link in /proc/net/dev."""
    best = ("", 0, 0)
    for line in dev.splitlines()[2:]:
        name, data = line.split(":")
        v = data.split()
        if name.strip() != "lo" and int(v[0]) + int(v[8]) > best[1] + best[2]:
            best = (name.strip(), int(v[0]), int(v[8]))
    return best


def rate(n):
    for unit in ("B/S", "KB/S", "MB/S"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.0f} GB/S"


def elapsed(s):
    s = int(s)
    return f"T+ {s // 3600:03d}:{s // 60 % 60:02d}:{s % 60:02d}"


class Ship:
    def __init__(self):
        self.cpu = cpu_times(read("/proc/stat"))
        self.net = net_bytes(read("/proc/net/dev"))
        self.when = time.monotonic()
        self.load = deque([0.0] * 60, 60)
        self.down, self.up = deque([0.0] * 60, 60), deque([0.0] * 60, 60)
        self.log = deque(maxlen=7)
        self.state = {}
        self.note("SYSTEMS ONLINE")
        self.sample()

    def note(self, msg):
        self.log.append((time.strftime("%H:%M"), msg))

    def watch(self, key, value, messages):
        """Log a state change; the first reading only sets the baseline."""
        if key in self.state and self.state[key] != value and value in messages:
            self.note(messages[value])
        self.state[key] = value

    def sample(self):
        now = time.monotonic()
        dt = max(now - self.when, 0.1)
        self.when = now
        cpu = cpu_times(read("/proc/stat"))
        self.pct = percent(self.cpu, cpu)
        self.cpu = cpu
        self.load.append(self.pct)
        self.temp = int(hwmon("thinkpad", "temp1_input") or 0) / 1000
        self.fan = int(hwmon("thinkpad", "fan1_input") or 0)
        mem = dict(line.split(":") for line in read("/proc/meminfo").splitlines())
        total, free = int(mem["MemTotal"].split()[0]), int(mem["MemAvailable"].split()[0])
        self.mem_total, self.mem_used = total / 2**20, (total - free) / 2**20
        fs = os.statvfs("/")
        self.disk_total, self.disk_used = fs.f_blocks * fs.f_frsize / 2**30, (fs.f_blocks - fs.f_bavail) * fs.f_frsize / 2**30
        bat = Path("/sys/class/power_supply/BAT0")
        self.bat = int(read(bat / "capacity", "0"))
        self.bat_state = read(bat / "status", "Unknown").upper()
        self.watts = int(read(bat / "power_now", "0")) / 1e6
        iface, rx, tx = net_bytes(read("/proc/net/dev"))
        same = iface == self.net[0]
        self.rx, self.tx = (rx - self.net[1]) / dt if same else 0, (tx - self.net[2]) / dt if same else 0
        self.net = (iface, rx, tx)
        self.iface = iface
        self.link = read(f"/sys/class/net/{iface}/operstate") == "up" if iface else False
        self.down.append(self.rx)
        self.up.append(self.tx)
        self.uptime = float(read("/proc/uptime", "0 0").split()[0])
        self.watch("cells", self.bat_state, {"CHARGING": "MAINS CONNECTED", "DISCHARGING": "RUNNING ON CELLS"})
        self.watch("low", self.bat < 15, {True: "CELLS BELOW 15 %", False: "CELLS RECOVERED"})
        self.watch("hot", self.temp > 85, {True: "REACTOR OVER 85 C", False: "REACTOR COOLING"})
        self.watch("mem", self.mem_used / self.mem_total > 0.9, {True: "LIFE SUPPORT OVER 90 %"})
        self.watch("link", self.link, {True: f"LINK UP {iface.upper()}", False: "LINK LOST"})

    def alerts(self):
        out = []
        if self.bat < 15 and self.bat_state == "DISCHARGING":
            out.append(f"CELLS {self.bat} %")
        if self.temp > 85:
            out.append(f"REACTOR {self.temp:.0f} C")
        if self.mem_used / self.mem_total > 0.9:
            out.append("LIFE SUPPORT")
        if not self.link:
            out.append("NO LINK")
        return out


# ---- the hull ----------------------------------------------------------------------------------------------------------


def box(x0, x1, w, h, y=0.0):
    """Edges of a block along x, width w and height h, centred at height y."""
    pts = [(x, y + sy * h / 2, sz * w / 2) for x in (x0, x1) for sy in (-1, 1) for sz in (-1, 1)]
    return [(pts[a], pts[b]) for a, b in ((0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7))]


def drum(x0, x1, r0, r1, y=0.0, z=0.0, sides=10, rings=2):
    """A cylinder or cone along x."""
    edges = []
    ring = lambda x, r, k: (x, y + r * math.cos(k * math.tau / sides), z + r * math.sin(k * math.tau / sides))
    for n in range(rings + 1):
        f = n / rings
        x, r = x0 + (x1 - x0) * f, r0 + (r1 - r0) * f
        edges += [(ring(x, r, k), ring(x, r, k + 1)) for k in range(sides)]
    edges += [(ring(x0, r0, k), ring(x1, r1, k)) for k in range(0, sides, 2)]
    return edges


def hull():
    """An original heavy hauler: a long spine, a blocky bridge up front, tanks amidships, three engines and a radiator mast."""
    e = box(-4.6, 3.4, 0.7, 0.6) + box(2.4, 4.3, 1.5, 1.0, 0.25) + box(3.0, 3.9, 0.9, 0.5, 1.0)
    e += box(-1.6, 1.8, 2.3, 1.3, -0.1) + box(-0.4, 0.5, 3.4, 0.25, 0.75)
    for z in (-1.15, 1.15):
        e += drum(-3.8, -1.9, 0.55, 0.55, 0.0, z, rings=3)
    for y, z in ((0.45, 0.0), (-0.3, -0.5), (-0.3, 0.5)):
        e += drum(-5.0, -4.5, 0.42, 0.26, y, z, rings=1)
    e += box(-3.3, -3.1, 0.08, 1.8, 1.2) + box(-3.6, -2.8, 2.2, 0.03, 1.9)
    return e


HULL = hull()


def project(p, yaw, tilt=math.radians(-17), scale=92, eye=26.0):
    x, y, z = p
    x, z = x * math.cos(yaw) - z * math.sin(yaw), x * math.sin(yaw) + z * math.cos(yaw)
    y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
    k = scale * eye / (eye + z)
    return W / 2 + x * k, 520 - y * k, z


def wireframe(c, yaw):
    near, far = [], []
    for a, b in HULL:
        p, q = project(a, yaw), project(b, yaw)
        (near if p[2] + q[2] < 0 else far).append((p, q))
    for edges, alpha, width in ((far, 0.33, 1.0), (near, 0.95, 1.3)):
        c.set_line_width(width)
        c.set_source_rgba(*rgb(AMBER, alpha))
        for p, q in edges:
            c.move_to(p[0], p[1])
            c.line_to(q[0], q[1])
        c.stroke()


# ---- the moving part of the console --------------------------------------------------------------------------------


def gauge(c, x, y, value, warn=False, cells=44):
    """A row of lamps."""
    lit = round(value / 100 * cells)
    for i in range(cells):
        on = i < lit
        c.set_source_rgba(*rgb((RED if warn else AMBER) if on else LINE, 1 if on else 0.6))
        c.rectangle(x + i * 8, y, 6, 14)
        c.fill()


def spark(c, x, y, w, h, data, colour, top=None):
    top = top or max(max(data), 1)
    c.set_line_width(1.2)
    c.set_source_rgba(*rgb(colour, 0.9))
    for i, v in enumerate(data):
        px, py = x + i * w / (len(data) - 1), y + h - min(v / top, 1) * h
        c.line_to(px, py) if i else c.move_to(px, py)
    c.stroke()


def row(c, x, y, key, value, colour=TEXT):
    text(c, x + 16, y, key, 14, MUTED)
    text(c, x + PANEL_W - 16, y, value, 14, colour, anchor=1)


def frame(c, base, ship, yaw):
    c.set_source_surface(base, 0, 0)
    c.paint()
    x = LEFT
    hot = ship.temp > 85
    row(c, x, 220, "LOAD", f"{ship.pct:.0f} %")
    gauge(c, x + 16, 232, ship.pct)
    row(c, x, 276, "CORE", f"{ship.temp:.0f} C", RED if hot else TEXT)
    gauge(c, x + 16, 288, min(ship.temp, 100), hot)
    row(c, x, 332, "COOLANT", f"{ship.fan} RPM")
    spark(c, x + 16, 350, PANEL_W - 32, 94, ship.load, AMBER, 100)
    used = 100 * ship.mem_used / ship.mem_total
    row(c, x, 544, "ATMOSPHERE", f"{ship.mem_used:.1f} / {ship.mem_total:.1f} GB")
    gauge(c, x + 16, 556, used, used > 90)
    row(c, x, 610, "RESERVE", f"{100 - used:.0f} %")
    used = 100 * ship.disk_used / ship.disk_total
    row(c, x, 748, "LOADED", f"{ship.disk_used:.0f} / {ship.disk_total:.0f} GB")
    gauge(c, x + 16, 760, used, used > 90)
    row(c, x, 814, "FREE", f"{ship.disk_total - ship.disk_used:.0f} GB")
    x = RIGHT
    low = ship.bat < 15
    row(c, x, 220, "CHARGE", f"{ship.bat} %", RED if low else TEXT)
    gauge(c, x + 16, 232, ship.bat, low)
    row(c, x, 276, "STATE", ship.bat_state)
    row(c, x, 304, "DRAW", f"{ship.watts:.1f} W")
    text(c, x + PANEL_W / 2, 400, f"{ship.bat}", 72, RED if low else AMBER, face=STENCIL, anchor=0.5)
    row(c, x, 544, "LINK", ship.iface.upper() or "NONE", TEXT if ship.link else RED)
    row(c, x, 572, "RX", rate(ship.rx))
    spark(c, x + 16, 588, PANEL_W - 32, 100, ship.down, AMBER)
    row(c, x, 720, "TX", rate(ship.tx))
    spark(c, x + 16, 736, PANEL_W - 32, 100, ship.up, ORANGE)
    wireframe(c, yaw)
    text(c, LEFT, 1040, elapsed(ship.uptime), 72, TEXT, face=STENCIL)
    alerts = ship.alerts()
    if alerts:
        c.set_source_rgba(*rgb(RED))
        c.rectangle(LEFT, 1064, 640, 40)
        c.fill()
        text(c, LEFT + 16, 1092, "WARNING  " + "  ".join(alerts), 20, BG0, face=STENCIL)
    else:
        text(c, LEFT, 1090, "ALL SYSTEMS NOMINAL", 20, AMBER, face=STENCIL)
    for i, (when, msg) in enumerate(ship.log):
        y = 984 + i * 24
        text(c, 760, y, when, 14, MUTED)
        text(c, 830, y, msg, 14, SUB)


def scanlines():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 3)
    c = cairo.Context(s)
    c.set_source_rgba(0, 0, 0, 0.16)
    c.rectangle(0, 2, 1, 1)
    c.fill()
    p = cairo.SurfacePattern(s)
    p.set_extend(cairo.EXTEND_REPEAT)
    return p


def test():
    assert percent((100, 50), (200, 75)) == 75
    assert percent((100, 50), (100, 50)) == 0
    assert net_bytes("a\nb\n    lo: 9 0 0 0 0 0 0 0 9 0\n  wl0: 5 0 0 0 0 0 0 0 7 0\n") == ("wl0", 5, 7)
    assert elapsed(3661) == "T+ 001:01:01" and rate(10) == "10 B/S" and rate(2048) == "2 KB/S"
    assert project((0, 0, 0), 1.0)[:2] == (W / 2, 520)
    for p, q in HULL:  # the hull stays between the side panels at any heading
        for yaw in (0, 0.8, 1.6, 2.4):
            assert LEFT + PANEL_W < project(p, yaw)[0] < RIGHT and 160 < project(p, yaw)[1] < 870, (p, yaw)
    s = Ship.__new__(Ship)
    s.log, s.state = deque(maxlen=7), {}
    s.watch("x", False, {True: "UP"})
    s.watch("x", True, {True: "UP"})
    assert [m for _, m in s.log] == ["UP"]
    print("ok")


def daemon():
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import Gio, GLib, Gtk, GtkLayerShell as Shell

    base, lines, ship = fixed(), scanlines(), Ship()
    yaw = [0.6]
    win = Gtk.Window()
    Shell.init_for_window(win)
    Shell.set_namespace(win, "consola")
    Shell.set_layer(win, Shell.Layer.BOTTOM)  # hyprpaper restarts on the background layer and would land on top
    for edge in (Shell.Edge.TOP, Shell.Edge.BOTTOM, Shell.Edge.LEFT, Shell.Edge.RIGHT):
        Shell.set_anchor(win, edge, True)
    Shell.set_exclusive_zone(win, -1)  # under the bar too
    win.set_app_paintable(True)

    def draw(w, c):
        a = w.get_allocation()
        k = min(a.width / W, a.height / H)
        c.set_source_rgba(*rgb(BG0))
        c.paint()
        c.translate((a.width - W * k) / 2, (a.height - H * k) / 2)
        c.scale(k, k)
        frame(c, base, ship, yaw[0])
        c.set_source(lines)
        c.paint()

    def sync(*_):
        wanted = PIN.is_file() and PIN.read_text().strip().endswith(PLATE)
        win.show_all() if wanted else win.hide()

    def tick():
        ship.sample()  # keeps the log true while hidden
        if win.get_visible():
            yaw[0] += math.radians(1.5)
            win.queue_draw()
        return True

    win.connect("draw", draw)
    monitor = Gio.File.new_for_path(str(PIN)).monitor_file(Gio.FileMonitorFlags.NONE, None)
    monitor.connect("changed", sync)
    sync()
    GLib.timeout_add_seconds(TICK, tick)
    Gtk.main()


def png(path):
    ship = Ship()
    time.sleep(0.3)
    ship.sample()
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    frame(c, fixed(), ship, 0.6)
    c.set_source(scanlines())
    c.paint()
    s.write_to_png(path)


if __name__ == "__main__":
    if "--test" in sys.argv:
        test()
    elif "--png" in sys.argv:
        png(sys.argv[sys.argv.index("--png") + 1])
    else:
        daemon()
