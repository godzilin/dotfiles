hl.on("hyprland.start", function()
    -- Plasma Login logs straight into Hyprland (/etc/plasmalogin.conf [Autologin]): lock at once, so the password
    -- is asked by the active theme's hyprlock instead of KDE's greeter. A login typed at the greeter is not locked.
    hl.exec_cmd([[sh -c '[ "$(loginctl show-session "$XDG_SESSION_ID" -p Service --value)" = plasmalogin-autologin ] && exec hyprlock']])
    hl.exec_cmd("waybar")
    hl.exec_cmd(os.getenv("HOME") .. "/.config/hypr/scripts/wallpaper.sh apply")  -- hyprpaper, on the pinned or rotating wallpaper
    hl.exec_cmd("hypridle")
    hl.exec_cmd("swaync")
    hl.exec_cmd(os.getenv("HOME") .. "/.config/hypr/scripts/theme-daemons.sh start")  -- Dock etc. of the active theme
    hl.exec_cmd("/usr/lib/polkit-kde-authentication-agent-1")
    hl.exec_cmd("/usr/lib/pam_kwallet_init")
    hl.exec_cmd("/usr/bin/kdeconnectd")
    hl.exec_cmd("wl-paste --watch cliphist store")
    -- Notifies if you booted from a snapper snapshot (CachyOS/limine)
    hl.exec_cmd("limine-snapper-notify")
    hl.exec_cmd("sh -c 'sleep 3 && arch-update --tray'")
end)
