#!/bin/sh
# One-time setup for the "blanco" theme: packages and the WhiteSur-Light GTK theme (pinned release) in ~/.themes.
# Icons (WhiteSur-light) and cursor come from the same author: see the README.
set -e
sudo pacman -S --needed nwg-dock-hyprland inter-font ttf-dejavu ttf-nerd-fonts-symbols sassc
tag=2026-09-10
src=$(mktemp -d)
git clone -q --depth 1 --branch "$tag" https://github.com/vinceliuice/WhiteSur-gtk-theme.git "$src"
"$src/install.sh" -d "$HOME/.themes" -c light -o normal -t default -m --round
rm -rf "$src"
# Dock pins (only if you have none yet)
[ -f "$HOME/.cache/nwg-dock-pinned" ] || printf '%s\n' thunar firefox apple-music Alacritty discord code-oss steam systemsettings > "$HOME/.cache/nwg-dock-pinned"
