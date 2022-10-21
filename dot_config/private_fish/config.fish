if status is-interactive
    # Commands to run in interactive sessions can go here
end

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
eval $HOME/miniconda3/bin/conda "shell.fish" "hook" $argv | source
# <<< conda initialize <<<

fish_vi_key_bindings
source $HOME/.env

[ ! -f $HOME/.env ] && cp $HOME/.env.example $HOME/.env

