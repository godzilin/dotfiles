-- Shortcuts kept from KDE where possible. Cheat sheet: see the README in this folder.
local mod      = "SUPER"
local terminal = "alacritty"
local menu     = "fuzzel"
local scripts  = os.getenv("HOME") .. "/.config/hypr/scripts/"
local exec     = hl.dsp.exec_cmd

-- Apps (same keys as KDE)
hl.bind(mod .. " + masculine", exec(terminal))  -- Super+º
hl.bind(mod .. " + Return",    exec(terminal))
hl.bind(mod .. " + W",         exec("firefox"))
hl.bind(mod .. " + D",         exec("discord"))
hl.bind(mod .. " + S",         exec("steam"))
hl.bind(mod .. " + X",         exec("lutris"))
hl.bind(mod .. " + C",         exec("systemsettings"))
hl.bind(mod .. " + E",         exec("thunar"))

-- Launcher: tap Super alone (like KDE), or Super+Space / Alt+F1
hl.bind(mod .. " + Super_L", exec("pkill fuzzel || " .. menu), { release = true })
hl.bind(mod .. " + Space",   exec("pkill fuzzel || " .. menu))
hl.bind("ALT + F1",          exec("pkill fuzzel || " .. menu))

-- Clipboard history, notifications, power
hl.bind(mod .. " + V", exec("cliphist list | fuzzel --dmenu --prompt '󰅌 ' | cliphist decode | wl-copy"))
hl.bind(mod .. " + N", exec("swaync-client -t -sw"))
hl.bind(mod .. " + B", exec(scripts .. "powerprofile.sh"))
hl.bind(mod .. " + L", exec("loginctl lock-session"))
hl.bind("CTRL + ALT + Delete", exec(scripts .. "powermenu.sh"))
hl.bind(mod .. " + SHIFT + B", exec("pkill waybar; waybar"))  -- if the bar dies or glitches

-- Screenshots (saved to ~/Pictures/Screenshots and copied)
local shot = "~/Pictures/Screenshots/$(date +%F_%H-%M-%S).png"
hl.bind("Print",         exec("grim -g \"$(slurp)\" - | tee " .. shot .. " | wl-copy"))
hl.bind("SHIFT + Print", exec("grim - | tee " .. shot .. " | wl-copy"))

-- Windows
hl.bind(mod .. " + Q",        hl.dsp.window.close())
hl.bind("ALT + F4",           hl.dsp.window.close())
hl.bind(mod .. " + CTRL + Escape", hl.dsp.window.kill())
hl.bind(mod .. " + F",        hl.dsp.window.float({ action = "toggle" }))
hl.bind(mod .. " + Prior",    hl.dsp.window.fullscreen({ mode = "maximized" }))  -- Super+PgUp
hl.bind(mod .. " + F11",      hl.dsp.window.fullscreen())
hl.bind(mod .. " + T",        hl.dsp.layout("togglesplit"))
hl.bind(mod .. " + P",        hl.dsp.window.pin())
-- "Minimize": Super+PgDown hides into a drawer, Super+Backspace shows/hides the drawer
hl.bind(mod .. " + Next",      hl.dsp.window.move({ workspace = "special:min", follow = false }))
hl.bind(mod .. " + BackSpace", hl.dsp.workspace.toggle_special("min"))

hl.bind("ALT + Tab", function()
    hl.dispatch(hl.dsp.window.cycle_next())
    hl.dispatch(hl.dsp.window.bring_to_top())
end)
hl.bind("ALT + SHIFT + Tab", function()
    hl.dispatch(hl.dsp.window.cycle_next({ prev = true }))
    hl.dispatch(hl.dsp.window.bring_to_top())
end)

-- Focus / move with arrows (Super+Alt+arrows also focus, as in KDE)
for _, dir in ipairs({ "left", "right", "up", "down" }) do
    hl.bind(mod .. " + " .. dir,           hl.dsp.focus({ direction = dir }))
    hl.bind(mod .. " + ALT + " .. dir,     hl.dsp.focus({ direction = dir }))
    hl.bind(mod .. " + SHIFT + " .. dir,   hl.dsp.window.move({ direction = dir }))
end

