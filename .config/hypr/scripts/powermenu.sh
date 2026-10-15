#!/bin/sh
# Power menu with fuzzel (Ctrl+Alt+Del)
choice=$(printf 'BLOQUEAR\nCERRAR SESIÓN\nSUSPENDER\nREINICIAR\nAPAGAR\n' |
    fuzzel --dmenu --prompt '⏻ ' --placeholder 'SYSTEM' --lines 5 --width 24 --no-icons)
case "$choice" in
    BLOQUEAR)        loginctl lock-session ;;
    "CERRAR SESIÓN") hyprctl dispatch 'hl.dsp.exit()' ;;
    SUSPENDER)       systemctl suspend ;;
    REINICIAR)       systemctl reboot ;;
    APAGAR)          systemctl poweroff ;;
esac
