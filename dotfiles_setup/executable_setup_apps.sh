#!/bin/bash

sudo true
echo "Installing spotify 🎵 . . ."
sudo snap install spotify --classic
echo "Installing Microsoft Teams 💬 . . ."
sudo snap install teams --classic
echo "Installing vs-code 👨 💻 . . ."
sudo snap install code --classic
echo "Installing whatsdesk 💬 . . ."
sudo snap install whatsdesk --classic
echo "Installing Sublime Merge 🌳 . . ."
sudo snap install sublime-merge --classic
echo "Installing Google Chrome 🌐 . . ."
sudo apt install -y google-chrome-stable

echo "Installing DBeaver 📓 . . ."
REQUIRED_PKG="dbeaver-ce"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
echo "Checking for $REQUIRED_PKG: $PKG_OK"
if [ "" = "$PKG_OK" ]; then
	TEMP_DEB="$(mktemp)" &&
	wget -O "$TEMP_DEB" 'https://dbeaver.io/files/dbeaver-ce_latest_amd64.deb' &&
	sudo dpkg -i "$TEMP_DEB"
	rm -f "$TEMP_DEB"
fi

echo "Installing TickTick: To-do list 📝 . . ."
REQUIRED_PKG="ticktick"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
echo "Checking for $REQUIRED_PKG: $PKG_OK"
if [ "" = "$PKG_OK" ]; then
  TICKTICKVERSION="1.0.40"
	TEMP_DEB="$(mktemp)" &&
	wget -O "$TEMP_DEB" "https://appest-public.s3.amazonaws.com/download/linux/linux_deb_x64/ticktick-${TICKTICKVERSION}-amd64.deb" &&
	sudo dpkg -i "$TEMP_DEB"
	rm -f "$TEMP_DEB"
fi

