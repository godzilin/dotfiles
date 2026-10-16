#!/bin/sh
# Wallpaper of the active theme. hyprpaper.conf reads ~/.cache/nostromo/wallpaper: a symlink to the theme's
# rotation/ folder, or to one image pinned in the selector popup (pins are per theme: ~/.cache/nostromo/wallpaper-<theme>).
#   wallpaper.sh             toggle the selector popup (waybar button)
#   wallpaper.sh apply       re-link for the active theme and restart hyprpaper (autostart, `tema`)
#   wallpaper.sh set FILE    pin FILE;   wallpaper.sh set random   back to the rotation
themes="$HOME/.config/dotfiles/themes"
cache="$HOME/.cache/nostromo"
pin="$cache/wallpaper-$(basename "$(readlink "$themes/current")")"
case "$1" in
    apply) ;;
    set) mkdir -p "$cache"
         if [ "$2" = random ]; then rm -f "$pin"; else printf '%s\n' "$2" > "$pin"; fi ;;
    *) pkill -f "^python3 .*wallpopup\.py" || exec python3 "$HOME/.config/hypr/scripts/wallpopup.py"
       exit ;;
esac
mkdir -p "$cache"
target="$themes/current/wallpapers/rotation"
[ -f "$pin" ] && [ -f "$(cat "$pin")" ] && target=$(cat "$pin")
ln -sfn "$target" "$cache/wallpaper"
pkill -x hyprpaper
while pgrep -x hyprpaper >/dev/null; do sleep 0.05; done  # its IPC socket must be free for the new one
setsid -f hyprpaper >/dev/null 2>&1
