-- "Azul" palette: Windows 95/98 system colours. Same values in theme.json (which holds the DOS ones for terminal popups).
C = {
    bg0    = "000000",
    bg     = "c0c0c0", -- 3D face
    bg1    = "dfdfdf", -- 3D light
    bg2    = "808080", -- 3D shadow
    line   = "000000", -- 3D dark shadow
    muted  = "808080",
    sub    = "000000",
    text   = "000000",
    amber  = "000080", -- accent: active title bar navy; key kept so shared code works
    yellow = "ffff00",
    orange = "ff8000",
    red    = "ff0000",
    green  = "008000",
    teal   = "008080", -- desktop
    blue   = "1084d0", -- Windows 98 title gradient end
}

-- rgba("000080", "ee") -> "rgba(000080ee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
