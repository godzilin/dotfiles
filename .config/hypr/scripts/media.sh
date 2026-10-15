#!/bin/sh
# Toggle the now-playing popup under the waybar media module
pkill -f "^python3 .*mediapopup\.py" || exec python3 "$HOME/.config/hypr/scripts/mediapopup.py"
