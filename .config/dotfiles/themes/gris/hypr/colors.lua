-- NeXTSTEP palette: the four greys of the 2-bit MegaPixel display, red only for errors.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    black = "000000", -- title bars, outlines, text
    dark  = "555555", -- the Workspace background, shadows
    light = "aaaaaa", -- every panel and window face
    white = "ffffff", -- bevel highlights, text fields
    red   = "a02828",
}

-- rgba("000000", "ee") -> "rgba(000000ee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
