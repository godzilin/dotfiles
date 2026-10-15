# Dotfiles repo (bare): dots status, dots add -u, dots commit...
function dots --wraps git --description 'git for dotfiles'
    git --git-dir=$HOME/.dotfiles --work-tree=$HOME $argv
end
