#!/bin/bash

github_username=desenfirman

echo "Downloading OMF"
curl https://raw.githubusercontent.com/oh-my-fish/oh-my-fish/master/bin/install > install_omf && fish install --noninteractive && rm install_omf

echo "Applying fish config using chezmoi"
chezmoi init --apply $github_username

echo "Change sh to fish"
chsh -s $(which fish)

curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
