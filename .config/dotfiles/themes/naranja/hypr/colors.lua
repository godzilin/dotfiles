-- "Nostromo" palette: warm dark base, phosphor amber, cassette stripes.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0    = "15100c", -- deepest
    bg     = "1e1610", -- base
    bg1    = "2a1f17", -- surfaces
    bg2    = "3a2b20",
    line   = "57432f", -- borders, separators
    muted  = "9a8468",
    sub    = "c9b89a",
    text   = "efe3cb", -- cream
    amber  = "f28c28", -- accent
    yellow = "eec068",
    orange = "e0662a",
    red    = "d6503a",
    green  = "a3a86b",
    teal   = "7fa39a",
    blue   = "8ea0a8",
}

-- rgba("f28c28", "ee") -> "rgba(e9a23bee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