-- Resize with Super+R then arrows, Escape to leave
hl.define_submap("resize", function()
    hl.bind("right", hl.dsp.window.resize({ x = 40,  y = 0 }),   { repeating = true })
    hl.bind("left",  hl.dsp.window.resize({ x = -40, y = 0 }),   { repeating = true })
    hl.bind("up",    hl.dsp.window.resize({ x = 0,   y = -40 }), { repeating = true })
    hl.bind("down",  hl.dsp.window.resize({ x = 0,   y = 40 }),  { repeating = true })
    hl.bind("Escape", hl.dsp.submap("reset"))
    hl.bind("Return", hl.dsp.submap("reset"))
end)
hl.bind(mod .. " + R", hl.dsp.submap("resize"))

-- Mouse: Super+left drag moves, Super+right drag resizes
hl.bind(mod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Workspaces: Super+1..9 (Shift moves the window), Ctrl+F1..F4 as in KDE
for i = 1, 9 do
    hl.bind(mod .. " + " .. i,          hl.dsp.focus({ workspace = i }))
    hl.bind(mod .. " + SHIFT + " .. i,  hl.dsp.window.move({ workspace = i }))
end
for i = 1, 4 do
    hl.bind("CTRL + F" .. i, hl.dsp.focus({ workspace = i }))
end
hl.bind(mod .. " + CTRL + right",         hl.dsp.focus({ workspace = "r+1" }))
hl.bind(mod .. " + CTRL + left",          hl.dsp.focus({ workspace = "r-1" }))
hl.bind(mod .. " + CTRL + SHIFT + right", hl.dsp.window.move({ workspace = "r+1" }))
hl.bind(mod .. " + CTRL + SHIFT + left",  hl.dsp.window.move({ workspace = "r-1" }))
hl.bind(mod .. " + mouse_down",           hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mod .. " + mouse_up",             hl.dsp.focus({ workspace = "e-1" }))

-- Media keys (work on the lock screen too)
local always = { locked = true, repeating = true }
hl.bind("XF86AudioRaiseVolume",         exec("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), always)
hl.bind("XF86AudioLowerVolume",         exec("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),      always)
hl.bind("SHIFT + XF86AudioRaiseVolume", exec("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 1%+"), always)
hl.bind("SHIFT + XF86AudioLowerVolume", exec("wpctl set-volume @DEFAULT_AUDIO_SINK@ 1%-"),      always)
hl.bind("XF86AudioMute",                exec("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true })
hl.bind("XF86AudioMicMute",             exec("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),   { locked = true })
hl.bind("XF86MonBrightnessUp",          exec("brightnessctl -e4 -n2 set 5%+"), always)
hl.bind("XF86MonBrightnessDown",        exec("brightnessctl -e4 -n2 set 5%-"), always)
hl.bind("SHIFT + XF86MonBrightnessUp",  exec("brightnessctl -e4 -n2 set 1%+"), always)
hl.bind("SHIFT + XF86MonBrightnessDown",exec("brightnessctl -e4 -n2 set 1%-"), always)
hl.bind("XF86KbdBrightnessUp",          exec("brightnessctl -d tpacpi::kbd_backlight set +1"), { locked = true })
hl.bind("XF86KbdBrightnessDown",        exec("brightnessctl -d tpacpi::kbd_backlight set 1-"), { locked = true })
hl.bind("XF86AudioPlay",  exec("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPause", exec("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioNext",  exec("playerctl next"),       { locked = true })
hl.bind("XF86AudioPrev",  exec("playerctl previous"),   { locked = true })

-- Bar popups (calendar, now playing) close on any click outside them. non_consuming: the click still reaches the app.
-- Clicks on the bar are left alone, so its buttons can toggle the popups themselves.
local popups = {
    ["nostromo-calendar"] = "pkill -f '^python3 .*calpopup\\.py'",
    ["nostromo-media"]    = "pkill -f '^python3 .*mediapopup\\.py'",
    ["nostromo-weather"]  = "pkill -f '^python3 .*weather\\.py popup'",
}
local function xy(v) return v.x or v[1], v.y or v[2] end
hl.bind("mouse:272", function()
    local cur = hl.get_cursor_pos()
    if not cur or cur.y < 40 then return end
    for class, close in pairs(popups) do
        local win = hl.get_windows({ class = class })[1]
        if win then
            local x, y = xy(win.at)
            local w, h = xy(win.size)
            if cur.x < x or cur.x > x + w or cur.y < y or cur.y > y + h then
                hl.exec_cmd(close)
            end
        end
    end
end, { non_consuming = true })
