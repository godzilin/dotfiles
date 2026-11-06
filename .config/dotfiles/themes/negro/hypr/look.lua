-- Fósforo: a green phosphor tube. Square corners, no shadows, no blur, no animations; crt.glsl paints the whole screen.
local home = os.getenv("HOME")
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
        screen_shader = home .. "/.config/dotfiles/themes/negro/hypr/crt.glsl",
    },
    animations = { enabled = false }, -- a terminal just redraws
    debug = { damage_tracking = 0 }, -- the tube bends the picture: repainting only what changed leaves torn patches
    cursor = { no_hardware_cursors = true }, -- a hardware cursor would skip the tube and float out of place
    dwindle = { preserve_split = true },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        background_color        = rgba(C.bg0),
        focus_on_activate       = true,
    },
})

-- Bigger pixels, as on a tube: 1536x960 instead of 1920x1200. The popups below are placed for that size.
hl.monitor({ output = "eDP-1", mode = "preferred", position = "auto", scale = 1.25 })

hl.bind("SUPER + SHIFT + C", hl.dsp.exec_cmd(home .. "/.config/dotfiles/themes/negro/scripts/crt.sh"))

-- Calendar popup from the waybar clock: floats right above it (the bar is at the bottom)
hl.window_rule({
    name  = "calendar-popup",
    match = { class = "^nostromo-calendar$" },
    float = true,
    pin   = true,
    size  = "400 410",
    move  = "568 520",
})

-- Now-playing popup from the waybar media module
hl.window_rule({
    name  = "media-popup",
    match = { class = "^nostromo-media$" },
    float = true,
    pin   = true,
    size  = "420 380",
    move  = "250 550",
})

-- Wallpaper selector from the waybar wallpaper button
hl.window_rule({
    name  = "wallpaper-popup",
    match = { class = "^nostromo-wallpaper$" },
    float = true,
    pin   = true,
    size  = "580 540",
    move  = "950 390",
})

-- Weather popup from the waybar weather module
hl.window_rule({
    name  = "weather-popup",
    match = { class = "^nostromo-weather$" },
    float = true,
    pin   = true,
    size  = "460 580",
    move  = "60 350",
})
