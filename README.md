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

### Installing the .deb Package

Build the .deb package first:

```bash
cd netui-gtk
sudo ./build_deb.sh
```

This produces `netui-gtk_1.0.0_all.deb` in the project root.

Then install using your distribution's package manager:

#### Debian / Ubuntu / Linux Mint / Kali
```bash
# Install
sudo apt install ./netui-gtk_1.0.0_all.deb

# Or with dpkg directly
sudo dpkg -i netui-gtk_1.0.0_all.deb
sudo apt install -f  # Fix any missing dependencies
```

#### Fedora / RHEL / CentOS (with alien)
```bash
# Install alien to convert .deb to .rpm
sudo dnf install alien
sudo alien -r netui-gtk_1.0.0_all.deb
sudo rpm -ivh netui-gtk-1.0.0-2.noarch.rpm
```

#### Arch Linux / Manjaro (with debtap)
```bash
# Install debtap
yay -S debtap
# Or: sudo pacman -S debtap (if in community repo)

# Convert and install
sudo debtap -u
debtap netui-gtk_1.0.0_all.deb  # Answer prompts
sudo pacman -U netui-gtk-1.0.0-1-any.pkg.tar.zst
```

#### openSUSE
```bash
# Install dpkg and convert
sudo zypper install dpkg
sudo dpkg -i netui-gtk_1.0.0_all.deb
sudo zypper install -f  # Fix dependencies
```

---

### Uninstalling the .deb Package

#### Debian / Ubuntu / Linux Mint / Kali
```bash
sudo apt remove netui-gtk
# Or purge (removes config files too):
sudo apt purge netui-gtk
```

#### Fedora / RHEL / CentOS (if installed via alien/rpm)
```bash
sudo rpm -e netui-gtk
```

#### Arch Linux / Manjaro (if installed via debtap)
```bash
sudo pacman -R netui-gtk
```

#### openSUSE
```bash
sudo zypper remove netui-gtk
```

#### Cleanup any leftover files
```bash
# Remove configuration (optional)
rm -rf ~/.config/netui-gtk

# Remove desktop file (if leftover)
rm -f ~/.local/share/applications/netui-gtk.desktop
```

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

### Build Wheel Package (pip installable)

```bash
python3 -m build --wheel --outdir dist/
pip install dist/netui_gtk-1.0.0-py3-none-any.whl
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

## Documentation

- **[docs/INSTALL.md](docs/INSTALL.md)** - Complete installation guide with troubleshooting
- **[docs/UNINSTALL.md](docs/UNINSTALL.md)** - Complete uninstallation guide
- **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** - Detailed usage instructions
- **[docs/NETWORK_BACKEND_INTEGRATION.md](docs/NETWORK_BACKEND_INTEGRATION.md)** - NetworkManager/systemd-networkd integration
- **[docs/NEW_FEATURES.md](docs/NEW_FEATURES.md)** - Feature list and capabilities
- **[docs/SAFETY_FIXES.md](docs/SAFETY_FIXES.md)** - Security and safety improvements
- **[docs/IMPROVEMENTS.md](docs/IMPROVEMENTS.md)** - Technical improvements documentation

---

## License

This project is licensed under the MIT License.

## Credits

Created by Samy Abdellatif. Includes code from pynetlinux.