#!/bin/sh
# Theme launcher (Super key, Start button): toggles the Start menu
pkill -f "^python3 .*startmenu\.py menu$" || exec python3 "$(dirname "$(readlink -f "$0")")/startmenu.py" menu
