#!/bin/bash
# Uninstallation script for netui-gtk

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}NetUI-GTK Uninstallation Script${NC}"
echo "================================"

# Check if running with sudo
if [ "$EUID" -eq 0 ]; then
    INSTALL_MODE="system"
    DESKTOP_DIR="/usr/share/applications"
    BIN_DIR="/usr/local/bin"
    POLKIT_DIR="/usr/share/polkit-1/actions"
    echo -e "${GREEN}Uninstalling system-wide installation...${NC}"
else
    INSTALL_MODE="user"
    DESKTOP_DIR="$HOME/.local/share/applications"
    BIN_DIR="$HOME/.local/bin"
    POLKIT_DIR=""
    echo -e "${YELLOW}Uninstalling user installation...${NC}"
fi

# Remove desktop file
if [ -f "$DESKTOP_DIR/netui-gtk.desktop" ]; then
    echo "Removing desktop file..."
    rm -f "$DESKTOP_DIR/netui-gtk.desktop"
    echo "  ✓ Removed $DESKTOP_DIR/netui-gtk.desktop"
else
    echo "  ℹ Desktop file not found"
fi

# Remove executable
if [ -f "$BIN_DIR/netui-gtk" ]; then
    echo "Removing executable..."
    rm -f "$BIN_DIR/netui-gtk"
    echo "  ✓ Removed $BIN_DIR/netui-gtk"
else
    echo "  ℹ Executable not found"
fi

# Remove PolicyKit policy (system-wide only)
if [ "$INSTALL_MODE" = "system" ] && [ -n "$POLKIT_DIR" ]; then
    if [ -f "$POLKIT_DIR/com.github.netui-gtk.policy" ]; then
        echo "Removing PolicyKit policy..."
        rm -f "$POLKIT_DIR/com.github.netui-gtk.policy"
        echo "  ✓ Removed PolicyKit policy"
    fi
fi

# Update desktop database
if command -v update-desktop-database > /dev/null; then
    echo "Updating desktop database..."
    if [ "$INSTALL_MODE" = "system" ]; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    else
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
fi

echo ""
echo -e "${GREEN}Uninstallation complete!${NC}"
echo ""

# Ask about configuration removal
echo -e "${YELLOW}Configuration Cleanup${NC}"
echo "User configuration files are at: ~/.config/netui-gtk/"
echo ""

if [ -d "$HOME/.config/netui-gtk" ]; then
    read -p "Do you want to remove configuration files? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing configuration..."
        rm -rf "$HOME/.config/netui-gtk/"
        echo "  ✓ Removed configuration directory"
    else
        echo "  ℹ Configuration files preserved"
    fi
else
    echo "  ℹ No configuration directory found"
fi

# Remove Python cache files from source directory
if [ -d "__pycache__" ]; then
    echo ""
    echo "Cleaning up cache files..."
    rm -rf __pycache__
    rm -rf netmanage/__pycache__
    echo "  ✓ Removed cache files"
fi

# Remove compiled Python files
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -delete 2>/dev/null || true

echo ""
echo -e "${GREEN}All cleanup complete!${NC}"
echo ""
echo "NetUI-GTK has been removed from your system."
echo ""
