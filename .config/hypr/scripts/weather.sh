#!/bin/sh
# Toggle the weather popup under the waybar weather module: the active theme's own (scripts/weatherpanel.py) if it
# has one, else the terminal one
theme="$HOME/.config/dotfiles/themes/current/scripts/weatherpanel.py"
if pkill -f "^python3 .*(weather\.py popup|weatherpanel\.py)"; then
    exit 0
elif [ -f "$theme" ]; then
    exec python3 "$theme"
else
    alacritty --class nostromo-weather -o window.opacity=1.0 \
        -e python3 "$HOME/.config/hypr/scripts/weather.py" popup
fi
