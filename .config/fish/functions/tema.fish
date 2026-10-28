function tema --description 'Cambia el tema del escritorio: tema <color>; sin argumentos lista los temas'
    set -l dir ~/.config/dotfiles/themes
    set -l actual (path basename (readlink $dir/current))
    if test (count $argv) -eq 0
        for t in (path filter -d $dir/* | path basename | string match -v current)
            set -l mark ' '
            test $t = $actual; and set mark '*'
            printf '%s %-8s %s\n' $mark $t (jq -r .name $dir/$t/theme.json)
        end
        return
    end

    set -l t $argv[1]
    set -l json $dir/$t/theme.json
    if not test -f $json
        echo "tema: no existe '$t' (temas: "(path filter -d $dir/* | path basename | string match -v current | string join ', ')")" >&2
        return 1
    end
    set -l gtk (jq -r .gtk_theme $json)
    if not path filter -q -d ~/.themes/$gtk ~/.local/share/themes/$gtk /usr/share/themes/$gtk
        echo "tema: falta el tema GTK '$gtk'; instálalo con $dir/$t/install.sh" >&2
        return 1
    end

    ~/.config/hypr/scripts/theme-daemons.sh stop  # programs of the old theme (Dock...)
    ln -sfn $t $dir/current

    # GTK/portal apps and the cursor
    set -l ui (jq -r .font_ui $json) (jq -r .font_size $json)
    gsettings set org.gnome.desktop.interface gtk-theme $gtk
    gsettings set org.gnome.desktop.wm.preferences button-layout (jq -r .buttons $json)
    gsettings set org.gnome.desktop.interface color-scheme (jq -r .color_scheme $json)
    gsettings set org.gnome.desktop.interface icon-theme (jq -r .icons $json)
    gsettings set org.gnome.desktop.interface cursor-theme (jq -r .cursor $json)
    gsettings set org.gnome.desktop.interface cursor-size (jq -r .cursor_size $json)
    gsettings set org.gnome.desktop.interface font-name "$ui[1]  $ui[2]"
    gsettings set org.gnome.desktop.interface document-font-name "$ui[1]  $ui[2]"
    gsettings set org.gnome.desktop.interface monospace-font-name (jq -r .font_mono $json)"  $ui[2]"

    # Qt/KDE apps read kdeglobals (QT_QPA_PLATFORMTHEME=kde)
    mkdir -p ~/.local/share/color-schemes
    for f in $dir/$t/kde/*.colors
        ln -sf $f ~/.local/share/color-schemes/
    end
    set -l acc (jq -r .palette.accent $json)
    set -l rgb (printf '%d,%d,%d' 0x(string sub -s 2 -l 2 $acc) 0x(string sub -s 4 -l 2 $acc) 0x(string sub -s 6 -l 2 $acc))
    kwriteconfig6 --file kdeglobals --group General --key AccentColor $rgb  # a custom accent would override the scheme
    kwriteconfig6 --file kdeglobals --group General --key LastUsedCustomAccentColor $rgb
    # kded's gtkconfig reacts to a new scheme by replacing ~/.config/gtk-*/gtk.css (our symlinks) with its own
    # file and editing settings.ini (the theme's tracked file): unload it first and put our links back after
    qdbus6 org.kde.kded6 /kded org.kde.kded6.unloadModule gtkconfig >/dev/null 2>&1
    plasma-apply-colorscheme (jq -r .kde_colors $json) >/dev/null
    for v in 3.0 4.0
        rm -f ~/.config/gtk-$v/colors.css
        ln -sfn ../dotfiles/themes/current/gtk-$v/gtk.css ~/.config/gtk-$v/gtk.css
    end
    kwriteconfig6 --file kdeglobals --group Icons --key Theme (jq -r .icons $json)
    kwriteconfig6 --file kdeglobals --group General --key font "$ui[1],$ui[2],-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
    set -l qs (jq -r '.qt_style // empty' $json)  # e.g. "Windows" for azul; empty = Plasma's default (Breeze)
    if test -n "$qs"
        kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle $qs
    else
        kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle --delete
    end

    ~/.config/dotfiles/firefox/theme.sh  # Firefox ignores activeThemeID from user.js once a theme is recorded

    # Obsidian: the vault's theme "Tema" is this link (ignored by the vault's git/Syncthing); touching it reloads it live
    set -l vault ~/Obsidian/Vault/.obsidian
    if test -d $vault
        mkdir -p $vault/themes
        ln -sfn ~/.config/dotfiles/themes/current/obsidian $vault/themes/Tema
        # appearance.json syncs between machines and has come back as {} (no theme chosen): select "Tema" again
        set -l app $vault/appearance.json
        test -s $app; or echo '{}' >$app
        if test (jq -r '.cssTheme // ""' $app) != Tema
            jq '.cssTheme = "Tema"' $app >$app.tmp; and cat $app.tmp >$app  # cat keeps the inode Obsidian watches
            rm -f $app.tmp
        end
        touch $dir/$t/obsidian/theme.css
    end

    # Fonts that ship inside the theme (fonts/), seen through ~/.config/fontconfig/conf.d/60-theme-fonts.conf
    fc-cache -f ~/.config/dotfiles/themes/current/fonts 2>/dev/null

    # Live reload of whatever is running
    if set -q HYPRLAND_INSTANCE_SIGNATURE
        hyprctl reload >/dev/null
        hyprctl setcursor (jq -r .cursor $json) (jq -r .cursor_size $json) >/dev/null
        pkill -x waybar; setsid -f waybar >/dev/null 2>&1
        pkill -x swaync; setsid -f swaync >/dev/null 2>&1  # restart, not reload: it must see the theme's fonts
        ~/.config/hypr/scripts/wallpaper.sh apply  # hyprpaper on this theme's pinned or rotating wallpaper
        ~/.config/hypr/scripts/theme-daemons.sh start
    end
    echo "tema: $t ("(jq -r .name $json)"). Firefox, Apple Music, las terminales abiertas y las fuentes de Obsidian lo cogen al reiniciarlos."
end
