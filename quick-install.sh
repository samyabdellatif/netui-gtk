#!/bin/bash
# Quick installation script for NetUI-GTK
# Checks dependencies and installs automatically

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                                                       ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}       ${GREEN}NetUI-GTK Quick Install Wizard${NC}              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}       Network Interface Manager                   ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                                                       ${BLUE}║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if already installed
ALREADY_INSTALLED=false
if [ -f "/usr/local/bin/netui-gtk" ] || [ -f "$HOME/.local/bin/netui-gtk" ]; then
    ALREADY_INSTALLED=true
    echo -e "${YELLOW}⚠  NetUI-GTK appears to be already installed${NC}"
    echo ""
    echo "What would you like to do?"
    echo "  1) Reinstall"
    echo "  2) Uninstall"
    echo "  3) Cancel"
    echo ""
    read -p "Enter choice [1-3]: " CHOICE
    
    case $CHOICE in
        2)
            echo ""
            echo -e "${GREEN}Launching uninstaller...${NC}"
            echo ""
            
            # Detect if system or user install
            if [ -f "/usr/local/bin/netui-gtk" ]; then
                echo "Detected system-wide installation"
                sudo ./uninstall.sh
            else
                echo "Detected user installation"
                ./uninstall.sh
            fi
            exit 0
            ;;
        3)
            echo "Installation cancelled."
            exit 0
            ;;
        1)
            echo ""
            echo -e "${GREEN}Proceeding with reinstallation...${NC}"
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
fi

echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to ask yes/no question
ask_yes_no() {
    while true; do
        read -p "$1 [y/N] " -n 1 -r
        echo
        case $REPLY in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            "" ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

echo -e "${GREEN}Step 1:${NC} Checking system requirements..."
echo ""

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "  ✓ Python 3 found: ${GREEN}$PYTHON_VERSION${NC}"
else
    echo -e "  ${RED}✗ Python 3 not found${NC}"
    echo "  Please install Python 3 first"
    exit 1
fi

# Check GTK
if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" 2>/dev/null; then
    echo -e "  ✓ GTK+ 3 bindings: ${GREEN}Installed${NC}"
else
    echo -e "  ${RED}✗ GTK+ 3 bindings not found${NC}"
    echo ""
    echo "  Install with:"
    
    # Detect package manager
    if command_exists apt; then
        echo "    sudo apt install python3-gi gir1.2-gtk-3.0"
    elif command_exists dnf; then
        echo "    sudo dnf install python3-gobject gtk3"
    elif command_exists pacman; then
        echo "    sudo pacman -S python-gobject gtk3"
    else
        echo "    Please install python3-gobject and gtk3 for your distribution"
    fi
    
    if ask_yes_no "  Try to install automatically?"; then
        if command_exists apt; then
            sudo apt update && sudo apt install -y python3-gi gir1.2-gtk-3.0
        elif command_exists dnf; then
            sudo dnf install -y python3-gobject gtk3
        elif command_exists pacman; then
            sudo pacman -S --noconfirm python-gobject gtk3
        fi
    else
        exit 1
    fi
fi

# Check iproute2
if command_exists ip; then
    echo -e "  ✓ iproute2 (ip): ${GREEN}Installed${NC}"
else
    echo -e "  ${YELLOW}⚠ iproute2 not found${NC}"
    echo "  Installing iproute2..."
    
    if command_exists apt; then
        sudo apt install -y iproute2
    elif command_exists dnf; then
        sudo dnf install -y iproute
    elif command_exists pacman; then
        sudo pacman -S --noconfirm iproute2
    fi
fi

# Check DHCP client
DHCP_CLIENT=""
if command_exists dhclient; then
    DHCP_CLIENT="dhclient"
elif command_exists dhcpcd; then
    DHCP_CLIENT="dhcpcd"
elif command_exists udhcpc; then
    DHCP_CLIENT="udhcpc"
fi

if [ -n "$DHCP_CLIENT" ]; then
    echo -e "  ✓ DHCP client: ${GREEN}$DHCP_CLIENT${NC}"
else
    echo -e "  ${YELLOW}⚠ No DHCP client found${NC}"
    echo "  DHCP functionality will be limited"
    
    if ask_yes_no "  Install DHCP client (dhclient)?"; then
        if command_exists apt; then
            sudo apt install -y isc-dhcp-client
        elif command_exists dnf; then
            sudo dnf install -y dhclient
        elif command_exists pacman; then
            sudo pacman -S --noconfirm dhclient
        fi
    fi
fi

echo ""
echo -e "${GREEN}Step 2:${NC} Running system check..."
echo ""

python3 check_system.py || true

echo ""
echo -e "${GREEN}Step 3:${NC} Installation type"
echo ""
echo "Choose installation type:"
echo "  1) System-wide (recommended) - requires sudo"
echo "  2) User-only - no sudo needed"
echo ""

read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Installing system-wide...${NC}"
        sudo ./install.sh
        ;;
    2)
        echo ""
        echo -e "${GREEN}Installing for current user...${NC}"
        ./install.sh
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Step 4:${NC} Safety check"
echo ""

if ask_yes_no "Run safety check for service conflicts?"; then
    ./safety-check.sh
fi

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                                                       ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}       ${GREEN}✓ Installation Complete!${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                                                       ${BLUE}║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Quick start guide:${NC}"
echo ""
echo "  1. Launch from terminal:"
echo -e "     ${BLUE}netui-gtk${NC}"
echo ""
echo "  2. Or find it in your application menu:"
echo -e "     ${BLUE}System → NetUI GTK${NC}"
echo ""
echo "  3. Use CLI features:"
echo -e "     ${BLUE}netui-gtk --check${NC}   (system check)"
echo -e "     ${BLUE}netui-gtk --list${NC}    (list interfaces)"
echo -e "     ${BLUE}netui-gtk --version${NC} (show version)"
echo ""
echo -e "${YELLOW}Important notes:${NC}"
echo "  • Application requires root privileges"
echo "  • Stop NetworkManager if using manual configuration"
echo "  • See USER_GUIDE.md for detailed usage"
echo ""
echo -e "${GREEN}Documentation:${NC}"
echo "  • User Guide:      USER_GUIDE.md"
echo "  • New Features:    NEW_FEATURES.md"
echo "  • Safety Info:     SAFETY_FIXES.md"
echo "  • Improvements:    IMPROVEMENTS.md"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
