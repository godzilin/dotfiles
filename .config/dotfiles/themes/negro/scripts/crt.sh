#!/bin/sh
# Turn the CRT tube (hypr/crt.glsl) on and off: Super+Shift+C or the CRT cell in the bar.
shader="$HOME/.config/dotfiles/themes/negro/hypr/crt.glsl"
if hyprctl getoption decoration:screen_shader | grep -q crt.glsl; then shader=""; fi
hyprctl eval "hl.config({ decoration = { screen_shader = \"$shader\" } })" >/dev/null
