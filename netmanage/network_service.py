"""
Network service management module for NetworkManager and systemd-networkd
Provides unified interface for managing network interfaces through different backends
"""

import subprocess
import logging

logger = logging.getLogger(__name__)


class NetworkService:
    """Unified network service manager"""
    
    @staticmethod
    def detect_interface_manager(interface_name):
        """
        Detect which service manages an interface.
        Returns: 'networkmanager', 'systemd-networkd', 'manual', or None
        """
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
                    if interface_name in line:
                        if 'unmanaged' in line.lower():
                            return 'manual'
                        elif 'connected' in line.lower() or 'disconnected' in line.lower():
                            return 'networkmanager'
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
            if result.returncode == 0:
                output = result.stdout.lower()
                if 'state:' in output and any(state in output for state in ['routable', 'configured', 'configuring']):
                    return 'systemd-networkd'
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return 'manual'


class NetworkManagerBackend:
    """NetworkManager operations using nmcli"""
    
    @staticmethod
    def connect_dhcp(interface_name):
        """Connect interface using DHCP via NetworkManager"""
        try:
            # First, ensure interface is managed
            subprocess.run(
                ['nmcli', 'device', 'set', interface_name, 'managed', 'yes'],
                capture_output=True,
                timeout=10
            )
            
            # Connect using DHCP
            result = subprocess.run(
                ['nmcli', 'device', 'connect', interface_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"NetworkManager: Connected {interface_name} via DHCP")
                return True, "Connected successfully via NetworkManager"
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"NetworkManager: Failed to connect {interface_name}: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except Exception as e:
            logger.error(f"NetworkManager error: {e}")
            return False, str(e)
    
    @staticmethod
    def disconnect(interface_name):
        """Disconnect interface via NetworkManager"""
        try:
            result = subprocess.run(
                ['nmcli', 'device', 'disconnect', interface_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"NetworkManager: Disconnected {interface_name}")
                return True, "Disconnected successfully"
            else:
                return False, result.stderr or result.stdout
                
        except Exception as e:
            logger.error(f"NetworkManager disconnect error: {e}")
            return False, str(e)
    
    @staticmethod
    def set_manual_ip(interface_name, ip_address, netmask, gateway=None, dns_servers=None):
        """Configure static IP via NetworkManager"""
        try:
            # Create connection name
            conn_name = f"netui-{interface_name}"
            
            # Delete existing connection if exists
            subprocess.run(
                ['nmcli', 'connection', 'delete', conn_name],
                capture_output=True,
                timeout=5
            )
            
            # Calculate CIDR from netmask
            cidr = NetworkManagerBackend._netmask_to_cidr(netmask)
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
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Activate the connection
                activate_result = subprocess.run(
                    ['nmcli', 'connection', 'up', conn_name],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if activate_result.returncode == 0:
                    logger.info(f"NetworkManager: Set static IP for {interface_name}")
                    return True, "Static IP configured successfully"
                else:
                    return False, activate_result.stderr or activate_result.stdout
            else:
                return False, result.stderr or result.stdout
                
        except Exception as e:
            logger.error(f"NetworkManager static IP error: {e}")
            return False, str(e)
    
    @staticmethod
    def _netmask_to_cidr(netmask):
        """Convert netmask to CIDR notation"""
        try:
            return sum([bin(int(x)).count('1') for x in netmask.split('.')])
        except:
            return 24  # Default to /24


class SystemdNetworkdBackend:
    """systemd-networkd operations"""
    
    @staticmethod
    def connect_dhcp(interface_name):
        """Connect interface using DHCP via systemd-networkd"""
        try:
            # Create network file
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
            subprocess.run(
                ['systemctl', 'restart', 'systemd-networkd'],
                capture_output=True,
                timeout=10
            )
            
            # Reconfigure interface
            subprocess.run(
                ['networkctl', 'reconfigure', interface_name],
                capture_output=True,
                timeout=10
            )
            
            logger.info(f"systemd-networkd: Configured {interface_name} for DHCP")
            return True, "Configured for DHCP via systemd-networkd"
            
        except PermissionError:
            return False, "Permission denied: Need root access"
        except Exception as e:
            logger.error(f"systemd-networkd error: {e}")
            return False, str(e)
    
    @staticmethod
    def set_manual_ip(interface_name, ip_address, netmask, gateway=None, dns_servers=None):
        """Configure static IP via systemd-networkd"""
        try:
            network_file = f"/etc/systemd/network/50-{interface_name}.network"
            
            cidr = SystemdNetworkdBackend._netmask_to_cidr(netmask)
            
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
            subprocess.run(
                ['systemctl', 'restart', 'systemd-networkd'],
                capture_output=True,
                timeout=10
            )
            
            # Reconfigure interface
            subprocess.run(
                ['networkctl', 'reconfigure', interface_name],
                capture_output=True,
                timeout=10
            )
            
            logger.info(f"systemd-networkd: Configured static IP for {interface_name}")
            return True, "Static IP configured via systemd-networkd"
            
        except PermissionError:
            return False, "Permission denied: Need root access"
        except Exception as e:
            logger.error(f"systemd-networkd error: {e}")
            return False, str(e)
    
    @staticmethod
    def _netmask_to_cidr(netmask):
        """Convert netmask to CIDR notation"""
        try:
            return sum([bin(int(x)).count('1') for x in netmask.split('.')])
        except:
            return 24


def connect_interface_dhcp(interface_name):
    """
    Connect interface using DHCP with automatic backend detection.
    Returns: (success: bool, message: str)
    """
    manager = NetworkService.detect_interface_manager(interface_name)
    logger.info(f"Interface {interface_name} is managed by: {manager}")
    
    if manager == 'networkmanager':
        return NetworkManagerBackend.connect_dhcp(interface_name)
    elif manager == 'systemd-networkd':
        return SystemdNetworkdBackend.connect_dhcp(interface_name)
    else:
        # Use traditional DHCP client
        from netmanage.dhcpc import lease
        try:
            result = lease(interface_name)
            return True, f"Connected via DHCP client: {result}"
        except Exception as e:
            return False, str(e)


def disconnect_interface(interface_name):
    """
    Disconnect interface with automatic backend detection.
    Releases DHCP lease and removes IP address.
    Returns: (success: bool, message: str)
    """
    manager = NetworkService.detect_interface_manager(interface_name)
    logger.info(f"Disconnecting {interface_name} (managed by {manager})")
    
    if manager == 'networkmanager':
        return NetworkManagerBackend.disconnect(interface_name)
    else:
        # Manual disconnect - handle multiple network managers
        try:
            import subprocess
            import shutil
            import os
            
            # Check for netctl (Arch Linux network profile manager)
            if shutil.which('netctl'):
                try:
                    # Stop netctl profile for this interface
                    result = subprocess.run(
                        ['netctl', 'stop-all'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        logger.info(f"Stopped netctl profiles")
                    
                    # Also try to find and stop specific profile
                    # Check for wpa_supplicant controlled by netctl
                    if os.path.exists(f'/run/netctl/wpa_supplicant-{interface_name}.conf'):
                        subprocess.run(['killall', f'wpa_supplicant'], 
                                     capture_output=True, timeout=5)
                        logger.info(f"Stopped wpa_supplicant for {interface_name}")
                except Exception as e:
                    logger.debug(f"Error stopping netctl: {e}")
            
            # Try to kill ALL dhcpcd processes for this interface
            # dhcpcd spawns multiple processes, need to kill them all
            try:
                # First try the clean way
                result = subprocess.run(['dhcpcd', '-k', interface_name], 
                                      capture_output=True, timeout=5)
                logger.info(f"Sent kill signal to dhcpcd for {interface_name}")
                
                # Wait a moment
                import time
                time.sleep(0.5)
                
                # Force kill any remaining dhcpcd processes for this interface
                subprocess.run(['pkill', '-f', f'dhcpcd.*{interface_name}'], 
                             capture_output=True, timeout=5)
                logger.info(f"Force killed remaining dhcpcd processes for {interface_name}")
                
            except Exception as e:
                logger.debug(f"Error stopping dhcpcd: {e}")
            
            # Try dhclient as well
            if shutil.which('dhclient'):
                try:
                    subprocess.run(['dhclient', '-r', interface_name], 
                                 capture_output=True, timeout=5)
                    logger.info(f"Released dhclient lease for {interface_name}")
                except Exception as e:
                    logger.debug(f"Error stopping dhclient: {e}")
            
            # Flush all IP addresses from interface
            result = subprocess.run(['ip', 'addr', 'flush', 'dev', interface_name], 
                         capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                logger.info(f"Flushed IP addresses from {interface_name}")
            
            # Additional cleanup: remove default route through this interface
            try:
                subprocess.run(['ip', 'route', 'del', 'default', 'dev', interface_name], 
                             capture_output=True, timeout=5)
            except Exception:
                pass  # Route might not exist
            
            # Final verification - wait a bit and check if IP is gone
            import time
            time.sleep(1)
            
            # Check if interface still has IP
            check_result = subprocess.run(['ip', 'addr', 'show', interface_name], 
                                        capture_output=True, text=True, timeout=5)
            if 'inet ' in check_result.stdout:
                logger.warning(f"Interface {interface_name} still has IP after disconnect")
                return False, "Interface disconnected but IP may reappear (managed by system service). Try: sudo systemctl stop netctl"
            else:
                logger.info(f"Successfully disconnected {interface_name}")
                return True, "Disconnected successfully"
                
        except Exception as e:
            logger.error(f"Error disconnecting {interface_name}: {e}")
            return False, str(e)


def set_manual_config(interface_name, ip_address, netmask, gateway=None, dns_servers=None):
    """
    Configure static IP with automatic backend detection.
    Returns: (success: bool, message: str)
    """
    manager = NetworkService.detect_interface_manager(interface_name)
    logger.info(f"Configuring {interface_name} (managed by {manager}) with static IP")
    
    if manager == 'networkmanager':
        return NetworkManagerBackend.set_manual_ip(interface_name, ip_address, netmask, gateway, dns_servers)
    elif manager == 'systemd-networkd':
        return SystemdNetworkdBackend.set_manual_ip(interface_name, ip_address, netmask, gateway, dns_servers)
    else:
        # Manual configuration - return success to let existing code handle it
        return None, "Using manual configuration"
