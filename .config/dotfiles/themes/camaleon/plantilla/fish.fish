# Camaleón palette for CLI tools (sourced by fish/config.fish)
set -gx BAT_THEME ansi
set -gx FZF_DEFAULT_OPTS "--color=bg+:#{{bg2}},bg:-1,fg:#{{sub}},fg+:#{{text}},hl:#{{accent}},hl+:#{{accent}},border:#{{line}},prompt:#{{accent}},pointer:#{{accent}},marker:#{{orange}},info:#{{muted}},spinner:#{{accent}},header:#{{muted}} --border=rounded --prompt='› ' --pointer='▮'"
set -g fish_color_command {{text}}
set -g fish_color_param {{sub}}
set -g fish_color_quote {{yellow}}
set -g fish_color_error {{red}}
set -g fish_color_autosuggestion {{faint}}
set -g fish_color_comment {{muted}}
set -g fish_color_operator {{accent}}
set -g fish_color_redirection {{accent}}
set -g fish_color_valid_path --underline
