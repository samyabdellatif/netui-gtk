"""
Network service management module.
Provides unified interface for managing network interfaces through different backends:
- NetworkManager (nmcli)
- systemd-networkd
- Manual (direct ip commands + DHCP clients)
"""
import subprocess
import logging
import os
import shutil
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Backend identifiers
BACKEND_NETWORKMANAGER = 'networkmanager'
BACKEND_SYSTEMD_NETWORKD = 'systemd-networkd'
BACKEND_NETCTL = 'netctl'
BACKEND_WPA_SUPPLICANT = 'wpa_supplicant'
BACKEND_DHCPCD = 'dhcpcd'
BACKEND_DHCLIENT = 'dhclient'
BACKEND_WICD = 'wicd'
BACKEND_MANUAL = 'manual'

# All known network managers (for system detection)
ALL_MANAGERS = (
    BACKEND_NETWORKMANAGER,
    BACKEND_SYSTEMD_NETWORKD,
    BACKEND_NETCTL,
    BACKEND_WPA_SUPPLICANT,
    BACKEND_DHCPCD,
    BACKEND_DHCLIENT,
    BACKEND_WICD,
    BACKEND_MANUAL,
)

# Human-readable labels
MANAGER_LABELS = {
    BACKEND_NETWORKMANAGER: 'NetworkManager',
    BACKEND_SYSTEMD_NETWORKD: 'systemd-networkd',
    BACKEND_NETCTL: 'netctl',
    BACKEND_WPA_SUPPLICANT: 'wpa_supplicant',
    BACKEND_DHCPCD: 'dhcpcd',
    BACKEND_DHCLIENT: 'dhclient',
    BACKEND_WICD: 'wicd',
    BACKEND_MANUAL: 'Manual',
}


class NetworkServiceError(Exception):
    """Base exception for network service operations."""
    pass


class BackendNotFoundError(NetworkServiceError):
    """Raised when a required backend tool is not available."""
    pass


class CommandTimeoutError(NetworkServiceError):
    """Raised when a subprocess times out."""
    pass


def _netmask_to_cidr(netmask: str) -> int:
    """Convert netmask to CIDR notation (e.g., 255.255.255.0 -> 24)."""
    try:
        return sum(bin(int(x)).count('1') for x in netmask.split('.'))
    except (ValueError, AttributeError):
        return 24  # Default to /24


def _run_command(cmd: list, timeout: int = 10, check: bool = False) -> subprocess.CompletedProcess:
    """
    Run a subprocess command safely.
    Raises CommandTimeoutError on timeout.
    """
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check
        )
    except subprocess.TimeoutExpired:
        raise CommandTimeoutError(f"Command timed out: {' '.join(cmd)}")
    except FileNotFoundError:
        raise BackendNotFoundError(f"Command not found: {cmd[0]}")


