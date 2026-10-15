#!/bin/sh
# start|stop the extra programs of the active theme ("daemons" in theme.json), e.g. the Dock of blanco.
# Called by autostart.lua and by `tema` around a switch.
json="$HOME/.config/dotfiles/themes/current/theme.json"
jq -r '.daemons[]?' "$json" | while read -r cmd; do
    case "$1" in
        start) setsid -f sh -c "exec $cmd" >/dev/null 2>&1 ;;
        stop)  pkill -f "^${cmd%% *}" ;;
    esac
done
