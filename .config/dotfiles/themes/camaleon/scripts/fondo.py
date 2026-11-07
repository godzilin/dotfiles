#!/usr/bin/env python3
"""Wallpaper of the "camaleon" theme, and the theme repaints itself from it (generar.py). Started by theme-daemons.sh.

Every ROTATE seconds it picks a new wallpaper, looked up again each time, so anything you add shows up in the next
round:
  1. a Wallpaper Engine wallpaper (Workshop subscriptions, its built-in ones and your own; scene or video), drawn by linux-wallpaperengine on every
     monitor; its preview image gives the colours. Only where it is installed (the desktop: install.sh).
  2. otherwise, or when it is missing, has no wallpapers or crashes: a random image from ~/Pictures/Wallpapers in
     hyprpaper.
A picture pinned in the waybar selector (wallpaper-camaleon in ~/.cache/nostromo) stops the rotation until "Rotar"."""
import json
import random
import re
import shutil
import signal
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
BAD = CACHE / "camaleon-we-malos"  # wallpapers linux-wallpaperengine failed to draw; delete it to retry them
ROTATE = 30 * 60
IMAGES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
WE_TYPES = {"scene", "video"}  # web and application wallpapers rarely work in linux-wallpaperengine

we = None  # the running linux-wallpaperengine
we_broken_until = 0.0


def pictures():
    for d in (HOME / "Pictures/Wallpapers", HOME / "Pictures/wallpapers"):
        if d.is_dir():
            return d
    return None


def steam_libraries():
    vdf = HOME / ".local/share/Steam/steamapps/libraryfolders.vdf"
    try:
        return [Path(p) for p in re.findall(r'"path"\s+"([^"]+)"', vdf.read_text())]
    except OSError:
        return []


def workshop():
    """[(folder, preview image)] of the Wallpaper Engine wallpapers it can draw, and the assets folder, or ([], None)."""
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
                items.append((d, prev))
    return (items, assets) if assets else ([], None)


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
    try:
        p = Path(PIN.read_text().strip())
    except OSError:
        return None
    return p if p.is_file() else None


def pick(current):
    """Next wallpaper as ("we", folder, preview) or ("img", path, path), never the current one if there is a choice."""
    global we_broken_until
    stop_we()
    items, assets = workshop()
    bad = set(BAD.read_text().splitlines()) if BAD.exists() else set()
    items = [i for i in items if str(i[0]) not in bad]
    random.shuffle(items)
    items.sort(key=lambda i: i[0] == current)  # the current one only if it is the only one left
    for folder, prev in items[:3]:
        if start_we(folder, assets):
            return ("we", folder, prev)
        stop_we()
        CACHE.mkdir(parents=True, exist_ok=True)
        with BAD.open("a") as f:  # e.g. 3D scenes with a perspective camera: never again
            f.write(f"{folder}\n")
        print(f"fondo: linux-wallpaperengine cannot draw {folder}", file=sys.stderr)
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
    pics = pictures()
    rotation = HERE / "wallpapers/rotation"  # what the waybar selector lists and pins from
    if pics and not rotation.exists():
        rotation.parent.mkdir(exist_ok=True)
        rotation.symlink_to(pics)
    shown, painted, since = None, None, 0.0
    try:
        while True:
            pin = pinned()
            if pin:
                if shown != ("pin", pin):
                    stop_we()  # wallpaper.sh already put the pin in hyprpaper
                    shown = ("pin", pin)
            elif (shown is None or shown[0] == "pin" or time.time() - since > ROTATE
                  or (shown[0] == "we" and we.poll() is not None)):
                if shown and shown[0] == "we" and we.poll() is not None:
                    we_broken_until = time.time() + 3600  # crashed while running
                nxt = pick(shown[1] if shown else None)
                shown, since = (nxt or ("none", None, None)), time.time()
            src = shown[1] if shown[0] == "pin" else shown[2]
            if src and src != painted:
                repaint(src)
                painted = src
            time.sleep(5)
    finally:
        stop_we()


if __name__ == "__main__":
    main()
