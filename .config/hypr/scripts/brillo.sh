#!/bin/sh
# Modulo custom/brillo de waybar: brillo real del monitor por DDC/CI. brillo.sh [+|-] lo sube o baja un 5 %.
# shortcut: solo el primer monitor DDC (el HDMI del sobremesa no responde); con otro, cambia --display
cache=${XDG_RUNTIME_DIR:-/tmp}/brillo
case $1 in
    +|-)
        # ddcutil tarda ~1 s: los giros de rueda que llegan mientras trabaja se descartan
        flock -n "$cache.lock" ddcutil --display 1 --noverify setvcp 10 "$1" 5 >/dev/null 2>&1
        rm -f "$cache"
        pkill -RTMIN+8 waybar
        exit 0 ;;
esac
[ -s "$cache" ] || ddcutil --display 1 --brief getvcp 10 2>/dev/null | awk '{print $4}' >"$cache"
value=$(cat "$cache")
[ -n "$value" ] || exit 0
printf '{"text":"☀ %s%%","tooltip":"Brillo de la pantalla principal (rueda para cambiarlo)"}\n' "$value"
