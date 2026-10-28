#!/bin/sh
# Toggle the weather popup under the waybar weather module: the GTK panel (weatherpanel.py) when the active theme
# styles it (popups/weatherpanel.css), else the terminal one
dir="$HOME/.config/hypr/scripts"
if pkill -f "^python3 .*(weather\.py popup|weatherpanel\.py)"; then
    exit 0
elif [ -f "$HOME/.config/dotfiles/themes/current/popups/weatherpanel.css" ]; then
    exec python3 "$dir/weatherpanel.py"
else
    alacritty --class nostromo-weather -o window.opacity=1.0 -e python3 "$dir/weather.py" popup
fi
