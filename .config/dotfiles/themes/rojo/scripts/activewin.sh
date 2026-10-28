#!/bin/sh
# Focused app in capitals for the bar (GTK CSS cannot uppercase text): prints on every focus change
# the theme's own popups get Russian names, like the rest of the bar (tr only uppercases ASCII, so they come in capitals)
name() { hyprctl activewindow -j | jq -r '.class // empty' | sed 's/.*\.//' | tr '[:lower:]' '[:upper:]' |
    sed 's/^NOSTROMO-CALENDAR$/КАЛЕНДАРЬ/; s/^NOSTROMO-WEATHER$/ПОГОДА/; s/^NOSTROMO-MEDIA$/МУЗЫКА/; s/^NOSTROMO-WALLPAPER$/ФОН/'; }
name
socat -U - "UNIX-CONNECT:$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock" | while read -r ev; do
    case "$ev" in activewindow\>\>*|closewindow\>\>*|workspace\>\>*) name ;; esac
done
