# dotfiles

Hyprland en un ThinkPad con CachyOS, con varios temas intercambiables: cada color es un estilo
distinto que cambia todo el escritorio (barra, ventanas, terminal, GTK/Qt, Firefox, fondos...).

```fish
tema            # lista los temas, * = activo
tema naranja    # cambia de tema y recarga lo que está abierto
```

| Tema | Estilo |
|---|---|
| `naranja` | **Nostromo**: cassette futurism con la calma de macOS |
| `blanco` | **macOS**: claro y translúcido, barra de menús con menú Apple, Dock, Spotlight |

Firefox, Apple Music y las terminales ya abiertas cogen el tema nuevo al reiniciarlas.
Si un tema necesita algo de fuera (tema GTK, paquetes), `tema` avisa y su `themes/<color>/install.sh` lo instala.

## naranja: Nostromo

Base oscura cálida, ámbar de fósforo, franjas de cinta de casete y tipografía IBM Plex.

![Escritorio](../.config/dotfiles/themes/naranja/screenshots/desktop.png)
![Bloqueo](../.config/dotfiles/themes/naranja/screenshots/lock.png)

### Paleta

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

## blanco: macOS

Imitación de macOS Sonoma en claro: barra de menús translúcida (menú Apple, app activa en negrita, extras y reloj),
Dock con `nwg-dock-hyprland`, Spotlight con fuzzel, notificaciones y bloqueo como en macOS, Terminal.app "Basic"
con el prompt de zsh, Firefox tipo Safari con semáforos y fondos generados por código (`wallpapers/macos.py`).

![Escritorio](../.config/dotfiles/themes/blanco/screenshots/desktop.png)

Tema GTK [WhiteSur](https://github.com/vinceliuice/WhiteSur-gtk-theme) (versión fijada), iconos WhiteSur-light,
fuente Inter (lo más cercano a SF Pro que se puede distribuir) y DejaVu Sans Mono (la base de Menlo).
Primera vez: `~/.config/dotfiles/themes/blanco/install.sh`.

## Cómo están organizados los temas

Cada tema vive en `.config/dotfiles/themes/<color>/` y `themes/current` (local, fuera de git) apunta al activo.
Las rutas que leen las apps (`.config/waybar/style.css`, `.config/hypr/look.lua`, `.config/gtk-3.0/gtk.css`...)
son enlaces a `themes/current/...`, así que cambiar de tema es mover ese enlace y recargar.
Lo común (atajos, reglas, scripts, música) existe una sola vez y lee los colores de `themes/current/theme.json`.

| En el tema | Qué es |
|---|---|
| `theme.json` | paleta, fuentes, iconos, cursor, tema GTK y esquema KDE (lo aplica `tema`; lo leen los popups) |
| `hypr/` | `colors.lua`, `look.lua` (bordes, sombras, animaciones), `hyprlock.conf` |
| `waybar/`, `swaync/`, `fuzzel/`, `alacritty/`, `starship.toml`, `fish.fish` | barra, notificaciones, lanzador, terminal, prompt y colores de la shell |
| `gtk-3.0/`, `gtk-4.0/`, `kde/` | apps GTK y Qt |
| `firefox/`, `apple-music/` | `userChrome.css`/`userContent.css` + `user.js` |
| `popups/`, `fastfetch/`, `wallpapers/`, `screenshots/` | popup de música, logo, fondos generados por código |
| `scripts/`, `nwg-dock-hyprland/`, `install.sh` | extras propios del tema (menú Apple, Dock) y su instalación |
| `"daemons"` en `theme.json` | programas que solo corren con ese tema (el Dock); `tema` los para y arranca |

## Qué hay

| Ruta | Qué es |
|---|---|
| `.config/hypr/` | Hyprland en Lua (0.56+), hypridle, hyprpaper, scripts. Chuleta de atajos en su `README.md` |
| `.config/waybar/scripts/` | Módulo de música de la barra |
| `.config/fish/` | Shell; `functions/tema.fish` cambia de tema |
| `.config/dotfiles/firefox/install.sh` | Enlaza el tema activo de Firefox en cada perfil (una vez, con Firefox cerrado) |

## Instalar

```fish
git clone --bare https://github.com/godzilin/dotfiles.git ~/.dotfiles
function dots; git --git-dir=$HOME/.dotfiles --work-tree=$HOME $argv; end
dots checkout          # si se queja de archivos existentes, muévelos antes
dots config status.showUntrackedFiles no
sudo pacman -S --needed - < ~/.config/dotfiles/packages.txt
tema naranja           # crea themes/current y aplica GTK, Qt, iconos y cursor
```

Los iconos WhiteSur-orange salen de [vinceliuice/WhiteSur-icon-theme](https://github.com/vinceliuice/WhiteSur-icon-theme)
(`./install.sh -t orange`).

## Filosofía (para que no se rompa)

- Solo paquetes de los repos oficiales. Sin `-git`, sin plugins de Hyprland.
- Config pequeña y en módulos. Tras cada cambio: `Hyprland --verify-config`.
- KDE sigue instalado como sesión de respaldo.
- Snapshots de btrfs con snapper antes de cada actualización.
