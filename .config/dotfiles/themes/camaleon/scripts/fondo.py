#!/usr/bin/env python3
"""Wallpaper of the "camaleon" theme, and the theme repaints itself from it (generar.py). Started by theme-daemons.sh.

Every ROTATE seconds it picks a new wallpaper, looked up again each time, so anything you add shows up in the next
round:
  1. a Wallpaper Engine wallpaper (Workshop subscriptions, its built-in ones and your own; scene or video), drawn by linux-wallpaperengine on every
     monitor; its preview image gives the colours. Only where it is installed (the desktop: install.sh).
  2. otherwise, or when it is missing, has no wallpapers or crashes: a random image from ~/Pictures/Wallpapers (or
     Bosque's wallpapers if that folder does not exist) in hyprpaper.
The waybar selector has a tab per source: a click pins that wallpaper (wallpaper-camaleon in ~/.cache/nostromo holds an
image or a Wallpaper Engine folder) and "Rotar" goes back to rotating, only through that tab's source (camaleon-modo:
"we" or "img"). The Wallpaper Engine tab lists camaleon-we.json, written here on every scan."""
import json
import random
import re
import shutil
import signal
import struct
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import generar  # noqa: E402

HOME = Path.home()
CACHE = HOME / ".cache/nostromo"
PIN = CACHE / "wallpaper-camaleon"
MODE = CACHE / "camaleon-modo"
WE_LIST = CACHE / "camaleon-we.json"
OUT = CACHE / "camaleon-we-fuera"  # left out of "Rotar" with a right click in the selector; can still be pinned
HIDDEN = CACHE / "camaleon-we-ocultos"  # hidden from the selector and the rotation (right click > Ocultar)
BAD = CACHE / "camaleon-we-malos"  # wallpapers linux-wallpaperengine failed to draw; delete it to retry them
ROTATE = 30 * 60
IMAGES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
LOW_RES = 1280  # scenes narrower than this are drawn that small and stretched: pixelated, left out of "Rotar"
WE_TYPES = {"scene", "video"}  # web and application wallpapers rarely work in linux-wallpaperengine

we = None  # the running linux-wallpaperengine
we_broken_until = 0.0


def pictures():
    """First folder with images: yours, else Bosque's (an empty ~/Pictures/Wallpapers would leave nothing to show).
    Points wallpapers/rotation, what the waybar selector lists and pins from, at it."""
    for d in (HOME / "Pictures/Wallpapers", HOME / "Pictures/wallpapers", HERE.parent / "verde/wallpapers/rotation"):
        if d.is_dir() and any(f.suffix.lower() in IMAGES for f in d.rglob("*")):
            rotation = HERE / "wallpapers/rotation"
            if not rotation.exists() or rotation.is_symlink() and rotation.resolve() != d.resolve():
                rotation.parent.mkdir(exist_ok=True)
                tmp = rotation.with_name("rotation.tmp")
                tmp.unlink(missing_ok=True)
                tmp.symlink_to(d)
                tmp.replace(rotation)
            return d
    return None


def steam_libraries():
    vdf = HOME / ".local/share/Steam/steamapps/libraryfolders.vdf"
    try:
        return [Path(p) for p in re.findall(r'"path"\s+"([^"]+)"', vdf.read_text())]
    except OSError:
        return []


