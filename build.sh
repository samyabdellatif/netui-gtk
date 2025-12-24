#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Install PyInstaller
echo "Installing PyInstaller..."
pip3 install pyinstaller

# Build the standalone executable
echo "Building netui-gtk..."
pyinstaller --noconfirm --onefile --windowed \
    --name "netui-gtk" \
    --hidden-import="gi" \
    __main__.py

echo "------------------------------------------------"
echo "Build Complete!"
echo "Your standalone executable is located at: dist/netui-gtk"