class NetworkService:
    """Unified network service manager."""

    @staticmethod
    def detect_interface_manager(interface_name: str) -> str:
        """
        Detect which service manages an interface.
        Returns: 'networkmanager', 'systemd-networkd', 'netctl', 'wpa_supplicant',
                 'dhcpcd', 'dhclient', 'wicd', or 'manual'
        """
        # Check NetworkManager
        try:
            result = _run_command(['nmcli', 'device', 'status'], timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if interface_name in line:
                        line_lower = line.lower()
                        if 'unmanaged' in line_lower:
                            # Fall through to check other managers
                            break
                        elif 'connected' in line_lower or 'disconnected' in line_lower:
                            return BACKEND_NETWORKMANAGER
        except (CommandTimeoutError, BackendNotFoundError):
            pass

        # Check systemd-networkd
        try:
            result = _run_command(['networkctl', 'status', interface_name], timeout=5)
            if result.returncode == 0:
                output = result.stdout.lower()
                if 'state:' in output and any(
                    state in output for state in ['routable', 'configured', 'configuring']
                ):
                    return BACKEND_SYSTEMD_NETWORKD
        except (CommandTimeoutError, BackendNotFoundError):
            pass

        # Check netctl (Arch Linux)
        try:
            result = _run_command(['netctl', 'list'], timeout=5)
            if result.returncode == 0 and interface_name in result.stdout:
                # Check if a profile is active for this interface
                active_result = _run_command(['netctl', 'is-active', interface_name], timeout=5)
                if 'active' in active_result.stdout.lower():
                    return BACKEND_NETCTL
        except (CommandTimeoutError, BackendNotFoundError):
            pass

        # Check wpa_supplicant (check if process running on this interface)
        try:
            result = subprocess.run(
                ['pgrep', '-af', f'wpa_supplicant.*{interface_name}'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return BACKEND_WPA_SUPPLICANT
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Check if interface has an active dhcpcd lease
        if shutil.which('dhcpcd'):
            try:
                result = subprocess.run(
                    ['dhcpcd', '--dumplease', interface_name],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    return BACKEND_DHCPCD
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # Check if interface has an active dhclient lease
        if shutil.which('dhclient'):
            # dhclient doesn't provide a simple check, but we can look at leases file
            lease_files = [
                f'/var/lib/dhcp/dhclient.{interface_name}.leases',
                f'/var/lib/dhcpcd/dhclient.{interface_name}.leases',
                f'/var/lib/dhcp/dhclient-{interface_name}.leases',
            ]
            for lease_file in lease_files:
                if os.path.exists(lease_file):
                    try:
                        with open(lease_file, 'r') as f:
                            content = f.read()
                        if 'lease' in content and 'binding state active' in content:
                            return BACKEND_DHCLIENT
                    except (FileNotFoundError, PermissionError):
                        pass

        # Check wicd
        try:
            result = _run_command(['wicd-cli', '--wired', '--list-networks'], timeout=5)
            if result.returncode == 0 and interface_name in result.stdout:
                return BACKEND_WICD
        except (CommandTimeoutError, BackendNotFoundError):
            pass

        # Check for systemd-networkd .network files for this interface
        try:
            if os.path.isdir('/etc/systemd/network'):
                for f in os.listdir('/etc/systemd/network'):
                    if f.endswith('.network'):
                        try:
                            with open(os.path.join('/etc/systemd/network', f), 'r') as fh:
                                content = fh.read()
                            if interface_name in content:
                                return BACKEND_SYSTEMD_NETWORKD
                        except (FileNotFoundError, PermissionError):
                            pass
        except (FileNotFoundError, PermissionError):
            pass

        return BACKEND_MANUAL

    @staticmethod
    def detect_installed_managers() -> list:
        """
        Detect all network manager tools installed and running on the system.
        Returns: list of dicts with {id, name, installed, running, description}
        """
        managers = []

        # Check each known manager
        checks = [
            (
                BACKEND_NETWORKMANAGER,
                'NetworkManager',
                'NetworkManager (nmcli)',
                'Full-featured network manager with connection profiles',
                ['nmcli', 'NetworkManager'],
            ),
            (
                BACKEND_SYSTEMD_NETWORKD,
                'systemd-networkd',
                'systemd-networkd',
                "Systemd's built-in network configuration daemon",
                ['networkctl', 'systemd-networkd'],
            ),
            (
                BACKEND_NETCTL,
                'netctl',
                'netctl',
                'Profile-based network manager (Arch Linux)',
                ['netctl'],
            ),
            (
                BACKEND_WPA_SUPPLICANT,
                'wpa_supplicant',
                'wpa_supplicant',
                'Wi-Fi Protected Access authentication (WPA/WPA2)',
                ['wpa_supplicant'],
            ),
            (
                BACKEND_DHCPCD,
                'dhcpcd',
                'dhcpcd',
                'DHCP client daemon with robust lease management',
                ['dhcpcd'],
            ),
            (
                BACKEND_DHCLIENT,
                'dhclient',
                'dhclient (ISC DHCP)',
                'Classic ISC DHCP client',
                ['dhclient'],
            ),
            (
                BACKEND_WICD,
                'wicd',
                'Wicd',
                'Lightweight network connection manager',
                ['wicd-cli', 'wicd'],
            ),
        ]

        for manager_id, name, display_name, description, binaries in checks:
            # Check if any of the binaries are installed
            installed = any(shutil.which(bin) for bin in binaries)

            # Check if the service is running
            running = False
            service_name = None
            for bin in binaries:
                if bin in ('nmcli', 'networkctl', 'netctl', 'wpa_supplicant', 'dhcpcd', 'dhclient', 'wicd-cli', 'wicd'):
                    service_name = bin
                    break

            if service_name:
                # Check common service names
                service_names = []
                if manager_id == BACKEND_NETWORKMANAGER:
                    service_names = ['NetworkManager']
                elif manager_id == BACKEND_SYSTEMD_NETWORKD:
                    service_names = ['systemd-networkd']
                elif manager_id == BACKEND_NETCTL:
                    service_names = ['netctl']
                elif manager_id == BACKEND_WPA_SUPPLICANT:
                    service_names = ['wpa_supplicant']
                elif manager_id == BACKEND_DHCPCD:
                    service_names = ['dhcpcd']
                elif manager_id == BACKEND_DHCLIENT:
                    service_names = ['dhclient']
                elif manager_id == BACKEND_WICD:
                    service_names = ['wicd']

                for svc in service_names:
                    try:
                        result = subprocess.run(
                            ['systemctl', 'is-active', svc],
                            capture_output=True, text=True, timeout=3
                        )
                        if result.returncode == 0 and result.stdout.strip() == 'active':
                            running = True
                            break
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        pass

            # Also check for processes
            if not running:
                try:
                    result = subprocess.run(
                        ['pgrep', '-x', service_name] if service_name else ['true'],
                        capture_output=True, timeout=3
                    )
                    if result.returncode == 0:
                        running = True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

            managers.append({
                'id': manager_id,
                'name': name,
                'display_name': display_name,
                'installed': installed,
                'running': running,
                'description': description,
            })

        return managers

    @staticmethod
    def get_manager_status_text(managers: list) -> str:
        """
        Generate human-readable summary of network managers.
        """
        if not managers:
            return "No network managers detected"

        lines = []
        for mgr in managers:
            status = "running" if mgr['running'] else ("installed" if mgr['installed'] else "not found")
            lines.append(f"  {mgr['display_name']}: {status}")

        return "\n".join(lines)


class NetworkManagerBackend:
    """NetworkManager operations using nmcli."""

    @staticmethod
    def connect_dhcp(interface_name: str) -> Tuple[bool, str]:
        """Connect interface using DHCP via NetworkManager."""
        try:
            # Ensure interface is managed
            _run_command(
                ['nmcli', 'device', 'set', interface_name, 'managed', 'yes'],
                timeout=10
            )

            # Connect using DHCP
            result = _run_command(
                ['nmcli', 'device', 'connect', interface_name],
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"NetworkManager: Connected {interface_name} via DHCP")
                return True, "Connected successfully via NetworkManager"
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"NetworkManager: Failed to connect {interface_name}: {error_msg}")
                return False, error_msg

        except (CommandTimeoutError, BackendNotFoundError) as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"NetworkManager error: {e}")
            return False, str(e)

    @staticmethod
    def disconnect(interface_name: str) -> Tuple[bool, str]:
        """Disconnect interface via NetworkManager."""
        try:
            result = _run_command(
                ['nmcli', 'device', 'disconnect', interface_name],
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"NetworkManager: Disconnected {interface_name}")
                return True, "Disconnected successfully"
            else:
                return False, result.stderr or result.stdout

        except (CommandTimeoutError, BackendNotFoundError) as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"NetworkManager disconnect error: {e}")
            return False, str(e)

    @staticmethod
    def set_manual_ip(interface_name: str, ip_address: str, netmask: str,
                      gateway: Optional[str] = None,
                      dns_servers: Optional[str] = None) -> Tuple[bool, str]:
        """Configure static IP via NetworkManager."""
        try:
            conn_name = f"netui-{interface_name}"

            # Delete existing connection if exists
            _run_command(['nmcli', 'connection', 'delete', conn_name], timeout=5)

            # Calculate CIDR from netmask
            cidr = _netmask_to_cidr(netmask)
            ip_with_cidr = f"{ip_address}/{cidr}"

            # Build nmcli command
            cmd = [
                'nmcli', 'connection', 'add',
                'type', 'ethernet',
                'con-name', conn_name,
                'ifname', interface_name,
                'ipv4.method', 'manual',
                'ipv4.addresses', ip_with_cidr
            ]

            if gateway:
                cmd.extend(['ipv4.gateway', gateway])

            if dns_servers:
                cmd.extend(['ipv4.dns', dns_servers])

            result = _run_command(cmd, timeout=10)

            if result.returncode == 0:
                # Activate the connection
                activate_result = _run_command(
                    ['nmcli', 'connection', 'up', conn_name],
                    timeout=15
                )

                if activate_result.returncode == 0:
                    logger.info(f"NetworkManager: Set static IP for {interface_name}")
                    return True, "Static IP configured successfully"
                else:
                    return False, activate_result.stderr or activate_result.stdout
            else:
                return False, result.stderr or result.stdout

        except (CommandTimeoutError, BackendNotFoundError) as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"NetworkManager static IP error: {e}")
            return False, str(e)


