# NetUI-GTK

A lightweight, Python-based graphical user interface for managing network interfaces on Linux systems using GTK+ 3.

> **✅ Stable**: This project is actively maintained and production-ready.

## Features

### 📋 Interface Management
- View real-time status, MAC addresses, and IP addresses for all interfaces
- Toggle interfaces **UP/DOWN** with a single switch
- **Refresh** interface list without restarting the application

### 🌐 IP Configuration
- **DHCP**: One-click connect/disconnect with automatic backend detection
- **Static IP**: Configure IP address, subnet mask, gateway, and DNS servers
- **Dual-Stack**: Full IPv4 and IPv6 support
- **Smart input validation**: Prevents invalid IP addresses and netmasks before applying

### ⚡ Smart Backend Integration
- 🔌 Automatically detects and uses **NetworkManager** (nmcli)
- 🔧 Integrates with **systemd-networkd**
- 📡 Detects **netctl**, **wpa_supplicant**, **dhcpcd**, **dhclient**, and **Wicd** managers
- 🎯 Shows which network manager controls **each interface** with color-coded badges
- 🖥️ **System network managers panel** - shows all installed/running network tools with descriptions
- ✅ **No service conflicts!** Works alongside existing network managers
- ⚡ Falls back to direct control (`ip` commands)

### 🔧 Advanced Features
- 📊 **Real-time statistics**: RX/TX bytes, packets, errors (auto-refreshing)
- 🔧 **MTU configuration**: Set custom MTU (jumbo frames, PPPoE optimization)
- 🎭 **MAC address cloning**: Change MAC address with validation
- 👁️ **Promiscuous mode**: Enable/disable for packet capture
- 🚀 **Link speed & carrier**: Display link speed, duplex, and cable status
- 🔍 **Driver information**: View kernel driver details

### 🎨 Professional Modern UI
- **Header bar navigation** with app title, subtitle, and refresh controls
- **Live summary stats bar** showing Total/Up/Down/Connected interface counts
- **Smart interface classification** with colored type badges (Ethernet, Wi-Fi, Bridge, Virtual, Loopback)
- **Real-time status indicators** with color-coded dots and backend badges (NetworkManager/systemd-networkd/Manual)
- **Card-based layout** with rich interface detail (MAC, IP, status, backend)
- **Instant search/filter** to quickly find any interface
- **Empty states** for no interfaces and no search results
- **Consistent modern styling** across all windows (main, static config, advanced settings) with a cohesive color palette
- **Resilient CSS loading** - external stylesheet with inline fallback
- **Persistent window size** remembered across sessions (XDG standards)
- **Desktop integration** with proper `.desktop` file
- **Works reliably** across all major Linux distros (GTK+ 3 compatible CSS only)
- **No automatic network operations during initialization** - switches connect signals after state is set
- **No window rebuild warnings** - refresh updates only the inner content, keeping the titlebar intact

### 🛡️ Safety & Reliability
- **Input validation**: All fields validated before changes are applied
- **Graceful error handling**: Clear error dialogs for all failure modes
- **Concurrent operation safety**: No race conditions during async network operations
- **Non-destructive commands**: Routes modified per-interface, not globally
- **Bundled icon**: App loads its own icon directly, avoiding icon-theme crashes

---

## Installation

### Option 1: Quick Install Wizard (Recommended)

The quick install wizard checks dependencies, installs missing packages, and sets up NetUI-GTK automatically.

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk
./quick-install.sh
```

The wizard will:
1. Check for Python 3, GTK+ 3 bindings, iproute2, and a DHCP client
2. Offer to install any missing dependencies automatically
3. Ask whether to install **system-wide** (recommended) or **user-only**
4. Optionally run a safety check for service conflicts

### Option 2: Manual Install (From Source)

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk

# Install system-wide (recommended, requires sudo)
sudo ./install.sh

# Or install for current user only (no sudo needed)
./install.sh
```

### Option 3: Debian/Ubuntu Package (.deb)

```bash
# Build the .deb package
./build_deb.sh

# Install
sudo dpkg -i netui-gtk_1.0.0_all.deb

# If you get dependency errors, run:
sudo apt install -f
```

### Option 4: Arch Linux Package

The source tarball (`netui-gtk-1.0.0.tar.gz`) is included in the repository.

```bash
# Build the package (validates checksums automatically)
makepkg -f

# Install
sudo pacman -U netui-gtk-1.0.0-1-any.pkg.tar.zst
```

### Option 5: Run from Source (Development)

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

# Run directly (requires root for network management)
sudo python3 __main__.py

# Or with CLI options
python3 __main__.py --check  # Check dependencies
python3 __main__.py --list   # List interfaces
python3 __main__.py --version
```

---

## Uninstallation

### From Source Install

```bash
# System-wide (requires sudo)
sudo ./uninstall.sh

# User-only
./uninstall.sh
```

### From Package

```bash
# Debian/Ubuntu
sudo dpkg -r netui-gtk

