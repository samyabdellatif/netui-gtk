"""
Manual configuration window for netui-gtk.
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import subprocess
import ipaddress
import shutil

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

        if not self.interface:
            return

        try:
            # Configure IP and Netmask
            if ip and mask:
                # Convert netmask to CIDR prefix (e.g., 255.255.255.0 -> 24)
                cidr = ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
                
                # Use 'ip' command instead of deprecated 'ifconfig'
                subprocess.run(["ip", "addr", "flush", "dev", self.interface.name], check=True)
                subprocess.run(["ip", "addr", "add", f"{ip}/{cidr}", "dev", self.interface.name], check=True)
                subprocess.run(["ip", "link", "set", self.interface.name, "up"], check=True)
            
            # Configure Gateway
            if gw:
                # Use 'ip route' instead of deprecated 'route' command
                subprocess.run(["ip", "route", "del", "default"], stderr=subprocess.DEVNULL)
                subprocess.run(["ip", "route", "add", "default", "via", gw, "dev", self.interface.name], check=True)
            
            # Configure DNS
            if dns1 or dns2:
                # Check for systemd-resolved (resolvectl) for better compatibility
                if shutil.which("resolvectl"):
                    cmd = ["resolvectl", "dns", self.interface.name]
                    if dns1: cmd.append(dns1)
                    if dns2: cmd.append(dns2)
                    subprocess.run(cmd, check=True)
                else:
                    with open("/etc/resolv.conf", "w") as f:
                        if dns1:
                            f.write(f"nameserver {dns1}\n")
                        if dns2:
                            f.write(f"nameserver {dns2}\n")
            
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