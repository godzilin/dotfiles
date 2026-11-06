-- "Yoru" palette: violet night, neon magenta and cyan, the four colours of the striped sun.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0    = "0e0a1a", -- deepest
    bg     = "15102a", -- base
    bg1    = "1e1738", -- surfaces
    bg2    = "2a2048",
    line   = "40316a", -- borders, separators
    muted  = "8f80b8",
    sub    = "c4bbdc",
    text   = "f1edf8", -- cream
    amber  = "b79bff", -- accent
    yellow = "ffcf6b",
    orange = "ff9a62",
    red    = "ff6b6b",
    green  = "7fe0b0",
    teal   = "6fd9e0",
    blue   = "7f9dff",
}

-- rgba("b79bff", "ee") -> "rgba(e9a23bee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
