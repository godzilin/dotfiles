#!/bin/sh
# One-time setup for the "negro" theme (Fósforo): IBM 3270 font (official repo) and green Papirus folders
# (the same Papirus-Verde icon theme the verde theme builds).
set -e
sudo pacman -S --needed ttf-3270-nerd papirus-icon-theme adw-gtk-theme capitaine-cursors
[ -d "$HOME/.local/share/icons/Papirus-Verde" ] || "$(dirname "$0")/../verde/install.sh"
