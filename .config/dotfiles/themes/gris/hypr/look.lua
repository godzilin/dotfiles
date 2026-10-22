-- NeXTSTEP: square windows with a black frame (the active one) on the dark grey Workspace, a hard drop shadow,
-- no blur. The vertical menu (waybar) sits top-left and the Dock (nwg-dock-hyprland) runs down the right edge.
hl.config({
    general = {
        gaps_in     = 4,
        gaps_out    = 10,
        border_size = 2,
        col = {
            active_border   = rgba(C.black),
            inactive_border = rgba(C.dark),
        },
        resize_on_border = true,
        layout = "dwindle",
    },
    decoration = {
        rounding = 0,
        shadow = {
            enabled      = true,
            range        = 2,   -- a hard shadow offset to the bottom-right, like NeXT panels
            render_power = 1,
            sharp        = true,
            offset       = "3 3",
            color        = rgba(C.black, "aa"),
            color_inactive = rgba(C.black, "66"),
        },
        blur = { enabled = false },
    },
    animations = { enabled = true },
    dwindle = { preserve_split = true },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        background_color        = rgba(C.dark),
        focus_on_activate       = true,
    },
})

-- NeXT windows opened with a quick zoom out of their icon; keep it short and linear
hl.curve("lin", { type = "bezier", points = { {0.25, 0.25}, {0.75, 0.75} } })

hl.animation({ leaf = "global",     enabled = true,  speed = 3, bezier = "lin" })
hl.animation({ leaf = "windowsIn",  enabled = true,  speed = 2, bezier = "lin", style = "popin 60%" })
hl.animation({ leaf = "windowsOut", enabled = true,  speed = 2, bezier = "lin", style = "popin 60%" })
hl.animation({ leaf = "border",     enabled = false })
hl.animation({ leaf = "fade",       enabled = false })
hl.animation({ leaf = "workspaces", enabled = true,  speed = 3, bezier = "lin", style = "slidevert" })

-- Calendar popup from the waybar clock: opens beside the menu column, like a NeXT submenu
hl.window_rule({
    name  = "calendar-popup",
    match = { class = "^nostromo-calendar$" },
    float = true,
    pin   = true,
    size  = "450 430",
    move  = "170 10",
})

-- Now-playing popup from the waybar media module
hl.window_rule({
    name  = "media-popup",
    match = { class = "^nostromo-media$" },
    float = true,
    pin   = true,
    size  = "420 380",
    move  = "170 10",
})

-- Wallpaper selector from the waybar wallpaper button
hl.window_rule({
    name  = "wallpaper-popup",
    match = { class = "^nostromo-wallpaper$" },
    float = true,
    pin   = true,
    size  = "580 540",
    move  = "170 10",
})

-- Weather popup from the waybar weather module
hl.window_rule({
    name  = "weather-popup",
    match = { class = "^nostromo-weather$" },
    float = true,
    pin   = true,
    size  = "510 600",
    move  = "170 10",
})
