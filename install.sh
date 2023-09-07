#!/bin/bash

github_username=desenfirman

echo "Applying fish config using chezmoi"
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --one-shot $github_username

echo "Downloading OMF"
curl https://raw.githubusercontent.com/oh-my-fish/oh-my-fish/master/bin/install > install && fish install --noninteractive && rm install

echo "Install some vim stuff"
curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# echo "Change sh to fish"
# chsh -s $(which fish)
