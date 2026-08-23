#!/bin/bash

# ========== Config ==========
MINICONDA_VERSION="py39_4.9.2"  # <- This is version 3.9.20 equivalent (Python 3.9 + Miniconda 4.9.2)
USERNAME=$(whoami)
INSTALL_DIR="/opt/$USERNAME/miniconda3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_URL="https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh"
INSTALLER_PATH="/tmp/miniconda_installer.sh"

# ========== Provision ==========
echo "Checking Miniconda installation in $INSTALL_DIR"

if [[ ! -d "$INSTALL_DIR" ]]; then
    echo "Miniconda not found. Installing version $MINICONDA_VERSION..."

    # Create base dir if needed, with proper permissions
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown -R "$USERNAME:$USERNAME" "$(dirname "$INSTALL_DIR")"

    # Download and install
    wget "$INSTALLER_URL" -O "$INSTALLER_PATH"
    bash "$INSTALLER_PATH" -b -u -p "$INSTALL_DIR"
    rm -f "$INSTALLER_PATH"

    echo "Miniconda $MINICONDA_VERSION installed to $INSTALL_DIR"
else
    echo "Miniconda already exists at $INSTALL_DIR"
    "$INSTALL_DIR/bin/python" --version
fi

# ========== PATH Management ==========
if ! grep -q "$INSTALL_DIR/bin" <<< "$PATH"; then
    echo "Adding Miniconda to PATH in ~/.bashrc"
    echo "export PATH=\"$INSTALL_DIR/bin:\$PATH\"" >> ~/.bashrc
    source ~/.bashrc
fi

# ========== Pip Requirements ==========
if [[ -f "$INSTALL_DIR/bin/pip" ]]; then
    echo "Installing requirements from $SCRIPT_DIR/pip_requirements.txt"
    "$INSTALL_DIR/bin/pip" install -r "$SCRIPT_DIR/pip_requirements.txt"
else
    echo "Missing pip binary. Please check Miniconda installation."
fi

