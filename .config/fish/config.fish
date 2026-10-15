source /usr/share/cachyos-fish-config/cachyos-config.fish

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end

thefuck --alias | source
set -x HALCONROOT $HOME/MVTec/HALCON-26.05-Progress-Student-Edition

if status is-interactive
    # CLI colours of the active theme (`tema`)
    source ~/.config/dotfiles/themes/current/fish.fish

    starship init fish | source
    zoxide init fish --cmd cd | source  # `cd foo` jumps to the most used dir matching "foo"
end
