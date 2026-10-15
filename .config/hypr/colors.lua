-- Catppuccin Mocha. Global so every module can use it: C.mauve, C.base...
C = {
    base     = "1e1e2e",
    mantle   = "181825",
    crust    = "11111b",
    surface0 = "313244",
    surface1 = "45475a",
    overlay0 = "6c7086",
    text     = "cdd6f4",
    mauve    = "cba6f7",
    lavender = "b4befe",
    blue     = "89b4fa",
    pink     = "f5c2e7",
    red      = "f38ba8",
}

-- rgba("cba6f7", "ee") -> "rgba(cba6f7ee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
