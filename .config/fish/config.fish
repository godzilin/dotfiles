source /usr/share/cachyos-fish-config/cachyos-config.fish

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end

thefuck --alias | source
set -x HALCONROOT $HOME/MVTec/HALCON-26.05-Progress-Student-Edition
