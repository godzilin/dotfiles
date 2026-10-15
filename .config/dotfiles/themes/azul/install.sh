#!/bin/sh
# One-time setup for the "azul" theme (Windows 95/98): Chicago95 GTK theme, icons and cursors
# from a pinned commit, copied into ~/.themes, ~/.local/share/icons and ~/.icons. No sudo needed.
# The W95FA font (OFL) ships inside the theme (fonts/) and is only visible while azul is active.
set -e
commit=5da19b8b  # grassmunk/Chicago95, 2026-10-01
src=$(mktemp -d)
git clone -q https://github.com/grassmunk/Chicago95.git "$src"
git -C "$src" checkout -q "$commit"
mkdir -p "$HOME/.themes" "$HOME/.local/share/icons" "$HOME/.icons"
rm -rf "$HOME/.themes/Chicago95" "$HOME/.local/share/icons/Chicago95" "$HOME/.icons/Chicago95_Animated_Hourglass_Cursors"
cp -r "$src/Theme/Chicago95" "$HOME/.themes/"
cp -r "$src/Icons/Chicago95" "$HOME/.local/share/icons/"
cp -r "$src/Cursors/Chicago95_Animated_Hourglass_Cursors" "$HOME/.icons/"
gtk-update-icon-cache -q "$HOME/.local/share/icons/Chicago95" 2>/dev/null || true
# MS-DOS Prompt font for the terminal (Perfect DOS VGA 437 remake, as shipped by Chicago95)
mkdir -p "$HOME/.local/share/fonts"
cp "$src/Fonts/vga_font/MorePerfectDOSVGA.ttf" "$HOME/.local/share/fonts/"
fc-cache -f "$HOME/.local/share/fonts"
rm -rf "$src"
