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
    ln -sfn $t $dir/current

    # GTK/portal apps and the cursor
    set -l ui (jq -r .font_ui $json) (jq -r .font_size $json)
    gsettings set org.gnome.desktop.interface gtk-theme (jq -r .gtk_theme $json)
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
    plasma-apply-colorscheme (jq -r .kde_colors $json) >/dev/null
    kwriteconfig6 --file kdeglobals --group Icons --key Theme (jq -r .icons $json)
    kwriteconfig6 --file kdeglobals --group General --key font "$ui[1],$ui[2],-1,5,400,0,0,0,0,0,0,0,0,0,0,1"

    # Live reload of whatever is running
    if set -q HYPRLAND_INSTANCE_SIGNATURE
        hyprctl reload >/dev/null
        hyprctl setcursor (jq -r .cursor $json) (jq -r .cursor_size $json) >/dev/null
        pkill -SIGUSR2 -x waybar
        swaync-client -rs >/dev/null 2>&1
        pkill -x hyprpaper; setsid -f hyprpaper >/dev/null 2>&1
    end
    echo "tema: $t ("(jq -r .name $json)"). Firefox, Apple Music y las terminales abiertas lo cogen al reiniciarlas."
end