class SystemdNetworkdBackend:
    """systemd-networkd operations."""

    @staticmethod
    def connect_dhcp(interface_name: str) -> Tuple[bool, str]:
        """Connect interface using DHCP via systemd-networkd."""
        try:
            network_file = f"/etc/systemd/network/50-{interface_name}.network"

            network_config = f"""[Match]
Name={interface_name}

[Network]
DHCP=yes
"""

            # Write config file
            with open(network_file, 'w') as f:
                f.write(network_config)

            # Restart networkd
            _run_command(['systemctl', 'restart', 'systemd-networkd'], timeout=10)

            # Reconfigure interface
            _run_command(['networkctl', 'reconfigure', interface_name], timeout=10)

            logger.info(f"systemd-networkd: Configured {interface_name} for DHCP")
            return True, "Configured for DHCP via systemd-networkd"

        except PermissionError:
            return False, "Permission denied: Need root access"
        except (CommandTimeoutError, BackendNotFoundError) as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"systemd-networkd error: {e}")
            return False, str(e)

    @staticmethod
    def set_manual_ip(interface_name: str, ip_address: str, netmask: str,
                      gateway: Optional[str] = None,
                      dns_servers: Optional[str] = None) -> Tuple[bool, str]:
        """Configure static IP via systemd-networkd."""
        try:
            network_file = f"/etc/systemd/network/50-{interface_name}.network"

            cidr = _netmask_to_cidr(netmask)

            network_config = f"""[Match]
Name={interface_name}

[Network]
Address={ip_address}/{cidr}
"""

            if gateway:
                network_config += f"Gateway={gateway}\n"

            if dns_servers:
                for dns in dns_servers.split():
                    network_config += f"DNS={dns}\n"

            # Write config file
            with open(network_file, 'w') as f:
                f.write(network_config)

            # Restart networkd
            _run_command(['systemctl', 'restart', 'systemd-networkd'], timeout=10)

            # Reconfigure interface
            _run_command(['networkctl', 'reconfigure', interface_name], timeout=10)

            logger.info(f"systemd-networkd: Configured static IP for {interface_name}")
            return True, "Static IP configured via systemd-networkd"

        except PermissionError:
            return False, "Permission denied: Need root access"
        except (CommandTimeoutError, BackendNotFoundError) as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"systemd-networkd error: {e}")
            return False, str(e)


