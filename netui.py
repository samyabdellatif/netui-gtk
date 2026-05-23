"""
Main code of netui-gtk.
:Copyright: © 2020, Samy Abdellatif.
:License: MIT.

ifconfig,route are forked from https://github.com/rlisagor/pynetlinux under the MIT licence
thanks for developers rlisagor Roman Lisagor, Robert Grant, and williamjoy williamjoy
"""
from netmanage.ifconfig import *
from netmanage.route import *
from netmanage.dhcpc import *
from netmanage.network_service import connect_interface_dhcp, disconnect_interface, NetworkService
from config import get_config

import gi
import logging
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from manual_config import ManualConfigWindow
from advanced_config import AdvancedConfigWindow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class netUImainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="network interfaces")
        # Load configuration
        self.config = get_config()
        
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
        
        # setting and icon and border
        # self.set_default_icon_from_file("iplinkgui.ico")
        self.set_border_width(10)
        
        # Make window more prominent with saved size preferences
        window_width = self.config.get('window_width', 600)
        window_height = self.config.get('window_height', 400)
        self.set_default_size(window_width, window_height)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        
        # Save window size before closing (using delete-event to ensure size is still valid)
        self.connect("delete-event", self.on_window_delete)
        
        try:
            self.create_ui()
            logger.info("UI created successfully")
        except Exception as e:
            logger.error(f"Failed to create UI: {e}")
            self.show_error_dialog("UI Creation Error", f"Failed to create user interface: {e}")
    
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
        
    def show_error_dialog(self, title, message):
        """Display an error dialog to user"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            message_format=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
        
    def show_info_dialog(self, title, message):
        """Display an info dialog to the user"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def create_ui(self):
        """Create the main user interface"""
        #defining listbox
        lbox = Gtk.ListBox()
        lbox.set_selection_mode(Gtk.SelectionMode.NONE)
        lbox.set_margin_top(10)
        lbox.set_margin_bottom(10)
        lbox.set_margin_start(10)
        lbox.set_margin_end(10)

        #Header Row
        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        #inserting horizontal box inside the listbox row container
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.add(hbox)

        #inserting label and button widgets inside the horizontal box
        label = Gtk.Label(label="<b>Interface Details</b>", use_markup=True, width_chars=35, xalign=0)
        hbox.pack_start(label,True,True,10)
        #inserting label and button widgets inside the horizontal box
        label = Gtk.Label(label="<b>Status</b>", use_markup=True, width_chars=10, xalign=0.5)
        hbox.pack_start(label,True,True,10)
        #inserting label and button widgets inside the horizontal box
        label = Gtk.Label(label="<b>Connection</b>", use_markup=True, width_chars=12, xalign=0.5)
        hbox.pack_start(label,True,True,10)
        #inserting label and button widgets inside the horizontal box
        label = Gtk.Label(label="<b>Configuration</b>", use_markup=True, width_chars=12, xalign=0.5)
        hbox.pack_start(label,True,True,10)
        #inserting label and button widgets inside the horizontal box
        label = Gtk.Label(label="<b>Advanced</b>", use_markup=True, width_chars=12, xalign=0.5)
        hbox.pack_start(label,True,True,10)
        # adding the row to the listbox
        lbox.add(row)

        # Iterate through interfaces and add one row for each 
        for iface_index in range(len(self.intF_list)):
            try:
                interface = self.intF_list[iface_index]
                
                # Get interface details with error handling
                try:
                    mac_addr = interface.get_mac()
                    ip_addr = interface.get_ip()
                    interfaceDetails = f"{interface.name} | {mac_addr} | {ip_addr}"
                except Exception as e:
                    logger.error(f"Error getting details for {interface.name}: {e}")
                    interfaceDetails = f"{interface.name} | Error getting details"
                
                #defining listbox row container
                row = Gtk.ListBoxRow()
                row.set_activatable(False)

                #inserting horizontal box inside the listbox row container
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                row.add(hbox)

                #inserting label and button widgets inside the horizontal box
                label = Gtk.Label(label=interfaceDetails, width_chars=35, xalign=0)
                hbox.pack_start(label, True, True, 10)

                # Up/Down switch
                switch = Gtk.Switch()
                switch.connect("notify::active", self.on_UpDown_activated, iface_index)
                switch.props.valign = Gtk.Align.CENTER
                try:
                    if interface.is_up():
                        switch.props.active = True
                    else:
                        switch.props.active = False
                except Exception as e:
                    logger.error(f"Error checking interface status for {interface.name}: {e}")
                    switch.props.active = False
                    switch.set_sensitive(False)  # Disable switch if status can't be determined
                hbox.pack_start(switch, True, False, 0)

                # Connect/Disconnect switch
                switch = Gtk.Switch()
                switch.connect("notify::active", self.on_ConDiscon_activated, iface_index)
                switch.props.valign = Gtk.Align.CENTER
                try:
                    ip_addr = interface.get_ip()
                    if str(ip_addr) != "None" and ip_addr is not None:
                        switch.props.active = True
                    else:
                        switch.props.active = False
                except Exception as e:
                    logger.error(f"Error checking IP for {interface.name}: {e}")
                    switch.props.active = False
                    switch.set_sensitive(False)  # Disable switch if IP can't be determined
                hbox.pack_start(switch, True, False, 0)

                # Manual Config Button
                btn_config = Gtk.Button(label="Manual Config")
                btn_config.connect("clicked", self.on_config_clicked, interface)
                hbox.pack_start(btn_config, True, False, 0)

                # Advanced Button
                btn_advanced = Gtk.Button(label="Advanced")
                btn_advanced.connect("clicked", self.on_advanced_clicked, interface)
                hbox.pack_start(btn_advanced, True, False, 0)

                # adding the row to the listbox
                lbox.add(row)
                
            except Exception as e:
                logger.error(f"Error creating UI row for interface {iface_index}: {e}")
                # Create a row with error information
                row = Gtk.ListBoxRow()
                row.set_activatable(False)
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                row.add(hbox)
                label = Gtk.Label(label=f"Error loading interface {iface_index}: {str(e)}", width_chars=40, xalign=0)
                hbox.pack_start(label, True, True, 10)
                lbox.add(row)

        # adding the listbox to the window container (self)
        self.add(lbox)
        logger.info("Window and UI components created successfully")

    def on_config_clicked(self, widget, interface):
        """Handle manual config button click"""
        try:
            win = ManualConfigWindow(interface=interface)
            win.set_transient_for(self)
            win.set_modal(True)
            win.show_all()
        except Exception as e:
            logger.error(f"Failed to open manual config window: {e}")
            self.show_error_dialog("Configuration Error", f"Failed to open configuration window: {e}")
    
    def on_advanced_clicked(self, widget, interface):
        """Handle advanced button click"""
        try:
            win = AdvancedConfigWindow(interface=interface)
            win.set_transient_for(self)
            win.set_modal(False)  # Non-modal so statistics can update
            win.show_all()
        except Exception as e:
            logger.error(f"Failed to open advanced window: {e}")
            self.show_error_dialog("Advanced Error", f"Failed to open advanced window: {e}")

    def on_UpDown_activated(self, switch, gparam, i):
        """Handle interface up/down switch activation"""
        try:
            interface = self.intF_list[i]
            interface_name = interface.name
            
            if switch.get_active():
                # Try to bring interface up
                try:
                    if not interface.is_up():
                        interface.up()
                        logger.info(f"Successfully brought up interface {interface_name}")
                        self.show_info_dialog("Interface Up", f"Interface {interface_name} has been brought up successfully.")
                    else:
                        logger.info(f"Interface {interface_name} was already up")
                        self.show_info_dialog("Interface Status", f"Interface {interface_name} was already up.")
                except PermissionError:
                    logger.error(f"Permission denied when bringing up {interface_name}")
                    self.show_error_dialog("Permission Error", f"Failed to bring up {interface_name}: Permission denied. Please run as root or use sudo.")
                    switch.set_active(False)  # Revert switch
                except Exception as e:
                    logger.error(f"Failed to bring up {interface_name}: {e}")
                    self.show_error_dialog("Interface Error", f"Failed to bring up {interface_name}: {e}")
                    switch.set_active(False)  # Revert switch
            else:
                # Try to bring interface down
                try:
                    if interface.is_up():
                        interface.down()
                        logger.info(f"Successfully brought down interface {interface_name}")
                        self.show_info_dialog("Interface Down", f"Interface {interface_name} has been brought down successfully.")
                    else:
                        logger.info(f"Interface {interface_name} was already down")
                        self.show_info_dialog("Interface Status", f"Interface {interface_name} was already down.")
                except PermissionError:
                    logger.error(f"Permission denied when bringing down {interface_name}")
                    self.show_error_dialog("Permission Error", f"Failed to bring down {interface_name}: Permission denied. Please run as root or use sudo.")
                    switch.set_active(True)  # Revert switch
                except Exception as e:
                    logger.error(f"Failed to bring down {interface_name}: {e}")
                    self.show_error_dialog("Interface Error", f"Failed to bring down {interface_name}: {e}")
                    switch.set_active(True)  # Revert switch
                    
        except IndexError:
            logger.error(f"Invalid interface index: {i}")
            self.show_error_dialog("Interface Error", f"Invalid interface index: {i}")
        except Exception as e:
            logger.error(f"Unexpected error in on_UpDown_activated: {e}")
            self.show_error_dialog("Unexpected Error", f"An unexpected error occurred: {e}")

    def _on_connect_complete(self, result_tuple, interface, switch, manager):
        """Called on GTK main thread when async connect completes."""
        success, message = result_tuple
        if success:
            logger.info(f"Connect succeeded for {interface.name}, polling for IP...")
            self._poll_for_ip(interface, switch, 15)
        else:
            logger.error(f"Failed to connect {interface.name}: {message}")
            self.show_error_dialog("Connection Error", f"Failed to connect {interface.name}:\n{message}")
            switch.set_active(False)

    def _on_disconnect_complete(self, result_tuple, interface, switch):
        """Called on GTK main thread when async disconnect completes."""
        success, message = result_tuple
        if success:
            logger.info(f"Disconnect succeeded for {interface.name}, polling IP removal...")
            self._poll_for_disconnect(interface, switch, 10)
        else:
            logger.error(f"Failed to disconnect {interface.name}: {message}")
            self.show_error_dialog("Disconnection Error", f"Failed to disconnect {interface.name}:\n{message}")
            switch.set_active(True)

    def on_ConDiscon_activated(self, switch, gparam, i):
        """Handle interface connect/disconnect switch activation (non-blocking)."""
        try:
            interface = self.intF_list[i]
            interface_name = interface.name
        except IndexError:
            logger.error(f"Invalid interface index: {i}")
            self.show_error_dialog("Interface Error", f"Invalid interface index: {i}")
            return
        
        if switch.get_active():
            # Connect using async worker to avoid GUI freeze
            manager = NetworkService.detect_interface_manager(interface_name)
            logger.info(f"Interface {interface_name} is managed by: {manager}")
            logger.info(f"Connecting {interface_name} via DHCP (async)...")
            
            from netmanage.async_worker import AsyncWorker
            AsyncWorker.run_async(
                connect_interface_dhcp,
                lambda success_data, iface=interface, sw=switch, mgr=manager:
                    self._on_connect_complete(success_data, iface, sw, mgr),
                interface_name=interface_name
            )
        else:
            # Disconnect using async worker to avoid GUI freeze
            logger.info(f"Disconnecting {interface_name} (async)...")
            
            from netmanage.async_worker import AsyncWorker
            AsyncWorker.run_async(
                disconnect_interface,
                lambda success_data, iface=interface, sw=switch:
                    self._on_disconnect_complete(success_data, iface, sw),
                interface_name=interface_name
            )

    def _poll_for_ip(self, interface, switch, max_attempts=15):
        """Poll for IP assignment without blocking the GUI."""
        self._poll_count = 0
        self._poll_max = max_attempts
        self._poll_interface = interface
        self._poll_switch = switch
        GLib.timeout_add(1000, self._poll_check_ip)

    def _poll_check_ip(self):
        """Called every second to check if IP has been assigned."""
        self._poll_count += 1
        try:
            new_ip = self._poll_interface.get_ip()
            if new_ip and str(new_ip) != "None":
                manager = NetworkService.detect_interface_manager(self._poll_interface.name)
                backend_info = f" (via {manager})" if manager != 'manual' else ""
                logger.info(f"Connected {self._poll_interface.name} with IP: {new_ip}{backend_info}")
                self.show_info_dialog(
                    "Connection Successful",
                    f"{self._poll_interface.name} connected successfully{backend_info}\nIP: {new_ip}"
                )
                return False
        except Exception as e:
            logger.error(f"Error checking IP: {e}")

        if self._poll_count >= self._poll_max:
            logger.warning(f"IP not assigned after {self._poll_max} seconds")
            self.show_info_dialog(
                "Connection Started",
                f"{self._poll_interface.name} connection initiated.\nIP assignment may still be in progress."
            )
            return False
        return True

    def _poll_for_disconnect(self, interface, switch, max_attempts=10):
        """Poll for IP removal without blocking the GUI."""
        self._disconnect_count = 0
        self._disconnect_max = max_attempts
        self._disconnect_interface = interface
        self._disconnect_switch = switch
        GLib.timeout_add(500, self._poll_disconnect_check)

    def _poll_disconnect_check(self):
        """Called every 0.5 seconds to check if IP has been cleared."""
        self._disconnect_count += 1
        try:
            new_ip = self._disconnect_interface.get_ip()
            if not new_ip or str(new_ip) == "None":
                logger.info(f"Disconnected {self._disconnect_interface.name}")
                self.show_info_dialog(
                    "Disconnection Successful",
                    f"{self._disconnect_interface.name} has been disconnected successfully."
                )
                return False
        except Exception as e:
            logger.error(f"Error checking IP: {e}")

        if self._disconnect_count >= self._disconnect_max:
            logger.warning(f"IP not cleared after {self._disconnect_max * 0.5} seconds")
            self.show_info_dialog(
                "Disconnection Partial",
                f"{self._disconnect_interface.name} disconnected but may still have an IP.\nTry toggling the Status switch."
            )
            return False
        return True
