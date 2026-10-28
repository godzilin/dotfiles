-- "Neón" palette: violet night, neon magenta and cyan, the four colours of the striped sun.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0    = "0b0217", -- deepest
    bg     = "120427", -- base
    bg1    = "1b0838", -- surfaces
    bg2    = "26104b",
    line   = "3a1b6b", -- borders, separators
    muted  = "8a6bbd",
    sub    = "c3aee6",
    text   = "f6ecff", -- cream
    amber  = "9d7bff", -- accent
    yellow = "ffd319",
    orange = "ff8a3d",
    red    = "ff3864",
    green  = "4dffb4",
    teal   = "2de2e6",
    blue   = "6a7bff",
}

-- rgba("9d7bff", "ee") -> "rgba(e9a23bee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
