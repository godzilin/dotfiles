#!/bin/sh
# App launcher of the active theme (azul: Start menu); fuzzel when the theme has none
theme="$HOME/.config/dotfiles/themes/current/scripts/launcher.sh"
[ -x "$theme" ] && exec "$theme"
pkill -x fuzzel || exec fuzzel
