# Repair Plan: netui-gtk Codebase Issues

**Date:** 2026-05-23  
**Based on:** CODEBASE_ASSESSMENT.md  
**Goal:** Fix all identified issues one by one, with clear instructions for each step.

---

## Issue Index

| # | Issue | Severity | File(s) | Est. Effort | Dependencies |
|---|-------|----------|---------|-------------|--------------|
| 1 | Module-level code execution on import | 🔴 Critical | `netui.py` | 30 min | None |
| 2 | `ifconfig.py` module-level socket + deprecated Python | 🔴 Critical | `netmanage/ifconfig.py` | 45 min | None |
| 3 | Dead code: `_check_interface_managed()` | 🟡 Medium | `netui.py` | 10 min | None |
| 4 | Duplicate `_netmask_to_cidr()` methods | 🟡 Medium | `netmanage/network_service.py` | 15 min | None |
| 5 | Window size race condition (`destroy` vs `delete-event`) | 🟡 Medium | `netui.py` | 15 min | None |
| 6 | Hard-coded `time.sleep()` blocking GUI | 🟡 Medium | `netui.py`, `netmanage/network_service.py` | 1 hr | #1 (refactoring helps) |
| 7 | GUI freezing on network operations (async) | 🟡 Medium | `netui.py`, `__main__.py` | 2 hr | #6 (same root cause) |

**Note:** Issue #3 (Deprecated Python Patterns) from the assessment is included within Issue #2 in this plan, since both affect `ifconfig.py`.

---

## Issue #1: Module-Level Code Execution on Import

### Description
In `netui.py` lines 16-50, code runs at **import time** rather than when the class is instantiated:

```python
# This runs when ANY file imports from netui:
intF_list = list_ifs()  # Enumerates ALL network interfaces
```

This means:
- Importing `netui` triggers network interface enumeration as a side effect
- The global `intF_list` variable is tied to module lifecycle
- Hard to test or reuse any code from this module

### Step-by-Step Fix

#### Step 1.1: Move interface enumeration into the class constructor

**File:** `netui.py`
**Action:** Replace the module-level try/except block (lines 16-50) with an instance variable.

**Remove** these lines (exact block to delete):
```python
try:
    logger.info("Initializing interface list...")
    intF_list = list_ifs()
    logger.info(f"Found {len(intF_list)} interfaces")
    
    for iface in intF_list:
        try:
            if iface.is_up():
                ip_addr = iface.get_ip()
                mac_addr = iface.get_mac()
                logger.info(f"Interface {iface.name} is UP - IP: {ip_addr}, MAC: {mac_addr}")
                print(f"{iface.name} interface is UP , IP ADDRESS: {ip_addr}")
            else:
                logger.info(f"{iface.name} interface is DOWN")
                print(f"{iface.name} interface is DOWN")
        except Exception as e:
            logger.error(f"Error checking interface {iface.name}: {e}")
            print(f"Error checking interface {iface.name}: {e}")

    total_iface = len(intF_list)
    logger.info(f"Total number of interfaces installed: {total_iface}")
    print(f"total number of interfaces installed : {total_iface}")
    
except Exception as e:
    logger.error(f"Failed to initialize interface list: {e}")
    print(f"Error: Failed to initialize network interfaces: {e}")
```

#### Step 1.2: Add `self.intF_list` to `__init__`

Inside `netUImainWindow.__init__()`, add this after `self.config = get_config()`:

```python
# Initialize interface list (moved from module-level to avoid import side effects)
self.intF_list = []
try:
    self.intF_list = list_ifs()
    logger.info(f"Found {len(self.intF_list)} interfaces")
    for iface in self.intF_list:
        if iface.is_up():
            logger.info(f"Interface {iface.name} is UP - IP: {iface.get_ip()}")
        else:
            logger.info(f"Interface {iface.name} is DOWN")
except Exception as e:
    logger.error(f"Failed to initialize interface list: {e}")
```

#### Step 1.3: Replace all `intF_list` references with `self.intF_list`

In `netui.py`, replace every occurrence of `intF_list` with `self.intF_list`:

