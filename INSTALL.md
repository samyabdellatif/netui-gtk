# NetUI-GTK Installation Guide

## Quick Installation (Recommended)

The fastest way to install NetUI-GTK with automatic dependency checking:

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk
chmod +x quick-install.sh
./quick-install.sh
```

This interactive wizard will:
- ✓ Check all dependencies
- ✓ Install missing packages (with your permission)
- ✓ Run system compatibility check
- ✓ Guide you through installation
- ✓ Run safety checks
- ✓ Verify installation

---

## Manual Installation

### Prerequisites

**Required:**
- Python 3.6+
- GTK+ 3.0 with Python bindings
- iproute2 (provides `ip` command)
- Root/sudo access (for network management)

**Optional:**
- DHCP client: `dhclient`, `dhcpcd`, or `udhcpc`
- PolicyKit (for graphical privilege elevation)

### Step 1: Install Dependencies

**Debian/Ubuntu/Mint:**
```bash
sudo apt update
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

**openSUSE:**
```bash
sudo zypper install python3-gobject-Gdk gtk3 iproute2 dhclient
```

### Step 2: Clone Repository

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk
```

### Step 3: Verify Dependencies

```bash
python3 check_system.py
```

### Step 4: Install

**Option A: Using Makefile (Recommended)**
```bash
# Check system
make check

# Install system-wide
sudo make install

# OR install for current user
make install-user
```

**Option B: Using install script**
```bash
# System-wide installation
sudo ./install.sh

# OR user-only installation
./install.sh
```

**Option C: Using setup.py**
```bash
sudo python3 setup.py install
```

---

## Installation Methods Comparison

| Method | Command | Scope | Requires Sudo | PolicyKit |
|--------|---------|-------|---------------|-----------|
| Quick Install | `./quick-install.sh` | Both | Yes* | Yes |
| Makefile (system) | `sudo make install` | System | Yes | Yes |
| Makefile (user) | `make install-user` | User | No | No |
| Install Script (system) | `sudo ./install.sh` | System | Yes | Yes |
| Install Script (user) | `./install.sh` | User | No | No |
| Setup.py | `sudo python3 setup.py install` | System | Yes | No |

*Only for installing missing dependencies

---

## Post-Installation

### Verify Installation

```bash
# Check if installed
which netui-gtk

# Test version
netui-gtk --version

# Run system check
netui-gtk --check

# List interfaces (may need sudo)
sudo netui-gtk --list
```

### Add to PATH (User Installation Only)

If you installed for current user only, add to your shell config:

**Bash (~/.bashrc):**
```bash
export PATH="$PATH:$HOME/.local/bin"
```

**Zsh (~/.zshrc):**
```bash
export PATH="$PATH:$HOME/.local/bin"
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

---

## Running the Application

### From GUI
1. Open your application menu
2. Navigate to: **System** → **NetUI GTK**
3. Enter password when prompted

### From Terminal
```bash
# Main GUI
netui-gtk

# Check dependencies
netui-gtk --check

# List network interfaces
netui-gtk --list

# Show version
netui-gtk --version
```

### From Source (Development)
```bash
cd netui-gtk
sudo python3 __main__.py

# Or using Makefile
make run
```

---

## Installed Files

### System-Wide Installation
```
/usr/local/bin/netui-gtk              - Executable wrapper
/usr/share/applications/               - Desktop entry
  └─ netui-gtk.desktop
/usr/share/polkit-1/actions/           - PolicyKit rules
  └─ com.github.netui-gtk.policy
```

### User Installation
```
~/.local/bin/netui-gtk                 - Executable wrapper
~/.local/share/applications/           - Desktop entry
  └─ netui-gtk.desktop
~/.config/netui-gtk/                   - Configuration
  └─ settings.json
```

---

## Troubleshooting Installation

### Issue: "python3-gi not found"

**Solution:**
```bash
# Debian/Ubuntu
sudo apt install python3-gi gir1.2-gtk-3.0

# Fedora
sudo dnf install python3-gobject gtk3

# Arch
sudo pacman -S python-gobject gtk3
```

### Issue: "netui-gtk: command not found"

**Solution 1:** Add to PATH (user install)
```bash
export PATH="$PATH:$HOME/.local/bin"
```

**Solution 2:** Use full path
```bash
~/.local/bin/netui-gtk
```

