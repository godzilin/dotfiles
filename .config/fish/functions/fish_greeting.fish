# Skull scans in, then fastfetch draws over it (overrides the CachyOS greeting)
function fish_greeting
    python3 ~/.config/fastfetch/intro.py
    fastfetch
end
