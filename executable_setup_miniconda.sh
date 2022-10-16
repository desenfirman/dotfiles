#!/bin/bash
echo "Checking miniconda in $HOME/miniconda"
if [[ !  -d ~/miniconda3 ]]; then
	echo "Miniconda didnt exists. Installing latest miniconda from repo.anaconda.com"
	mkdir -p ~/miniconda3
	wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
	bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
	rm -rf ~/miniconda3/miniconda.sh
else
	echo "Miniconda already exists in local. Checking mininconda python version"
	~/miniconda3/bin/python --version
fi

if [[ -f ~/miniconda3/bin/pip ]]; then
	echo "Installing requirements from file ~/pip_requirements.txt"
	~/miniconda3/bin/pip install -r pip_requirements.txt
else
	echo "Couldn't install some pip requirements from file ~/pip_requirements.txt due missing pip binary file"
	echo "Please make sure miniconda is properly installed"
fi


