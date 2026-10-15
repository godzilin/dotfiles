#!/bin/sh
# Power menu with fuzzel (Ctrl+Alt+Del)
choice=$(printf '󰌾  Bloquear\n󰍃  Cerrar sesión\n󰤄  Suspender\n󰜉  Reiniciar\n󰐥  Apagar\n' |
    fuzzel --dmenu --prompt '' --lines 5 --width 20)
case "$choice" in
    *Bloquear*)  loginctl lock-session ;;
    *Cerrar*)    hyprctl dispatch 'hl.dsp.exit()' ;;
    *Suspender*) systemctl suspend ;;
    *Reiniciar*) systemctl reboot ;;
    *Apagar*)    systemctl poweroff ;;
esac
