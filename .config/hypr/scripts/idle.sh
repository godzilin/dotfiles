#!/bin/sh
# Idle and lid actions (hypridle.conf, binds.lua).
# Plugged in, the laptop never dims, locks, blanks or sleeps; those only happen on battery.
# Closing the lid only turns the built-in screen off (logind ignores the lid: /etc/systemd/logind.conf.d/10-tapa.conf).
mark=${XDG_RUNTIME_DIR:-/tmp}/idle
on_battery() { [ "$(cat /sys/class/power_supply/AC/online)" = 0 ]; }
lid_open() { grep -q open /proc/acpi/button/lid/*/state; }
dpms() { hyprctl dispatch "hl.dsp.dpms({ action = \"$1\"$2 })" >/dev/null; }

case $1 in
    # On battery only, and leave a mark so the matching resume undoes only what was done
    dim)        on_battery && touch "$mark-dim" && brightnessctl -s set 10 ;;
    kbd-off)    on_battery && touch "$mark-kbd" && brightnessctl -sd tpacpi::kbd_backlight set 0 ;;
    lock)       on_battery && loginctl lock-session ;;
    screen-off) on_battery && touch "$mark-screen" && dpms off ;;
    suspend)    on_battery && systemctl suspend ;;

    undim)      [ -e "$mark-dim" ] && rm "$mark-dim" && brightnessctl -r ;;
    kbd-on)     [ -e "$mark-kbd" ] && rm "$mark-kbd" && brightnessctl -rd tpacpi::kbd_backlight ;;
    # Back from idle or sleep: every screen on, except the built-in one if the lid is shut
    screen-on)  rm -f "$mark-screen"; dpms on; lid_open || dpms off ', monitor = "eDP-1"' ;;

    lid-close)  dpms off ', monitor = "eDP-1"' ;;
    lid-open)   dpms on ', monitor = "eDP-1"' ;;
    *)          echo "uso: idle.sh dim|undim|kbd-off|kbd-on|lock|screen-off|screen-on|suspend|lid-close|lid-open" >&2; exit 1 ;;
esac
exit 0
