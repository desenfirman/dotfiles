if status is-interactive
end

# Set base venv
set -l USERNAME (whoami)
set -l VENV_PATH /opt/$USERNAME/python-base-env

# Activate venv
if test -f "$VENV_PATH/bin/activate.fish"
    source "$VENV_PATH/bin/activate.fish"
end

fish_vi_key_bindings

if test -f $HOME/.env
    source $HOME/.env
else if test -f $HOME/.env.example
    cp $HOME/.env.example $HOME/.env
    source $HOME/.env
end


# opencode
fish_add_path /home/mis-stf08-dese/.opencode/bin
# Added by dbt Fusion extension (ensure dbt binary dir on PATH)
if not contains "/home/mis-stf08-dese/.local/bin" $PATH
  set -gx PATH "/home/mis-stf08-dese/.local/bin" $PATH
end
# Added by dbt Fusion extension
alias dbtf "/home/mis-stf08-dese/.local/bin/dbt"
