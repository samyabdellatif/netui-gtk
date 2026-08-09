"""
Network interface model with proper validation and error handling.
Provides a clean abstraction over Linux network interfaces.
"""
import fcntl
import os
import re
import socket
import struct
import ctypes
import array
import math
import logging
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

# ioctl constants (from linux/sockios.h)
SIOCGIFCONF = 0x8912
SIOCGIFINDEX = 0x8933
SIOCGIFFLAGS = 0x8913
SIOCSIFFLAGS = 0x8914
SIOCGIFHWADDR = 0x8927
SIOCSIFHWADDR = 0x8924
SIOCGIFADDR = 0x8915
SIOCSIFADDR = 0x8916
SIOCGIFNETMASK = 0x891B
SIOCSIFNETMASK = 0x891C
SIOCETHTOOL = 0x8946

# From linux/if.h
IFF_UP = 0x1

# From linux/socket.h
AF_UNIX = 1
AF_INET = 2

# From linux/ethtool.h
ETHTOOL_GSET = 0x00000001
ETHTOOL_SSET = 0x00000002
ETHTOOL_GLINK = 0x0000000a
ETHTOOL_SPAUSEPARAM = 0x00000013

ADVERTISED_10baseT_Half = (1 << 0)
ADVERTISED_10baseT_Full = (1 << 1)
ADVERTISED_100baseT_Half = (1 << 2)
ADVERTISED_100baseT_Full = (1 << 3)
ADVERTISED_1000baseT_Half = (1 << 4)
ADVERTISED_1000baseT_Full = (1 << 5)
ADVERTISED_Autoneg = (1 << 6)

SYSFS_NET_PATH = "/sys/class/net"
PROCFS_NET_PATH = "/proc/net/dev"
SIZE_OF_IFREQ = 40

# Interface name validation: Linux allows up to 15 chars, alphanumeric + _-.
IFACE_NAME_RE = re.compile(r'^[a-zA-Z0-9_.-]{1,15}$')


class InterfaceError(Exception):
    """Base exception for interface operations."""
    pass


class InterfaceNotFoundError(InterfaceError):
    """Raised when an interface does not exist."""
    pass


class InvalidInterfaceNameError(InterfaceError):
    """Raised when an interface name is invalid."""
    pass


class InterfacePermissionError(InterfaceError):
    """Raised when an operation requires elevated privileges."""
    pass


class _SocketManager:
    """
    Thread-safe socket manager for ioctl operations.
    Uses a datagram socket (correct type for network interface ioctls).
    """

    _instance = None
    _lock = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._sock = None
            cls._instance._lock = __import__('threading').Lock()
        return cls._instance

    def get_fd(self) -> int:
        """Get the socket file descriptor, creating it if needed."""
        with self._lock:
            if self._sock is None:
                try:
                    # Use SOCK_DGRAM for network interface ioctls (correct type)
                    self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                except OSError as e:
                    raise InterfaceError(f"Failed to create network socket: {e}")
            return self._sock.fileno()

    def close(self) -> None:
        """Close the socket."""
        with self._lock:
            if self._sock is not None:
                try:
                    self._sock.close()
                except OSError:
                    pass
                self._sock = None


def _get_socket_fd() -> int:
    """Get the shared socket file descriptor."""
    return _SocketManager().get_fd()


def _validate_interface_name(name: str) -> None:
    """Validate an interface name."""
    if not name or not IFACE_NAME_RE.match(name):
        raise InvalidInterfaceNameError(f"Invalid interface name: {name!r}")


def _validate_mac(mac: str) -> None:
    """Validate a MAC address format."""
    if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
        raise ValueError(f"Invalid MAC address format: {mac}")


def _validate_ipv4(ip: str) -> None:
    """Validate an IPv4 address."""
    try:
        socket.inet_aton(ip)
    except OSError:
        raise ValueError(f"Invalid IPv4 address: {ip}")


def _validate_netmask(netmask: int) -> None:
    """Validate a netmask prefix length (0-32)."""
    if not 0 <= netmask <= 32:
        raise ValueError(f"Invalid netmask prefix: {netmask} (must be 0-32)")


