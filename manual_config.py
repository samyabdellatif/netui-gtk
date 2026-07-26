"""
Manual configuration window for netui-gtk.
Provides static IP, gateway, DNS, and IPv6 configuration.
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import subprocess
import ipaddress
import shutil
import os
import re
from netmanage.network_service import set_manual_config, NetworkService
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ManualConfigWindow(Gtk.Window):
    """Window for manual network interface configuration."""
    
    def __init__(self, interface=None):
        self.interface = interface
        title = "Manual Interface Configuration"
        if self.interface:
            title += f" - {self.interface.name}"
        Gtk.Window.__init__(self, title=title)
        self.set_border_width(10)
        self.set_default_size(450, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Main layout container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)
        
        # Info label
        info_label = Gtk.Label(
            label="<i>Configure static IP settings for this interface.</i>",
            use_markup=True,
            xalign=0
        )
        vbox.pack_start(info_label, False, False, 0)
        
        # Scrolled window for form
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)
        
        # Grid for form fields
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(8)
        grid.set_margin_top(5)
        grid.set_margin_bottom(5)
        grid.set_margin_start(5)
        grid.set_margin_end(5)
        scrolled.add(grid)
        
        row = 0
        
        # IPv4 Section
        section_label = Gtk.Label(label="<b>IPv4 Configuration</b>", use_markup=True, xalign=0)
        grid.attach(section_label, 0, row, 2, 1)
        row += 1
        
        # IP Address
        label_ip = Gtk.Label(label="IPv4 Address:", xalign=0)
        self.entry_ip = Gtk.Entry()
        self.entry_ip.set_placeholder_text("e.g., 192.168.1.100")
        grid.attach(label_ip, 0, row, 1, 1)
        grid.attach(self.entry_ip, 1, row, 1, 1)
        row += 1
        
        # Subnet Mask
        label_mask = Gtk.Label(label="Subnet Mask:", xalign=0)
        self.entry_mask = Gtk.Entry()
        self.entry_mask.set_placeholder_text("e.g., 255.255.255.0")
        grid.attach(label_mask, 0, row, 1, 1)
        grid.attach(self.entry_mask, 1, row, 1, 1)
        row += 1
        
        # Gateway
        label_gw = Gtk.Label(label="Gateway:", xalign=0)
        self.entry_gw = Gtk.Entry()
        self.entry_gw.set_placeholder_text("e.g., 192.168.1.1")
        grid.attach(label_gw, 0, row, 1, 1)
        grid.attach(self.entry_gw, 1, row, 1, 1)
        row += 1
        
        # DNS 1
        label_dns1 = Gtk.Label(label="DNS Server 1:", xalign=0)
        self.entry_dns1 = Gtk.Entry()
        self.entry_dns1.set_placeholder_text("e.g., 8.8.8.8")
        grid.attach(label_dns1, 0, row, 1, 1)
        grid.attach(self.entry_dns1, 1, row, 1, 1)
        row += 1
        
        # DNS 2
        label_dns2 = Gtk.Label(label="DNS Server 2:", xalign=0)
        self.entry_dns2 = Gtk.Entry()
        self.entry_dns2.set_placeholder_text("e.g., 8.8.4.4")
        grid.attach(label_dns2, 0, row, 1, 1)
        grid.attach(self.entry_dns2, 1, row, 1, 1)
        row += 1
        
        # Separator for IPv6
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(separator, 0, row, 2, 1)
        row += 1
        
        # IPv6 Section
        label_ipv6 = Gtk.Label(label="<b>IPv6 Configuration (Optional)</b>", use_markup=True, xalign=0)
        grid.attach(label_ipv6, 0, row, 2, 1)
        row += 1
        
        # IPv6 Address
        label_ipv6_addr = Gtk.Label(label="IPv6 Address:", xalign=0)
        self.entry_ipv6 = Gtk.Entry()
        self.entry_ipv6.set_placeholder_text("e.g., 2001:db8::1/64")
        grid.attach(label_ipv6_addr, 0, row, 1, 1)
        grid.attach(self.entry_ipv6, 1, row, 1, 1)
        row += 1
        
        # IPv6 Gateway
        label_ipv6_gw = Gtk.Label(label="IPv6 Gateway:", xalign=0)
        self.entry_ipv6_gw = Gtk.Entry()
        self.entry_ipv6_gw.set_placeholder_text("e.g., fe80::1")
        grid.attach(label_ipv6_gw, 0, row, 1, 1)
        grid.attach(self.entry_ipv6_gw, 1, row, 1, 1)
        row += 1
        
        # Button Box
        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.END)
        bbox.set_spacing(10)
        vbox.pack_end(bbox, False, False, 0)
        
        # Cancel Button
        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.get_style_context().add_class("cancel")
        btn_cancel.connect("clicked", self.on_cancel_clicked)
        bbox.add(btn_cancel)
        
        # Save/Apply Button
        btn_save = Gtk.Button(label="Apply")
        btn_save.get_style_context().add_class("apply")
        btn_save.connect("clicked", self.on_apply_clicked)
        bbox.add(btn_save)
    
    def on_cancel_clicked(self, widget):
        self.destroy()
    
    def _validate_ipv4(self, ip: str) -> bool:
        """Validate IPv4 address format."""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False
    
    def _validate_ipv4_netmask(self, mask: str) -> bool:
        """Validate IPv4 netmask format."""
        try:
            ipaddress.IPv4Network(f"0.0.0.0/{mask}")
            return True
        except (ipaddress.NetmaskValueError, ValueError):
            return False
    
    def _validate_ipv6(self, ip: str) -> bool:
        """Validate IPv6 address format."""
        try:
            ipaddress.IPv6Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False
    
    def _validate_mac(self, mac: str) -> bool:
        """Validate MAC address format."""
        return bool(re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac))
    
    def _show_validation_error(self, field_name: str, message: str) -> None:
        """Show a validation error dialog."""
        dialog = Gtk.MessageDialog(
            parent=self, flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=f"Invalid {field_name}"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def on_apply_clicked(self, widget):
        """Handle apply button click with validation."""
        ip = self.entry_ip.get_text().strip()
        mask = self.entry_mask.get_text().strip()
        gw = self.entry_gw.get_text().strip()
        dns1 = self.entry_dns1.get_text().strip()
        dns2 = self.entry_dns2.get_text().strip()
        ipv6 = self.entry_ipv6.get_text().strip()
        ipv6_gw = self.entry_ipv6_gw.get_text().strip()
        
        if not self.interface:
            return
        
        # Validate required fields
        if not ip:
            self._show_validation_error("IP Address", "IPv4 address is required.")
            return
        
        if not mask:
            self._show_validation_error("Subnet Mask", "Subnet mask is required.")
            return
        
        # Validate IP format
        if not self._validate_ipv4(ip):
            self._show_validation_error("IP Address", f"'{ip}' is not a valid IPv4 address.")
            return
        
        # Validate netmask
        if not self._validate_ipv4_netmask(mask):
            self._show_validation_error("Subnet Mask", f"'{mask}' is not a valid netmask.")
            return
        
        # Validate gateway if provided
        if gw and not self._validate_ipv4(gw):
            self._show_validation_error("Gateway", f"'{gw}' is not a valid IPv4 address.")
            return
        
        # Validate DNS if provided
        if dns1 and not self._validate_ipv4(dns1):
            self._show_validation_error("DNS Server 1", f"'{dns1}' is not a valid IPv4 address.")
            return
        
        if dns2 and not self._validate_ipv4(dns2):
            self._show_validation_error("DNS Server 2", f"'{dns2}' is not a valid IPv4 address.")
            return
        
        # Validate IPv6 if provided
        if ipv6:
            try:
                ipaddress.IPv6Interface(ipv6)
            except ValueError as e:
                self._show_validation_error("IPv6 Address", f"'{ipv6}' is not valid: {e}")
                return
        
        if ipv6_gw and not self._validate_ipv6(ipv6_gw):
            self._show_validation_error("IPv6 Gateway", f"'{ipv6_gw}' is not a valid IPv6 address.")
            return
        
        try:
            # Detect backend
            manager = NetworkService.detect_interface_manager(self.interface.name)
            logger.info(f"Configuring {self.interface.name} (managed by {manager})")
            
            # Configure IPv4
            if ip and mask:
                # Try to use NetworkManager/systemd-networkd if managing the interface
                if manager in ['networkmanager', 'systemd-networkd']:
                    dns_servers = " ".join(filter(None, [dns1, dns2]))
                    success, message = set_manual_config(
                        self.interface.name, ip, mask, gw, dns_servers
                    )
                    
                    if success:
                        self._show_success_dialog(f"Configuration Applied via {manager}", message)
                        self.destroy()
                        return
                    elif success is None:
                        # Fall through to manual configuration
                        logger.info("Falling back to manual configuration")
                    else:
                        # Error occurred
                        raise RuntimeError(message)
                
                # Manual configuration (traditional method)
                # Convert netmask to CIDR prefix (e.g., 255.255.255.0 -> 24)
                cidr = ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
                
                # Flush existing IPs and set new one
                subprocess.run(
                    ["ip", "addr", "flush", "dev", self.interface.name],
                    check=True, timeout=10
                )
                subprocess.run(
                    ["ip", "addr", "add", f"{ip}/{cidr}", "dev", self.interface.name],
                    check=True, timeout=10
                )
                subprocess.run(
                    ["ip", "link", "set", self.interface.name, "up"],
                    check=True, timeout=10
                )
            
            # Configure Gateway - ONLY replace the default route for this specific interface
            if gw:
                # Remove existing default route for this interface only (not ALL default routes)
                try:
                    subprocess.run(
                        ["ip", "route", "del", "default", "dev", self.interface.name],
                        stderr=subprocess.DEVNULL, timeout=10
                    )
                except subprocess.TimeoutExpired:
                    logger.warning("Timeout removing old default route")
                
                # Add new default route
                subprocess.run(
                    ["ip", "route", "add", "default", "via", gw, "dev", self.interface.name],
                    check=True, timeout=10
                )
            
            # Configure IPv6
            if ipv6:
                try:
                    # Validate IPv6 address with prefix
                    ipaddress.IPv6Interface(ipv6)
                    subprocess.run(
                        ["ip", "-6", "addr", "add", ipv6, "dev", self.interface.name],
                        check=True, timeout=10
                    )
                except ValueError as e:
                    raise ValueError(f"Invalid IPv6 address format: {e}")
                except subprocess.TimeoutExpired:
                    raise RuntimeError("IPv6 address configuration timed out")
            
            # Configure IPv6 Gateway
            if ipv6_gw:
                try:
                    # Validate IPv6 gateway
                    ipaddress.IPv6Address(ipv6_gw)
                    subprocess.run(
                        ["ip", "-6", "route", "add", "default", "via", ipv6_gw, "dev", self.interface.name],
                        stderr=subprocess.DEVNULL, timeout=10
                    )
                except ValueError as e:
                    raise ValueError(f"Invalid IPv6 gateway format: {e}")
                except subprocess.TimeoutExpired:
                    raise RuntimeError("IPv6 gateway configuration timed out")
            
            # Configure DNS
            if dns1 or dns2:
                self._configure_dns(dns1, dns2)
            
            self._show_success_dialog(
                "Configuration Applied",
                f"Static IP configuration applied to {self.interface.name}."
            )
            self.destroy()
            
        except Exception as e:
            self._show_error_dialog("Configuration Error", str(e))
    
    def _configure_dns(self, dns1: str, dns2: str) -> None:
        """Configure DNS servers safely."""
        # Check for systemd-resolved (resolvectl) for better compatibility
        if shutil.which("resolvectl"):
            cmd = ["resolvectl", "dns", self.interface.name]
            if dns1:
                cmd.append(dns1)
            if dns2:
                cmd.append(dns2)
            subprocess.run(cmd, check=True, timeout=10)
        else:
            # Check if resolv.conf is a symlink (systemd-resolved)
            if os.path.islink("/etc/resolv.conf"):
                raise RuntimeError(
                    "Cannot modify /etc/resolv.conf - it's managed by systemd-resolved.\n"
                    "Use 'resolvectl' command or install it: sudo apt install systemd-resolved"
                )
            
            # Backup existing resolv.conf
            try:
                with open("/etc/resolv.conf", "r") as f:
                    existing = f.read()
            except (FileNotFoundError, PermissionError):
                existing = ""
            
            # Write new DNS configuration
            try:
                with open("/etc/resolv.conf", "w") as f:
                    f.write("# Generated by netui-gtk\n")
                    if dns1:
                        f.write(f"nameserver {dns1}\n")
                    if dns2:
                        f.write(f"nameserver {dns2}\n")
            except PermissionError:
                raise RuntimeError("Permission denied writing /etc/resolv.conf")
    
    def _show_success_dialog(self, title: str, message: str) -> None:
        """Show a success dialog."""
        dialog = Gtk.MessageDialog(
            parent=self, flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def _show_error_dialog(self, title: str, message: str) -> None:
        """Show an error dialog."""
        dialog = Gtk.MessageDialog(
            parent=self, flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    win = ManualConfigWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()