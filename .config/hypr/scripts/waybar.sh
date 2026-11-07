#!/bin/sh
# Starts waybar. With hosts/<hostname>-waybar.json, waybar-host.py builds one bar per monitor from the theme's config.
host=$(cat /etc/hostname)
h="$HOME/.config/hypr/hosts/$host-waybar.json"
if [ -f "$h" ] && out=$(python3 -I "$HOME/.config/hypr/scripts/waybar-host.py" "$h"); then
    exec waybar -c "${out%% *}" -s "${out#* }"
fi
exec waybar