| Location | Change |
|----------|--------|
| `create_ui()` line `for iface_index in range(len(intF_list)):` | `for iface_index in range(len(self.intF_list)):` |
| `create_ui()` line `interface = intF_list[iface_index]` | `interface = self.intF_list[iface_index]` |
| `on_UpDown_activated()` line `interface = intF_list[i]` | `interface = self.intF_list[i]` |
| `on_ConDiscon_activated()` line `interface = intF_list[i]` | `interface = self.intF_list[i]` |

#### Step 1.4: Verify

Run the app to confirm it works:
```bash
python3 __main__.py --help
```

Then test visually:
```bash
# Create test interface first
sudo ip link add dummy0 type dummy
sudo ip link set dummy0 up
# Run the app
sudo python3 __main__.py
# Clean up
sudo ip link delete dummy0
```

---

## Issue #2: `ifconfig.py` Module-Level Socket + Deprecated Python

### Description
Two sub-problems in `netmanage/ifconfig.py`:
1. **Socket initialized at import time** (line ~382: `init()`) — creates a global socket that can fail in restricted environments
2. **Deprecated methods** — `ecmd.tostring()` (removed in Python 3.12+), Python 2 byte string `'\x00'` syntax, `array.array("B", "\x00" * N)` uses str instead of bytes

### Step-by-Step Fix

#### Step 2.1: Replace `array.tostring()` with `array.tobytes()`

This affects **4 locations** in `ifconfig.py`:

| Line | Current | Replace with |
|------|---------|--------------|
| ~188 | `res = ecmd.tostring()` | `res = ecmd.tobytes()` |
| ~199 | `res = ecmd.tostring()` | `res = ecmd.tobytes()` |
| ~247 | `res = ifreqs.tostring()` | `res = ifreqs.tobytes()` |

Also the commented debug print on ~228:
| ~228 | `#print struct.unpack('I', ecmd[4:8].tostring())[0]` | `# struct.unpack('I', ecmd[4:8].tobytes())[0]` |

#### Step 2.2: Fix Python 2 byte string syntax

In `iterifs()` function, change:
```python
# Before:
ifreqs = array.array("B", "\x00" * SIZE_OF_IFREQ * 30)

# After:
ifreqs = array.array("B", b"\x00" * SIZE_OF_IFREQ * 30)
```

#### Step 2.3: Make socket initialization lazy

**Replace the module-level `init()` call** (last line of file) with a function that initializes on first use:

**Remove this line:**
```python
# Do this when loading the module
init()
```

**Add a lazy initialization function:**
```python
def _get_socket():
    """Get or initialize the global socket lazily."""
    global sock, sockfd
    if sock is None:
        init()
    if sockfd is None:
        raise RuntimeError("Network socket initialization failed")
    return sockfd
```

**Wrap `sockfd` usage** — every method that uses `sockfd` directly must call `_get_socket()` instead.

For example, in `Interface.up()`:
```python
def up(self):
    sock = _get_socket()
    ifreq = struct.pack('16sh', bytes(self.name, 'utf-8'), 0)
    flags = struct.unpack('16sh', fcntl.ioctl(sock, SIOCGIFFLAGS, ifreq))[1]
    flags = flags | IFF_UP
    ifreq = struct.pack('16sh', bytes(self.name, 'utf-8'), flags)
    fcntl.ioctl(sock, SIOCSIFFLAGS, ifreq)
```

Repeat for all methods that access `sockfd` directly:
- `up()`
- `down()`
- `is_up()`
- `get_mac()`
- `set_mac()`
- `get_ip()`
- `set_ip()`
- `get_netmask()`
- `set_netmask()`
- `get_index()`
- `get_link_info()`
- `set_link_mode()`
- `set_link_auto()`
- `set_pause_param()`
- `iterifs()` — uses `sockfd` in the `ioctl` call

#### Step 2.4: Verify

```bash
# Syntax check
python3 -c "from netmanage.ifconfig import Interface; print('Import OK')"

# With Python 3.12 if available:
python3.12 -c "from netmanage.ifconfig import Interface; print('Python 3.12 OK')"
```

---

## Issue #3: Dead Code — `_check_interface_managed()` Method

### Description
In `netui.py` lines 88-111, the method `_check_interface_managed()` is defined on `netUImainWindow` but **never called**. The actual interface manager detection is done by `NetworkService.detect_interface_manager()` in `network_service.py`.

