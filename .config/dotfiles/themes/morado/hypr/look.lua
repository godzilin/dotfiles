hl.config({
    general = {
        gaps_in     = 4,
        gaps_out    = 8,
        border_size = 2,
        col = {
            active_border   = rgba(C.amber, "dd"),
            inactive_border = rgba(C.line, "cc"),
        },
        resize_on_border = true,
        layout = "dwindle",
    },
    decoration = {
        rounding       = 10,
        rounding_power = 2.5, -- squircle-ish corners, macOS style
        shadow = {
            enabled      = true,
            range        = 16,
            render_power = 3,
            offset       = "0 4",
            color        = rgba(C.bg0, "aa"),
            color_inactive = rgba(C.bg0, "55"),
        },
        blur = {
            enabled  = true,
            size     = 5,
            passes   = 2,
            noise    = 0.02, -- a bit of film grain
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

-- Short and calm: no bounce, no spinning borders
hl.curve("out",    { type = "bezier", points = { {0.16, 1}, {0.3, 1} } })
hl.curve("inout",  { type = "bezier", points = { {0.65, 0}, {0.35, 1} } })

hl.animation({ leaf = "global",      enabled = true, speed = 6, bezier = "out" })
hl.animation({ leaf = "windows",     enabled = true, speed = 4, bezier = "out" })
hl.animation({ leaf = "windowsIn",   enabled = true, speed = 4, bezier = "out", style = "popin 92%" })
hl.animation({ leaf = "windowsOut",  enabled = true, speed = 3, bezier = "out", style = "popin 92%" })
hl.animation({ leaf = "border",      enabled = true, speed = 4, bezier = "out" })
hl.animation({ leaf = "fade",        enabled = true, speed = 3, bezier = "out" })
hl.animation({ leaf = "layers",      enabled = true, speed = 3, bezier = "out", style = "fade" })
hl.animation({ leaf = "workspaces",  enabled = true, speed = 4, bezier = "inout", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 4, bezier = "out", style = "slidevert" })

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
    move  = "760 44",
})

-- Now-playing popup from the waybar media module
hl.window_rule({
    name  = "media-popup",
    match = { class = "^nostromo-media$" },
    float = true,
    pin   = true,
    size  = "420 380",
    move  = "250 44",
})

-- Wallpaper selector from the waybar wallpaper button
hl.window_rule({
    name  = "wallpaper-popup",
    match = { class = "^nostromo-wallpaper$" },
    float = true,
    pin   = true,
    size  = "580 540",
    move  = "1330 44",
})

-- Weather popup from the waybar weather module
hl.window_rule({
    name  = "weather-popup",
    match = { class = "^nostromo-weather$" },
    float = true,
    pin   = true,
    size  = "460 660",
    move  = "60 44",
})
