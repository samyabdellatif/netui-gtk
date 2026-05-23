# NetUI-GTK Cleanup & Uninstall Summary

## Quick Reference

| Action | Command | Cleans Config? | Cleans Cache? |
|--------|---------|----------------|---------------|
| Quick uninstall | `./quick-install.sh` → Option 2 | Interactive | Yes |
| System uninstall | `sudo make uninstall` | Interactive | Yes |
| User uninstall | `make uninstall-user` | Interactive | Yes |
| Script (system) | `sudo ./uninstall.sh` | Interactive | Yes |
| Script (user) | `./uninstall.sh` | Interactive | Yes |
| Clean cache only | `make clean` | No | Yes |

---

## What Gets Cleaned Up

### ✅ Always Removed (Automatic)

**Installed Files:**
- `/usr/local/bin/netui-gtk` (system) or `~/.local/bin/netui-gtk` (user)
- Desktop entry: `netui-gtk.desktop`
- PolicyKit policy: `com.github.netui-gtk.policy` (system only)

**Cache Files:**
- `__pycache__/` directories
- `*.pyc` compiled Python files
- `*.pyo` optimized Python files
- Build artifacts from `dist/` and `build/`

**System Database:**
- Desktop database automatically updated
- Menu cache refreshed

### ❓ Interactive Removal (You'll Be Asked)

**Configuration Directory:**
- `~/.config/netui-gtk/settings.json`
  - Window size and position
  - IPv6 display preference
  - Preferred DHCP client
  - Other user preferences

**When to say YES to config removal:**
- ✓ Complete fresh start
- ✓ Troubleshooting configuration issues
- ✓ Not planning to reinstall

**When to say NO (preserve config):**
- ✓ Temporarily uninstalling
- ✓ Planning to upgrade/reinstall
- ✓ Want to keep your preferences

---

## Uninstall Methods Comparison

### Method 1: Quick Install Wizard
```bash
./quick-install.sh
```
**Features:**
- ✓ Auto-detects installation type (system/user)
- ✓ No need to remember if you used sudo
- ✓ Interactive config cleanup
- ✓ Provides reinstall option
- ✓ Clear visual feedback

**Best for:** Users who want simple, guided uninstall

### Method 2: Makefile
```bash
sudo make uninstall      # System-wide
make uninstall-user      # User only
```
**Features:**
- ✓ Fast and direct
- ✓ Integrates with build system
- ✓ Same tool for install/uninstall
- ✓ Can combine with other targets

**Best for:** Developers and power users

### Method 3: Direct Script
```bash
sudo ./uninstall.sh      # System-wide
./uninstall.sh           # User only
```
**Features:**
- ✓ Most explicit control
- ✓ Can be scripted/automated
- ✓ Works without make

**Best for:** Automation and scripting

### Method 4: Manual Removal
```bash
# See UNINSTALL.md for commands
```
**Features:**
- ✓ Works if scripts fail
- ✓ Complete control
- ✓ Educational (learn file locations)

**Best for:** Troubleshooting script failures

---

## Cleanup Scenarios

### Scenario 1: Complete Removal
**Goal:** Remove everything, fresh start

```bash
./quick-install.sh → Option 2 (Uninstall)
# Answer "y" to config removal
rm -rf ~/netui-gtk  # Remove source if downloaded
```

**Result:**
- ✅ All installed files removed
- ✅ Configuration removed
- ✅ Cache cleaned
- ✅ Desktop integration removed

---

### Scenario 2: Reinstall/Upgrade
**Goal:** Fix installation or upgrade version

```bash
./quick-install.sh → Option 1 (Reinstall)
# Answer "n" to config removal (preserve settings)
```

**Result:**
- ✅ All installed files replaced
- ✅ Configuration preserved
- ✅ Cache cleaned
- ✅ Settings maintained

---

### Scenario 3: Switch Install Type
**Goal:** Change from user to system-wide (or vice versa)

```bash
# Uninstall current
./quick-install.sh → Option 2
# Answer "n" to preserve config

# Install new type
./quick-install.sh → Option 1
# Choose different install type
```

**Result:**
- ✅ Old installation removed
- ✅ New installation in different location
- ✅ Configuration preserved
- ✅ Seamless transition

---

### Scenario 4: Clean Development Environment
**Goal:** Clean build artifacts without uninstalling

```bash
make clean
```

**Result:**
- ✅ `__pycache__` removed
- ✅ `*.pyc` files removed
- ✅ Build artifacts removed
- ❌ Installed app still works
- ❌ Configuration untouched

---

## Files and Directories Reference

### System-Wide Installation

**Executable:**
```
/usr/local/bin/netui-gtk
```

**Desktop Integration:**
```
/usr/share/applications/netui-gtk.desktop
/usr/share/polkit-1/actions/com.github.netui-gtk.policy
```

**Configuration (per-user):**
```
~/.config/netui-gtk/settings.json
```

### User Installation

**Executable:**
```
~/.local/bin/netui-gtk
```

