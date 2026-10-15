-- Windows 95/98: square corners, no shadows, no blur, no animations.
-- The window border carries the Windows 98 title-bar gradient: navy to blue when active, greys when not.
hl.config({
    general = {
        gaps_in     = 2,
        gaps_out    = 4,
        border_size = 3,
        col = {
            active_border   = { colors = { rgba(C.amber), rgba(C.blue) }, angle = 0 },
            inactive_border = { colors = { rgba("808080"), rgba("b5b5b5") }, angle = 0 },
        },
        resize_on_border = true,
        layout = "dwindle",
    },
    decoration = {
        rounding = 0,
        shadow   = { enabled = false },
        blur     = { enabled = false },
    },
    animations = { enabled = false }, -- Windows 95 just draws the new state
    dwindle = { preserve_split = true },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        background_color        = rgba(C.teal),
        focus_on_activate       = true,
    },
})

-- Popups hang from the system tray, above the taskbar (1920x1200 screen, 34 px taskbar)
hl.window_rule({
    name  = "calendar-popup",
    match = { class = "^nostromo-calendar$" },
    float = true,
    pin   = true,
    size  = "400 410",
    move  = "1514 752",
})
hl.window_rule({
    name  = "media-popup",
    match = { class = "^nostromo-media$" },
    float = true,
    pin   = true,
    size  = "400 330",
    move  = "1300 832",
})
hl.window_rule({
    name  = "weather-popup",
    match = { class = "^nostromo-weather$" },
    float = true,
    pin   = true,
    size  = "460 580",
    move  = "1240 582",
})

-- Start menu dialogs (Ejecutar, Apagar el sistema): small, floating, Run sits bottom-left like in Windows
hl.window_rule({
    name  = "win95-dialog",
    match = { class = "^win95-dialog$" },
    float = true,
    center = true,
})
hl.window_rule({
    name  = "win95-run",
    match = { class = "^win95-dialog$", title = "^Ejecutar$" },
    move  = "8 1036",
})