### Step-by-Step Fix

#### Step 3.1: Remove the dead method

**File:** `netui.py`
**Action:** Delete the entire `_check_interface_managed()` method (lines 88-111):

```python
    def _check_interface_managed(self, interface_name):
        """Check if interface is managed by NetworkManager or systemd-networkd."""
        import subprocess
        
        # Check NetworkManager
        try:
            result = subprocess.run(
                ['nmcli', 'device', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if interface_name in line and 'unmanaged' not in line.lower():
                        return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check systemd-networkd
        try:
            result = subprocess.run(
                ['networkctl', 'status', interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and 'configured' in result.stdout.lower():
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return False
```

#### Step 3.2: Verify

```bash
# Confirm the method is gone
grep -n "_check_interface_managed" netui.py
# Should return no matches
```

---

## Issue #4: Duplicate `_netmask_to_cidr()` Methods

### Description
In `netmanage/network_service.py`, both `NetworkManagerBackend` and `SystemdNetworkdBackend` define an identical `_netmask_to_cidr()` static method. This violates DRY (Don't Repeat Yourself).

### Step-by-Step Fix

#### Step 4.1: Create a module-level utility function

**File:** `netmanage/network_service.py`
**Action:** Add a standalone function before the class definitions:

```python
def _netmask_to_cidr(netmask):
    """Convert netmask to CIDR notation (e.g., 255.255.255.0 -> 24)."""
    try:
        return sum([bin(int(x)).count('1') for x in netmask.split('.')])
    except (ValueError, AttributeError):
        return 24  # Default to /24
```

#### Step 4.2: Remove from both classes

**Delete** `NetworkManagerBackend._netmask_to_cidr()` (static method body):
```python
    @staticmethod
    def _netmask_to_cidr(netmask):
        """Convert netmask to CIDR notation"""
        try:
            return sum([bin(int(x)).count('1') for x in netmask.split('.')])
        except:
            return 24  # Default to /24
```

**Delete** `SystemdNetworkdBackend._netmask_to_cidr()` (static method body):
```python
    @staticmethod
    def _netmask_to_cidr(netmask):
        """Convert netmask to CIDR notation"""
        try:
            return sum([bin(int(x)).count('1') for x in netmask.split('.')])
        except:
            return 24
```

#### Step 4.3: Update callers

In `NetworkManagerBackend.set_manual_ip()`, change:
```python
# Before:
cidr = NetworkManagerBackend._netmask_to_cidr(netmask)

# After:
cidr = _netmask_to_cidr(netmask)
```

In `SystemdNetworkdBackend.set_manual_ip()`, change:
```python
# Before:
cidr = SystemdNetworkdBackend._netmask_to_cidr(netmask)

# After:
cidr = _netmask_to_cidr(netmask)
```

#### Step 4.4: Verify

```bash
python3 -c "
from netmanage.network_service import _netmask_to_cidr
assert _netmask_to_cidr('255.255.255.0') == 24
assert _netmask_to_cidr('255.255.0.0') == 16
assert _netmask_to_cidr('255.0.0.0') == 8
assert _netmask_to_cidr('invalid') == 24
print('All _netmask_to_cidr tests passed')
"
```

---

## Issue #5: Window Size Race Condition (Destroy Signal)

### Description
In `netui.py`, `on_window_destroy()` connects to the `destroy` signal, but by the time `destroy` fires, `self.get_size()` may already return `(0, 0)` because the window is being torn down.

### Step-by-Step Fix

#### Step 5.1: Change signal connection in `__init__`

**File:** `netui.py` in `netUImainWindow.__init__()`
**Action:** Replace the `destroy` signal connection with `delete-event`:

**Before:**
```python
# Save window size on destroy
self.connect("destroy", self.on_window_destroy)
```

**After:**
```python
# Save window size before closing
self.connect("delete-event", self.on_window_delete)
```

#### Step 5.2: Replace the method

**Before:**
```python
def on_window_destroy(self, widget):
    """Save window size before closing."""
    try:
        width, height = self.get_size()
        self.config.set('window_width', width)
        self.config.set('window_height', height)
        logger.info(f"Window size saved: {width}x{height}")
    except Exception as e:
        logger.error(f"Failed to save window size: {e}")
```

**After:**
```python
def on_window_delete(self, widget, event):
    """Save window size before closing and quit."""
    try:
        width, height = self.get_size()
        if width > 0 and height > 0:
            self.config.set('window_width', width)
            self.config.set('window_height', height)
            logger.info(f"Window size saved: {width}x{height}")
    except Exception as e:
        logger.error(f"Failed to save window size: {e}")
    Gtk.main_quit()
    return False  # Allow the window to close
```

> **Note:** The `delete-event` handler must return `False` to allow the window to close, or `True` to block closure.

#### Step 5.3: Update `__main__.py` if needed

Check `__main__.py` — it currently has:
```python
win = netUImainWindow()
win.connect("destroy", Gtk.main_quit)
```

Since we moved `Gtk.main_quit()` into the `delete-event` handler, the `destroy` connection in `__main__.py` will still work as a safety net, but it's redundant. Either:
- Keep it (no harm, double quit is safe), or
- Remove it (cleaner)

#### Step 5.4: Verify

```bash
# Start the app, resize window, close, then check config file
sudo python3 __main__.py &
sleep 2
# Close the window (user manually closes)
# Then check:
cat ~/.config/netui-gtk/settings.json
# Should show the saved window_width and window_height (not 0)
```

---

## Issue #6: Hard-coded `time.sleep()` Blocking GUI

### Description
In `netui.py`, `time.sleep(1)` is used to wait for IP assignment after DHCP connect, and `time.sleep(0.5)` after disconnect. These block the GTK main loop, freezing the GUI.

### Step-by-Step Fix

#### Step 6.1: Replace `time.sleep()` with `GLib.timeout_add()` polling

**File:** `netui.py` in `on_ConDiscon_activated()`
**Action:** Replace blocking sleeps with a non-blocking polling approach.

**Replace this code** (after `success, message = connect_interface_dhcp(interface_name)`):
```python
if success:
    # Verify connection
    import time
    time.sleep(1)  # Give time for IP assignment
    new_ip = interface.get_ip()
    
    if new_ip and str(new_ip) != "None":
        ...
    else:
        ...
```

**With:**
```python
if success:
    # Verify connection using non-blocking polling
    self._poll_for_ip(interface, switch, 15)  # Poll for up to 15 seconds
```

#### Step 6.2: Create a polling helper method

Add this method to `netUImainWindow`:

```python
def _poll_for_ip(self, interface, switch, max_attempts=15):
    """Poll for IP assignment without blocking the GUI."""
    self._poll_count = 0
    self._poll_max = max_attempts
    self._poll_interface = interface
    self._poll_switch = switch
    
    GLib.timeout_add(1000, self._poll_check_ip)  # Check every 1 second

def _poll_check_ip(self):
    """Called every second to check if IP has been assigned."""
    self._poll_count += 1
    
    try:
        new_ip = self._poll_interface.get_ip()
        if new_ip and str(new_ip) != "None":
            # IP assigned successfully
            manager = NetworkService.detect_interface_manager(self._poll_interface.name)
            backend_info = f" (via {manager})" if manager != 'manual' else ""
            logger.info(f"Connected {self._poll_interface.name} with IP: {new_ip}{backend_info}")
            self.show_info_dialog(
                "Connection Successful",
                f"{self._poll_interface.name} connected successfully{backend_info}\nIP: {new_ip}"
            )
            return False  # Stop polling
    except Exception as e:
        logger.error(f"Error checking IP: {e}")
    
    if self._poll_count >= self._poll_max:
        # Timeout - IP not assigned
        logger.warning(f"IP not assigned after {self._poll_max} seconds")
        self.show_info_dialog(
            "Connection Started",
            f"{self._poll_interface.name} connection initiated.\nIP assignment may still be in progress."
        )
        return False  # Stop polling
    
    return True  # Continue polling
```

#### Step 6.3: Apply the same fix to the disconnect path

Replace the disconnect verification (after `disconnect_interface()`):
```python
# Before:
import time
time.sleep(0.5)
new_ip = interface.get_ip()

# After:
self._poll_for_disconnect(interface, switch, 10)  # Poll for up to 10 seconds
```

Add the disconnect polling method:
```python
def _poll_for_disconnect(self, interface, switch, max_attempts=10):
    """Poll for IP removal without blocking the GUI."""
    self._disconnect_count = 0
    self._disconnect_max = max_attempts
    self._disconnect_interface = interface
    self._disconnect_switch = switch
    
    GLib.timeout_add(500, self._poll_disconnect_check)  # Check every 0.5 seconds

def _poll_disconnect_check(self):
    """Called every 0.5 seconds to check if IP has been cleared."""
    self._disconnect_count += 1
    
    try:
        new_ip = self._disconnect_interface.get_ip()
        if not new_ip or str(new_ip) == "None":
            # IP cleared successfully
            logger.info(f"Disconnected {self._disconnect_interface.name}")
            self.show_info_dialog(
                "Disconnection Successful",
                f"{self._disconnect_interface.name} has been disconnected successfully."
            )
            return False  # Stop polling
    except Exception as e:
        logger.error(f"Error checking IP: {e}")
    
    if self._disconnect_count >= self._disconnect_max:
        # Timeout - IP still present
        logger.warning(f"IP not cleared after {self._disconnect_max * 0.5} seconds")
        self.show_info_dialog(
            "Disconnection Partial",
            f"{self._disconnect_interface.name} disconnected but may still have an IP.\nTry toggling the Status switch."
        )
        return False  # Stop polling
    
    return True  # Continue polling
```

#### Step 6.4: Add `from gi.repository import GLib` to imports

In `netui.py`, add `GLib` to the import line:
```python
from gi.repository import Gtk, GLib
```

#### Step 6.5: Verify

```bash
sudo python3 __main__.py
# Test connect/disconnect - GUI should remain responsive during polling
```

---

## Issue #7: GUI Freezing on Network Operations (Async Threading)

### Description
All `subprocess.run()` calls for DHCP (`dhcpcd`, `dhclient`, `nmcli`, etc.) are blocking calls in the main GTK thread. A 30-second DHCP timeout freezes the GUI completely.

### Step-by-Step Fix

This is the most complex fix. There are two approaches:

**Approach A (Simpler):** Use `GLib.timeout_add()` + a `threading.Thread` to run blocking operations in the background.
**Approach B (More Robust):** Refactor network operations to use `Gio.Task` / `Gio.Subprocess`.

**Recommendation:** Approach A — simpler, less refactoring, still solves the freeze.

#### Step 7.1: Create an async helper module

**New file:** `netmanage/async_worker.py`

```python
"""
Async worker for running network operations in a background thread.
Prevents GUI freezing during blocking network calls.
"""
import threading
import logging
from gi.repository import GLib

logger = logging.getLogger(__name__)


class AsyncWorker:
    """Runs blocking operations in a background thread and calls back on the GTK main thread."""
    
    @staticmethod
    def run_async(target_func, callback, on_error=None, *args, **kwargs):
        """
        Run a blocking function in a background thread.
        
        Args:
            target_func: The blocking function to run
            callback: Called on GTK main thread with (success, result) on completion
            on_error: Called on GTK main thread with exception info on failure
            *args, **kwargs: Passed to target_func
        """
        def worker():
            try:
                result = target_func(*args, **kwargs)
                # Schedule callback on GTK main thread
                GLib.idle_add(callback, True, result)
            except Exception as e:
                logger.error(f"Async worker error: {e}")
                if on_error:
                    GLib.idle_add(on_error, e)
                else:
                    GLib.idle_add(callback, False, str(e))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
```

#### Step 7.2: Add `__init__.py` content

**File:** `netmanage/__init__.py`
Make sure it has:
```python
# Empty - package marker
```

#### Step 7.3: Use `AsyncWorker` in `on_ConDiscon_activated()`

In `netui.py`, replace the direct call to `connect_interface_dhcp()`:
```python
# Before:
success, message = connect_interface_dhcp(interface_name)

# After:
from netmanage.async_worker import AsyncWorker

# Show a "Connecting..." status
self._show_connecting_status(interface_name)

# Run asynchronously
def _on_connect_complete(result_tuple, iface=interface, sw=switch):
    success, message = result_tuple
    if success:
        # Now poll for IP (non-blocking)
        GLib.idle_add(lambda: self._poll_for_ip(iface, sw, 15))
    else:
        logger.error(f"Failed to connect {iface.name}: {message}")
        GLib.idle_add(lambda: self.show_error_dialog(
            "Connection Error", f"Failed to connect {iface.name}:\n{message}"))
        GLib.idle_add(lambda: sw.set_active(False))

AsyncWorker.run_async(connect_interface_dhcp, _on_connect_complete, interface_name=interface_name)
```

#### Step 7.4: Apply same pattern to disconnect

```python
def _on_disconnect_complete(result_tuple, iface=interface, sw=switch):
    success, message = result_tuple
    if success:
        GLib.idle_add(lambda: self._poll_for_disconnect(iface, sw, 10))
    else:
        GLib.idle_add(lambda: self.show_error_dialog(
            "Disconnection Error", f"Failed to disconnect {iface.name}:\n{message}"))
        GLib.idle_add(lambda: sw.set_active(True))

AsyncWorker.run_async(disconnect_interface, _on_disconnect_complete, interface_name=interface_name)
```

#### Step 7.5: Add a status indicator

Add a method to show connection status:
```python
def _show_connecting_status(self, interface_name):
    """Show a brief status in the title bar or status bar."""
    # For now, just log it - could add a proper status bar later
    logger.info(f"Connecting {interface_name} in background...")
```

#### Step 7.6: Update `set_manual_config` in `manual_config.py` (optional but recommended)

The manual configuration window also does blocking `subprocess.run()` calls. Apply the same async pattern there.

#### Step 7.7: Verify

```bash
sudo python3 __main__.py
# Test connect/disconnect - GUI should remain fully responsive
# You should be able to interact with the window while DHCP runs
```

---

## Fix Application Order

The fixes should be applied in this order to minimize merge conflicts and dependency issues:

```
Issue #1  →  Issue #3  →  Issue #4  →  Issue #5  →  Issue #2  →  Issue #6  →  Issue #7
```

| Order | Issue | Why this order |
|-------|-------|----------------|
| 1st | **#1** Module-level code | Changes global variable usage everywhere — do this first to avoid rework |
| 2nd | **#3** Dead code removal | Simple deletion, no dependencies |
| 3rd | **#4** Duplicate methods | Simple refactoring in `network_service.py` |
| 4th | **#5** Window size race | Small change to signal handler |
| 5th | **#2** `ifconfig.py` socket + deprecated | Complex changes in `ifconfig.py` — no code depends on this changing |
| 6th | **#6** Hard-coded `time.sleep()` | Depends on #1 (moves to `self.intF_list`) |
| 7th | **#7** Async threading | Depends on #6 (shares some patterns) |

---

## Testing After Each Fix

After applying each fix, run this verification:

```bash
# 1. Syntax check
python3 -c "import py_compile; py_compile.compile('netui.py', doraise=True); py_compile.compile('netmanage/network_service.py', doraise=True)"
python3 -c "import py_compile; py_compile.compile('netmanage/ifconfig.py', doraise=True)"

# 2. Import check
python3 -c "from netmanage.ifconfig import Interface; print('ifconfig OK')"
python3 -c "from netmanage.network_service import NetworkService; print('network_service OK')"

# 3. Run the app in test mode with dummy interface
sudo ip link add test-dummy0 type dummy
sudo ip link set test-dummy0 up
sudo python3 __main__.py &
sleep 3
sudo kill %1 2>/dev/null
sudo ip link delete test-dummy0

# 4. Check for any errors in output
```

---

## Rollback Instructions

If any fix breaks functionality:

### Per-file rollback with git:
```bash
# Restore a single file
git checkout -- netui.py

# Restore multiple files
git checkout -- netui.py netmanage/ifconfig.py netmanage/network_service.py

# See what changed
git diff
```

### If you haven't committed yet:
```bash
# Restore everything to last commit
git restore .
```

### Create a branch for safe experimentation:
```bash
git checkout -b repair-plan
# ... apply fixes ...
# If something breaks, switching back is instant:
git checkout main
```

---

*End of Repair Plan*