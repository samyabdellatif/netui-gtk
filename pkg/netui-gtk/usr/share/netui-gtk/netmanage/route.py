"""
Routing table utilities.
Reads /proc/net/route to find default interface and gateway.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

ROUTE_FILE = "/proc/net/route"


def _read_route_file() -> list:
    """Read and parse the route file, returning list of (iface, dest, gw) tuples."""
    routes = []
    try:
        with open(ROUTE_FILE, 'r') as f:
            # Skip header line
            next(f, None)
            for line in f:
                parts = line.split()
                if len(parts) < 3:
                    continue
                routes.append((parts[0], parts[1], parts[2]))
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"Error reading {ROUTE_FILE}: {e}")
    return routes


def get_default_if() -> Optional[str]:
    """Return the default interface name, or None if no default route exists."""
    for iface, dest, _ in _read_route_file():
        try:
            if int(dest, 16) == 0:
                return iface
        except ValueError:
            continue
    return None


def get_default_gw() -> Optional[str]:
    """Return the default gateway IP, or None if no default route exists."""
    for _, dest, gw_hex in _read_route_file():
        try:
            if int(dest, 16) == 0:
                # Convert hex gateway to dotted decimal
                octets = []
                for i in range(8, 1, -2):
                    octet = int(gw_hex[i - 2:i], 16)
                    octets.append(str(octet))
                return ".".join(octets)
        except (ValueError, IndexError):
            continue
    return None