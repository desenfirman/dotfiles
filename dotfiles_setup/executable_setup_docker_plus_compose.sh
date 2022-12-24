#!/bin/sh

sudo true

set -o errexit
set -o nounset

IFS=$(printf '\n\t')

# Docker
printf "Installing Docker Engine"
sudo apt remove --yes docker docker-engine docker.io containerd runc || true
sudo apt update
sudo apt --yes --no-install-recommends install apt-transport-https ca-certificates
wget --quiet --output-document=- https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository --yes "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu $(lsb_release --codename --short) stable"
sudo apt update
sudo apt --yes --no-install-recommends install docker-ce docker-ce-cli containerd.io
sudo usermod --append --groups docker "$USER"
sudo systemctl enable docker
printf '\nDocker installed successfully\n\n'

printf 'Waiting for Docker to start...\n\n'
sleep 5


# Docker Compose

compose_release() {
	curl --silent "https://api.github.com/repos/docker/compose/releases/latest" |
	grep -Po '"tag_name": "\K.*?(?=")'
}

if [ ! -f /usr/local/bin/docker-compose ]; then
	echo "Docker compose not found in system path. Installing docker-compose binary"
	sudo curl -L https://github.com/docker/compose/releases/download/$(compose_release)/docker-compose-$(uname -s)-$(uname -m) \
		-o /usr/local/bin/docker-compose \
		&& sudo chmod +x /usr/local/bin/docker-compose
	echo "Docker compose succesfully installed"
else
	echo "Seems like you already has a docker-compose in your system path"
fi

echo "Checking docker-compose version"
echo "$(docker-compose --version) installed"
