# NetUI-GTK New Features

## Advanced Network Management Features Added

### 🎯 Overview
The following advanced features have been added to provide comprehensive network interface management capabilities:

---

## New Features

### 1. **Real-Time Statistics Monitoring** 📊

**Location**: Advanced → Statistics Tab

Provides live monitoring of network traffic with auto-refresh every 2 seconds:

- **Received Bytes** - Total data received (with human-readable format)
- **Transmitted Bytes** - Total data sent (with human-readable format)
- **Received Packets** - Number of packets received
- **Transmitted Packets** - Number of packets sent
- **RX Errors** - Receive errors count
- **TX Errors** - Transmit errors count
- **RX Dropped** - Dropped incoming packets
- **TX Dropped** - Dropped outgoing packets
- **Collisions** - Network collisions detected

**Usage**:
1. Select interface row
2. Click "Advanced" button
3. View Statistics tab for live data

**Benefits**:
- Monitor network performance in real-time
- Identify connection quality issues
- Debug network problems
- Track bandwidth usage

---

### 2. **MTU Configuration** 🔧

**Location**: Advanced → Link Settings Tab

Configure Maximum Transmission Unit (MTU) for interfaces:

- **Default**: 1500 bytes (Ethernet)
- **Range**: 68 - 65535 bytes
- **Common values**:
  - 1500 - Standard Ethernet
  - 1492 - PPPoE connections
  - 9000 - Jumbo frames (high-performance networks)

**Usage**:
1. Click "Advanced" → "Link Settings"
2. Enter MTU value
3. Click "Set MTU"

**When to adjust**:
- PPPoE connections (use 1492)
- VPN tunnels (reduce by 50-100)
- High-performance networks (use 9000 for jumbo frames)
- Troubleshooting fragmentation issues

---

### 3. **MAC Address Cloning** 🎭

**Location**: Advanced → Link Settings Tab

Change interface MAC address (hardware address):

- **Format**: AA:BB:CC:DD:EE:FF
- **Use Cases**:
  - Bypass MAC filtering
  - Impersonate another device
  - Privacy enhancement
  - Testing network equipment

**Usage**:
1. Click "Advanced" → "Link Settings"
2. Enter new MAC address
3. Click "Clone MAC"

**⚠️ Important**:
- Interface will be restarted
- Connection will be temporarily lost
- Changes are temporary (reset on reboot unless persisted)
- Some networks may detect MAC changes

---

### 4. **Link Status & Speed Display** 🚀

**Location**: Advanced → Statistics Tab

Real-time display of physical link information:

- **Operational State**: UP, DOWN, UNKNOWN
- **Carrier Status**: Cable connected/disconnected (color-coded)
- **Link Speed**: Actual connection speed (10/100/1000 Mbps)
- **MTU**: Current MTU setting

**Color Coding**:
- 🟢 Green = Connected
- 🔴 Red = Disconnected

**Benefits**:
- Quickly identify cable issues
- Verify link speed negotiation
- Monitor interface state

---

### 5. **Promiscuous Mode** 👁️

**Location**: Advanced → Advanced Tab

Enable/disable promiscuous mode for packet capture:

**What it does**:
- Allows interface to capture ALL network traffic (not just packets for this device)
- Required for network analysis tools (Wireshark, tcpdump, etc.)

**Usage**:
1. Click "Advanced" → "Advanced" tab
2. Toggle "Promiscuous Mode" switch

**Use Cases**:
- Network troubleshooting
- Packet analysis
- Network monitoring
- Security auditing

**⚠️ Note**: 
- Requires root privileges
- May violate network policies
- Use responsibly and legally

---

### 6. **Driver Information** 🔍

**Location**: Advanced → Advanced Tab

Display network driver details:

- **Driver Name**: Kernel module in use
- **Module Alias**: Hardware identification

**Benefits**:
- Identify hardware compatibility
- Troubleshoot driver issues
- Verify correct driver loading

---

## Technical Details

### Files Added:

1. **netmanage/advanced.py** - Backend functions for advanced features
   - MTU management
   - Statistics reading
   - Link speed detection
   - Promiscuous mode control
   - MAC cloning
   - Driver information

