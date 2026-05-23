#!/bin/bash
# Installation script for netui-gtk
# Installs .desktop file and creates necessary directories
# Supports both system-wide and user-only installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}   ${GREEN}NetUI-GTK Installation Script${NC}          ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}   Network Interface Manager                ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running with sudo (needed for system-wide installation)
if [ "$EUID" -eq 0 ]; then
    INSTALL_MODE="system"
    DESKTOP_DIR="/usr/share/applications"
    BIN_DIR="/usr/local/bin"
    POLKIT_DIR="/usr/share/polkit-1/actions"
    echo -e "${GREEN}Installing system-wide...${NC}"
else
    INSTALL_MODE="user"
    DESKTOP_DIR="$HOME/.local/share/applications"
    BIN_DIR="$HOME/.local/bin"
    POLKIT_DIR=""
    echo -e "${YELLOW}Installing for current user only...${NC}"
    echo -e "${YELLOW}(Run with sudo for system-wide installation)${NC}"
fi

# Create directories if they don't exist
mkdir -p "$DESKTOP_DIR"
mkdir -p "$BIN_DIR"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install .desktop file
echo "Installing desktop file..."
cp "$SCRIPT_DIR/netui-gtk.desktop" "$DESKTOP_DIR/"
chmod 644 "$DESKTOP_DIR/netui-gtk.desktop"

# Create wrapper script in bin directory
echo "Creating executable wrapper..."
cat > "$BIN_DIR/netui-gtk" << 'EOF'
#!/bin/bash
# NetUI-GTK launcher script

# Get the actual script location
SCRIPT_LOCATION="INSTALL_PATH_PLACEHOLDER"

# Check for root privileges and re-run with pkexec if needed
if [ $EUID -ne 0 ]; then
    if command -v pkexec > /dev/null; then
        exec pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY HOME=$HOME "$0" "$@"
    elif command -v sudo > /dev/null; then
        exec sudo -E "$0" "$@"
    else
        # For GUI, show error dialog if zenity is available
        if command -v zenity > /dev/null && [ -n "$DISPLAY" ]; then
            zenity --error --text="This application requires root privileges.\nPlease install 'policykit-1' or 'sudo'."
        else
            echo "Error: This application requires root privileges."
            echo "Please install 'policykit-1' or 'sudo'."
        fi
        exit 1
    fi
fi

# Run the actual application
cd "$SCRIPT_LOCATION"
exec python3 "$SCRIPT_LOCATION/__main__.py" "$@"
EOF

# Replace placeholder with actual path
sed -i "s|INSTALL_PATH_PLACEHOLDER|$SCRIPT_DIR|g" "$BIN_DIR/netui-gtk"
chmod +x "$BIN_DIR/netui-gtk"

# Update desktop database
if command -v update-desktop-database > /dev/null; then
    echo "Updating desktop database..."
    if [ "$INSTALL_MODE" = "system" ]; then
        update-desktop-database "$DESKTOP_DIR"
    else
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
fi

# Install PolicyKit policy for system-wide installation
if [ "$INSTALL_MODE" = "system" ] && [ -n "$POLKIT_DIR" ]; then
    echo "Installing PolicyKit policy..."
    mkdir -p "$POLKIT_DIR"
    cp "$SCRIPT_DIR/com.github.netui-gtk.policy" "$POLKIT_DIR/"
    chmod 644 "$POLKIT_DIR/com.github.netui-gtk.policy"
    echo "PolicyKit policy installed for GUI privilege escalation"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${GREEN}✓ Installation Complete!${NC}                   ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Installed files:${NC}"
echo "  • Desktop file: $DESKTOP_DIR/netui-gtk.desktop"
echo "  • Executable:   $BIN_DIR/netui-gtk"
if [ "$INSTALL_MODE" = "system" ] && [ -n "$POLKIT_DIR" ]; then
    echo "  • PolicyKit:    $POLKIT_DIR/com.github.netui-gtk.policy"
fi
echo ""
echo -e "${GREEN}How to use:${NC}"
echo "  • Terminal:  netui-gtk [--check|--list|--version]"
echo "  • GUI Menu:  System → NetUI GTK"
echo ""

if [ "$INSTALL_MODE" = "user" ]; then
    echo -e "${YELLOW}⚠ PATH Setup Required${NC}"
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo ""
        echo "Add to your ~/.bashrc or ~/.zshrc:"
        echo -e "${BLUE}  export PATH=\"\$PATH:$BIN_DIR\"${NC}"
        echo ""
        echo "Then run: source ~/.bashrc"
        echo ""
    else
        echo -e "${GREEN}✓ $BIN_DIR is already in your PATH${NC}"
        echo ""
    fi
fi

echo -e "${GREEN}Next steps:${NC}"
echo "  1. Run safety check:  ./safety-check.sh"
echo "  2. Test installation: netui-gtk --check"
echo "  3. Launch app:        netui-gtk"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}Enjoy NetUI-GTK!${NC} 🚀"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
