#!/usr/bin/env python3
"""A working astrolabe on the desktop of the "dorado" theme: a layer under the windows, drawn over the b-astrolabio plate
while that plate is the pinned wallpaper (the selector hides it by pinning another or going random). Once a minute the
rete turns to the real sidereal time for the latitude in weather.conf: stars above the horizon are lit, the rest stay
dim, the Sun and Moon sit at their true places and the rule reads the solar hour on the limb. Between minutes it costs
nothing; the fixed plate is one cached surface.
  instrumento.py                 the daemon (theme.json "daemons")
  instrumento.py --png FILE [ISO time]   one frame to a file
  instrumento.py --test          self-check of the projection"""
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import cairo

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "wallpapers")]
import astrolabio as A  # noqa: E402
import luna as L  # noqa: E402

W, H, TAU = A.W, A.H, A.TAU
CX, CY, R = W / 2, H / 2 + 15, 480  # clear of the bar
AH = (0x8a, 0x70, 0x42)  # the darker brass of the rule
STARS = {name: A.S[name][:2] for name in ("Vega", "Arcturus", "Capella", "Deneb", "Regulus", "Aldebaran", "Betelgeuse", "Rigel", "Pollux", "Dubhe")}
STARS["Altair"] = (19.85, 8.87)
PIN = Path.home() / ".cache/nostromo/wallpaper-dorado"
PLATE = "b-astrolabio.jpg"


def radii(r=R):
    """Plate radius of the equator and of the Tropic of Cancer."""
    re = r / math.tan(math.radians(90 + L.EPS) / 2)
    return re, re * math.tan(math.radians(90 - L.EPS) / 2)


def place(ra, dec, lst, re):
    """Stereographic point of (ra, dec, degrees): meridian towards the top of the screen, east on the left, sky turning clockwise."""
    r = re * math.tan(math.radians(90 - dec) / 2)
    h = math.radians(lst - ra)
    return CX + r * math.sin(h), CY - r * math.cos(h)


def ecliptic_circle(lst):
    """Centre and radius of the ecliptic: its far side touches Capricorn at right ascension 18 h."""
    re, rc = radii()
    x, y = place(270, 90, lst, re)  # the pole, i.e. the centre
    d = (R - rc) / 2
    h = math.radians(lst - 270)
    return x + d * math.sin(h), y - d * math.cos(h), (R + rc) / 2


def fixed(lat):
    """The plate that does not move, as a surface."""
    s, c = A.sheet(CX, CY)
    A.dust(c, 500, 2)
    A.tympan(c, CX, CY, R, math.radians(lat))
    return s


