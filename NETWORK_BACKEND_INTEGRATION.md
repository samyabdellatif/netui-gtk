# NetworkManager and systemd-networkd Integration

## Overview

NetUI-GTK now **automatically detects and integrates** with NetworkManager and systemd-networkd instead of requiring you to stop these services. The app intelligently uses the appropriate backend for each interface.

## How It Works

### Automatic Backend Detection

When you connect an interface or configure IP settings, NetUI-GTK:

1. **Detects the manager**: Checks if the interface is managed by:
   - NetworkManager (nmcli)
   - systemd-networkd (networkctl)
   - Manual control (direct `ip` commands)

2. **Uses the right tool**: Automatically selects the appropriate backend:
   - **NetworkManager** → Uses `nmcli` commands
   - **systemd-networkd** → Creates `.network` files
   - **Manual** → Uses traditional `ip` and `dhclient` commands

3. **No conflicts**: Works seamlessly with existing network services

## Features

### ✅ DHCP Connection

**Before (old behavior):**
- App would warn about NetworkManager conflicts
- Required stopping NetworkManager: `sudo systemctl stop NetworkManager`
- Used only dhclient/dhcpcd

**Now (new behavior):**
- Detects if interface is managed by NetworkManager
- Automatically uses `nmcli device connect <interface>` if managed
- Falls back to dhclient if not managed
- **No service conflicts!**

**Example:**
```bash
# Interface managed by NetworkManager
$ nmcli device status
wlp3s0  wifi  connected  MyNetwork

# NetUI-GTK detects this and uses:
nmcli device connect wlp3s0  # Instead of dhclient
```

### ✅ Static IP Configuration

**NetworkManager-managed interfaces:**
```bash
# NetUI-GTK automatically creates connection:
nmcli connection add type ethernet \
    con-name netui-eth0 \
    ifname eth0 \
    ipv4.method manual \
    ipv4.addresses 192.168.1.100/24 \
    ipv4.gateway 192.168.1.1 \
    ipv4.dns "8.8.8.8 8.8.4.4"
```

**systemd-networkd managed interfaces:**
```bash
# NetUI-GTK creates /etc/systemd/network/50-eth0.network:
[Match]
Name=eth0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=8.8.8.8
DNS=8.8.4.4
```

**Manual interfaces:**
```bash
# NetUI-GTK uses traditional ip commands:
ip addr add 192.168.1.100/24 dev eth0
ip route add default via 192.168.1.1
```

### ✅ Interface Disconnect

**NetworkManager:**
- Uses `nmcli device disconnect <interface>`

**Manual:**
- Uses `ip addr flush dev <interface>`

## User Experience

### Visual Feedback

When you connect or configure an interface, you'll see messages like:

- ✓ "Connected successfully **via networkmanager**"
- ✓ "Static IP configured via **systemd-networkd**"
- ✓ "Connected via DHCP client" (manual mode)

### GUI Integration

No configuration needed! The app automatically:
1. Detects your network setup
2. Uses the right backend
3. Shows which method was used
4. Handles errors gracefully

## Technical Details

### Backend Selection Logic

```python
def detect_interface_manager(interface_name):
    """Returns: 'networkmanager', 'systemd-networkd', or 'manual'"""
    
    # Check NetworkManager
    if nmcli shows interface as managed:
        return 'networkmanager'
    
    # Check systemd-networkd
    if networkctl shows interface as configured:
        return 'systemd-networkd'
    
    # Default to manual
    return 'manual'
```

### Supported Operations

| Operation | NetworkManager | systemd-networkd | Manual |
|-----------|---------------|------------------|--------|
| DHCP Connect | ✅ nmcli | ✅ .network file | ✅ dhclient |
| Static IP | ✅ nmcli | ✅ .network file | ✅ ip addr |
| Gateway | ✅ nmcli | ✅ .network file | ✅ ip route |
| DNS | ✅ nmcli | ✅ .network file | ✅ resolv.conf |
| Disconnect | ✅ nmcli | ⚠️ Flush IP | ✅ ip addr flush |

## Benefits

### For NetworkManager Users

✅ **No need to stop NetworkManager**
- App works alongside NetworkManager
- Uses nmcli for managed interfaces
- Preserves your existing connections

### For systemd-networkd Users

✅ **Native systemd integration**
- Creates proper .network files
- Follows systemd-networkd conventions
- Configurations persist across reboots

### For Manual Users

✅ **Traditional control maintained**
- Direct ip/dhclient commands
- No service dependencies
- Maximum flexibility

## Examples

### Example 1: Mixed Environment

You have:
- `wlp3s0` (WiFi) managed by NetworkManager
- `eth0` (Ethernet) manually configured

