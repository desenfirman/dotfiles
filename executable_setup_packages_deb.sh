#!/bin/bash

sudo true
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
  golang
  # wmctrl and xdotool needed for setwindow script


sudo snap install tela-icons
sudo snap install chezmoi --classic

# Install astronomer Airflow astro cli packages
curl -sSL install.astronomer.io | sudo bash -s