def workshop(hidden_too=False):
    """[(folder, preview image, title, low resolution)] of the Wallpaper Engine wallpapers it can draw, and the assets folder, or ([], None)."""
    if time.time() < we_broken_until or not shutil.which("linux-wallpaperengine"):
        return [], None
    libs = steam_libraries()
    assets = next((a for lib in libs if (a := lib / "steamapps/common/wallpaper_engine/assets").is_dir()), None)
    items = []
    folders = [lib / "steamapps/workshop/content/431960" for lib in libs]
    folders += [assets.parent / "projects" / p for p in ("defaultprojects", "myprojects")] if assets else []
    for top in folders:  # Workshop subscriptions, the wallpapers that ship with it and your own
        for d in top.glob("*"):
            try:
                p = json.loads((d / "project.json").read_text(errors="ignore"))
            except (OSError, ValueError):
                continue
            prev = d / str(p.get("preview", ""))
            if str(p.get("type", "")).lower() in WE_TYPES and prev.is_file():
                low = (scene_width(d) or LOW_RES) < LOW_RES
                items.append((d, prev, str(p.get("title") or d.name), low))
    bad = set(BAD.read_text().splitlines()) if BAD.exists() else set()
    items = [i for i in items if str(i[0]) not in bad]
    CACHE.mkdir(parents=True, exist_ok=True)
    WE_LIST.write_text(json.dumps([{"folder": str(d), "preview": str(pv), "title": t, "lowres": low}
                                   for d, pv, t, low in items],
                                  ensure_ascii=False))
    if not hidden_too:  # the selector lists hidden ones too, in its "Ocultos" tab
        hidden = set(HIDDEN.read_text().splitlines()) if HIDDEN.exists() else set()
        items = [i for i in items if str(i[0]) not in hidden]
    return (items, assets) if assets else ([], None)


def scene_width(folder):
    """Width of a scene's orthographic projection (its render size in linux-wallpaperengine), or None (video, 3D)."""
    try:
        f = folder / "scene.json"
        if f.exists():
            text = f.read_text(errors="ignore")
        else:  # inside scene.pkg: "PKGV..." then [name, offset, length] entries, then the files
            b, o = (folder / "scene.pkg").read_bytes(), 0

            def string():
                nonlocal o
                n = struct.unpack_from("<I", b, o)[0]
                o += 4 + n
                return b[o - n:o].decode(errors="ignore")
            string()
            count = struct.unpack_from("<I", b, o)[0]
            o += 4
            entries = []
            for _ in range(count):
                name = string()
                entries.append((name, *struct.unpack_from("<II", b, o)))
                o += 8
            text = next((b[o + off:o + off + n].decode(errors="ignore") for name, off, n in entries
                         if name == "scene.json"), "")
        m = re.search(r'"orthogonalprojection"\s*:\s*\{[^}]*?"width"\s*:\s*(\d+)', text, re.S)
        return int(m[1]) if m else None
    except (OSError, struct.error):
        return None


def monitors():
    out = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True).stdout
    return [m["name"] for m in json.loads(out or "[]")]


def stop_we():
    global we
    if we and we.poll() is None:
        we.terminate()
        try:
            we.wait(5)
        except subprocess.TimeoutExpired:
            we.kill()
    we = None


def hyprpaper(image):
    """Same as wallpaper.sh apply, with one image: hyprpaper.conf reads ~/.cache/nostromo/wallpaper."""
    CACHE.mkdir(parents=True, exist_ok=True)
    link = CACHE / "wallpaper"
    tmp = CACHE / "wallpaper.tmp"
    tmp.unlink(missing_ok=True)
    tmp.symlink_to(image)
    tmp.replace(link)
    restart_hyprpaper(start=True)


def restart_hyprpaper(start):
    subprocess.run(["pkill", "-x", "hyprpaper"])
    while subprocess.run(["pgrep", "-x", "hyprpaper"], capture_output=True).returncode == 0:
        time.sleep(0.05)  # its IPC socket must be free for the new one
    if start:
        subprocess.Popen(["hyprpaper"], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def start_we(folder, assets):
    """True if linux-wallpaperengine is still alive after a few seconds."""
    global we
    cmd = ["linux-wallpaperengine", "--silent", "--fps", "30", "--assets-dir", str(assets)]
    for m in monitors():
        cmd += ["--screen-root", m, "--bg", str(folder), "--scaling", "fill"]  # pauses itself over fullscreen games
    restart_hyprpaper(start=False)  # both draw on the background layer
    we = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)
    return we.poll() is None


