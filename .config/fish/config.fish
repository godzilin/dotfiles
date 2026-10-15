source /usr/share/cachyos-fish-config/cachyos-config.fish

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end

thefuck --alias | source
set -x HALCONROOT $HOME/MVTec/HALCON-26.05-Progress-Student-Edition

if status is-interactive
    # Nostromo palette for CLI tools
    set -gx BAT_THEME ansi
    set -gx FZF_DEFAULT_OPTS "--color=bg+:#2f2b23,bg:-1,fg:#b3a891,fg+:#e8dfc8,hl:#e9a23b,hl+:#e9a23b,border:#3d382d,prompt:#e9a23b,pointer:#e9a23b,marker:#d9652b,info:#857c69,spinner:#e9a23b,header:#857c69 --border=rounded --prompt='› ' --pointer='▮'"
    set -g fish_color_command e8dfc8
    set -g fish_color_param b3a891
    set -g fish_color_quote e0c36a
    set -g fish_color_error c8553d
    set -g fish_color_autosuggestion 4a4438
    set -g fish_color_comment 857c69
    set -g fish_color_operator e9a23b
    set -g fish_color_redirection e9a23b
    set -g fish_color_valid_path --underline

    starship init fish | source
    zoxide init fish --cmd cd | source  # `cd foo` jumps to the most used dir matching "foo"
end
