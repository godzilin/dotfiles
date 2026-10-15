#!/bin/sh
# Toggle the calendar popup under the waybar clock
# Closing the script closes its terminal
if ! pkill -f "^python3 .*calpopup\.py"; then
    alacritty --class nostromo-calendar -o 'window.dimensions={columns=40,lines=20}' -o window.opacity=1.0 \
        -e python3 "$HOME/.config/hypr/scripts/calpopup.py"
fi
