-- "Bosque" palette: forest at dusk, moss, sunlight between the firs, bark and berries.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0    = "0f140f", -- deepest
    bg     = "151c15", -- base
    bg1    = "1d261c", -- surfaces
    bg2    = "263224",
    line   = "34432f", -- borders, separators
    muted  = "7f8f72",
    sub    = "aab89a",
    text   = "e4e6d0", -- lichen
    amber  = "9cc26b", -- accent (moss; the key keeps its name, the common config reads C.amber)
    yellow = "e3c56e",
    orange = "c9894b",
    red    = "c0624a",
    green  = "7fae6e",
    teal   = "6aa39a",
    blue   = "7f9fb5",
}

-- rgba("9cc26b", "ee") -> "rgba(9cc26bee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
