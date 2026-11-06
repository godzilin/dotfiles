#!/usr/bin/env python3
"""The almanac of the "dorado" theme: Sun, Moon and sidereal time from low-precision series (Astronomical Almanac: about
a degree for the Sun and Moon, a couple of minutes for sunrise; plenty for a bar). Used by the bar, the calendar panel
(hypr/scripts/calpanel.py), hyprlock and the desktop astrolabe (instrumento.py).
  luna.py          waybar JSON: phase glyph (Nerd Font weather set) and the Sun's sign; tooltip with the rest
  luna.py --texto  one line of plain text, for hyprlock
  luna.py --test   self-check against known new and full moons, solstices and sunrises"""
import calendar
import json
import math
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SYNODIC = 29.530588853
J2000 = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
EPS = 23.44  # obliquity of the ecliptic
HOME = (43.2627, -2.9253, "Bilbao")
SIGNS = ("Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis")
NAMES = ((0.033, "Luna nueva"), (0.217, "Luna creciente"), (0.283, "Cuarto creciente"), (0.467, "Gibosa creciente"), (0.533, "Luna llena"),
         (0.717, "Gibosa menguante"), (0.783, "Cuarto menguante"), (0.967, "Luna menguante"), (1.0, "Luna nueva"))


def sind(x):
    return math.sin(math.radians(x))


def cosd(x):
    return math.cos(math.radians(x))


def days(when):
    return (when - J2000).total_seconds() / 86400


def sun_lon(when):
    """Ecliptic longitude of the Sun, degrees."""
    d = days(when)
    g = 357.528 + 0.9856003 * d
    return (280.460 + 0.9856474 * d + 1.915 * sind(g) + 0.020 * sind(2 * g)) % 360


def moon_ecl(when):
    """Ecliptic longitude and latitude of the Moon, degrees."""
    t = days(when) / 36525
    lon = 218.32 + 481267.881 * t + 6.29 * sind(135.0 + 477198.87 * t) - 1.27 * sind(259.3 - 413335.36 * t) \
        + 0.66 * sind(235.7 + 890534.22 * t) + 0.21 * sind(269.9 + 954397.74 * t) - 0.19 * sind(357.5 + 35999.05 * t) \
        - 0.11 * sind(186.5 + 966404.03 * t)
    lat = 5.13 * sind(93.3 + 483202.02 * t) + 0.28 * sind(228.2 + 960400.89 * t) - 0.28 * sind(318.3 + 6003.15 * t) \
        - 0.17 * sind(217.6 - 407332.21 * t)
    return lon % 360, lat


def equatorial(lon, lat=0.0):
    """Ecliptic to right ascension and declination, degrees."""
    ra = math.degrees(math.atan2(sind(lon) * cosd(EPS) - math.tan(math.radians(lat)) * sind(EPS), cosd(lon))) % 360
    return ra, math.degrees(math.asin(sind(lat) * cosd(EPS) + cosd(lat) * sind(EPS) * sind(lon)))


def sidereal(when, lon):
    """Local sidereal time, degrees."""
    return (280.46061837 + 360.98564736629 * days(when) + lon) % 360


def altitude(ra, dec, lst, lat):
    return math.degrees(math.asin(sind(lat) * sind(dec) + cosd(lat) * cosd(dec) * cosd(lst - ra)))