class Interface:
    """Represents a Linux network interface."""

    def __init__(self, name: str):
        _validate_interface_name(name)
        self.name = name

    def __repr__(self) -> str:
        return f"<Interface {self.name}>"

    def __eq__(self, other) -> bool:
        return isinstance(other, Interface) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    # --- Status operations ---

    def is_up(self) -> bool:
        """Return True if the interface is up."""
        sk = _get_socket_fd()
        ifreq = struct.pack('16sh', self.name.encode('utf-8'), 0)
        try:
            flags = struct.unpack('16sh', fcntl.ioctl(sk, SIOCGIFFLAGS, ifreq))[1]
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")
        return bool(flags & IFF_UP)

    def up(self) -> None:
        """Bring the interface up."""
        sk = _get_socket_fd()
        ifreq = struct.pack('16sh', self.name.encode('utf-8'), 0)
        try:
            flags = struct.unpack('16sh', fcntl.ioctl(sk, SIOCGIFFLAGS, ifreq))[1]
            flags |= IFF_UP
            ifreq = struct.pack('16sh', self.name.encode('utf-8'), flags)
            fcntl.ioctl(sk, SIOCSIFFLAGS, ifreq)
        except PermissionError:
            raise InterfacePermissionError(
                f"Permission denied bringing up {self.name}. Run as root."
            )
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")

    def down(self) -> None:
        """Bring the interface down."""
        sk = _get_socket_fd()
        ifreq = struct.pack('16sh', self.name.encode('utf-8'), 0)
        try:
            flags = struct.unpack('16sh', fcntl.ioctl(sk, SIOCGIFFLAGS, ifreq))[1]
            flags &= ~IFF_UP
            ifreq = struct.pack('16sh', self.name.encode('utf-8'), flags)
            fcntl.ioctl(sk, SIOCSIFFLAGS, ifreq)
        except PermissionError:
            raise InterfacePermissionError(
                f"Permission denied bringing down {self.name}. Run as root."
            )
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")

    # --- Address operations ---

    def get_mac(self) -> Optional[str]:
        """Get the MAC address, or None if unavailable."""
        sk = _get_socket_fd()
        ifreq = struct.pack('16sH14s', self.name.encode('utf-8'), AF_UNIX, b'\x00' * 14)
        try:
            res = fcntl.ioctl(sk, SIOCGIFHWADDR, ifreq)
            address = struct.unpack('16sH14s', res)[2]
            mac = struct.unpack('6B8x', address)
            return ":".join(['%02X' % i for i in mac])
        except OSError:
            return None

    def set_mac(self, new_mac: str) -> None:
        """Set the MAC address. Interface must be down."""
        _validate_mac(new_mac)
        sk = _get_socket_fd()
        macbytes = [int(i, 16) for i in new_mac.split(':')]
        ifreq = struct.pack('16sH6B8x', self.name.encode('utf-8'), AF_UNIX, *macbytes)
        try:
            fcntl.ioctl(sk, SIOCSIFHWADDR, ifreq)
        except PermissionError:
            raise InterfacePermissionError(
                f"Permission denied setting MAC on {self.name}. Run as root."
            )
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")

    def get_ip(self) -> Optional[str]:
        """Get the IPv4 address, or None if not assigned."""
        sk = _get_socket_fd()
        ifreq = struct.pack('16sH14s', self.name.encode('utf-8'), AF_INET, b'\x00' * 14)
        try:
            res = fcntl.ioctl(sk, SIOCGIFADDR, ifreq)
            ip = struct.unpack('16sH2x4s8x', res)[2]
            return socket.inet_ntoa(ip)
        except OSError:
            return None

    def set_ip(self, new_ip: str) -> None:
        """Set the IPv4 address."""
        _validate_ipv4(new_ip)
        sk = _get_socket_fd()
        ipbytes = socket.inet_aton(new_ip)
        ifreq = struct.pack('16sH2s4s8s', self.name.encode('utf-8'), AF_INET, b'\x00' * 2, ipbytes, b'\x00' * 8)
        try:
            fcntl.ioctl(sk, SIOCSIFADDR, ifreq)
        except PermissionError:
            raise InterfacePermissionError(
                f"Permission denied setting IP on {self.name}. Run as root."
            )
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")

    def get_netmask(self) -> Optional[int]:
        """Get the netmask prefix length (0-32), or None if unavailable."""
        sk = _get_socket_fd()
        ifreq = struct.pack('16sH14s', self.name.encode('utf-8'), AF_INET, b'\x00' * 14)
        try:
            res = fcntl.ioctl(sk, SIOCGIFNETMASK, ifreq)
            netmask = socket.ntohl(struct.unpack('16sH2xI8x', res)[2])
            if netmask == 0:
                return 0
            # Count leading 1s
            prefix = 0
            for i in range(31, -1, -1):
                if netmask & (1 << i):
                    prefix += 1
                else:
                    break
            return prefix
        except OSError:
            return None

    def set_netmask(self, netmask: int) -> None:
        """Set the netmask prefix length (0-32)."""
        _validate_netmask(netmask)
        sk = _get_socket_fd()
        if netmask == 0:
            nmbytes = 0
        else:
            nmbytes = socket.htonl(((1 << netmask) - 1) << (32 - netmask))
        ifreq = struct.pack('16sH2si8s', self.name.encode('utf-8'), AF_INET, b'\x00' * 2, nmbytes, b'\x00' * 8)
        try:
            fcntl.ioctl(sk, SIOCSIFNETMASK, ifreq)
        except PermissionError:
            raise InterfacePermissionError(
                f"Permission denied setting netmask on {self.name}. Run as root."
            )
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")

    def get_index(self) -> int:
        """Get the interface index."""
        sk = _get_socket_fd()
        ifreq = struct.pack('16si', self.name.encode('utf-8'), 0)
        try:
            res = fcntl.ioctl(sk, SIOCGIFINDEX, ifreq)
            return struct.unpack("16si", res)[1]
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")

    # --- Link operations ---

    def get_link_info(self) -> Tuple[int, Optional[bool], Optional[bool], bool]:
        """
        Get link information.
        Returns: (speed_mbps, duplex, autoneg, link_up)
        """
        sk = _get_socket_fd()
        # Get link params
        ecmd = array.array('B', struct.pack('I39s', ETHTOOL_GSET, b'\x00' * 39))
        ifreq = struct.pack('16sP', self.name.encode('utf-8'), ecmd.buffer_info()[0])
        try:
            fcntl.ioctl(sk, SIOCETHTOOL, ifreq)
            res = ecmd.tobytes()
            speed, duplex, auto = struct.unpack('12xHB3xB24x', res)
        except OSError:
            speed, duplex, auto = 65535, 255, 255

        # Get link up/down state
        ecmd = array.array('B', struct.pack('2I', ETHTOOL_GLINK, 0))
        ifreq = struct.pack('16sP', self.name.encode('utf-8'), ecmd.buffer_info()[0])
        try:
            fcntl.ioctl(sk, SIOCETHTOOL, ifreq)
            res = ecmd.tobytes()
            up = bool(struct.unpack('4xI', res)[0])
        except OSError:
            up = False

        if speed == 65535:
            speed = 0
        # duplex: 0=half, 1=full, 255=unknown
        if duplex == 255:
            duplex = None
        else:
            duplex = bool(duplex)
        # auto: 0=off, 1=on, 255=unknown
        if auto == 255:
            auto = None
        else:
            auto = bool(auto)
        return speed, duplex, auto, up

    def set_link_mode(self, speed: int, duplex: bool) -> None:
        """Set link speed and duplex mode."""
        if speed < 0:
            raise ValueError(f"Invalid speed: {speed}")
        sk = _get_socket_fd()
        ecmd = array.array('B', struct.pack('I39s', ETHTOOL_GSET, b'\x00' * 39))
        ifreq = struct.pack('16sP', self.name.encode('utf-8'), ecmd.buffer_info()[0])
        try:
            fcntl.ioctl(sk, SIOCETHTOOL, ifreq)
            ecmd[0:4] = array.array('B', struct.pack('I', ETHTOOL_SSET))
            ecmd[12:14] = array.array('B', struct.pack('H', speed))
            ecmd[14] = 1 if duplex else 0
            ecmd[18] = 0  # Autonegotiation off
            fcntl.ioctl(sk, SIOCETHTOOL, ifreq)
        except PermissionError:
            raise InterfacePermissionError(
                f"Permission denied setting link mode on {self.name}. Run as root."
            )
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")

    def set_link_auto(self, ten: bool = True, hundred: bool = True, thousand: bool = True) -> None:
        """Enable autonegotiation with specified speeds."""
        sk = _get_socket_fd()
        ecmd = array.array('B', struct.pack('I39s', ETHTOOL_GSET, b'\x00' * 39))
        ifreq = struct.pack('16sP', self.name.encode('utf-8'), ecmd.buffer_info()[0])
        try:
            fcntl.ioctl(sk, SIOCETHTOOL, ifreq)
            ecmd[0:4] = array.array('B', struct.pack('I', ETHTOOL_SSET))

            advertise = 0
            if ten:
                advertise |= ADVERTISED_10baseT_Half | ADVERTISED_10baseT_Full
            if hundred:
                advertise |= ADVERTISED_100baseT_Half | ADVERTISED_100baseT_Full
            if thousand:
                advertise |= ADVERTISED_1000baseT_Half | ADVERTISED_1000baseT_Full

            # Preserve existing supported modes that we want to advertise
            supported = struct.unpack('I', ecmd[4:8].tobytes())[0]
            newmode = supported & advertise
            ecmd[8:12] = array.array('B', struct.pack('I', newmode))
            ecmd[18] = 1  # Autonegotiation on
            fcntl.ioctl(sk, SIOCETHTOOL, ifreq)
        except PermissionError:
            raise InterfacePermissionError(
                f"Permission denied setting autoneg on {self.name}. Run as root."
            )
        except OSError as e:
            raise InterfaceNotFoundError(f"Interface {self.name} not found: {e}")

    # --- Statistics ---

    def get_stats(self) -> Optional[Dict[str, int]]:
        """Get interface statistics from /proc/net/dev."""
        try:
            with open(PROCFS_NET_PATH, 'r') as fp:
                # Skip headers
                fp.readline()
                fp.readline()
                for line in fp:
                    if ':' not in line:
                        continue
                    name, stats_str = line.split(':', 1)
                    if name.strip() != self.name:
                        continue
                    stats = [int(a) for a in stats_str.strip().split()]
                    titles = [
                        "rx_bytes", "rx_packets", "rx_errs", "rx_drop", "rx_fifo",
                        "rx_frame", "rx_compressed", "rx_multicast", "tx_bytes",
                        "tx_packets", "tx_errs", "tx_drop", "tx_fifo", "tx_colls",
                        "tx_carrier", "tx_compressed"
                    ]
                    return dict(zip(titles, stats))
        except (FileNotFoundError, PermissionError, ValueError) as e:
            logger.warning(f"Error reading stats for {self.name}: {e}")
        return None

    # --- Properties ---

    @property
    def index(self) -> int:
        return self.get_index()

    @property
    def mac(self) -> Optional[str]:
        return self.get_mac()

    @mac.setter
    def mac(self, value: str) -> None:
        self.set_mac(value)

    @property
    def ip(self) -> Optional[str]:
        return self.get_ip()

    @ip.setter
    def ip(self, value: str) -> None:
        self.set_ip(value)

    @property
    def netmask(self) -> Optional[int]:
        return self.get_netmask()

    @netmask.setter
    def netmask(self, value: int) -> None:
        self.set_netmask(value)


