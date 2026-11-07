-- "Camaleón" palette: forest at dusk, moss, sunlight between the firs, bark and berries.
-- Same values live in waybar/style.css, alacritty, fuzzel, swaync, hyprlock... (see ~/.github/README.md)
C = {
    bg0    = "{{bg0}}", -- deepest
    bg     = "{{bg}}", -- base
    bg1    = "{{bg1}}", -- surfaces
    bg2    = "{{bg2}}",
    line   = "{{line}}", -- borders, separators
    muted  = "{{muted}}",
    sub    = "{{sub}}",
    text   = "{{text}}", -- lichen
    amber  = "{{accent}}", -- accent (moss; the key keeps its name, the common config reads C.amber)
    yellow = "{{yellow}}",
    orange = "{{orange}}",
    red    = "{{red}}",
    green  = "{{green}}",
    teal   = "{{teal}}",
    blue   = "{{blue}}",
}

-- rgba("{{accent}}", "ee") -> "rgba({{accent}}ee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
