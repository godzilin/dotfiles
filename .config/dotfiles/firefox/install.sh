#!/bin/sh
# Link the Nostromo user.js and chrome/ into every Firefox profile. Close Firefox first.
src=$(dirname "$(readlink -f "$0")")
for base in "$HOME/.config/mozilla/firefox" "$HOME/.mozilla/firefox"; do
    [ -f "$base/profiles.ini" ] || continue
    for p in $(sed -n 's/^Path=//p' "$base/profiles.ini"); do
        dir="$base/$p"; [ -d "$dir" ] || continue
        [ -e "$dir/chrome" ] && [ ! -L "$dir/chrome" ] && mv "$dir/chrome" "$dir/chrome.bak"
        ln -sfn "$src/chrome" "$dir/chrome"
        ln -sf "$src/user.js" "$dir/user.js"
        echo "linked $dir"
    done
done
