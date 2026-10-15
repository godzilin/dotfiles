-- Ignore apps asking to maximize themselves (keeps tiling predictable)
hl.window_rule({
    name  = "suppress-maximize-events",
    match = { class = ".*" },
    suppress_event = "maximize",
})

-- Fix some XWayland drag-and-drop issues (from the upstream example)
hl.window_rule({
    name  = "fix-xwayland-drags",
    match = { class = "^$", title = "^$", xwayland = true, float = true, fullscreen = false, pin = false },
    no_focus = true,
})

-- Small utility windows float, centered
hl.window_rule({
    name  = "float-utilities",
    match = { class = "^(pavucontrol|org.pulseaudio.pavucontrol|org.kde.polkit-kde-authentication-agent-1|org.kde.kdeconnect.app|blueman-manager|nm-connection-editor)$" },
    float = true,
    center = true,
    size  = "900 600",
})

-- File open/save dialogs
hl.window_rule({
    name  = "float-dialogs",
    match = { title = "^(Open File|Save File|Open|Save As|Abrir.*|Guardar.*)$" },
    float = true,
    center = true,
})

-- Firefox picture-in-picture stays on top
hl.window_rule({
    name  = "pip",
    match = { title = "^(Picture-in-Picture|Imagen en imagen)$" },
    float = true,
    pin   = true,
})

-- Steam popups (friends, settings) float; main window tiles
hl.window_rule({
    name  = "steam-popups",
    match = { class = "^steam$", title = "^(Friends List|Steam Settings|Lista de amigos|Parámetros de Steam)$" },
    float = true,
})

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
    size  = "400 410",
    move  = "760 44",
})
