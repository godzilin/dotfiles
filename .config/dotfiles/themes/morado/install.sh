#!/bin/sh
# One-time setup for the "morado" theme (synthwave). Fonts ship inside the theme (fonts/, OFL: Orbitron, Rajdhani,
# Share Tech Mono). Builds ~/.local/share/icons/Papirus-Morado: Papirus-Dark with violet folders, without touching /usr.
set -e
sudo pacman -S --needed papirus-icon-theme adw-gtk-theme
src=/usr/share/icons/Papirus
dst="$HOME/.local/share/icons/Papirus-Morado"
rm -rf "$dst"; mkdir -p "$dst"
sed -e 's/^Name=.*/Name=Papirus-Morado/' -e 's/^Inherits=.*/Inherits=Papirus-Dark,breeze-dark,hicolor/' \
    /usr/share/icons/Papirus-Dark/index.theme > "$dst/index.theme"
for dir in "$src"/*/places; do
    size=$(basename "$(dirname "$dir")")
    mkdir -p "$dst/$size/places"
    for f in "$dir"/*.svg; do
        t=$(basename "$(readlink -f "$f")")  # follow chains: folder-videos -> folder-video -> folder-blue-video
        case "$t" in folder-blue*|user-blue*) ln -sf "$dir/$(echo "$t" | sed 's/-blue/-violet/')" "$dst/$size/places/$(basename "$f")" ;; esac
    done
done
gtk-update-icon-cache -q "$dst" 2>/dev/null || true
