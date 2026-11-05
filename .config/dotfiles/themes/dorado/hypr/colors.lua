-- "Astrolabio" palette: night ink, brass and parchment; never pure black or white, so it is easy on the eyes.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0    = "0d111a", -- deepest
    bg     = "131824", -- base
    bg1    = "1a2030", -- surfaces
    bg2    = "232a3b",
    line   = "333c50", -- borders, separators
    muted  = "858b9a",
    sub    = "b9b3a4",
    text   = "e4dcc8", -- parchment
    amber  = "d6b16a", -- brass, the accent
    yellow = "e6cb82",
    orange = "d99c62",
    red    = "dc7f70",
    green  = "9dbb8f",
    teal   = "83b6ae",
    blue   = "8fabd0",
}

-- rgba("d6b16a", "ee") -> "rgba(d6b16aee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