def rete(c, when, lat, lon, place_name):
    re, _ = radii()
    lst = L.sidereal(when, lon)
    sun = L.equatorial(L.sun_lon(when))
    sun_alt = L.altitude(*sun, lst, lat)
    if sun_alt > 0:  # daytime: the sky above the horizon takes a little warmth
        phi = math.radians(lat)
        c.save()
        c.arc(CX, CY, R, 0, TAU)
        c.clip()
        c.arc(CX, CY - re * math.cos(phi) / math.sin(phi), re / math.sin(phi), 0, TAU)
        c.set_source_rgba(*A.rgb(A.BRASS, 0.035))
        c.fill()
        c.restore()
    ex, ey, er = ecliptic_circle(lst)
    A.ring(c, CX, CY, R - 1, A.BRASS, 0.85, 2.4)
    A.ring(c, ex, ey, er, A.BRASS, 0.85, 2.4)
    A.ring(c, ex, ey, er - 22, A.BRASS, 0.5, 1)

    # the zodiac at true longitudes, which the projection spaces unevenly
    def at(lam, r_):
        x, y = place(*L.equatorial(lam), lst, re)
        t = math.atan2(y - ey, x - ex)
        return ex + r_ * math.cos(t), ey + r_ * math.sin(t), t

    c.set_source_rgba(*A.rgb(A.BRASS, 0.6))
    for lam in range(0, 360, 5):
        x0, y0, _ = at(lam, er)
        x1, y1, _ = at(lam, er - (22 if lam % 30 == 0 else 6))
        c.move_to(x0, y0)
        c.line_to(x1, y1)
    c.set_line_width(1)
    c.stroke()
    for i, name in enumerate(L.SIGNS):
        _, _, t = at(i * 30 + 15, er)
        A.radial_text(c, ex, ey, er - 16, t, name, 12.5, A.BRASS, 0.8, "Alegreya")

    # spokes that hold the rete together
    rot = math.radians(lst)
    c.set_line_width(1.8)
    c.set_source_rgba(*A.rgb(A.BRASS, 0.75))
    for t0 in (-1.1, -0.2, 0.75, 1.75, 2.75, 3.75, 4.7):
        t = t0 + rot
        d = (ex - CX) * math.cos(t) + (ey - CY) * math.sin(t)
        r_ = d + math.sqrt(d * d - (ex - CX) ** 2 - (ey - CY) ** 2 + (er - 22) ** 2)  # where the ray meets the inner circle
        c.move_to(CX + r_ * math.cos(t), CY + r_ * math.sin(t))
        c.line_to(CX + 70 * math.cos(t), CY + 70 * math.sin(t))
    c.stroke()

    # star pointers: flames of brass; lit above the horizon
    for name, (ra_h, dec) in STARS.items():
        ra = ra_h * 15
        px, py = place(ra, dec, lst, re)
        up = L.altitude(ra, dec, lst, lat) > 0
        t = math.atan2(py - CY, px - CX)
        foot = (px - 34 * math.cos(t - 0.45), py - 34 * math.sin(t - 0.45))
        c.move_to(px, py)
        c.curve_to(foot[0] + 8 * math.cos(t + 1.2), foot[1] + 8 * math.sin(t + 1.2), foot[0], foot[1], foot[0] - 12 * math.cos(t), foot[1] - 12 * math.sin(t))
        c.set_line_width(2.4)
        c.set_source_rgba(*A.rgb(A.BRASS, 0.85 if up else 0.4))
        c.stroke()
        A.star(c, px, py, 2.0 if up else 3.8, A.GOLD if up else A.MUTED)
        right = px >= CX
        A.text(c, px + (9 if right else -9), py + 16, name, 14, A.PARCH if up else A.MUTED, 0.85 if up else 0.5, "Alegreya",
               cairo.FONT_SLANT_ITALIC, anchor=0 if right else 1)

    for r_ in (70, 26):
        A.ring(c, CX, CY, r_, A.BRASS, 0.7, 1.5)

    # the rule, laid on the Sun: its point reads the solar hour on the limb
    sx, sy = place(*sun, lst, re)
    t = math.atan2(sy - CY, sx - CX)
    dx, dy, nx, ny = math.cos(t), math.sin(t), -math.sin(t), math.cos(t)
    far = R + 40
    c.move_to(CX - far * dx + 8 * nx, CY - far * dy + 8 * ny)
    c.line_to(CX + far * dx + 2 * nx, CY + far * dy + 2 * ny)
    c.line_to(CX + far * dx - 2 * nx, CY + far * dy - 2 * ny)
    c.line_to(CX - far * dx - 8 * nx, CY - far * dy - 8 * ny)
    c.close_path()
    c.set_source_rgba(*A.rgb(AH, 0.8))
    c.fill()
    c.arc(CX, CY, 9, 0, TAU)
    c.set_source_rgba(*A.rgb(A.BRASS, 0.95))
    c.fill()

    # Moon, then the Sun on top of the rule
    mlon, mlat = L.moon_ecl(when)
    A.moon_disc(c, *place(*L.equatorial(mlon, mlat), lst, re), 11, L.age(when), 0)
    A.ring(c, *place(*L.equatorial(mlon, mlat), lst, re), 12.5, A.BRASS, 0.7)
    for k in range(12):
        a = k * TAU / 12
        c.move_to(sx + 12 * math.cos(a), sy + 12 * math.sin(a))
        c.line_to(sx + (20 if k % 2 else 25) * math.cos(a), sy + (20 if k % 2 else 25) * math.sin(a))
    c.set_line_width(1.6)
    c.set_source_rgba(*A.rgb(A.GOLD, 0.95))
    c.stroke()
    c.arc(sx, sy, 10, 0, TAU)
    c.fill()

    hours = ((L.sidereal(when, lon) - sun[0]) / 15 + 12) % 24
    sign, deg = L.sign(L.sun_lon(when))
    A.plate(c, "VIVA", f"Astrolabio de {place_name}",
            f"Sol en {sign} {deg}°, a {sun_alt:.0f}° de altura  ·  hora solar {int(hours):02d}:{int(hours % 1 * 60):02d}")


