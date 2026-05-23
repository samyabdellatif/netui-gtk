"""
Advanced interface configuration window for netui-gtk.
Provides MTU, statistics, link speed, and advanced settings.
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import logging
from netmanage.advanced import *

logger = logging.getLogger(__name__)


class AdvancedConfigWindow(Gtk.Window):
    def __init__(self, interface=None):
        self.interface = interface
        title = "Advanced Interface Settings"
        if self.interface:
            title += f" - {self.interface.name}"
        Gtk.Window.__init__(self, title=title)
        self.set_border_width(10)
        self.set_default_size(500, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Main layout container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)
        
        # Create notebook for tabs
        notebook = Gtk.Notebook()
        vbox.pack_start(notebook, True, True, 0)
        
        # Tab 1: Statistics
        stats_page = self.create_statistics_page()
        notebook.append_page(stats_page, Gtk.Label(label="Statistics"))
        
        # Tab 2: Link Settings
        link_page = self.create_link_settings_page()
        notebook.append_page(link_page, Gtk.Label(label="Link Settings"))
        
        # Tab 3: Advanced
        advanced_page = self.create_advanced_page()
        notebook.append_page(advanced_page, Gtk.Label(label="Advanced"))
        
        # Close button
        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.END)
        vbox.pack_end(bbox, False, False, 0)
        
        btn_close = Gtk.Button(label="Close")
        btn_close.connect("clicked", lambda w: self.destroy())
        bbox.add(btn_close)
        
        # Auto-refresh timer for statistics
        self.timer_id = GLib.timeout_add_seconds(2, self.update_statistics)
    
    def create_statistics_page(self):
        """Create statistics monitoring page."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        scroll.add(vbox)
        
        # Interface info
        frame = Gtk.Frame(label="Interface Information")
        info_grid = Gtk.Grid()
        info_grid.set_column_spacing(10)
        info_grid.set_row_spacing(5)
        info_grid.set_margin_top(10)
        info_grid.set_margin_bottom(10)
        info_grid.set_margin_start(10)
        info_grid.set_margin_end(10)
        frame.add(info_grid)
        vbox.pack_start(frame, False, False, 0)
        
        if self.interface:
            row = 0
            # Operational State
            label = Gtk.Label(label="<b>Operational State:</b>", use_markup=True, xalign=0)
            self.operstate_label = Gtk.Label(xalign=0)
            info_grid.attach(label, 0, row, 1, 1)
            info_grid.attach(self.operstate_label, 1, row, 1, 1)
            row += 1
            
            # Carrier
            label = Gtk.Label(label="<b>Carrier (Cable):</b>", use_markup=True, xalign=0)
            self.carrier_label = Gtk.Label(xalign=0)
            info_grid.attach(label, 0, row, 1, 1)
            info_grid.attach(self.carrier_label, 1, row, 1, 1)
            row += 1
            
            # Link Speed
            label = Gtk.Label(label="<b>Link Speed:</b>", use_markup=True, xalign=0)
            self.speed_label = Gtk.Label(xalign=0)
            info_grid.attach(label, 0, row, 1, 1)
            info_grid.attach(self.speed_label, 1, row, 1, 1)
            row += 1
            
            # MTU
            label = Gtk.Label(label="<b>MTU:</b>", use_markup=True, xalign=0)
            self.mtu_label = Gtk.Label(xalign=0)
            info_grid.attach(label, 0, row, 1, 1)
            info_grid.attach(self.mtu_label, 1, row, 1, 1)
        
        # Statistics frame
        frame = Gtk.Frame(label="Network Statistics")
        stats_grid = Gtk.Grid()
        stats_grid.set_column_spacing(10)
        stats_grid.set_row_spacing(5)
        stats_grid.set_margin_top(10)
        stats_grid.set_margin_bottom(10)
        stats_grid.set_margin_start(10)
        stats_grid.set_margin_end(10)
        frame.add(stats_grid)
        vbox.pack_start(frame, False, False, 0)
        
        # Store labels for updating
        self.stat_labels = {}
        
        if self.interface:
            stats = get_interface_stats(self.interface.name)
            row = 0
            for stat_name, value in stats.items():
                label = Gtk.Label(label=f"<b>{stat_name}:</b>", use_markup=True, xalign=0)
                value_label = Gtk.Label(xalign=0)
                stats_grid.attach(label, 0, row, 1, 1)
                stats_grid.attach(value_label, 1, row, 1, 1)
                self.stat_labels[stat_name] = value_label
                row += 1
        
        # Initial update
        self.update_statistics()
        
        return scroll
    
    def create_link_settings_page(self):
        """Create link settings page."""
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        
        row = 0
        
        # MTU Setting
        label = Gtk.Label(label="<b>MTU (Maximum Transmission Unit):</b>", use_markup=True, xalign=0)
        grid.attach(label, 0, row, 2, 1)
        row += 1
        
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label_mtu = Gtk.Label(label="MTU:", xalign=0)
        self.entry_mtu = Gtk.Entry()
        self.entry_mtu.set_placeholder_text("1500 (default for Ethernet)")
        if self.interface:
            current_mtu = get_mtu(self.interface.name)
            if current_mtu:
                self.entry_mtu.set_text(str(current_mtu))
        
        btn_set_mtu = Gtk.Button(label="Set MTU")
        btn_set_mtu.connect("clicked", self.on_set_mtu)
        
        hbox.pack_start(label_mtu, False, False, 0)
        hbox.pack_start(self.entry_mtu, True, True, 0)
        hbox.pack_start(btn_set_mtu, False, False, 0)
        grid.attach(hbox, 0, row, 2, 1)
        row += 1
        
        # Info label
        info_label = Gtk.Label(
            label="<i>Common MTU values:\n• 1500 - Ethernet default\n• 1492 - PPPoE\n• 9000 - Jumbo frames</i>",
            use_markup=True,
            xalign=0
        )
        grid.attach(info_label, 0, row, 2, 1)
        row += 1
        
        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(separator, 0, row, 2, 1)
        row += 1
        
        # MAC Cloning
        label = Gtk.Label(label="<b>MAC Address Cloning:</b>", use_markup=True, xalign=0)
        grid.attach(label, 0, row, 2, 1)
        row += 1
        
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label_mac = Gtk.Label(label="New MAC:", xalign=0)
        self.entry_mac = Gtk.Entry()
        self.entry_mac.set_placeholder_text("AA:BB:CC:DD:EE:FF")
        if self.interface:
            try:
                current_mac = self.interface.get_mac()
                self.entry_mac.set_text(current_mac)
            except:
                pass
        
        btn_set_mac = Gtk.Button(label="Clone MAC")
        btn_set_mac.connect("clicked", self.on_clone_mac)
        
        hbox.pack_start(label_mac, False, False, 0)
        hbox.pack_start(self.entry_mac, True, True, 0)
        hbox.pack_start(btn_set_mac, False, False, 0)
        grid.attach(hbox, 0, row, 2, 1)
        row += 1
        
        warning_label = Gtk.Label(
            label="<i><span foreground='red'>⚠ Warning:</span> Changing MAC requires interface restart</i>",
            use_markup=True,
            xalign=0
        )
        grid.attach(warning_label, 0, row, 2, 1)
        
        return grid
    
    def create_advanced_page(self):
        """Create advanced settings page."""
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        
        row = 0
        
        # Promiscuous Mode
        label = Gtk.Label(label="<b>Promiscuous Mode:</b>", use_markup=True, xalign=0)
        grid.attach(label, 0, row, 1, 1)
        
        self.promisc_switch = Gtk.Switch()
        if self.interface:
            self.promisc_switch.set_active(get_promiscuous_mode(self.interface.name))
        self.promisc_switch.connect("notify::active", self.on_promisc_toggled)
        grid.attach(self.promisc_switch, 1, row, 1, 1)
        row += 1
        
        info_label = Gtk.Label(
            label="<i>Promiscuous mode allows capturing all network traffic\n(required for packet sniffing)</i>",
            use_markup=True,
            xalign=0
        )
        grid.attach(info_label, 0, row, 2, 1)
        row += 1
        
        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(separator, 0, row, 2, 1)
        row += 1
        
        # Driver Info
        label = Gtk.Label(label="<b>Driver Information:</b>", use_markup=True, xalign=0)
        grid.attach(label, 0, row, 2, 1)
        row += 1
        
        if self.interface:
            driver_info = get_driver_info(self.interface.name)
            if driver_info:
                for key, value in driver_info.items():
                    label = Gtk.Label(label=f"{key.title()}:", xalign=0)
                    value_label = Gtk.Label(label=value, xalign=0, selectable=True)
                    grid.attach(label, 0, row, 1, 1)
                    grid.attach(value_label, 1, row, 1, 1)
                    row += 1
            else:
                label = Gtk.Label(label="<i>No driver information available</i>", use_markup=True, xalign=0)
                grid.attach(label, 0, row, 2, 1)
        
        return grid
    
    def update_statistics(self):
        """Update statistics display."""
        if not self.interface:
            return False
        
        try:
            # Update stats
            stats = get_interface_stats(self.interface.name)
            for stat_name, value in stats.items():
                if stat_name in self.stat_labels:
                    if 'Bytes' in stat_name:
                        display_value = format_bytes(value)
                    else:
                        display_value = f"{value:,}"
                    self.stat_labels[stat_name].set_text(display_value)
            
            # Update info
            if hasattr(self, 'operstate_label'):
                self.operstate_label.set_text(get_operstate(self.interface.name))
            
            if hasattr(self, 'carrier_label'):
                carrier = get_carrier_state(self.interface.name)
                self.carrier_label.set_markup(
                    f"<span foreground='{'green' if carrier else 'red'}'>{'Connected' if carrier else 'Disconnected'}</span>"
                )
            
            if hasattr(self, 'speed_label'):
                self.speed_label.set_text(get_link_speed(self.interface.name))
            
            if hasattr(self, 'mtu_label'):
                mtu = get_mtu(self.interface.name)
                self.mtu_label.set_text(str(mtu) if mtu else "Unknown")
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
        
        return True  # Continue timer
    
    def on_set_mtu(self, widget):
        """Handle MTU set button."""
        if not self.interface:
            return
        
        try:
            mtu_value = self.entry_mtu.get_text()
            set_mtu(self.interface.name, mtu_value)
            
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                message_format="MTU Updated"
            )
            dialog.format_secondary_text(f"MTU set to {mtu_value} for {self.interface.name}")
            dialog.run()
            dialog.destroy()
            
            self.update_statistics()
        except Exception as e:
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                message_format="MTU Error"
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
    
    def on_clone_mac(self, widget):
        """Handle MAC clone button."""
        if not self.interface:
            return
        
        try:
            new_mac = self.entry_mac.get_text()
            clone_mac_address(self.interface.name, new_mac)
            
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                message_format="MAC Address Updated"
            )
            dialog.format_secondary_text(
                f"MAC address set to {new_mac} for {self.interface.name}\n"
                "Interface has been restarted."
            )
            dialog.run()
            dialog.destroy()
        except Exception as e:
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                message_format="MAC Clone Error"
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
    
    def on_promisc_toggled(self, switch, gparam):
        """Handle promiscuous mode toggle."""
        if not self.interface:
            return
        
        try:
            set_promiscuous_mode(self.interface.name, switch.get_active())
        except Exception as e:
            logger.error(f"Error setting promiscuous mode: {e}")
            # Revert switch
            switch.set_active(not switch.get_active())
            
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                message_format="Promiscuous Mode Error"
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
    
    def destroy(self):
        """Clean up timer on destroy."""
        if self.timer_id:
            GLib.source_remove(self.timer_id)
        Gtk.Window.destroy(self)