# Arch
sudo pacman -R netui-gtk
```

---

## After Installation

- **GUI**: Launch from your application menu (System → NetUI GTK)
- **CLI**: Run `netui-gtk` from terminal

The application requires **root privileges** to manage network interfaces. When launched from the menu or terminal, it will automatically request elevated privileges via `pkexec` or `sudo`.

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

The main window displays:
1. **Header bar** with the NetUI title, subtitle, and a refresh button
2. **Summary stats bar** - at-a-glance counts of total, up, down, and connected interfaces
3. **Search bar** - type to instantly filter interfaces by name
4. **Interface cards** with:
   - Interface name and type badge (Ethernet, Wi-Fi, Bridge, etc.)
   - Status indicator (UP/DOWN with color-coded dot)
   - Backend manager badge (NetworkManager, systemd-networkd, Manual)
   - MAC address and IP address details
   - Status switch (toggle interface up/down)
   - Connection switch (connect via DHCP / disconnect)
   - Config button (static IP configuration)
   - Advanced button (statistics, MTU, MAC cloning, promiscuous mode)
5. **Footer** showing the total interface count and requirements

### CLI Mode

```bash
netui-gtk --check     # Check system dependencies
netui-gtk --list      # List network interfaces
netui-gtk --version   # Show version
```

### Keyboard Shortcuts
- **Close window**: `Ctrl+W` or `Alt+F4`

---

## Requirements

### Python
- Python 3.6+
- PyGObject (python3-gi)
- GTK+ 3.0 (gir1.2-gtk-3.0)

### System Tools
- `ip` (from iproute2 package) - **required**
- One of: `dhclient`, `dhcpcd`, or `udhcpc` - **recommended for DHCP**
- `nmcli` (from NetworkManager) - **optional, for NetworkManager integration**
- `networkctl` (from systemd) - **optional, for systemd-networkd integration**
- `resolvectl` (from systemd-resolved) - **optional, for DNS configuration**

---

## Project Structure

```
netui-gtk/
├── __init__.py          # Package initialization
├── __main__.py          # Application entry point
├── netui.py             # Main window and UI logic
├── config.py            # Configuration management (XDG)
├── manual_config.py     # Static IP configuration window
├── advanced_config.py   # Advanced settings window
├── check_system.py      # System dependency checker
├── styles/
│   └── style.css        # CSS stylesheet for modern UI
├── netmanage/
│   ├── __init__.py      # Backend package
│   ├── ifconfig.py      # Low-level interface control (ioctl)
│   ├── route.py         # Routing table reader
│   ├── dhcpc.py         # DHCP client interface
│   ├── advanced.py      # Advanced features (MTU, stats, MAC)
│   ├── async_worker.py  # Background thread for async operations
│   └── network_service.py  # NetworkManager/systemd-networkd integration
├── install.sh           # Installation script
├── uninstall.sh         # Uninstallation script
├── quick-install.sh     # Quick install wizard
├── safety-check.sh      # Service conflict checker
├── build.sh             # Build script
├── build_deb.sh         # Debian/Ubuntu package build script
├── PKGBUILD             # Arch Linux package build script
├── netui-gtk.install    # Arch Linux install hooks
├── netui-gtk.spec       # PyInstaller spec file
├── setup.py             # Python package setup
├── Makefile             # Build automation
└── README.md            # This file
```

---

## Architecture

### Thread Safety
Network operations that could block the GUI (DHCP lease, disconnect) run in **background threads** via `AsyncWorker`. Results are dispatched back to the main GTK thread using `GLib.idle_add()`.

### Backend Detection
The `NetworkService` class automatically detects which network manager controls each interface:
1. **NetworkManager** - checks via `nmcli device status`
2. **systemd-networkd** - checks via `networkctl status` and `/etc/systemd/network/*.network` files
3. **netctl** - checks via `netctl list` and `netctl is-active`
4. **wpa_supplicant** - checks running processes bound to the interface
5. **dhcpcd** - checks via `dhcpcd --dumplease`
6. **dhclient** - checks lease files for active bindings
7. **Wicd** - checks via `wicd-cli`
8. **Manual** - falls back to direct `ip` commands and DHCP clients

The UI displays a **system network managers panel** showing all installed/running tools, and each interface card shows a color-coded badge indicating which manager controls it.

### Input Validation
All user inputs are validated before execution:
- IPv4/IPv6 addresses validated using the `ipaddress` module
- Netmasks validated for correctness
- MAC addresses validated with regex
- Gateway and DNS fields checked for valid format

### Icon Handling
The application loads its bundled `netui.ico` directly via `GdkPixbuf` and sets it as the default window icon. This bypasses icon-theme lookup, which can crash on systems where the fallback `image-missing` icon fails to load (e.g., broken SVG loaders).

---

## License

This project is licensed under the MIT License.

## Credits

Created by **Samy Abdellatif**. Includes code from [pynetlinux](https://github.com/rlisagor/pynetlinux) (MIT License) by Roman Lisagor, Robert Grant, and williamjoy.