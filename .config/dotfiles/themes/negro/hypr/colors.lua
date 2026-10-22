-- "Fósforo" palette: pure black, one green phosphor (P1) in several intensities; red only for errors.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0   = "000000", -- deepest
    bg    = "040704", -- base
    bg1   = "091209", -- surfaces
    bg2   = "0f1f10",
    line  = "1a3a1d", -- borders, separators
    muted = "3f9147",
    sub   = "63cc6c",
    text  = "a6ffad", -- bright phosphor
    phos  = "33ff4d", -- accent
    red   = "ff5a4a",
}

-- rgba("33ff4d", "ee") -> "rgba(33ff4dee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
