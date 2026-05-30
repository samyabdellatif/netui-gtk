# netui-gtk

A lightweight, Python-based graphical user interface for managing network interfaces on Linux systems using GTK+ 3.

> **⚠️ Work in Progress**: This project is currently under active development. Features may change or be unstable.

## Features

*   **Interface Management**: View status, MAC, and IP addresses. Toggle interfaces UP/DOWN.
*   **DHCP & Static IP**: Easily switch between DHCP and manual configuration (IP, Subnet, Gateway).
*   **Smart Backend Integration**: 
    - 🔌 Automatically detects and uses NetworkManager (nmcli)
    - 🔧 Integrates with systemd-networkd
    - ⚡ Falls back to direct control (ip commands)
    - **No service conflicts!** Works alongside existing network managers
*   **IPv6 Support**: Configure IPv6 addresses and gateways alongside IPv4.
*   **DNS Configuration**: Set primary and secondary DNS servers.
*   **Advanced Features**:
    - 📊 Real-time network statistics monitoring (RX/TX bytes, packets, errors)
    - 🔧 MTU configuration (jumbo frames, PPPoE optimization)
    - 🎭 MAC address cloning
    - 👁️ Promiscuous mode for packet capture
    - 🚀 Link speed and carrier status display
    - 🔍 Driver information
*   **Auto-Sudo**: Automatically requests privileges when needed.
*   **NetworkManager Integration**: Automatically uses NetworkManager/systemd-networkd when available.
*   **Configuration Persistence**: Saves window size and preferences using XDG standards.
*   **Desktop Integration**: Proper .desktop file for application menus.

---

## Installation

### Quick Install (From Source)

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk

# Install system-wide (recommended)
sudo ./install.sh

# Or install for current user only
./install.sh
```

After installation:
- **GUI**: Launch from your application menu (System → NetUI GTK)
- **CLI**: Run `netui-gtk` from terminal

---

### Run from Source (Development)

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk

# Install dependencies (varies by distro)
# Debian/Ubuntu:
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 iproute2 isc-dhcp-client

# Arch:
sudo pacman -S python-gobject gtk3 iproute2 dhclient

# Fedora:
sudo dnf install python3-gobject gtk3 iproute dhclient

# Run directly
sudo python3 __main__.py

# Or with CLI options
python3 __main__.py --check  # Check dependencies
python3 __main__.py --list   # List interfaces
python3 __main__.py --version
```
---

## Safety Check

Before using netui-gtk, check for conflicts with system services:

```bash
./safety-check.sh
```

This will detect NetworkManager or systemd-networkd conflicts and offer to stop them safely.

---

## Usage

### GUI Mode
Launch from application menu or run `netui-gtk` from terminal.

### CLI Mode

```bash
netui-gtk --check     # Check system dependencies
netui-gtk --list      # List network interfaces
netui-gtk --version   # Show version
```
---

## License

This project is licensed under the MIT License.

## Credits

Created by Samy Abdellatif. Includes code from pynetlinux.