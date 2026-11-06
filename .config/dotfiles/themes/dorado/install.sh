#!/bin/sh
# One-time setup for the "dorado" theme (Astrolabio). Alegreya and Alegreya Sans ship inside the theme (fonts/, OFL).
# Builds ~/.local/share/icons/Papirus-Dorado: Papirus-Dark with pale brass folders, without touching /usr.
set -e
sudo pacman -S --needed papirus-icon-theme adw-gtk-theme ttf-ibmplex-mono-nerd
src=/usr/share/icons/Papirus
dst="$HOME/.local/share/icons/Papirus-Dorado"
rm -rf "$dst"; mkdir -p "$dst"
sed -e 's/^Name=.*/Name=Papirus-Dorado/' -e 's/^Inherits=.*/Inherits=Papirus-Dark,breeze-dark,hicolor/' \
    /usr/share/icons/Papirus-Dark/index.theme > "$dst/index.theme"
for dir in "$src"/*/places; do
    size=$(basename "$(dirname "$dir")")
    mkdir -p "$dst/$size/places"
    for f in "$dir"/*.svg; do
        t=$(basename "$(readlink -f "$f")")  # follow chains: folder-videos -> folder-video -> folder-blue-video
        case "$t" in folder-blue*|user-blue*) ln -sf "$dir/$(echo "$t" | sed 's/-blue/-paleorange/')" "$dst/$size/places/$(basename "$f")" ;; esac
    done
done
# Apple Music's launcher asks for WhiteSur's "music-app": point it at Papirus's own apple-music icon
for dir in "$src"/*/apps; do
    [ -f "$dir/apple-music.svg" ] || continue
    size=$(basename "$(dirname "$dir")")
    mkdir -p "$dst/$size/apps" && ln -sf "$dir/apple-music.svg" "$dst/$size/apps/music-app.svg"
done
gtk-update-icon-cache -q "$dst" 2>/dev/null || true
# The working astrolabe is the default wallpaper: instrumento.py shows itself while this plate is pinned
pin="$HOME/.cache/nostromo/wallpaper-dorado"
[ -f "$pin" ] || { mkdir -p "$(dirname "$pin")"; echo "$HOME/.config/dotfiles/themes/dorado/wallpapers/rotation/b-astrolabio.jpg" > "$pin"; }
