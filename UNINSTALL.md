# NetUI-GTK Uninstallation Guide

Complete guide for removing NetUI-GTK from your system.

---

## Quick Uninstall

### Method 1: Using Quick Install Wizard (Easiest)

```bash
cd netui-gtk
./quick-install.sh
```

When prompted, choose:
- **Option 2) Uninstall**

The wizard will:
1. Automatically detect your installation type (system/user)
2. Remove all installed files
3. Ask if you want to remove configuration
4. Clean up cache files
5. Confirm successful removal

### Method 2: Using Makefile

**For system-wide installation:**
```bash
sudo make uninstall
```

**For user installation:**
```bash
make uninstall-user
```

### Method 3: Direct Script

**For system-wide installation:**
```bash
sudo ./uninstall.sh
```

**For user installation:**
```bash
./uninstall.sh
```

---

## What Gets Removed

### Automatically Removed

✓ **Executable file**
- System: `/usr/local/bin/netui-gtk`
- User: `~/.local/bin/netui-gtk`

✓ **Desktop integration**
- System: `/usr/share/applications/netui-gtk.desktop`
- User: `~/.local/share/applications/netui-gtk.desktop`

✓ **PolicyKit policy** (system installation only)
- `/usr/share/polkit-1/actions/com.github.netui-gtk.policy`

✓ **Python cache files**
- `__pycache__/` directories
- `*.pyc` compiled files
- `*.pyo` optimized files

✓ **Desktop database** (automatically updated)

### Optional Removal (You'll Be Asked)

**Configuration directory:**
- `~/.config/netui-gtk/`
  - Contains: `settings.json` (window size, IPv6 preference, etc.)

**Answer "y" to remove configuration if:**
- You want a completely clean removal
- You're troubleshooting and want fresh settings
- You won't reinstall NetUI-GTK

**Answer "n" to keep configuration if:**
- You might reinstall later
- You want to preserve your settings
- You're just upgrading (reinstall instead)

---

## Verification

After uninstallation, verify removal:

```bash
# Check if command exists (should show nothing)
which netui-gtk

# Check if files are gone
ls /usr/local/bin/netui-gtk 2>/dev/null || echo "✓ Executable removed"
ls ~/.local/bin/netui-gtk 2>/dev/null || echo "✓ User executable removed"

# Check desktop entry
ls /usr/share/applications/netui-gtk.desktop 2>/dev/null || echo "✓ Desktop entry removed"
ls ~/.local/share/applications/netui-gtk.desktop 2>/dev/null || echo "✓ User desktop entry removed"

# Check if config exists
ls ~/.config/netui-gtk/ 2>/dev/null && echo "Config preserved" || echo "✓ Config removed"
```

---

## Manual Uninstallation

If scripts don't work, manually remove files:

### System-Wide Installation

```bash
# Remove executable
sudo rm -f /usr/local/bin/netui-gtk

# Remove desktop entry
sudo rm -f /usr/share/applications/netui-gtk.desktop

# Remove PolicyKit policy
sudo rm -f /usr/share/polkit-1/actions/com.github.netui-gtk.policy

# Update desktop database
sudo update-desktop-database /usr/share/applications 2>/dev/null || true
```

### User Installation

```bash
# Remove executable
rm -f ~/.local/bin/netui-gtk

# Remove desktop entry
rm -f ~/.local/share/applications/netui-gtk.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

### Remove Configuration (Optional)

```bash
# Remove user configuration
rm -rf ~/.config/netui-gtk/

# Verify removal
ls ~/.config/netui-gtk/ 2>/dev/null || echo "✓ Configuration removed"
```

### Clean Source Directory (Development)

```bash
cd netui-gtk

# Use Makefile
make clean

# Or manually
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
rm -rf build/ dist/ 2>/dev/null || true
```

---

## Troubleshooting

### "Permission denied" when uninstalling

**Problem:** Trying to uninstall system installation without sudo

**Solution:**
```bash
sudo ./uninstall.sh
# Or
sudo make uninstall
```

### "File not found" errors

**Problem:** Files already removed or different installation location

**Solution:**
- Check both system and user locations
- Run: `find ~ /usr -name "netui-gtk" 2>/dev/null`
- Manually remove found files

### Desktop entry still appears

**Problem:** Desktop database not updated

**Solution:**
```bash
# System
sudo update-desktop-database /usr/share/applications

# User
update-desktop-database ~/.local/share/applications

# Clear cache
rm -rf ~/.cache/menus/
```

### Configuration keeps coming back

**Problem:** Application creates new config on launch

**Solution:**
```bash
# Remove config after uninstalling app
rm -rf ~/.config/netui-gtk/

# Verify app is uninstalled first
which netui-gtk  # Should show nothing
```

### Python cache files remain

**Problem:** `__pycache__` directories not removed

**Solution:**
```bash
cd /path/to/netui-gtk
make clean

# Or find and remove all
find . -type d -name "__pycache__" -delete
find . -type f -name "*.pyc" -delete
```

---

## Uninstall vs. Reinstall

### When to Uninstall

- ✓ You no longer need NetUI-GTK
- ✓ Switching to a different network manager
- ✓ Troubleshooting requires clean removal
- ✓ Preparing system for different installation type

### When to Reinstall Instead

- ✓ Updating to newer version
- ✓ Fixing corrupted installation
- ✓ Changing installation options

**To reinstall:**
```bash
./quick-install.sh
# Choose option 1) Reinstall
```

---

## Complete Removal Checklist

Before uninstalling, ensure:

- [ ] No active network connections managed by NetUI-GTK
- [ ] Application is closed (check with `ps aux | grep netui-gtk`)
- [ ] Backup any custom configurations (if needed)

Run uninstallation:

- [ ] Execute uninstall script or make target
- [ ] Confirm configuration removal when asked
- [ ] Verify executable removed: `which netui-gtk`
- [ ] Verify desktop entry removed
- [ ] Check application menu (should not appear)

Final cleanup:

- [ ] Remove source directory (if not needed): `rm -rf ~/netui-gtk`
- [ ] Clear terminal history (optional): `history -c`

---

## After Uninstallation

### Restore Original Network Management

If you disabled NetworkManager or systemd-networkd:

**Enable NetworkManager:**
```bash
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```

**Enable systemd-networkd:**
```bash
sudo systemctl enable systemd-networkd
sudo systemctl start systemd-networkd
```

### Alternative Network Tools

Native Linux network management tools:

- **nmtui** - NetworkManager Text UI (TUI)
- **nmcli** - NetworkManager command-line
- **ip** - iproute2 command-line tool
- **ifconfig** - Classic network config (deprecated)

---

## Feedback

If you uninstalled due to issues:
- Report bugs: https://github.com/samyabdellatif/netui-gtk/issues
- Share feedback on what could be improved

---

## Reinstallation

To reinstall NetUI-GTK in the future:

```bash
cd netui-gtk
./quick-install.sh
```

Or download latest version:
```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk
./quick-install.sh
```

Your old configuration will be used if you didn't remove it!

---

**Uninstallation complete!** Thank you for using NetUI-GTK.
