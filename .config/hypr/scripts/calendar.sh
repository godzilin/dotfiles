#!/bin/sh
# Toggle the calendar popup under the waybar clock: the active theme's own (scripts/calpanel.py) if it has one,
# else the terminal one. Closing the script closes its window.
theme="$HOME/.config/dotfiles/themes/current/scripts/calpanel.py"
if pkill -f "^python3 .*(calpopup|calpanel)\.py"; then
    exit 0
elif [ -f "$theme" ]; then
    exec python3 "$theme"
else
    alacritty --class nostromo-calendar -o 'window.dimensions={columns=40,lines=20}' -o window.opacity=1.0 \
        -e python3 "$HOME/.config/hypr/scripts/calpopup.py"
fi
