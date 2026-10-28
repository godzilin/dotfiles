#!/bin/sh
# Toggle the calendar popup under the waybar clock: the GTK panel (calpanel.py) when the active theme styles it
# (popups/calpanel.css), else the terminal one. Closing the script closes its window.
dir="$HOME/.config/hypr/scripts"
if pkill -f "^python3 .*(calpopup|calpanel)\.py"; then
    exit 0
elif [ -f "$HOME/.config/dotfiles/themes/current/popups/calpanel.css" ]; then
    exec python3 "$dir/calpanel.py"
else
    alacritty --class nostromo-calendar -o 'window.dimensions={columns=40,lines=20}' -o window.opacity=1.0 \
        -e python3 "$dir/calpopup.py"
fi