def frame(c, base, when, lat, lon, place_name):
    c.set_source_surface(base, 0, 0)
    c.paint()
    rete(c, when, lat, lon, place_name)


def test():
    lst = 123.0
    re, rc = radii()
    assert abs(math.hypot(*(a - b for a, b in zip(place(0, -L.EPS, lst, re), (CX, CY)))) - R) < 1e-6, "Capricorn is the edge"
    ex, ey, er = ecliptic_circle(lst)
    for lam in range(0, 360, 7):
        x, y = place(*L.equatorial(lam), lst, re)
        assert abs(math.hypot(x - ex, y - ey) - er) < 0.1, lam
    # the horizon of the plate: a point of altitude 0 falls on the circle tympan() draws, on the side towards the top
    lat = 43.26
    for h in (-70, -20, 40):
        ra = lst - h
        # the declination that puts hour angle h on the horizon: tan(dec) = -cos(h) / tan(lat)
        dec = math.degrees(math.atan(-L.cosd(h) / math.tan(math.radians(lat))))
        assert abs(L.altitude(ra, dec, lst, lat)) < 1e-6
        x, y = place(ra, dec, lst, re)
        yc, r0 = re / math.tan(math.radians(lat)), re / L.sind(lat)
        assert abs(math.hypot(x - CX, y - (CY - yc)) - r0) < 1e-6, h
    assert place(lst, 0, lst, re)[1] < CY, "meridian at the top"
    assert place(lst + 30, 0, lst, re)[0] < CX, "east on the left"
    print("ok")


def daemon():
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import Gio, GLib, Gtk, GtkLayerShell as Shell

    lat, lon, name = L.location()
    base = fixed(lat)
    win = Gtk.Window()
    Shell.init_for_window(win)
    Shell.set_namespace(win, "astrolabio")
    Shell.set_layer(win, Shell.Layer.BOTTOM)  # hyprpaper restarts on the background layer and would land on top
    for edge in (Shell.Edge.TOP, Shell.Edge.BOTTOM, Shell.Edge.LEFT, Shell.Edge.RIGHT):
        Shell.set_anchor(win, edge, True)
    Shell.set_exclusive_zone(win, -1)  # under the bar too
    win.set_app_paintable(True)

    def draw(w, c):
        a = w.get_allocation()
        k = min(a.width / W, a.height / H)
        c.set_source_rgb(*A.rgb(A.INK)[:3])
        c.paint()
        c.translate((a.width - W * k) / 2, (a.height - H * k) / 2)
        c.scale(k, k)
        frame(c, base, datetime.now(timezone.utc), lat, lon, name)

    def sync(*_):
        wanted = PIN.is_file() and PIN.read_text().strip().endswith(PLATE)
        win.show_all() if wanted else win.hide()

    def tick():
        win.queue_draw()
        return True

    win.connect("draw", draw)
    monitor = Gio.File.new_for_path(str(PIN)).monitor_file(Gio.FileMonitorFlags.NONE, None)
    monitor.connect("changed", sync)
    sync()
    GLib.timeout_add_seconds(60, tick)
    Gtk.main()


def png(path, iso=None):
    lat, lon, name = L.location()
    when = datetime.fromisoformat(iso).astimezone(timezone.utc) if iso else datetime.now(timezone.utc)
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    frame(cairo.Context(s), fixed(lat), when, lat, lon, name)
    s.write_to_png(path)


if __name__ == "__main__":
    if "--test" in sys.argv:
        test()
    elif "--png" in sys.argv:
        png(*sys.argv[sys.argv.index("--png") + 1:])
    else:
        daemon()
