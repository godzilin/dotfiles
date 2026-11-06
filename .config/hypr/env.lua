hl.monitor({
    output   = "eDP-1",
    mode     = "preferred",
    position = "auto",
    scale    = 1,
})
-- Any other monitor (HDMI, dock...): sensible defaults, to the right
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto-right",
    scale    = "auto",
})

hl.env("XCURSOR_THEME", "WhiteSur-cursors")
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
-- Qt apps reuse the KDE look (kdeglobals), so Dolphin & co. match Plasma
hl.env("QT_QPA_PLATFORMTHEME", "kde")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")

-- Per-machine settings (monitors, GPU): hosts/<hostname>.lua, if there is one
local hostname = io.open("/etc/hostname"):read("l")
local hostfile = os.getenv("HOME") .. "/.config/hypr/hosts/" .. hostname .. ".lua"
local f = io.open(hostfile)
if f then
    f:close()
    dofile(hostfile)
end
