# Blanco: light syntax colours (Xcode-ish) for fish and fzf (sourced by fish/config.fish)
set -gx BAT_THEME ansi
set -gx FZF_DEFAULT_OPTS "--color=light,bg+:#e3e3e8,bg:-1,fg:#1d1d1f,fg+:#1d1d1f,hl:#007aff,hl+:#007aff,border:#d1d1d6,prompt:#007aff,pointer:#007aff,marker:#007aff,info:#8e8e93,spinner:#007aff,header:#8e8e93 --border=rounded --prompt='› ' --pointer='›'"
set -g fish_color_command 1d1d1f
set -g fish_color_param 3c3c43
set -g fish_color_quote c41a16
set -g fish_color_error ff3b30
set -g fish_color_autosuggestion 8e8e93
set -g fish_color_comment 8e8e93
set -g fish_color_operator 007aff
set -g fish_color_redirection 007aff
set -g fish_color_valid_path --underline
