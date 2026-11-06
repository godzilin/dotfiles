-- Desktop: RTX 3070, DP-1 main (144 Hz, VRR) and HDMI-A-1 on its right, as in Plasma
hl.monitor({
    output   = "DP-1",
    mode     = "2560x1440@143.97",
    position = "0x0",
    scale    = 1.25,
    vrr      = 2,  -- fullscreen only, like Plasma's "Automatic"
})
hl.monitor({
    output   = "HDMI-A-1",
    mode     = "1920x1080@60",
    position = "2048x126",  -- right of DP-1's 2048x1152 logical size, vertically centred
    scale    = 1.2,
})

hl.env("LIBVA_DRIVER_NAME", "nvidia")
hl.env("__GLX_VENDOR_LIBRARY_NAME", "nvidia")

-- With a fractional scale X11 apps would be upscaled: games and Steam keep the real 2560x1440, Steam scales itself
hl.config({ xwayland = { force_zero_scaling = true } })
hl.env("STEAM_FORCE_DESKTOPUI_SCALING", "1.25")

-- Each monitor has its own 1..9 (binds.lua adds the offset): ids 1-9 on DP-1, 11-19 on HDMI-A-1.
-- The bar shows 11-19 as 1-9 (format-icons in each theme); same-name workspaces confuse Waybar
workspace_offsets = { ["HDMI-A-1"] = 10 }
for i = 1, 9 do
    hl.workspace_rule({ workspace = tostring(i), monitor = "DP-1", default = i == 1, persistent = i <= 4 })
    hl.workspace_rule({
        workspace  = tostring(10 + i),
        monitor    = "HDMI-A-1",
        default    = i == 1,
        persistent = i <= 4,
    })
end
