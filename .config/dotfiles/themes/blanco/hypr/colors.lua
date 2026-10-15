-- "Blanco" palette: macOS light (system colors). Same values in theme.json.
C = {
    bg0    = "ffffff", -- window content
    bg     = "f6f6f6", -- window background
    bg1    = "ececec", -- sidebars, controls
    bg2    = "e3e3e8",
    line   = "d1d1d6", -- separators
    muted  = "8e8e93", -- tertiary label
    sub    = "6e6e73", -- secondary label
    text   = "1d1d1f", -- label
    amber  = "007aff", -- accent (systemBlue); key kept so shared code works
    yellow = "ffcc00",
    orange = "ff9500",
    red    = "ff3b30",
    green  = "34c759",
    teal   = "30b0c7",
    blue   = "007aff",
}

-- rgba("007aff", "ee") -> "rgba(007affee)"
function rgba(hex, alpha)
    return "rgba(" .. hex .. (alpha or "ff") .. ")"
end
