-- "Nostromo" palette: warm dark base, phosphor amber, cassette stripes.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0    = "121110", -- deepest
    bg     = "1a1814", -- base
    bg1    = "24211b", -- surfaces
    bg2    = "2f2b23",
    line   = "3d382d", -- borders, separators
    muted  = "857c69",
    sub    = "b3a891",
    text   = "e8dfc8", -- cream
    amber  = "e9a23b", -- accent
    yellow = "e0c36a",
    orange = "d9652b",
    red    = "c8553d",
    green  = "8fae7e",
    teal   = "6f9e98",
    blue   = "7b93a8",
}

-- rgba("e9a23b", "ee") -> "rgba(e9a23bee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
