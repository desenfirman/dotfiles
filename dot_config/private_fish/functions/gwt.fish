function gwt --description 'git worktree add + symlink .venv/.env from main repo'
    set -l main_root (git rev-parse --show-toplevel)
    set -l path $argv[1]
    set -l branch $argv[2]

    git worktree add $path $branch

    if test -e "$main_root/.venv"
        ln -sfn "$main_root/.venv" "$path/.venv"
    end
    if test -e "$main_root/.env"
        ln -sfn "$main_root/.env" "$path/.env"
    end
end
