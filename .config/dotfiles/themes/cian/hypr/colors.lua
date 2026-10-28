-- "Plano" palette: violet night, neon magenta and cyan, the four colours of the striped sun.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0    = "0b2a52", -- deepest
    bg     = "103566", -- base
    bg1    = "153f78", -- surfaces
    bg2    = "1c4b8c",
    line   = "3a6aa8", -- borders, separators
    muted  = "8eaed6",
    sub    = "c3d6ee",
    text   = "f3f8fe", -- cream
    amber  = "e9f3ff", -- accent
    yellow = "ffd56b",
    orange = "ffab5e",
    red    = "ff7a66",
    green  = "93e2b0",
    teal   = "86e0e8",
    blue   = "a9c9ff",
}

-- rgba("e9f3ff", "ee") -> "rgba(e9a23bee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
