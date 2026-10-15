hl.config({
    general = {
        gaps_in     = 5,
        gaps_out    = 10,
        border_size = 2,
        col = {
            active_border   = { colors = { rgba(C.mauve), rgba(C.blue) }, angle = 45 },
            inactive_border = rgba(C.surface0, "aa"),
        },
        resize_on_border = true,
        layout = "dwindle",
    },
    decoration = {
        rounding       = 12,
        rounding_power = 2,
        inactive_opacity = 0.95,
        shadow = {
            enabled      = true,
            range        = 12,
            render_power = 3,
            color        = rgba(C.crust, "99"),
        },
        blur = {
            enabled  = true,
            size     = 6,
            passes   = 3,
            vibrancy = 0.17,
            popups   = true,
        },
    },
    animations = { enabled = true },
    dwindle = { preserve_split = true },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        background_color        = rgba(C.crust),
        focus_on_activate       = true,
    },
})

hl.curve("smooth", { type = "bezier", points = { {0.25, 1}, {0.5, 1} } })
hl.curve("linear", { type = "bezier", points = { {0, 0},    {1, 1} } })
hl.curve("bounce", { type = "spring", mass = 1, stiffness = 200, dampening = 20 })

hl.animation({ leaf = "global",      enabled = true, speed = 8,   bezier = "default" })
hl.animation({ leaf = "border",      enabled = true, speed = 6,   bezier = "smooth" })
hl.animation({ leaf = "borderangle", enabled = true, speed = 60,  bezier = "linear", style = "loop" })
hl.animation({ leaf = "windows",     enabled = true, speed = 5,   spring = "bounce" })
hl.animation({ leaf = "windowsIn",   enabled = true, speed = 4,   spring = "bounce", style = "popin 80%" })
hl.animation({ leaf = "windowsOut",  enabled = true, speed = 2,   bezier = "smooth", style = "popin 80%" })
hl.animation({ leaf = "fade",        enabled = true, speed = 3,   bezier = "smooth" })
hl.animation({ leaf = "layers",      enabled = true, speed = 3,   bezier = "smooth", style = "slide" })
hl.animation({ leaf = "workspaces",  enabled = true, speed = 4,   bezier = "smooth", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 4, bezier = "smooth", style = "slidevert" })
