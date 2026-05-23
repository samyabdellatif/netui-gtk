"""
Advanced network interface management features.
Provides MTU configuration, statistics monitoring, and link speed information.
"""
import subprocess
import os
import logging

logger = logging.getLogger(__name__)


def get_mtu(interface_name):
    """Get MTU (Maximum Transmission Unit) for interface."""
    try:
        with open(f"/sys/class/net/{interface_name}/mtu", "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error getting MTU for {interface_name}: {e}")
        return None


def set_mtu(interface_name, mtu_value):
    """Set MTU for interface."""
    try:
        mtu = int(mtu_value)
        if mtu < 68 or mtu > 65535:
            raise ValueError(f"MTU must be between 68 and 65535, got {mtu}")
        
        subprocess.run(
            ["ip", "link", "set", interface_name, "mtu", str(mtu)],
            check=True,
            timeout=10
        )
        logger.info(f"Set MTU for {interface_name} to {mtu}")
        return True
    except (ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.error(f"Error setting MTU for {interface_name}: {e}")
        raise


def get_interface_stats(interface_name):
    """Get network statistics for interface."""
    stats_path = f"/sys/class/net/{interface_name}/statistics"
    stats = {}
    
    stat_files = {
        'rx_bytes': 'Received Bytes',
        'tx_bytes': 'Transmitted Bytes',
        'rx_packets': 'Received Packets',
        'tx_packets': 'Transmitted Packets',
        'rx_errors': 'RX Errors',
        'tx_errors': 'TX Errors',
        'rx_dropped': 'RX Dropped',
        'tx_dropped': 'TX Dropped',
        'collisions': 'Collisions',
    }
    
    for file, label in stat_files.items():
        try:
            with open(f"{stats_path}/{file}", "r") as f:
                stats[label] = int(f.read().strip())
        except (FileNotFoundError, ValueError):
            stats[label] = 0
    
    return stats


def format_bytes(bytes_val):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


def get_link_speed(interface_name):
    """Get link speed from sysfs."""
    try:
        with open(f"/sys/class/net/{interface_name}/speed", "r") as f:
            speed = int(f.read().strip())
            if speed > 0:
                return f"{speed} Mbps"
            return "Unknown"
    except (FileNotFoundError, ValueError):
        return "Unknown"


def get_carrier_state(interface_name):
    """Check if interface has carrier (cable connected)."""
    try:
        with open(f"/sys/class/net/{interface_name}/carrier", "r") as f:
            return int(f.read().strip()) == 1
    except (FileNotFoundError, ValueError):
        return False


def get_operstate(interface_name):
    """Get operational state of interface."""
    try:
        with open(f"/sys/class/net/{interface_name}/operstate", "r") as f:
            return f.read().strip().upper()
    except (FileNotFoundError, ValueError):
        return "UNKNOWN"


def get_driver_info(interface_name):
    """Get driver information for interface."""
    info = {}
    try:
        driver_path = f"/sys/class/net/{interface_name}/device/driver"
        if os.path.exists(driver_path):
            driver = os.path.basename(os.readlink(driver_path))
            info['driver'] = driver
        
        # Try to get driver version
        modalias_path = f"/sys/class/net/{interface_name}/device/modalias"
        if os.path.exists(modalias_path):
            with open(modalias_path, "r") as f:
                info['modalias'] = f.read().strip()
    except (FileNotFoundError, OSError):
        pass
    
    return info


def set_promiscuous_mode(interface_name, enable=True):
    """Enable or disable promiscuous mode."""
    try:
        if enable:
            subprocess.run(
                ["ip", "link", "set", interface_name, "promisc", "on"],
                check=True,
                timeout=10
            )
            logger.info(f"Enabled promiscuous mode for {interface_name}")
        else:
            subprocess.run(
                ["ip", "link", "set", interface_name, "promisc", "off"],
                check=True,
                timeout=10
            )
            logger.info(f"Disabled promiscuous mode for {interface_name}")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.error(f"Error setting promiscuous mode for {interface_name}: {e}")
        raise


def get_promiscuous_mode(interface_name):
    """Check if interface is in promiscuous mode."""
    try:
        result = subprocess.run(
            ["ip", "link", "show", interface_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "PROMISC" in result.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def clone_mac_address(interface_name, new_mac):
    """Set a custom MAC address (MAC cloning)."""
    try:
        # Validate MAC address format
        import re
        if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', new_mac):
            raise ValueError(f"Invalid MAC address format: {new_mac}")
        
        # Interface must be down to change MAC
        subprocess.run(
            ["ip", "link", "set", interface_name, "down"],
            check=True,
            timeout=10
        )
        
        subprocess.run(
            ["ip", "link", "set", interface_name, "address", new_mac],
            check=True,
            timeout=10
        )
        
        subprocess.run(
            ["ip", "link", "set", interface_name, "up"],
            check=True,
            timeout=10
        )
        
        logger.info(f"Set MAC address for {interface_name} to {new_mac}")
        return True
    except (ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.error(f"Error setting MAC address for {interface_name}: {e}")
        raise
