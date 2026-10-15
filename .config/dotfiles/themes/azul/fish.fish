# Azul: MS-DOS had no syntax colours; keep it grey, errors in bright red (sourced by fish/config.fish)
set -gx BAT_THEME ansi
set -gx FZF_DEFAULT_OPTS "--color=bg+:#0000aa,bg:-1,fg:#aaaaaa,fg+:#ffffff,hl:#ffff55,hl+:#ffff55,border:#aaaaaa,prompt:#aaaaaa,pointer:#ffffff,marker:#ffff55,info:#555555,spinner:#aaaaaa,header:#555555 --border=sharp --prompt='C:\\> ' --pointer='>'"
set -g fish_color_command ffffff
set -g fish_color_param aaaaaa
set -g fish_color_quote aaaaaa
set -g fish_color_error ff5555
set -g fish_color_autosuggestion 555555
set -g fish_color_comment 555555
set -g fish_color_operator aaaaaa
set -g fish_color_redirection aaaaaa
set -g fish_color_valid_path --underline
