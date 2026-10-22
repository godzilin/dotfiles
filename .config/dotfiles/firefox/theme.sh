#!/bin/sh
# Make every Firefox profile (and the Apple Music one) use the built-in theme its user.js asks for.
# Firefox only reads extensions.activeThemeID when nothing is recorded yet: the theme that wins is the one marked
# active in extensions.json, so `tema` calls this to flip it there. Profiles open right now are skipped
# (Firefox rewrites the file when it quits); run it again with them closed.
for base in "$HOME/.config/mozilla/firefox" "$HOME/.mozilla/firefox"; do
    [ -f "$base/profiles.ini" ] || continue
    sed -n 's/^Path=//p' "$base/profiles.ini" | while read -r p; do
        case $p in /*) dir=$p ;; *) dir="$base/$p" ;; esac
        db="$dir/extensions.json"
        want=$(sed -n 's/^user_pref("extensions.activeThemeID", "\([^"]*\)").*/\1/p' "$dir/user.js" 2>/dev/null | tail -n1)
        [ -n "$want" ] && [ -f "$db" ] || continue
        jq -e --arg t "$want" 'any(.addons[]; .id == $t)' "$db" >/dev/null || continue  # theme not in this Firefox
        jq -e --arg t "$want" 'all(.addons[] | select(.type == "theme"); .active == (.id == $t))' "$db" >/dev/null && continue
        if fuser -s "$dir/.parentlock" 2>/dev/null; then
            echo "firefox: $(basename "$dir") está abierto; ciérralo y repite (~/.config/dotfiles/firefox/theme.sh)" >&2
            continue
        fi
        tmp=$(mktemp) &&
        jq --arg t "$want" '.addons |= map(if .type == "theme"
                then .active = (.id == $t) | .userDisabled = (.id != $t) else . end)' "$db" >"$tmp" &&
        mv "$tmp" "$db" &&
        rm -f "$dir/addonStartup.json.lz4"  # startup cache of the active add-ons, rebuilt from extensions.json
    done
done