**Solution 3:** Reinstall system-wide
```bash
sudo ./install.sh
```

### Issue: "Permission denied"

**Solution:** Application needs root privileges
```bash
sudo netui-gtk
# Or just run normally, it will request privileges
```

### Issue: GUI doesn't launch

**Check:**
```bash
# Test GTK
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK OK')"

# Check errors
netui-gtk 2>&1 | tee error.log
```

### Issue: "NetworkManager conflicts"

**Solution:** See [safety-check.sh](safety-check.sh)
```bash
./safety-check.sh
```

---

## Uninstallation

### Quick Uninstall (Recommended)

The quick-install wizard now includes uninstall option:

```bash
./quick-install.sh
# Choose option 2) Uninstall
```

This will:
- ✓ Detect installation type (system/user)
- ✓ Remove all installed files
- ✓ Offer to remove configuration files
- ✓ Clean up cache files
- ✓ Update desktop database

### Using Makefile
```bash
# System-wide uninstall
sudo make uninstall

# User installation uninstall
make uninstall-user
```

### Using uninstall script
```bash
# System-wide
sudo ./uninstall.sh

# User installation
./uninstall.sh
```

The uninstall script will:
1. Remove executable from `/usr/local/bin` or `~/.local/bin`
2. Remove desktop entry file
3. Remove PolicyKit policy (system install only)
4. Ask if you want to remove configuration files
5. Clean up Python cache files
6. Update desktop database

### What Gets Removed

**Always removed:**
- Executable: `netui-gtk`
- Desktop entry: `netui-gtk.desktop`
- PolicyKit policy: `com.github.netui-gtk.policy` (system only)
- Python cache files: `__pycache__` directories

**Optional removal (you'll be asked):**
- User configuration: `~/.config/netui-gtk/`
  - Contains: `settings.json` (window size, preferences)

### Manual Uninstallation

**System-wide:**
```bash
sudo rm /usr/local/bin/netui-gtk
sudo rm /usr/share/applications/netui-gtk.desktop
sudo rm /usr/share/polkit-1/actions/com.github.netui-gtk.policy
rm -rf ~/.config/netui-gtk/  # Optional: config
```

**User installation:**
```bash
rm ~/.local/bin/netui-gtk
rm ~/.local/share/applications/netui-gtk.desktop
rm -rf ~/.config/netui-gtk/  # Optional: config
```

**Clean up cache:**
```bash
cd netui-gtk
make clean
# Or manually:
find . -type d -name "__pycache__" -delete
find . -type f -name "*.pyc" -delete
```

---

## Advanced Options

### Custom Installation Directory

Edit `install.sh` and change:
```bash
BIN_DIR="/custom/path/bin"
DESKTOP_DIR="/custom/path/share/applications"
```

### Skip PolicyKit Installation

Edit `install.sh` and comment out:
```bash
# POLKIT_DIR=""
```

### Build Debian Package

```bash
chmod +x build_deb.sh
./build_deb.sh
sudo apt install ./dist/netui-gtk_*.deb
```

### Build Standalone Binary

```bash
pip3 install pyinstaller
chmod +x build.sh
./build.sh
# Binary in: dist/netui-gtk
```

---

## Platform-Specific Notes

### Debian/Ubuntu
- Includes `isc-dhcp-client` (dhclient) by default
- NetworkManager usually active - may need to stop

### Fedora
- Use `dnf` instead of `apt`
- Includes NetworkManager by default

### Arch Linux
- Minimal by default - install all dependencies
- May need to start PolicyKit service: `systemctl start polkit`

### openSUSE
- Use `zypper` package manager
- NetworkManager usually active

---

## Getting Help

**Documentation:**
- [README.md](README.md) - Main documentation
- [USER_GUIDE.md](USER_GUIDE.md) - Usage guide
- [NEW_FEATURES.md](NEW_FEATURES.md) - Feature list
- [SAFETY_FIXES.md](SAFETY_FIXES.md) - Safety information
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Technical details

**Commands:**
```bash
make help              # Show Makefile options
netui-gtk --check      # System check
python3 check_system.py # Detailed dependency check
./safety-check.sh      # Service conflict check
```

**Support:**
- GitHub Issues: https://github.com/samyabdellatif/netui-gtk/issues
- Check logs: Run with `netui-gtk 2>&1 | tee debug.log`

---

**Installation complete! Enjoy NetUI-GTK!** 🚀
