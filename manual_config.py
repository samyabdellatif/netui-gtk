"""
Manual configuration window for netui-gtk.
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import subprocess
import ipaddress
import shutil
from netmanage.network_service import set_manual_config, NetworkService
import logging

logger = logging.getLogger(__name__)

class ManualConfigWindow(Gtk.Window):
    def __init__(self, interface=None):
        self.interface = interface
        title = "Manual Interface Configuration"
        if self.interface:
            title += f" - {self.interface.name}"
        Gtk.Window.__init__(self, title=title)
        self.set_border_width(10)
        self.set_default_size(400, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Main layout container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Grid for form fields
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        vbox.pack_start(grid, True, True, 0)

        # IP Address
        label_ip = Gtk.Label(label="IPv4 Address:", xalign=0)
        self.entry_ip = Gtk.Entry()
        grid.attach(label_ip, 0, 0, 1, 1)
        grid.attach(self.entry_ip, 1, 0, 1, 1)

        # Subnet Mask
        label_mask = Gtk.Label(label="Subnet Mask:", xalign=0)
        self.entry_mask = Gtk.Entry()
        grid.attach(label_mask, 0, 1, 1, 1)
        grid.attach(self.entry_mask, 1, 1, 1, 1)

        # Gateway
        label_gw = Gtk.Label(label="Gateway:", xalign=0)
        self.entry_gw = Gtk.Entry()
        grid.attach(label_gw, 0, 2, 1, 1)
        grid.attach(self.entry_gw, 1, 2, 1, 1)

        # DNS 1
        label_dns1 = Gtk.Label(label="DNS Server 1:", xalign=0)
        self.entry_dns1 = Gtk.Entry()
        grid.attach(label_dns1, 0, 3, 1, 1)
        grid.attach(self.entry_dns1, 1, 3, 1, 1)

        # DNS 2
        label_dns2 = Gtk.Label(label="DNS Server 2:", xalign=0)
        self.entry_dns2 = Gtk.Entry()
        grid.attach(label_dns2, 0, 4, 1, 1)
        grid.attach(self.entry_dns2, 1, 4, 1, 1)

        # Separator for IPv6
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(separator, 0, 5, 2, 1)

        # IPv6 Section Label
        label_ipv6 = Gtk.Label(label="<b>IPv6 Configuration (Optional)</b>", xalign=0, use_markup=True)
        grid.attach(label_ipv6, 0, 6, 2, 1)

        # IPv6 Address
        label_ipv6_addr = Gtk.Label(label="IPv6 Address:", xalign=0)
        self.entry_ipv6 = Gtk.Entry()
        self.entry_ipv6.set_placeholder_text("e.g., 2001:db8::1/64")
        grid.attach(label_ipv6_addr, 0, 7, 1, 1)
        grid.attach(self.entry_ipv6, 1, 7, 1, 1)

        # IPv6 Gateway
        label_ipv6_gw = Gtk.Label(label="IPv6 Gateway:", xalign=0)
        self.entry_ipv6_gw = Gtk.Entry()
        self.entry_ipv6_gw.set_placeholder_text("e.g., fe80::1")
        grid.attach(label_ipv6_gw, 0, 8, 1, 1)
        grid.attach(self.entry_ipv6_gw, 1, 8, 1, 1)

        # Button Box
        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.END)
        bbox.set_spacing(10)
        vbox.pack_end(bbox, False, False, 0)

        # Cancel Button
        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.connect("clicked", self.on_cancel_clicked)
        bbox.add(btn_cancel)

        # Save/Apply Button
        btn_save = Gtk.Button(label="Apply")
        btn_save.connect("clicked", self.on_apply_clicked)
        bbox.add(btn_save)

    def on_cancel_clicked(self, widget):
        self.destroy()

    def on_apply_clicked(self, widget):
        ip = self.entry_ip.get_text()
        mask = self.entry_mask.get_text()
        gw = self.entry_gw.get_text()
        dns1 = self.entry_dns1.get_text()
        dns2 = self.entry_dns2.get_text()
        ipv6 = self.entry_ipv6.get_text()
        ipv6_gw = self.entry_ipv6_gw.get_text()

        if not self.interface:
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
                        dialog = Gtk.MessageDialog(
                            parent=self, flags=0, 
                            message_type=Gtk.MessageType.INFO,
                            buttons=Gtk.ButtonsType.OK, 
                            text=f"Configuration Applied via {manager}"
                        )
                        dialog.format_secondary_text(message)
                        dialog.run()
                        dialog.destroy()
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
                
                # Use 'ip' command instead of deprecated 'ifconfig'
                subprocess.run(["ip", "addr", "flush", "dev", self.interface.name], check=True, timeout=10)
                subprocess.run(["ip", "addr", "add", f"{ip}/{cidr}", "dev", self.interface.name], check=True, timeout=10)
                subprocess.run(["ip", "link", "set", self.interface.name, "up"], check=True, timeout=10)
            
            # Configure Gateway
            if gw:
                # Use 'ip route' instead of deprecated 'route' command
                subprocess.run(["ip", "route", "del", "default"], stderr=subprocess.DEVNULL, timeout=10)
                subprocess.run(["ip", "route", "add", "default", "via", gw, "dev", self.interface.name], check=True, timeout=10)
            
            # Configure IPv6
            if ipv6:
                # IPv6 address should include prefix (e.g., 2001:db8::1/64)
                try:
                    # Validate IPv6 address
                    ipaddress.IPv6Interface(ipv6)
                    subprocess.run(["ip", "-6", "addr", "add", ipv6, "dev", self.interface.name], check=True, timeout=10)
                except ValueError as e:
                    raise ValueError(f"Invalid IPv6 address format: {e}")
                except subprocess.TimeoutExpired:
                    raise RuntimeError("IPv6 address configuration timed out")
            
            # Configure IPv6 Gateway
            if ipv6_gw:
                try:
                    # Validate IPv6 gateway
                    ipaddress.IPv6Address(ipv6_gw)
                    subprocess.run(["ip", "-6", "route", "add", "default", "via", ipv6_gw, "dev", self.interface.name], 
                                 stderr=subprocess.DEVNULL, timeout=10)
                except ValueError as e:
                    raise ValueError(f"Invalid IPv6 gateway format: {e}")
                except subprocess.TimeoutExpired:
                    raise RuntimeError("IPv6 gateway configuration timed out")
            
            # Configure DNS
            if dns1 or dns2:
                # Check for systemd-resolved (resolvectl) for better compatibility
                if shutil.which("resolvectl"):
                    cmd = ["resolvectl", "dns", self.interface.name]
                    if dns1: cmd.append(dns1)
                    if dns2: cmd.append(dns2)
                    subprocess.run(cmd, check=True, timeout=10)
                else:
                    # Check if resolv.conf is a symlink (systemd-resolved)
                    import os
                    if os.path.islink("/etc/resolv.conf"):
                        raise RuntimeError(
                            "Cannot modify /etc/resolv.conf - it's managed by systemd-resolved.\n"
                            "Use 'resolvectl' command or install it: sudo apt install systemd-resolved"
                        )
                    
                    # Backup existing resolv.conf
                    try:
                        with open("/etc/resolv.conf", "r") as f:
                            existing = f.read()
                    except:
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
            
            self.destroy()
            
        except Exception as e:
            dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK, text="Configuration Error")
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()

if __name__ == "__main__":
    win = ManualConfigWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()