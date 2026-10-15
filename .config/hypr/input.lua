hl.config({
    input = {
        kb_layout    = "es",
        follow_mouse = 1, -- same as FocusFollowsMouse in KDE
        touchpad = {
            natural_scroll       = true,
            tap_to_click         = true,
            disable_while_typing = true,
        },
    },
    gestures = {
        workspace_swipe_create_new = true,
    },
})

-- 3 fingers left/right: change workspace
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })

-- Same values as KDE had for this mouse. Exact name: hyprctl devices
hl.device({
    name          = "corsair-corsair-harpoon-rgb-pro-gaming-mouse",
    sensitivity   = -0.2,
    accel_profile = "flat",
})
