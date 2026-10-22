-- Fósforo: a green phosphor terminal. Square corners, no shadows, no blur, no animations.
hl.config({
    general = {
        gaps_in     = 3,
        gaps_out    = 6,
        border_size = 1,
        col = {
            active_border   = rgba(C.phos),
            inactive_border = rgba(C.line),
        },
        resize_on_border = true,
        layout = "dwindle",
    },
    decoration = {
        rounding = 0,
        shadow   = { enabled = false },
        blur     = { enabled = false },
    },
    animations = { enabled = false }, -- a terminal just redraws
    dwindle = { preserve_split = true },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        background_color        = rgba(C.bg0),
        focus_on_activate       = true,
    },
})

-- Calendar popup from the waybar clock: floats right above it (the bar is at the bottom)
hl.window_rule({
    name  = "calendar-popup",
    match = { class = "^nostromo-calendar$" },
    float = true,
    pin   = true,
    size  = "400 410",
    move  = "760 766",
})

-- Now-playing popup from the waybar media module
hl.window_rule({
    name  = "media-popup",
    match = { class = "^nostromo-media$" },
    float = true,
    pin   = true,
    size  = "420 380",
    move  = "250 796",
})

-- Wallpaper selector from the waybar wallpaper button
hl.window_rule({
    name  = "wallpaper-popup",
    match = { class = "^nostromo-wallpaper$" },
    float = true,
    pin   = true,
    size  = "580 540",
    move  = "1330 636",
})

-- Weather popup from the waybar weather module
hl.window_rule({
    name  = "weather-popup",
    match = { class = "^nostromo-weather$" },
    float = true,
    pin   = true,
    size  = "460 580",
    move  = "60 596",
})
