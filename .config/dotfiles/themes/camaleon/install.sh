#!/bin/sh
# One-time setup for the "camaleon" theme (Camaleón). Fonts are Bosque's (fonts -> ../verde/fonts).
# The desktop also gets linux-wallpaperengine (AUR) to draw Wallpaper Engine wallpapers: install Wallpaper Engine in
# Steam (Proton) and subscribe to wallpapers in its Workshop; scripts/fondo.py picks them up by itself.
set -e
sudo pacman -S --needed papirus-icon-theme adw-gtk-theme capitaine-cursors python-pillow python-numpy librsvg
[ "$(cat /etc/hostname)" = pcgodzilin ] && paru -S --needed linux-wallpaperengine-git
# `tema` needs theme.json, which generar.py writes: paint it once from any wallpaper (fondo.py repaints on start)
python3 "$(dirname "$(readlink -f "$0")")/generar.py"
