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

For complete feature list, see [NEW_FEATURES.md](NEW_FEATURES.md).

## Requirements

*   Linux with Python 3.x
*   GTK+ 3.0 & PyGObject (`python3-gi`)
*   `iproute2` (provides `ip` command)
*   DHCP client: `dhclient` (isc-dhcp-client), `dhcpcd`, or `udhcpc`

## Installation

### Quick Install (Recommended)

For GUI and CLI usage with desktop integration:

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk

# Install dependencies (Debian/Ubuntu example)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 iproute2 isc-dhcp-client

# Install system-wide (recommended)
sudo ./install.sh

# Or install for current user only
./install.sh
```

After installation:
- **GUI**: Launch from your application menu (System → NetUI GTK)
- **CLI**: Run `netui-gtk` from terminal

For detailed usage instructions, see [USER_GUIDE.md](USER_GUIDE.md).

### Safety Check

Before using netui-gtk, check for conflicts with system services:

```bash
./safety-check.sh
```

This will detect NetworkManager or systemd-networkd conflicts and offer to stop them safely.

### Uninstall

```bash
# Uninstall system-wide installation
sudo ./uninstall.sh

# Or uninstall user installation
./uninstall.sh
```

---

## Usage

### GUI Mode
Launch from application menu or run `netui-gtk` from terminal.

### CLI Mode

Check system dependencies:
```bash
netui-gtk --check
```

List network interfaces:
```bash
netui-gtk --list
```

Show version:
```bash
netui-gtk --version
```

For detailed usage, see [USER_GUIDE.md](USER_GUIDE.md).

---

## Uninstallation

To remove NetUI-GTK from your system:

```bash
# Using quick wizard (recommended)
./quick-install.sh
# Choose option 2) Uninstall

# Or directly
sudo ./uninstall.sh         # For system-wide install
./uninstall.sh              # For user install

# Or using Makefile
sudo make uninstall         # System-wide
make uninstall-user         # User install
```

The uninstall process will:
- Remove all installed files
- Offer to remove configuration files
- Clean up cache files
- Update desktop database

For complete uninstallation guide, see [UNINSTALL.md](UNINSTALL.md).

---

### Alternative: Run from Source (Development)

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk

# Install dependencies (Debian/Ubuntu example)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 iproute2 isc-dhcp-client

# Run directly
sudo python3 __main__.py

# Or with CLI options
python3 __main__.py --check  # Check dependencies
python3 __main__.py --list   # List interfaces
python3 __main__.py --version
```

### Method 2: Build Standalone Binary (Universal)
Create a single executable file that runs on most Linux distributions (Fedora, Arch, etc.) without requiring Python installation.

1.  **Install PyInstaller:**
    ```bash
    pip3 install pyinstaller
    ```

2.  **Build the binary:**
    ```bash
    chmod +x netui-gtk/build.sh
    ./netui-gtk/build.sh
    ```
    The executable will be located in `netui-gtk/dist/netui-gtk`.

### Method 3: Build Debian Package (.deb)
For native installation on Debian, Ubuntu, Linux Mint, and Kali Linux.

1.  **Run the build script:**
    ```bash
    chmod +x netui-gtk/build_deb.sh
    ./netui-gtk/build_deb.sh
    ```

2.  **Install the package:**
    ```bash
    sudo apt install ./netui-gtk/dist/netui-gtk_*.deb
    ```

---

## Documentation

- **[INSTALL.md](INSTALL.md)** - Complete installation guide with troubleshooting
- **[UNINSTALL.md](UNINSTALL.md)** - Complete uninstallation guide
- **[USER_GUIDE.md](USER_GUIDE.md)** - Detailed usage instructions
- **[NETWORK_BACKEND_INTEGRATION.md](NETWORK_BACKEND_INTEGRATION.md)** - NetworkManager/systemd-networkd integration
- **[NEW_FEATURES.md](NEW_FEATURES.md)** - Feature list and capabilities
- **[SAFETY_FIXES.md](SAFETY_FIXES.md)** - Security and safety improvements
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Technical improvements documentation

---

## License

This project is licensed under the MIT License.

## Credits

Created by Samy Abdellatif. Includes code from pynetlinux.