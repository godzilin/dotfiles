#!/bin/sh
# Toggle the weather popup under the waybar weather module
if ! pkill -f "^python3 .*weather\.py popup"; then
    alacritty --class nostromo-weather -o window.opacity=1.0 \
        -e python3 "$HOME/.config/hypr/scripts/weather.py" popup
fi
