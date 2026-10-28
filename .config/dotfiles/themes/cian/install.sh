#!/bin/sh
# One-time setup for the "cian" theme (blueprint). Fonts ship inside the theme (fonts/, OFL: B612 and B612 Mono).
# Builds ~/.local/share/icons/Papirus-Cian: Papirus-Dark with cyan folders, without touching /usr.
set -e
sudo pacman -S --needed papirus-icon-theme adw-gtk-theme
src=/usr/share/icons/Papirus
dst="$HOME/.local/share/icons/Papirus-Cian"
rm -rf "$dst"; mkdir -p "$dst"
sed -e 's/^Name=.*/Name=Papirus-Cian/' -e 's/^Inherits=.*/Inherits=Papirus-Dark,breeze-dark,hicolor/' \
    /usr/share/icons/Papirus-Dark/index.theme > "$dst/index.theme"
for dir in "$src"/*/places; do
    size=$(basename "$(dirname "$dir")")
    mkdir -p "$dst/$size/places"
    for f in "$dir"/*.svg; do
        t=$(basename "$(readlink -f "$f")")  # follow chains: folder-videos -> folder-video -> folder-blue-video
        case "$t" in folder-blue*|user-blue*) ln -sf "$dir/$(echo "$t" | sed 's/-blue/-cyan/')" "$dst/$size/places/$(basename "$f")" ;; esac
    done
done
gtk-update-icon-cache -q "$dst" 2>/dev/null || true
