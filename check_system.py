#!/usr/bin/env python3
"""
System check utility for netui-gtk.
Verifies all dependencies and system configuration.
"""
import sys
import shutil
import subprocess
import os

def check_command(cmd):
    """Check if a command exists."""
    return shutil.which(cmd) is not None

def check_python_module(module):
    """Check if a Python module can be imported."""
    try:
        __import__(module)
        return True
    except ImportError:
        return False

def get_system_info():
    """Get basic system information."""
    try:
        with open('/etc/os-release') as f:
            lines = f.readlines()
            info = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    info[key] = value.strip('"')
            return info.get('PRETTY_NAME', 'Unknown Linux')
    except:
        return 'Unknown Linux'

def check_networkmanager():
    """Check if NetworkManager is running."""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'NetworkManager'],
                              capture_output=True, text=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def check_root():
    """Check if running as root."""
    return os.geteuid() == 0

def main():
    print("=" * 60)
    print("NetUI-GTK System Check")
    print("=" * 60)
    print()
    
    # System info
    print(f"System: {get_system_info()}")
    print(f"Python: {sys.version.split()[0]}")
    print()
    
    # Check privilege
    print("Privileges:")
    if check_root():
        print("  ✓ Running as root")
    else:
        print("  ✗ Not running as root (required for network management)")
    print()
    
    # Check required commands
    print("Required Commands:")
    required_cmds = {
        'ip': 'iproute2',
        'sudo': 'sudo',
    }
    
    all_required_ok = True
    for cmd, pkg in required_cmds.items():
        if check_command(cmd):
            print(f"  ✓ {cmd:<15} (from {pkg})")
        else:
            print(f"  ✗ {cmd:<15} MISSING - install {pkg}")
            all_required_ok = False
    print()
    
    # Check DHCP clients
    print("DHCP Clients (at least one required):")
    dhcp_clients = ['dhclient', 'dhcpcd', 'udhcpc']
    dhcp_found = False
    for client in dhcp_clients:
        if check_command(client):
            print(f"  ✓ {client}")
            dhcp_found = True
        else:
            print(f"  ✗ {client} (optional)")
    
    if not dhcp_found:
        print("\n  WARNING: No DHCP client found!")
        print("  Install: sudo apt install isc-dhcp-client")
    print()
    
    # Check Python modules
    print("Python Modules:")
    modules = {
        'gi': 'python3-gi',
        'gi.repository.Gtk': 'gir1.2-gtk-3.0',
    }
    
    all_modules_ok = True
    for module, pkg in modules.items():
        if check_python_module(module):
            print(f"  ✓ {module:<25} (from {pkg})")
        else:
            print(f"  ✗ {module:<25} MISSING - install {pkg}")
            all_modules_ok = False
    print()
    
    # Check NetworkManager
    print("Network Management:")
    if check_networkmanager():
        print("  ⚠ NetworkManager is running")
        print("    This may conflict with manual network configuration.")
        print("    Consider: sudo systemctl stop NetworkManager")
    else:
        print("  ✓ NetworkManager not running (good for manual configuration)")
    print()
    
    # Check privilege escalation tools
    print("Privilege Escalation:")
    if check_command('pkexec'):
        print("  ✓ pkexec available (PolicyKit)")
    else:
        print("  ✗ pkexec not available")
    
    if check_command('sudo'):
        print("  ✓ sudo available")
    else:
        print("  ✗ sudo not available")
    print()
    
    # Summary
    print("=" * 60)
    if all_required_ok and all_modules_ok:
        print("✓ All required dependencies are installed!")
        if not dhcp_found:
            print("⚠ Consider installing a DHCP client for full functionality")
        print()
        print("You can run netui-gtk with: sudo python3 -m netui-gtk")
    else:
        print("✗ Some required dependencies are missing.")
        print()
        print("To install on Debian/Ubuntu:")
        print("  sudo apt install python3-gi gir1.2-gtk-3.0 iproute2 isc-dhcp-client")
        print()
        print("To install on Fedora/RHEL:")
        print("  sudo dnf install python3-gobject gtk3 iproute dhclient")
        print()
        print("To install on Arch:")
        print("  sudo pacman -S python-gobject gtk3 iproute2 dhclient")
    print("=" * 60)
    
    return 0 if (all_required_ok and all_modules_ok) else 1

if __name__ == '__main__':
    sys.exit(main())