def repaint(image):
    generar.main(Path(image).resolve())
    sh = lambda *c: subprocess.run(c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sh("hyprctl", "reload")
    sh("pkill", "-x", "waybar")
    subprocess.Popen(["setsid", "-f", str(HOME / ".config/hypr/scripts/waybar.sh")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sh("swaync-client", "-rs")
    sh(str(HOME / ".config/dotfiles/vscode/theme.py"))
    obsidian = HERE / "obsidian/theme.css"
    if obsidian.exists():
        obsidian.touch()  # Obsidian reloads its theme when the file changes


def pinned():
    """The pinned image, or the pinned Wallpaper Engine folder, or None."""
    try:
        p = Path(PIN.read_text().strip())
    except OSError:
        return None
    return p if p.is_file() or (p / "project.json").is_file() else None


def mode():
    try:
        return MODE.read_text().strip()
    except OSError:
        return "we"


def mark_bad(folder):
    CACHE.mkdir(parents=True, exist_ok=True)
    with BAD.open("a") as f:  # e.g. 3D scenes with a perspective camera: never again
        f.write(f"{folder}\n")
    print(f"fondo: linux-wallpaperengine cannot draw {folder}", file=sys.stderr)


def pick(current):
    """Next wallpaper as ("we", folder, preview) or ("img", path, path), never the current one if there is a choice."""
    global we_broken_until
    stop_we()
    items, assets = workshop() if mode() == "we" else ([], None)
    out = set(OUT.read_text().splitlines()) if OUT.exists() else set()
    items = [i for i in items if str(i[0]) not in out and not i[3]]
    random.shuffle(items)
    items.sort(key=lambda i: i[0] == current)  # the current one only if it is the only one left
    for folder, prev, *_ in items[:3]:
        if start_we(folder, assets):
            return ("we", folder, prev)
        stop_we()
        mark_bad(folder)
    else:
        if items:
            we_broken_until = time.time() + 3600  # three in a row failed: broken install or driver, retry in an hour
    pics = pictures()
    files = [f for f in pics.rglob("*") if f.suffix.lower() in IMAGES] if pics else []
    files = [f for f in files if f != current] or files
    if not files:
        return None
    f = random.choice(files)
    hyprpaper(f)
    return ("img", f, f)


def main():
    global we_broken_until
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))  # theme-daemons.sh stop: finally kills the wallpaper engine
    pictures()  # points the selector's wallpapers/rotation at the right folder
    shown, painted, since, rotating = None, None, 0.0, None
    try:
        while True:
            pin = pinned()
            if pin and (shown is None or shown[:2] != ("pin", pin)):
                stop_we()
                if pin.is_file():  # an image: wallpaper.sh already put it in hyprpaper
                    shown = ("pin", pin, pin)
                else:
                    items, assets = workshop(hidden_too=True)
                    prev = next((pv for d, pv, *_ in items if d == pin), None)
                    if prev and start_we(pin, assets):
                        shown = ("pin", pin, prev)
                    else:  # cannot draw it: forget the pin and rotate
                        stop_we()
                        mark_bad(pin)
                        PIN.unlink(missing_ok=True)
                        continue
            elif pin and shown[0] == "pin" and not pin.is_file() and we and we.poll() is not None:
                mark_bad(pin)  # the pinned Wallpaper Engine wallpaper crashed
                PIN.unlink(missing_ok=True)
                continue
            elif not pin and (shown is None or shown[0] == "pin" or time.time() - since > ROTATE
                              or rotating != mode() or (shown[0] == "we" and we.poll() is not None)):
                if shown and shown[0] == "we" and we.poll() is not None:
                    we_broken_until = time.time() + 3600  # crashed while running
                rotating = mode()
                nxt = pick(shown[1] if shown else None)
                shown, since = (nxt or ("none", None, None)), time.time()
            # wallpaper.sh apply (autostart runs it alongside this) links rotation/ and restarts hyprpaper, which then
            # shows and rotates other images than the one painted: put ours back, or keep hyprpaper off over Wallpaper Engine
            if shown[0] == "img" and (CACHE / "wallpaper").resolve() != shown[1].resolve():
                hyprpaper(shown[1])
            elif we and we.poll() is None and subprocess.run(["pgrep", "-x", "hyprpaper"], capture_output=True).returncode == 0:
                restart_hyprpaper(start=False)
            src = shown[2]
            if src and src != painted:
                repaint(src)
                painted = src
            time.sleep(5)
    finally:
        stop_we()


if __name__ == "__main__":
    main()
