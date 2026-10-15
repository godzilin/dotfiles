# dotfiles · GZ—01

Hyprland en un ThinkPad con CachyOS. Estética **cassette futurism** con la calma de macOS:
base oscura cálida, ámbar de fósforo, franjas de cinta de casete y tipografía IBM Plex.

![Escritorio](../.config/dotfiles/screenshots/desktop.png)
![Bloqueo](../.config/dotfiles/screenshots/lock.png)

## Paleta "Nostromo"

| | Color | Uso |
|---|---|---|
| ![](https://placehold.co/16/121110/121110.png) | `#121110` | fondo profundo |
| ![](https://placehold.co/16/1a1814/1a1814.png) | `#1a1814` | fondo |
| ![](https://placehold.co/16/24211b/24211b.png) | `#24211b` | superficies |
| ![](https://placehold.co/16/3d382d/3d382d.png) | `#3d382d` | líneas y bordes |
| ![](https://placehold.co/16/857c69/857c69.png) | `#857c69` | texto apagado |
| ![](https://placehold.co/16/e8dfc8/e8dfc8.png) | `#e8dfc8` | texto (crema) |
| ![](https://placehold.co/16/e9a23b/e9a23b.png) | `#e9a23b` | acento ámbar |
| ![](https://placehold.co/16/e0c36a/e0c36a.png) | `#e0c36a` | franja amarilla |
| ![](https://placehold.co/16/d9652b/d9652b.png) | `#d9652b` | franja naranja |
| ![](https://placehold.co/16/c8553d/c8553d.png) | `#c8553d` | franja roja / errores |

Fuentes: **IBM Plex Sans** (interfaz) y **BlexMono Nerd Font** (terminal, barra, lanzador).
Iconos: WhiteSur-orange-dark. Cursor: WhiteSur.

## Qué hay

| Ruta | Qué es |
|---|---|
| `.config/hypr/` | Hyprland en Lua (0.56+), hyprlock, hypridle, hyprpaper, scripts. Chuleta de atajos en su `README.md` |
| `.config/waybar/` | Barra estilo panel de pletina: `VOL`, `LUM`, `NET`, `PWR`, `BAT` |
| `.config/fuzzel/` | Lanzador, portapapeles y menú de apagado |
| `.config/swaync/` | Notificaciones (tema por defecto + paleta encima) |
| `.config/alacritty/` | Terminal |
| `.config/fish/`, `.config/starship.toml` | Shell y prompt |
| `.config/fastfetch/` | Logo de casete |
| `.config/gtk-3.0/`, `.config/gtk-4.0/` | Paleta para apps GTK (adw-gtk3 / libadwaita) |
| `.local/share/color-schemes/Nostromo.colors` | Paleta para apps Qt/KDE |
| `.config/dotfiles/wallpapers/` | Fondo generado por código (`nostromo.py`) |

## Instalar

```fish
git clone --bare https://github.com/godzilin/dotfiles.git ~/.dotfiles
function dots; git --git-dir=$HOME/.dotfiles --work-tree=$HOME $argv; end
dots checkout          # si se queja de archivos existentes, muévelos antes
dots config status.showUntrackedFiles no
sudo pacman -S --needed - < ~/.config/dotfiles/packages.txt
plasma-apply-colorscheme Nostromo
gsettings set org.gnome.desktop.interface gtk-theme adw-gtk3-dark
```

Los iconos WhiteSur-orange salen de [vinceliuice/WhiteSur-icon-theme](https://github.com/vinceliuice/WhiteSur-icon-theme)
(`./install.sh -t orange`).

## Filosofía (para que no se rompa)

- Solo paquetes de los repos oficiales. Sin `-git`, sin plugins de Hyprland.
- Config pequeña y en módulos. Tras cada cambio: `Hyprland --verify-config`.
- KDE sigue instalado como sesión de respaldo.
- Snapshots de btrfs con snapper antes de cada actualización.
