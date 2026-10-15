#!/bin/sh
# Prints the Chicago95 16 px icon for the taskbar tray (waybar image modules): trayicon.sh vol|net|bat
dir="$HOME/.local/share/icons/Chicago95/status/16"
case "$1" in
    vol)
        v=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ 2>/dev/null)
        case "$v" in
            *MUTED*|"") echo "$dir/audio-volume-muted.png" ;;
            *) echo "$dir/audio-volume-high.png" ;;
        esac ;;
    net)
        case "$(nmcli -t -f TYPE,STATE device 2>/dev/null | grep ':connected$' | head -1)" in
            wifi*)     echo "$dir/network-wireless-encrypted.png" ;;
            ethernet*) echo "$dir/network-idle.png" ;;
            *)         echo "$dir/network-offline.png" ;;
        esac ;;
    bat)
        b=/sys/class/power_supply/BAT0
        c=$(cat $b/capacity 2>/dev/null || echo 100)
        if [ "$(cat $b/status 2>/dev/null)" = Charging ]; then echo "$dir/battery-060-charging.png"
        elif [ "$c" -le 10 ]; then echo "$dir/battery-caution.png"
        elif [ "$c" -le 30 ]; then echo "$dir/battery-low.png"
        elif [ "$c" -le 70 ]; then echo "$dir/battery-good.png"
        else echo "$dir/battery-full.png"; fi ;;
esac
