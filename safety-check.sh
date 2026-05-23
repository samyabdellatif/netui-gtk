#!/bin/bash
# Quick safety check script for netui-gtk
# Run this before launching netui-gtk to avoid conflicts

echo "==================================================="
echo "NetUI-GTK Safety Check"
echo "==================================================="
echo ""

# Function to check if a service is running
check_service() {
    if systemctl is-active --quiet "$1" 2>/dev/null; then
        echo "⚠️  WARNING: $1 is running"
        return 0
    else
        echo "✓ $1 is not running (good)"
        return 1
    fi
}

# Check for conflicting services
echo "Checking for conflicting services..."
echo ""

nm_running=0
networkd_running=0

if check_service "NetworkManager"; then
    nm_running=1
fi

if check_service "systemd-networkd"; then
    networkd_running=1
fi

echo ""

# Provide recommendations
if [ $nm_running -eq 1 ] || [ $networkd_running -eq 1 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  CONFLICT DETECTED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Network services are running that may conflict with"
    echo "manual network configuration."
    echo ""
    echo "Options:"
    echo ""
    
    if [ $nm_running -eq 1 ]; then
        echo "1. Stop NetworkManager temporarily:"
        echo "   sudo systemctl stop NetworkManager"
        echo ""
        echo "2. Disable specific interfaces in NetworkManager:"
        echo "   Edit /etc/NetworkManager/NetworkManager.conf:"
        echo "   [keyfile]"
        echo "   unmanaged-devices=interface-name:eth0"
        echo ""
    fi
    
    if [ $networkd_running -eq 1 ]; then
        echo "3. Stop systemd-networkd temporarily:"
        echo "   sudo systemctl stop systemd-networkd"
        echo ""
    fi
    
    echo "4. Use these tools instead of netui-gtk:"
    if [ $nm_running -eq 1 ]; then
        echo "   - nmtui (NetworkManager TUI)"
        echo "   - nmcli (NetworkManager CLI)"
    fi
    if [ $networkd_running -eq 1 ]; then
        echo "   - networkctl (systemd-networkd)"
    fi
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    read -p "Do you want to stop conflicting services? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ $nm_running -eq 1 ]; then
            echo "Stopping NetworkManager..."
            sudo systemctl stop NetworkManager
        fi
        if [ $networkd_running -eq 1 ]; then
            echo "Stopping systemd-networkd..."
            sudo systemctl stop systemd-networkd
        fi
        echo "✓ Services stopped. You can now use netui-gtk safely."
        echo ""
        echo "To restore services later:"
        if [ $nm_running -eq 1 ]; then
            echo "  sudo systemctl start NetworkManager"
        fi
        if [ $networkd_running -eq 1 ]; then
            echo "  sudo systemctl start systemd-networkd"
        fi
    else
        echo ""
        echo "⚠️  Proceeding with services running may cause conflicts!"
    fi
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✓ NO CONFLICTS DETECTED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "It's safe to use netui-gtk for manual network configuration."
fi

echo ""
echo "==================================================="
