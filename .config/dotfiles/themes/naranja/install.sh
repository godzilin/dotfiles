#!/bin/sh
# One-time setup for the "naranja" theme (Nostromo). The stencil font ships inside the theme (fonts/, OFL).
# The bridge console is the default wallpaper: consola.py shows itself while this plate is pinned
pin="$HOME/.cache/nostromo/wallpaper-naranja"
[ -f "$pin" ] || { mkdir -p "$(dirname "$pin")"; echo "$HOME/.config/dotfiles/themes/naranja/wallpapers/rotation/0-consola.png" > "$pin"; }
