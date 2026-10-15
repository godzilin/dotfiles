-- macOS: no visible borders, a hairline at most, big soft shadows, rounded corners, translucency.
hl.config({
    general = {
        gaps_in     = 5,
        gaps_out    = 10,
        border_size = 1,
        col = {
            active_border   = "rgba(00000026)", -- hairline, same as macOS window edges
            inactive_border = "rgba(0000001a)",
        },
        resize_on_border = true,
        layout = "dwindle",
    },
    decoration = {
        rounding       = 12,
        rounding_power = 3, -- continuous (squircle) corners
        dim_inactive   = false,
        shadow = {
            enabled        = true,
            range          = 40,
            render_power   = 2,
            offset         = "0 14",
            color          = "rgba(00000047)",
            color_inactive = "rgba(00000024)",
        },
        blur = {
            enabled           = true,
            size              = 12,
            passes            = 4,
            noise             = 0.01,
            brightness        = 1.0,
            contrast          = 1.0,
            vibrancy          = 0.35, -- the "vibrancy" of macOS sidebars and menu bar
            vibrancy_darkness = 0.0,
            popups            = true,
        },
    },
    animations = { enabled = true },
    dwindle = { preserve_split = true },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        background_color        = "rgba(ececf0ff)",
        focus_on_activate       = true,
    },
})

-- Springy but quick, like macOS window zooms; no bounce
hl.curve("mac",    { type = "bezier", points = { {0.25, 1}, {0.5, 1} } })
hl.curve("macin",  { type = "bezier", points = { {0.2, 0.9}, {0.1, 1} } })
hl.curve("inout",  { type = "bezier", points = { {0.65, 0}, {0.35, 1} } })

hl.animation({ leaf = "global",      enabled = true, speed = 5, bezier = "mac" })
hl.animation({ leaf = "windows",     enabled = true, speed = 4, bezier = "mac" })
hl.animation({ leaf = "windowsIn",   enabled = true, speed = 4, bezier = "macin", style = "popin 80%" })
hl.animation({ leaf = "windowsOut",  enabled = true, speed = 3, bezier = "mac",   style = "popin 80%" })
hl.animation({ leaf = "border",      enabled = true, speed = 4, bezier = "mac" })
hl.animation({ leaf = "fade",        enabled = true, speed = 3, bezier = "mac" })
hl.animation({ leaf = "layers",      enabled = true, speed = 3, bezier = "mac", style = "fade" })
hl.animation({ leaf = "workspaces",  enabled = true, speed = 5, bezier = "inout", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 4, bezier = "mac", style = "slidevert" })

-- Translucent menu bar, Dock, Spotlight and notifications
hl.layer_rule({ name = "blur-waybar", match = { namespace = "^waybar$" },             blur = true, ignore_alpha = 0.1 })
hl.layer_rule({ name = "blur-dock",   match = { namespace = "^nwg-dock$" },           blur = true, ignore_alpha = 0.1 })
hl.layer_rule({ name = "blur-fuzzel", match = { namespace = "^launcher$" },           blur = true, ignore_alpha = 0.1 })
hl.layer_rule({ name = "blur-swaync", match = { namespace = "^swaync-.*$" },          blur = true, ignore_alpha = 0.1 })

-- Menu-bar popups hang from the right, like macOS menu extras (1920 px wide screen)
hl.window_rule({
    name  = "calendar-popup",
    match = { class = "^nostromo-calendar$" },
    float = true,
    pin   = true,
    size  = "400 410",
    move  = "1510 34",
})
hl.window_rule({
    name  = "media-popup",
    match = { class = "^nostromo-media$" },
    float = true,
    pin   = true,
    size  = "360 340",
    move  = "1300 34",
})
hl.window_rule({
    name  = "weather-popup",
    match = { class = "^nostromo-weather$" },
    float = true,
    pin   = true,
    size  = "460 580",
    move  = "1200 34",
})

-- "Acerca de este Mac" (Apple menu): small floating window in the middle
hl.window_rule({
    name  = "about-this-mac",
    match = { class = "^about-this-mac$" },
    float = true,
    center = true,
    size  = "760 420",
})
