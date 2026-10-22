#!/bin/sh
# One-time setup for the "rojo" theme (constructivism). Fonts ship inside the theme (fonts/, OFL).
# Builds ~/.local/share/icons/Papirus-Rojo: Papirus-Light with red folders, without touching /usr (no papirus-folders).
set -e
sudo pacman -S --needed papirus-icon-theme adw-gtk-theme
src=/usr/share/icons/Papirus
dst="$HOME/.local/share/icons/Papirus-Rojo"
rm -rf "$dst"; mkdir -p "$dst"
sed -e 's/^Name=.*/Name=Papirus-Rojo/' -e 's/^Inherits=.*/Inherits=Papirus-Light,breeze,hicolor/' \
    /usr/share/icons/Papirus-Light/index.theme > "$dst/index.theme"
for dir in "$src"/*/places; do
    size=$(basename "$(dirname "$dir")")
    mkdir -p "$dst/$size/places"
    for f in "$dir"/*.svg; do
        t=$(basename "$(readlink -f "$f")")  # follow chains: folder-videos -> folder-video -> folder-blue-video
        case "$t" in folder-blue*|user-blue*) ln -sf "$dir/$(echo "$t" | sed 's/-blue/-red/')" "$dst/$size/places/$(basename "$f")" ;; esac
    done
done
gtk-update-icon-cache -q "$dst" 2>/dev/null || true
