-- Constructivism: hard edges, thick red frame on the active window, a solid ink shadow offset like a misprinted plate,
-- wide poster margins, mechanical animations that slide in and overshoot a little.
hl.config({
    general = {
        gaps_in     = 7,
        gaps_out    = 16,
        border_size = 4,
        col = {
            active_border   = rgba(C.red),
            inactive_border = rgba(C.line),
        },
        resize_on_border = true,
        layout = "dwindle",
    },
    decoration = {
        rounding = 0,
        shadow = {
            enabled        = true,
            range          = 1,
            render_power   = 4,
            sharp          = true,
            offset         = "9 9",
            color          = rgba(C.line),
            color_inactive = rgba(C.line, "66"),
        },
        blur = { enabled = false },
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

-- A press stamping the sheet: fast in, small overshoot, hard stop
hl.curve("press", { type = "bezier", points = { {0.3, 1.35}, {0.4, 1} } })
hl.curve("cut",   { type = "bezier", points = { {0.7, 0}, {0.2, 1} } })

hl.animation({ leaf = "global",      enabled = true, speed = 4, bezier = "press" })
hl.animation({ leaf = "windows",     enabled = true, speed = 3, bezier = "press" })
hl.animation({ leaf = "windowsIn",   enabled = true, speed = 3, bezier = "press", style = "slide" })
hl.animation({ leaf = "windowsOut",  enabled = true, speed = 2, bezier = "cut",   style = "slide" })
hl.animation({ leaf = "border",      enabled = true, speed = 2, bezier = "cut" })
hl.animation({ leaf = "fade",        enabled = true, speed = 2, bezier = "cut" })
hl.animation({ leaf = "layers",      enabled = true, speed = 3, bezier = "press", style = "slide" })
hl.animation({ leaf = "workspaces",  enabled = true, speed = 3, bezier = "press", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 3, bezier = "press", style = "slidevert" })

-- Popups hang from the band at the top (1920 px wide screen, 44 px bar)
hl.window_rule({
    name  = "calendar-popup",
    match = { class = "^nostromo-calendar$" },
    float = true,
    pin   = true,
    size  = "400 410",
    move  = "760 58",
})
hl.window_rule({
    name  = "media-popup",
    match = { class = "^nostromo-media$" },
    float = true,
    pin   = true,
    size  = "420 380",
    move  = "1180 58",
})
hl.window_rule({
    name  = "weather-popup",
    match = { class = "^nostromo-weather$" },
    float = true,
    pin   = true,
    size  = "460 580",
    move  = "1440 58",
})