2. **advanced_config.py** - GTK UI for advanced configuration window
   - Multi-tab interface
   - Live statistics updates
   - Form validation
   - Error handling

### API Functions Available:

```python
# MTU
get_mtu(interface_name) → int
set_mtu(interface_name, mtu_value) → bool

# Statistics
get_interface_stats(interface_name) → dict
format_bytes(bytes_val) → str

# Link Info
get_link_speed(interface_name) → str
get_carrier_state(interface_name) → bool
get_operstate(interface_name) → str

# Promiscuous Mode
get_promiscuous_mode(interface_name) → bool
set_promiscuous_mode(interface_name, enable) → bool

# MAC Cloning
clone_mac_address(interface_name, new_mac) → bool

# Driver
get_driver_info(interface_name) → dict
```

---

## Updated Main Interface

### New Column: "Advanced"

Each interface row now has:
- Interface Details
- Status (UP/DOWN toggle)
- Connection (DHCP toggle)
- Configuration (Manual Config button)
- **Advanced (Advanced button)** ← NEW

### Window Size
- Adjusted to accommodate new column
- Optimized spacing for better readability

---

## Safety Features

All advanced features include:

✅ **Input Validation** - Prevents invalid values
✅ **Timeout Protection** - Commands won't hang
✅ **Error Dialogs** - Clear user feedback
✅ **Logging** - All operations logged
✅ **Graceful Failures** - Errors don't crash app

---

## Usage Examples

### Example 1: Monitor Bandwidth
```
1. Click "Advanced" on interface
2. Go to "Statistics" tab
3. Watch Received/Transmitted Bytes update in real-time
4. Keep window open for continuous monitoring
```

### Example 2: Fix MTU Issues
```
PPPoE connection dropping packets?
1. Click "Advanced"
2. Go to "Link Settings"
3. Change MTU from 1500 to 1492
4. Click "Set MTU"
5. Test connection
```

### Example 3: Bypass MAC Filter
```
Router only allows specific MAC addresses?
1. Note the allowed MAC address
2. Click "Advanced" → "Link Settings"
3. Enter the allowed MAC
4. Click "Clone MAC"
5. Interface restarts with new MAC
```

### Example 4: Network Packet Capture
```
Need to capture network traffic?
1. Click "Advanced" → "Advanced" tab
2. Enable "Promiscuous Mode"
3. Use Wireshark or tcpdump
4. Disable when done
```

---

## Comparison with Other Tools

| Feature | netui-gtk | nmtui | ifconfig | ip |
|---------|-----------|-------|----------|-----|
| GUI Interface | ✅ | ⚠️ (TUI) | ❌ | ❌ |
| Real-time Stats | ✅ | ❌ | ❌ | ❌ |
| MTU Config | ✅ | ❌ | ✅ | ✅ |
| MAC Cloning | ✅ | ❌ | ✅ | ✅ |
| Promiscuous Mode | ✅ | ❌ | ✅ | ✅ |
| Link Speed Display | ✅ | ❌ | ❌ | ⚠️ |
| Live Monitoring | ✅ | ❌ | ❌ | ❌ |
| IPv6 Support | ✅ | ✅ | ✅ | ✅ |

---

## Future Enhancements (Possible)

These features could be added in future versions:

- 📈 **Bandwidth graphs** - Visual traffic display
- 🌐 **VLAN management** - 802.1Q tagging
- 🔗 **Bonding/Bridging** - Link aggregation
- 📡 **Wireless settings** - SSID, encryption for WiFi
- 🔔 **Alerts** - Notify on errors/thresholds
- 💾 **Export stats** - Save statistics to file
- ⏱️ **Traffic shaping** - QoS configuration
- 🗺️ **Route visualization** - Network topology

---

## Requirements

All features use native Linux tools:
- `/sys/class/net/*` - sysfs interface (always available)
- `ip` command - iproute2 package
- No external dependencies

**Compatibility**: Works on all modern Linux distributions (kernel 2.6+)

---

**Enjoy the enhanced network management capabilities!** 🚀
