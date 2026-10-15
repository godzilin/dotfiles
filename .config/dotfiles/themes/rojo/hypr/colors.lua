-- "Rojo" palette: constructivist poster. Paper, ink and one red. Same values in theme.json.
C = {
    bg0    = "e4d8bf", -- paper, darker (behind windows)
    bg     = "efe6d2", -- paper
    bg1    = "f6efe0", -- paper, light
    bg2    = "c9bda3",
    line   = "141414", -- ink
    muted  = "8a8274",
    sub    = "2a2a2a",
    text   = "141414",
    amber  = "d42a1e", -- accent: poster red; key kept so shared code works
    yellow = "b8860b", -- ochre
    orange = "d4561e",
    red    = "d42a1e",
    green  = "3b5e3a",
    teal   = "2f5d62",
    blue   = "1f3a5f",
}

-- rgba("d42a1e", "ee") -> "rgba(d42a1eee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
