#!/usr/bin/env bash

set -euo pipefail

# Variables
APP_NAME="netscout"
VERSION="0.1.0"
USERNAME="${SUDO_USER:-${USER}}"
BUILD_DIRS=("dist" "build" "package")
INSTALLER="${APP_NAME}.deb"

# Function to print status messages
function info() {
    echo -e "\e[1;34m[INFO]\e[0m $1"
}

# Purge existing installation if present
info "Purging existing installation of ${APP_NAME} (if installed)..."
if dpkg -l | grep -q "^ii  ${APP_NAME} "; then
    sudo apt purge --autoremove -y "${APP_NAME}"
else
    info "No existing installation found."
fi

# Clean old build artifacts
for dir in "${BUILD_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        info "Removing existing directory: $dir"
        rm -rf "$dir"
    fi
done

if [[ -f "$INSTALLER" ]]; then
    info "Removing existing installer: $INSTALLER"
    rm -f "$INSTALLER"
fi

# Create executable
info "Creating standalone executable using PyInstaller..."
pyinstaller --onefile --name=$APP_NAME $APP_NAME.py

# Setup package structure
info "Creating package directory hierarchy..."
mkdir -p "package/usr/bin"

# Move executable
info "Copying executable to package directory..."
cp "dist/${APP_NAME}" "package/usr/bin/"

# Set permissions and ownership
info "Setting permissions and ownership for package directory..."
chmod 755 -R "package/"
chown "${USERNAME}:${USERNAME}" -R "package/"

# Build Debian installer with FPM
info "Creating Debian installer with FPM..."
fpm -C "package" -s dir -t deb -n "${APP_NAME}" -v "${VERSION}" -p "${INSTALLER}" --after-install "post_install_script.sh"

# Install generated package
info "Installing the new ${APP_NAME} package..."
sudo dpkg -i "${INSTALLER}"

info "Installation complete."