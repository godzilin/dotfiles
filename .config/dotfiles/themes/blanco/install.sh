#!/bin/sh
# One-time setup for the "blanco" theme: packages and the WhiteSur-Light GTK theme (pinned release) in ~/.themes.
# Icons (WhiteSur-light, with the Linux overlay built at the end) and cursor come from the same author: see the README.
set -e
sudo pacman -S --needed nwg-dock-hyprland inter-font ttf-dejavu ttf-nerd-fonts-symbols sassc
tag=2026-09-10
src=$(mktemp -d)
git clone -q --depth 1 --branch "$tag" https://github.com/vinceliuice/WhiteSur-gtk-theme.git "$src"
"$src/install.sh" -d "$HOME/.themes" -c light -o normal -t default -m --round
rm -rf "$src"
# Dock pins (only if you have none yet)
[ -f "$HOME/.cache/nwg-dock-pinned" ] || printf '%s\n' thunar firefox apple-music Alacritty discord code-oss steam systemsettings > "$HOME/.cache/nwg-dock-pinned"
# Icons: WhiteSur-light with Linux in place of the brand ones (WhiteSur-Linux, in ~/.local/share/icons):
# every file manager icon is the penguin face (icons/file-manager.svg), start-here is the Arch logo
dst="$HOME/.local/share/icons/WhiteSur-Linux"
rm -rf "$dst"; mkdir -p "$dst/scalable/apps" "$dst/scalable/places"
cat > "$dst/index.theme" <<'THEME'
[Icon Theme]
Name=WhiteSur-Linux
Comment=WhiteSur-light with Linux logos
Inherits=WhiteSur-light,hicolor,breeze
Directories=scalable/apps,scalable/places

[scalable/apps]
Size=128
MinSize=8
MaxSize=512
Type=Scalable
Context=Applications

[scalable/places]
Size=128
MinSize=8
MaxSize=512
Type=Scalable
Context=Places
THEME
here=$(cd "$(dirname "$0")" && pwd)
for n in system-file-manager file-manager user-file-manager thunar Thunar org.xfce.thunar org.xfce.filemanager \
         xfce-filemanager thunar-filemanager org.kde.dolphin nautilus org.gnome.Nautilus org.gnome.Files nemo \
         io.elementary.files dde-file-manager spacefm; do
    ln -sf "$here/icons/file-manager.svg" "$dst/scalable/apps/$n.svg"
done
for n in start-here start-here-symbolic start-here-kde start-here-kde-symbolic start-here-kde-plasma \
         start-here-kde-plasma-symbolic distributor-logo; do
    ln -sf "$here/icons/start-here.svg" "$dst/scalable/places/$n.svg"
done
gtk-update-icon-cache -q "$dst" 2>/dev/null || true