**NetUI-GTK behavior:**
- Clicking connect on `wlp3s0` → Uses `nmcli device connect wlp3s0`
- Clicking connect on `eth0` → Uses `dhclient eth0`
- **Both work perfectly!**

### Example 2: Corporate Network

Your IT department uses NetworkManager for all interfaces.

**Before:**
- Had to stop NetworkManager
- Lost WiFi connection
- Conflicted with company policy

**Now:**
- App detects NetworkManager
- Uses nmcli commands
- IT policies respected
- **Everything works!**

### Example 3: Server Environment

Server uses systemd-networkd for all network configuration.

**NetUI-GTK:**
- Detects systemd-networkd
- Creates .network files in `/etc/systemd/network/`
- Restarts networkd service
- Configuration persists after reboot

## Compatibility

### NetworkManager
- **Requires**: nmcli (part of NetworkManager package)
- **Tested with**: NetworkManager 1.20+
- **Distributions**: Ubuntu, Fedora, Debian, Arch (default)

### systemd-networkd
- **Requires**: networkctl (part of systemd)
- **Tested with**: systemd 240+
- **Distributions**: All modern systemd-based distros

### Manual Mode
- **Requires**: iproute2 (ip command), dhclient/dhcpcd
- **Works on**: All Linux distributions
- **Best for**: Servers, minimal installs, advanced users

## Configuration Files

### NetworkManager Connections
Created at: `/etc/NetworkManager/system-connections/netui-<interface>`

Example:
```ini
[connection]
id=netui-eth0
type=ethernet
interface-name=eth0

[ipv4]
method=manual
address1=192.168.1.100/24,192.168.1.1
dns=8.8.8.8;8.8.4.4
```

### systemd-networkd Files
Created at: `/etc/systemd/network/50-<interface>.network`

Example:
```ini
[Match]
Name=eth0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=8.8.8.8
```

## Troubleshooting

### Issue: "Permission denied"

**Solution**: App needs root access to:
- Modify NetworkManager connections (system-wide)
- Create systemd-networkd files in `/etc/systemd/network/`
- Run dhclient or ip commands

Run with: `sudo netui-gtk` or let PolicyKit handle elevation

### Issue: Changes don't persist after reboot

**NetworkManager/systemd-networkd:**
- Configurations persist automatically ✅

**Manual mode:**
- IP addresses set with `ip addr` are temporary
- Consider switching interface to NetworkManager/systemd-networkd management
- Or create systemd service to apply at boot

### Issue: "nmcli: command not found"

**Solution**: Install NetworkManager:
```bash
# Debian/Ubuntu
sudo apt install network-manager

# Fedora
sudo dnf install NetworkManager

# Arch
sudo pacman -S networkmanager
```

## Migration Guide

### From Manual to NetworkManager

1. Stop manual management
2. Enable NetworkManager:
   ```bash
   sudo systemctl enable NetworkManager
   sudo systemctl start NetworkManager
   ```
3. Use NetUI-GTK normally - it will detect NetworkManager

### From NetworkManager to Manual

1. Stop NetworkManager:
   ```bash
   sudo systemctl stop NetworkManager
   sudo systemctl disable NetworkManager
   ```
2. Use NetUI-GTK - it will switch to manual mode automatically

## Developer Information

### New Module: `netmanage/network_service.py`

Provides:
- `NetworkService.detect_interface_manager(interface)` - Backend detection
- `connect_interface_dhcp(interface)` - Unified DHCP connection
- `disconnect_interface(interface)` - Unified disconnection
- `set_manual_config(interface, ip, mask, gw, dns)` - Static IP configuration

### Integration Points

**netui.py:**
- Import: `from netmanage.network_service import connect_interface_dhcp, disconnect_interface, NetworkService`
- Connect: Uses `connect_interface_dhcp()` instead of direct `dhcpc.lease()`
- Disconnect: Uses `disconnect_interface()` instead of just `set_ip("0.0.0.0")`

**manual_config.py:**
- Import: `from netmanage.network_service import set_manual_config, NetworkService`
- Apply: Tries `set_manual_config()` first, falls back to manual if needed

## Future Enhancements

Planned features:
- [ ] WPA/WPA2 wireless configuration via NetworkManager
- [ ] VPN support through NetworkManager
- [ ] Bond/bridge interface creation
- [ ] VLAN configuration
- [ ] Connection profiles (save/load configurations)

## Summary

**Key Points:**
- ✅ Automatic backend detection
- ✅ No service conflicts
- ✅ Works with NetworkManager, systemd-networkd, and manual modes
- ✅ Intelligent fallback
- ✅ User-friendly error messages
- ✅ No configuration required

**The app just works!** 🎉