def connect_interface_dhcp(interface_name: str) -> Tuple[bool, str]:
    """
    Connect interface using DHCP with automatic backend detection.
    Returns: (success: bool, message: str)
    """
    manager = NetworkService.detect_interface_manager(interface_name)
    logger.info(f"Interface {interface_name} is managed by: {manager}")

    if manager == BACKEND_NETWORKMANAGER:
        return NetworkManagerBackend.connect_dhcp(interface_name)
    elif manager == BACKEND_SYSTEMD_NETWORKD:
        return SystemdNetworkdBackend.connect_dhcp(interface_name)
    else:
        # Use traditional DHCP client
        from netmanage.dhcpc import lease
        try:
            result = lease(interface_name)
            return True, f"Connected via DHCP client: {result}"
        except Exception as e:
            return False, str(e)


def disconnect_interface(interface_name: str) -> Tuple[bool, str]:
    """
    Disconnect interface with automatic backend detection.
    Releases DHCP lease and removes IP address.
    Returns: (success: bool, message: str)
    """
    manager = NetworkService.detect_interface_manager(interface_name)
    logger.info(f"Disconnecting {interface_name} (managed by {manager})")

    if manager == BACKEND_NETWORKMANAGER:
        return NetworkManagerBackend.disconnect(interface_name)
    else:
        # Manual disconnect - handle multiple network managers
        try:
            # Check for netctl (Arch Linux network profile manager)
            if shutil.which('netctl'):
                try:
                    # Stop netctl profile for this interface only
                    subprocess.run(
                        ['netctl', 'stop', interface_name],
                        capture_output=True, text=True, timeout=10
                    )
                    logger.info(f"Stopped netctl profile for {interface_name}")

                    # Kill wpa_supplicant for this specific interface only
                    # Use pkill with interface-specific pattern to avoid killing unrelated processes
                    wpa_file = f'/run/netctl/wpa_supplicant-{interface_name}.conf'
                    if os.path.exists(wpa_file):
                        # Kill only the wpa_supplicant process bound to this interface
                        subprocess.run(
                            ['pkill', '-f', f'wpa_supplicant.*{interface_name}'],
                            capture_output=True, timeout=5
                        )
                        logger.info(f"Stopped wpa_supplicant for {interface_name}")
                except Exception as e:
                    logger.debug(f"Error stopping netctl: {e}")

            # Try dhcpcd cleanly first
            if shutil.which('dhcpcd'):
                try:
                    subprocess.run(
                        ['dhcpcd', '-k', interface_name],
                        capture_output=True, timeout=5
                    )
                    logger.info(f"Sent kill signal to dhcpcd for {interface_name}")
                    time.sleep(0.5)
                except Exception as e:
                    logger.debug(f"Error stopping dhcpcd for {interface_name}: {e}")

            # Try dhclient as well
            if shutil.which('dhclient'):
                try:
                    subprocess.run(
                        ['dhclient', '-r', interface_name],
                        capture_output=True, timeout=5
                    )
                    logger.info(f"Released dhclient lease for {interface_name}")
                except Exception as e:
                    logger.debug(f"Error stopping dhclient for {interface_name}: {e}")

            # Flush all IP addresses from interface
            result = subprocess.run(
                ['ip', 'addr', 'flush', 'dev', interface_name],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                logger.info(f"Flushed IP addresses from {interface_name}")

            # Remove default route through this interface only
            try:
                subprocess.run(
                    ['ip', 'route', 'del', 'default', 'dev', interface_name],
                    capture_output=True, timeout=5
                )
            except Exception:
                pass  # Route might not exist

            # Wait for IP to be released
            time.sleep(1)

            # Check if interface still has IP
            check_result = subprocess.run(
                ['ip', 'addr', 'show', interface_name],
                capture_output=True, text=True, timeout=5
            )

            if 'inet ' in check_result.stdout:
                logger.warning(
                    f"Interface {interface_name} still has IP after disconnect"
                )
                return False, (
                    "Interface disconnected but IP may reappear "
                    "(managed by system service). "
                    "Try: sudo systemctl stop netctl"
                )
            else:
                logger.info(f"Successfully disconnected {interface_name}")
                return True, "Disconnected successfully"

        except Exception as e:
            logger.error(f"Error disconnecting {interface_name}: {e}")
            return False, str(e)


def set_manual_config(interface_name: str, ip_address: str, netmask: str,
                      gateway: Optional[str] = None,
                      dns_servers: Optional[str] = None) -> Tuple[Optional[bool], str]:
    """
    Configure static IP with automatic backend detection.
    Returns: (success: bool, message: str)
    """
    manager = NetworkService.detect_interface_manager(interface_name)
    logger.info(f"Configuring {interface_name} (managed by {manager}) with static IP")

    if manager == BACKEND_NETWORKMANAGER:
        return NetworkManagerBackend.set_manual_ip(
            interface_name, ip_address, netmask, gateway, dns_servers
        )
    elif manager == BACKEND_SYSTEMD_NETWORKD:
        return SystemdNetworkdBackend.set_manual_ip(
            interface_name, ip_address, netmask, gateway, dns_servers
        )
    else:
        # Manual configuration - return None to signal caller should handle it
        return None, "Using manual configuration"