def iterifs(physical: bool = True):
    """
    Iterate over all interfaces.
    If physical is True, exclude virtual interfaces (lo, etc).
    """
    if not os.path.isdir(SYSFS_NET_PATH):
        raise InterfaceError(f"Path {SYSFS_NET_PATH} not found. This module requires sysfs.")

    net_files = os.listdir(SYSFS_NET_PATH)
    interfaces = set()
    virtual = set()
    for d in net_files:
        path = os.path.join(SYSFS_NET_PATH, d)
        if not os.path.isdir(path):
            continue
        if not os.path.exists(os.path.join(path, "device")):
            virtual.add(d)
        interfaces.add(d)

    # Some virtual interfaces don't show up in sysfs (e.g., subinterfaces eth0:1)
    if not physical:
        sk = _get_socket_fd()
        ifreqs = array.array("B", b"\x00" * SIZE_OF_IFREQ * 30)
        buf_addr, _buf_len = ifreqs.buffer_info()
        ifconf = struct.pack("iP", SIZE_OF_IFREQ * 30, buf_addr)
        try:
            ifconf_res = fcntl.ioctl(sk, SIOCGIFCONF, ifconf)
            ifreqs_len, _ = struct.unpack("iP", ifconf_res)
            if ifreqs_len % SIZE_OF_IFREQ == 0:
                res = ifreqs.tobytes()
                for i in range(0, ifreqs_len, SIZE_OF_IFREQ):
                    d = res[i:i + 16].strip(b'\0').decode('utf-8', errors='replace')
                    if d:
                        interfaces.add(d)
        except OSError as e:
            logger.warning(f"Error enumerating subinterfaces: {e}")

    results = interfaces - virtual if physical else interfaces
    for d in sorted(results):
        try:
            yield Interface(d)
        except InvalidInterfaceNameError:
            logger.warning(f"Skipping invalid interface name: {d}")


def list_ifs(physical: bool = True) -> List[Interface]:
    """Return a list of interfaces."""
    return list(iterifs(physical))


def findif(name: str) -> Optional[Interface]:
    """Find an interface by name (searches both physical and virtual)."""
    for iface in iterifs(physical=False):
        if name == iface.name:
            return iface
    return None


def shutdown() -> None:
    """Close the shared socket."""
    _SocketManager().close()