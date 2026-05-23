# NetUI-GTK User Guide

## Table of Contents
1. [Installation](#installation)
2. [Launching the Application](#launching-the-application)
3. [Usage Guide](#usage-guide)
4. [Command-Line Options](#command-line-options)
5. [Troubleshooting](#troubleshooting)

## Installation

### System Requirements
- Linux operating system
- Python 3.x (usually pre-installed)
- GTK+ 3.0
- Root/sudo privileges (for network management)

### Install Dependencies

**Debian/Ubuntu/Mint:**
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 iproute2 isc-dhcp-client
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3-gobject gtk3 iproute dhclient
```

**Arch Linux:**
```bash
sudo pacman -S python-gobject gtk3 iproute2 dhclient
```

### Install NetUI-GTK

```bash
# Clone the repository
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk

# Check system dependencies
python3 check_system.py

# Install system-wide (recommended)
sudo ./install.sh

# OR install for current user only
./install.sh
```

### Verify Installation
```bash
netui-gtk --version
```

## Launching the Application

### From GUI (Application Menu)
1. Open your application menu
2. Look under **System**, **Network**, or **Settings**
3. Click on **NetUI GTK**
4. Enter your password when prompted

### From Terminal
```bash
netui-gtk
```

The application will automatically request root privileges using:
- **pkexec** (graphical prompt) - preferred for GUI
- **sudo** (terminal prompt) - fallback

## Usage Guide

### Main Window

The main window displays all network interfaces with:
- **Interface Details**: Name, MAC address, IP address
- **Status**: Toggle interface UP/DOWN
- **Connection**: Connect/Disconnect (DHCP)
- **Configuration**: Manual network configuration

### Managing Interfaces

#### Bring Interface Up/Down
1. Toggle the **Status** switch
2. Interface will be activated or deactivated

#### Connect via DHCP
1. Ensure interface is UP
2. Toggle the **Connection** switch
3. DHCP client will request an IP address

#### Manual Configuration
1. Click **Manual Config** button
2. Enter network details:
   - IPv4 Address (e.g., 192.168.1.100)
   - Subnet Mask (e.g., 255.255.255.0)
   - Gateway (e.g., 192.168.1.1)
   - DNS Server 1 (e.g., 8.8.8.8)
   - DNS Server 2 (optional)
   - IPv6 Address (optional, e.g., 2001:db8::1/64)
   - IPv6 Gateway (optional)
3. Click **Apply**

### Configuration Persistence

Your preferences are automatically saved in:
```
~/.config/netui-gtk/settings.json
```

Saved settings include:
- Window size and position
- Interface display preferences
- DHCP client preference

## Command-Line Options

### Check System Dependencies
```bash
netui-gtk --check
```
Verifies all required tools and dependencies are installed.

### List Network Interfaces
```bash
netui-gtk --list
```
Displays all network interfaces and their current status.

### Display Version
```bash
netui-gtk --version
```
Shows the application version.

### Run System Check Script
```bash
python3 check_system.py
```
Comprehensive system compatibility check.

## Troubleshooting

### Application Won't Start

**Check dependencies:**
```bash
python3 check_system.py
```

**Verify installation:**
```bash
which netui-gtk
netui-gtk --version
```

### No Privilege Escalation Dialog

**Install PolicyKit:**
```bash
# Debian/Ubuntu
sudo apt install policykit-1

# Fedora
sudo dnf install polkit

# Arch
sudo pacman -S polkit
```

### NetworkManager Conflicts

If you see a warning about NetworkManager:

**Option 1: Stop NetworkManager temporarily**
```bash
sudo systemctl stop NetworkManager
```

**Option 2: Disable NetworkManager for specific interface**
```bash
# Edit /etc/NetworkManager/NetworkManager.conf
[keyfile]
unmanaged-devices=interface-name:eth0
```

**Option 3: Use NetworkManager instead**
Consider using `nmtui` or `nmcli` for interfaces managed by NetworkManager.

### DHCP Not Working

**Check DHCP client:**
```bash
which dhclient dhcpcd udhcpc
```

**Install DHCP client:**
```bash
# Debian/Ubuntu
sudo apt install isc-dhcp-client

# Fedora
sudo dnf install dhclient

# Arch
sudo pacman -S dhclient
```

### Interface Changes Don't Persist After Reboot

NetUI-GTK makes runtime changes only. For persistent configuration:

**Option 1: Use system network configuration files**
- `/etc/network/interfaces` (Debian/Ubuntu)
- `/etc/sysconfig/network-scripts/` (RHEL/Fedora)
- `netctl` profiles (Arch)

**Option 2: Create startup script**
Save your configuration and apply at boot using systemd or init scripts.

### GUI Doesn't Launch (No Window Appears)

**Check for errors:**
```bash
netui-gtk 2>&1 | tee netui-gtk.log
```

**Verify GTK installation:**
```bash
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK OK')"
```

### Can't Manage Certain Interfaces

Some interfaces may be managed by other services:
- **Check NetworkManager:** `systemctl status NetworkManager`
- **Check systemd-networkd:** `systemctl status systemd-networkd`
- **Check network scripts:** `ls /etc/network/interfaces.d/`

### Uninstall NetUI-GTK

```bash
# System-wide uninstallation
sudo ./uninstall.sh

# User-only uninstallation
./uninstall.sh

# Remove configuration (optional)
rm -rf ~/.config/netui-gtk/
```

## Additional Resources

### Log Files
Application logs are printed to console. For debugging:
```bash
netui-gtk 2>&1 | tee debug.log
```

### Get Help
- Check the README.md
- Review IMPROVEMENTS.md for recent changes
- Run `netui-gtk --check` for system diagnostics

### Contributing
Report issues or contribute at:
https://github.com/samyabdellatif/netui-gtk

---

**Note:** NetUI-GTK is designed for manual network configuration. For automatic network management, consider using NetworkManager or systemd-networkd.
