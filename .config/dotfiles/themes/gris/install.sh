#!/bin/sh
# One-time setup for the "gris" theme (NeXTSTEP): Nimbus Sans and Nimbus Mono PS (URW, gsfonts) stand in for Helvetica and Courier.
# Builds ~/.local/share/icons/Papirus-Gris: Papirus (light) with grey folders, without touching /usr (no papirus-folders).
set -e
sudo pacman -S --needed gsfonts papirus-icon-theme adw-gtk-theme capitaine-cursors nwg-dock-hyprland
src=/usr/share/icons/Papirus
dst="$HOME/.local/share/icons/Papirus-Gris"
rm -rf "$dst"; mkdir -p "$dst"
sed -e 's/^Name=.*/Name=Papirus-Gris/' -e 's/^Inherits=.*/Inherits=Papirus,breeze,hicolor/' \
    /usr/share/icons/Papirus/index.theme > "$dst/index.theme"
for dir in "$src"/*/places; do
    size=$(basename "$(dirname "$dir")")
    mkdir -p "$dst/$size/places"
    for f in "$dir"/*.svg; do
        t=$(basename "$(readlink -f "$f")")  # follow chains: folder-videos -> folder-video -> folder-blue-video
        case "$t" in folder-blue*|user-blue*) ln -sf "$dir/$(echo "$t" | sed 's/-blue/-grey/')" "$dst/$size/places/$(basename "$f")" ;; esac
    done
done
# Apple Music's launcher asks for WhiteSur's "music-app": point it at Papirus's own apple-music icon
for dir in "$src"/*/apps; do
    [ -f "$dir/apple-music.svg" ] || continue
    size=$(basename "$(dirname "$dir")")
    mkdir -p "$dst/$size/apps" && ln -sf "$dir/apple-music.svg" "$dst/$size/apps/music-app.svg"
done
gtk-update-icon-cache -q "$dst" 2>/dev/null || true
