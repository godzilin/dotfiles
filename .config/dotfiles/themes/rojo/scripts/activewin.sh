#!/bin/sh
# Focused app in capitals for the bar (GTK CSS cannot uppercase text): prints on every focus change
name() { hyprctl activewindow -j | jq -r '.class // empty' | sed 's/.*\.//' | tr '[:lower:]' '[:upper:]'; }
name
socat -U - "UNIX-CONNECT:$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock" | while read -r ev; do
    case "$ev" in activewindow\>\>*|closewindow\>\>*|workspace\>\>*) name ;; esac
done