def sign(lon):
    return SIGNS[int(lon // 30)], int(lon % 30)


def location():
    """(lat, lon, name) from the weather config, Bilbao without it."""
    try:
        lat, lon, name = (Path.home() / ".config/nostromo/weather.conf").read_text().split(maxsplit=2)
        return float(lat), float(lon), name.strip()
    except (OSError, ValueError):
        return HOME


def sun_times(day, lat, lon):
    """Sunrise and sunset of a date as local datetimes, None during polar day or night."""
    noon = datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc)
    l_ = sun_lon(noon)
    ra, dec = equatorial(l_)
    eot = (280.460 + 0.9856474 * days(noon) - ra + 180) % 360 - 180  # equation of time, degrees
    cos_h = (sind(-0.833) - sind(lat) * sind(dec)) / (cosd(lat) * cosd(dec))
    if abs(cos_h) > 1:
        return None
    transit = noon + timedelta(hours=-(lon + eot) / 15)
    half = timedelta(hours=math.degrees(math.acos(cos_h)) / 15)
    return (transit - half).astimezone(), (transit + half).astimezone()


def age(when):
    """Fraction of the lunation, from the true Sun-Moon elongation: 0 new, 0.5 full."""
    return ((moon_ecl(when)[0] - sun_lon(when)) / 360) % 1


def phase_days(year, month):
    """{date: glyph} for the days of a month on which a quarter of the Moon falls."""
    out = {}
    for n in range(1, calendar.monthrange(year, month)[1] + 1):
        start = datetime(year, month, n).astimezone()
        a0, a1 = age(start), age(start + timedelta(days=1))
        for target in (0, 0.25, 0.5, 0.75):
            if (target - a0) % 1 < (a1 - a0) % 1:
                out[date(year, month, n)] = glyph(target)
    return out


def almanac():
    """One line for the calendar panel."""
    lat, lon, _ = location()
    now = datetime.now(timezone.utc)
    a = age(now)
    times = sun_times(date.today(), lat, lon)
    sun = f"Sale el Sol {times[0]:%H:%M}, se pone {times[1]:%H:%M}" if times else "El Sol no cruza el horizonte"
    return f"{sun}  ·  {name(a)}, {round(illumination(a) * 100)} %"


def illumination(a):
    return (1 - math.cos(a * 2 * math.pi)) / 2


def name(a):
    return next(n for limit, n in NAMES if a < limit)


def glyph(a):
    return chr(0xE38D + round(a * 28) % 28)  # nf-weather-moon_new ... moon_waning_crescent_6: 28 steps


def next_at(when, target):
    days = ((target - age(when)) % 1) * SYNODIC
    return when + timedelta(days=days)


def test():
    for y, m, d, h, want in ((2026, 8, 12, 17, 0.0), (2026, 11, 9, 7, 0.0), (2025, 3, 14, 6, 0.5), (2026, 11, 24, 14, 0.5)):
        got = age(datetime(y, m, d, h, tzinfo=timezone.utc))
        off = abs((got - want + 0.5) % 1 - 0.5) * SYNODIC
        assert off < 0.75, (y, m, d, off)
    assert name(0.0) == name(0.99) == "Luna nueva" and name(0.5) == "Luna llena" and name(0.25) == "Cuarto creciente"
    assert glyph(0.0) == chr(0xE38D) and glyph(0.5) == chr(0xE39B) and glyph(0.999) == chr(0xE38D)
    assert illumination(0.5) == 1 and illumination(0.0) == 0
    assert 23.3 < equatorial(sun_lon(datetime(2026, 6, 21, 12, tzinfo=timezone.utc)))[1] < 23.5
    assert sign(sun_lon(datetime(2026, 11, 6, tzinfo=timezone.utc)))[0] == "Escorpio"
    rise, set_ = sun_times(date(2026, 6, 21), 43.2627, -2.9253)  # Bilbao: about 04:30 and 19:50 UT
    assert abs(rise.astimezone(timezone.utc).hour * 60 + rise.astimezone(timezone.utc).minute - 270) < 10
    assert abs(set_.astimezone(timezone.utc).hour * 60 + set_.astimezone(timezone.utc).minute - 1190) < 10
    assert sun_times(date(2026, 6, 21), 80, 0) is None
    assert date(2026, 11, 9) in phase_days(2026, 11) and date(2026, 11, 24) in phase_days(2026, 11) and len(phase_days(2026, 11)) >= 4
    assert abs(equatorial(90)[0] - 90) < 1e-9
    print("ok")


def main():
    if "--test" in sys.argv:
        return test()
    now = datetime.now(timezone.utc)
    a = age(now)
    pct = round(illumination(a) * 100)
    if "--texto" in sys.argv:
        return print(f"{name(a)}  ·  {pct} %")
    fmt = lambda d: d.astimezone().strftime("%d/%m")
    print(json.dumps({
        "text": f"<span size='large'>{glyph(a)}</span>  Sol en {sign(sun_lon(now))[0]}",
        "tooltip": f"{name(a)}, {pct} % iluminada\nLlena el {fmt(next_at(now, 0.5))}  ·  Nueva el {fmt(next_at(now, 0.0))}\n{almanac().split('  ·  ')[0]}",
        "class": "llena" if 0.467 <= a < 0.533 else "nueva" if a < 0.033 or a >= 0.967 else "",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
