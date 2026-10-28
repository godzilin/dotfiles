#!/bin/sh
# Arch menu: drops from the  in the menu bar (fuzzel as a plain list, no search field)
user=$(getent passwd "$USER" | cut -d: -f5 | cut -d, -f1); user=${user:-$USER}
choice=$(printf '%s\n' "Acerca de CachyOS" "Ajustes del Sistema…" "Forzar salida…" "Reposo" "Reiniciar…" "Apagar equipo…" "Bloquear pantalla" "Cerrar la sesión de $user…" |
    fuzzel --dmenu --anchor top-left --x-margin 8 --y-margin 4 --width 26 --lines 8 --hide-prompt \
        --no-icons --font 'Inter:size=11' --line-height 24 --override border.radius=10 --override main.vertical-pad=6)
case "$choice" in
    "Acerca de CachyOS")    alacritty --class about-this-pc -o 'window.dimensions={columns=90,lines=22}' --hold -e fastfetch ;;
    "Ajustes del Sistema…") systemsettings ;;
    "Forzar salida…")       hyprctl kill ;;
    Reposo)                 systemctl suspend ;;
    Reiniciar…)             systemctl reboot ;;
    "Apagar equipo…")       systemctl poweroff ;;
    "Bloquear pantalla")    loginctl lock-session ;;
    "Cerrar la sesión"*)    hyprctl dispatch 'hl.dsp.exit()' ;;
esac
