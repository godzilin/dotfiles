hl.config({
    general = {
        gaps_in     = 6,
        gaps_out    = 14,
        border_size = 2,
        col = {
            active_border   = { colors = { rgba(C.amber, "ff"), rgba(C.teal, "ee"), rgba(C.blue, "ee"), rgba(C.amber, "ff") }, angle = 45 }, -- skin that shifts colour (borderangle loop below)
            inactive_border = rgba(C.line, "cc"),
        },
        resize_on_border = true,
        layout = "dwindle",
    },
    decoration = {
        rounding       = 18,
        rounding_power = 2.0, -- round like river stones
        shadow = {
            enabled      = true,
            range        = 24,
            render_power = 3,
            offset       = "0 6",
            color        = rgba(C.bg0, "aa"),
            color_inactive = rgba(C.bg0, "55"),
        },
        blur = {
            enabled  = true,
            size     = 7,
            passes   = 3,
            noise    = 0.01,
            popups   = true,
        },
    },
    animations = { enabled = true },
    dwindle = { preserve_split = true },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        background_color        = rgba(C.bg0),
        focus_on_activate       = true,
    },
})

-- A chameleon: still, then a quick snap (the tongue) and colour that keeps shifting slowly over the focused border
hl.curve("snap",   { type = "bezier", points = { {0.34, 1.56}, {0.64, 1} } })  -- overshoots ~10% and springs back
hl.curve("hop",    { type = "bezier", points = { {0.3, 1.3}, {0.5, 1} } })     -- a smaller bounce for whole desktops
hl.curve("smooth", { type = "bezier", points = { {0.25, 1}, {0.5, 1} } })
hl.curve("linear", { type = "bezier", points = { {0, 0}, {1, 1} } })

hl.animation({ leaf = "global",      enabled = true, speed = 6, bezier = "smooth" })
hl.animation({ leaf = "windows",     enabled = true, speed = 4, bezier = "snap" })
hl.animation({ leaf = "windowsIn",   enabled = true, speed = 4, bezier = "snap", style = "slide" })
hl.animation({ leaf = "windowsOut",  enabled = true, speed = 3, bezier = "hop", style = "popin 70%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 4, bezier = "snap" })
hl.animation({ leaf = "border",      enabled = true, speed = 8, bezier = "smooth" })
hl.animation({ leaf = "borderangle", enabled = true, speed = 80, bezier = "linear", style = "loop" })  -- one turn every ~8 s
hl.animation({ leaf = "fade",        enabled = true, speed = 6, bezier = "smooth" })
hl.animation({ leaf = "layers",      enabled = true, speed = 4, bezier = "snap", style = "slide" })
hl.animation({ leaf = "workspaces",  enabled = true, speed = 5, bezier = "hop", style = "slidefadevert 30%" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 4, bezier = "snap", style = "slidevert" })

-- Blur behind the bar, launcher and notifications
hl.layer_rule({ name = "blur-waybar", match = { namespace = "^waybar$" },     blur = true, ignore_alpha = 0.2 })
hl.layer_rule({ name = "blur-fuzzel", match = { namespace = "^launcher$" },   blur = true, ignore_alpha = 0.2 })
hl.layer_rule({ name = "blur-swaync", match = { namespace = "^swaync-.*$" },  blur = true, ignore_alpha = 0.2 })

-- Calendar popup from the waybar clock: floats right under it
hl.window_rule({
    name  = "calendar-popup",
    match = { class = "^nostromo-calendar$" },
    float = true,
    pin   = true,
    size  = "400 450",
    move  = "760 50",
})

-- Now-playing popup from the waybar media module
hl.window_rule({
    name  = "media-popup",
    match = { class = "^nostromo-media$" },
    float = true,
    pin   = true,
    size  = "420 380",
    move  = "300 50",
})

-- Wallpaper selector from the waybar wallpaper button
hl.window_rule({
    name  = "wallpaper-popup",
    match = { class = "^nostromo-wallpaper$" },
    float = true,
    pin   = true,
    size  = "580 540",
    move  = "1328 50",
})

-- Weather popup from the waybar weather module
hl.window_rule({
    name  = "weather-popup",
    match = { class = "^nostromo-weather$" },
    float = true,
    pin   = true,
    size  = "460 660",
    move  = "12 50",
})