**Desktop Integration:**
```
~/.local/share/applications/netui-gtk.desktop
```

**Configuration:**
```
~/.config/netui-gtk/settings.json
```

### Development/Source

**Cache Files:**
```
__pycache__/
netmanage/__pycache__/
*.pyc
*.pyo
```

**Build Artifacts:**
```
build/
dist/
*.egg-info/
```

---

## Post-Uninstall Verification

Run these commands to verify clean removal:

```bash
# 1. Check executable removed
which netui-gtk
# Expected: (nothing) or "not found"

# 2. Check system files
ls /usr/local/bin/netui-gtk 2>/dev/null
ls /usr/share/applications/netui-gtk.desktop 2>/dev/null
# Expected: "No such file or directory"

# 3. Check user files
ls ~/.local/bin/netui-gtk 2>/dev/null
ls ~/.local/share/applications/netui-gtk.desktop 2>/dev/null
# Expected: "No such file or directory"

# 4. Check configuration (if you removed it)
ls ~/.config/netui-gtk/ 2>/dev/null
# Expected: "No such file or directory" (if removed)
#       or: Shows directory (if preserved)

# 5. Check application menu
# Search for "NetUI" in your app launcher
# Expected: Should not appear

# 6. Check cache cleanup
find . -name "__pycache__" -o -name "*.pyc"
# Expected: (nothing) if cleaned
```

---

## Troubleshooting Cleanup Issues

### Issue: Files won't delete

**Cause:** Permission issues

**Solution:**
```bash
# For system files
sudo rm /usr/local/bin/netui-gtk
sudo rm /usr/share/applications/netui-gtk.desktop

# For user files (don't use sudo)
rm ~/.local/bin/netui-gtk
```

---

### Issue: App still appears in menu

**Cause:** Desktop database not updated

**Solution:**
```bash
# Update system database
sudo update-desktop-database /usr/share/applications

# Update user database
update-desktop-database ~/.local/share/applications

# Clear menu cache
rm -rf ~/.cache/menus/
```

---

### Issue: Configuration keeps coming back

**Cause:** App creates new config on launch

**Solution:**
```bash
# 1. Verify app is uninstalled
which netui-gtk  # Should show nothing

# 2. Then remove config
rm -rf ~/.config/netui-gtk/

# 3. If app is still installed, uninstall first
sudo ./uninstall.sh  # or ./uninstall.sh for user install
```

---

### Issue: Cache files remain

**Cause:** Script couldn't find all cache files

**Solution:**
```bash
# Clean from source directory
cd /path/to/netui-gtk
make clean

# Or manually find and remove
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

---

## Cleanup Automation

### Script to verify complete cleanup:

```bash
#!/bin/bash
# verify-cleanup.sh

echo "Verifying NetUI-GTK cleanup..."
echo ""

CLEAN=true

# Check executables
if [ -f "/usr/local/bin/netui-gtk" ]; then
    echo "❌ System executable still exists"
    CLEAN=false
fi

if [ -f "$HOME/.local/bin/netui-gtk" ]; then
    echo "❌ User executable still exists"
    CLEAN=false
fi

# Check desktop files
if [ -f "/usr/share/applications/netui-gtk.desktop" ]; then
    echo "❌ System desktop entry still exists"
    CLEAN=false
fi

if [ -f "$HOME/.local/share/applications/netui-gtk.desktop" ]; then
    echo "❌ User desktop entry still exists"
    CLEAN=false
fi

# Check PolicyKit
if [ -f "/usr/share/polkit-1/actions/com.github.netui-gtk.policy" ]; then
    echo "❌ PolicyKit policy still exists"
    CLEAN=false
fi

# Check cache
if [ -d "__pycache__" ] || [ -d "netmanage/__pycache__" ]; then
    echo "⚠️  Cache files still present (optional)"
fi

if $CLEAN; then
    echo "✅ All installed files removed successfully!"
else
    echo ""
    echo "Some files remain. Run manual cleanup or check permissions."
fi

# Check config (informational)
if [ -d "$HOME/.config/netui-gtk" ]; then
    echo ""
    echo "ℹ️  Configuration preserved at ~/.config/netui-gtk/"
fi
```

---

## Summary

NetUI-GTK provides **comprehensive cleanup** with multiple methods:

1. **Automatic cleanup**: Installed files, cache, desktop integration
2. **Interactive cleanup**: Configuration (preservable)
3. **Multiple methods**: Wizard, Makefile, scripts, manual
4. **Safe defaults**: Asks before removing user data
5. **Complete documentation**: UNINSTALL.md for details

**Recommended approach:**
```bash
./quick-install.sh → Option 2 (Uninstall)
```

This ensures proper cleanup while protecting user preferences.

---

For detailed information, see:
- [UNINSTALL.md](UNINSTALL.md) - Complete uninstall guide
- [INSTALL.md](INSTALL.md) - Installation guide
- [README.md](README.md) - Main documentation
