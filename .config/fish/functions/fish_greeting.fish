# The theme's intro (Nostromo: skull scans in), then fastfetch draws over it (overrides the CachyOS greeting)
function fish_greeting
    test -f ~/.config/fastfetch/intro.py; and python3 ~/.config/fastfetch/intro.py
    fastfetch
end
