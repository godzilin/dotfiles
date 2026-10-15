#!/bin/sh
# Prints the Chicago95 24 px icon for the taskbar tray (waybar image modules): trayicon.sh vol|net|bat
icons="$HOME/.local/share/icons/Chicago95"
icon() {  # the 24 px file wherever Chicago95 keeps it, else the 32 px one (waybar scales it)
    for d in status/24 panel/24 devices/24 status/32 panel/32 status/16; do
        [ -f "$icons/$d/$1.png" ] && { echo "$icons/$d/$1.png"; return; }
    done
}
case "$1" in
    vol)
        v=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ 2>/dev/null)
        case "$v" in
            *MUTED*|"") icon audio-volume-muted ;;
            *) icon audio-volume-high ;;
        esac ;;
    net)
        case "$(nmcli -t -f TYPE,STATE device 2>/dev/null | grep ':connected$' | head -1)" in
            wifi*)     icon network-wireless ;;
            ethernet*) icon network-idle ;;
            *)         icon network-offline ;;
        esac ;;
    bat)
        b=/sys/class/power_supply/BAT0
        c=$(cat $b/capacity 2>/dev/null || echo 100)
        if [ "$(cat $b/status 2>/dev/null)" = Charging ]; then icon battery-060-charging
        elif [ "$c" -le 10 ]; then icon battery-caution
        elif [ "$c" -le 30 ]; then icon battery-low
        elif [ "$c" -le 70 ]; then icon battery-good
        else icon battery-full; fi ;;
esac
