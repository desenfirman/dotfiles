#!/bin/bash

sudo true
sudo apt update
sudo apt install -y \
	gnome-tweaks \
	fonts-powerline \
	neovim \
	ocs-url \
	fish \
	snapd \
	htop \
	mysql-client-core-8.0 \
	libpq-dev \
	python3-dev \
	libmysqlclient-dev \
	wmctrl \
	xdotool \
	jq \
	socat \
  golang \
  neofetch \
  openjdk-11-jre \
  ripgrep \
  silversearcher-ag \
  fzf

  # wmctrl and xdotool needed for setwindow script
  # ripgrep, silversearcher-ag needed for fzf


sudo snap install tela-icons
sudo snap install chezmoi --classic
sudo snap install google-cloud-sdk --classic

echo "Installing astronomer Airlfow astro cli packages..."
curl -sSL install.astronomer.io | sudo bash -s

# Install act for github action stuff
echo "Installing act for github action stuff..."
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Install gitlab runner
echo "Installin gitlab-runner command..."
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt install gitlab-runner -y

