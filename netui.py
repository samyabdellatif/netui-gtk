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
from gi.repository import Gtk
from manual_config import ManualConfigWindow
from advanced_config import AdvancedConfigWindow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    logger.info("Initializing interface list...")
    intF_list = list_ifs()
    logger.info(f"Found {len(intF_list)} interfaces")
    
    for iface in intF_list:
        try:
            if iface.is_up():
                # Note: The automatic shutdown of eno1 interface has been removed
                # as it requires root permissions and causes startup failures
                ip_addr = iface.get_ip()
                mac_addr = iface.get_mac()
                logger.info(f"Interface {iface.name} is UP - IP: {ip_addr}, MAC: {mac_addr}")
                print(f"{iface.name} interface is UP , IP ADDRESS: {ip_addr}")
            else:
                logger.info(f"Interface {iface.name} is DOWN")
                print(f"{iface.name} interface is DOWN")
        except Exception as e:
            logger.error(f"Error checking interface {iface.name}: {e}")
            print(f"Error checking interface {iface.name}: {e}")

    total_iface = len(intF_list)
    logger.info(f"Total number of interfaces installed: {total_iface}")
    print(f"total number of interfaces installed : {total_iface}")
    
except Exception as e:
    logger.error(f"Failed to initialize interface list: {e}")
    print(f"Error: Failed to initialize network interfaces: {e}")
    
class netUImainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="network interfaces")
        # Load configuration
        self.config = get_config()
        
        # setting and icon and border
        # self.set_default_icon_from_file("iplinkgui.ico")
        self.set_border_width(10)
        
        # Make window more prominent with saved size preferences
        window_width = self.config.get('window_width', 600)
        window_height = self.config.get('window_height', 400)
        self.set_default_size(window_width, window_height)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        
        # Save window size on destroy
        self.connect("destroy", self.on_window_destroy)
        
        try:
            self.create_ui()
            logger.info("UI created successfully")
        except Exception as e:
            logger.error(f"Failed to create UI: {e}")
            self.show_error_dialog("UI Creation Error", f"Failed to create user interface: {e}")
    
    def on_window_destroy(self, widget):
        """Save window size before closing."""
        try:
            width, height = self.get_size()
            self.config.set('window_width', width)
            self.config.set('window_height', height)
            logger.info(f"Window size saved: {width}x{height}")
        except Exception as e:
            logger.error(f"Failed to save window size: {e}")
        
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
    
    def _check_interface_managed(self, interface_name):
        """Check if interface is managed by NetworkManager or systemd-networkd."""
        import subprocess
        
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
                    if interface_name in line and 'unmanaged' not in line.lower():
                        return True
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
            if result.returncode == 0 and 'configured' in result.stdout.lower():
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return False
        
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
        for iface_index in range(len(intF_list)):
            try:
                interface = intF_list[iface_index]
                
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
            interface = intF_list[i]
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

    def on_ConDiscon_activated(self, switch, gparam, i):
        """Handle interface connect/disconnect switch activation"""
        try:
            interface = intF_list[i]
            interface_name = interface.name
            
            if switch.get_active():
                # Detect which service manages the interface
                manager = NetworkService.detect_interface_manager(interface_name)
                logger.info(f"Interface {interface_name} is managed by: {manager}")
                
                # Try to connect (DHCP) using appropriate backend
                try:
                    logger.info(f"Attempting to connect {interface_name} via DHCP")
                    
                    # Use unified connection function that auto-detects backend
                    success, message = connect_interface_dhcp(interface_name)
                    
                    if success:
                        # Verify connection
                        import time
                        time.sleep(1)  # Give time for IP assignment
                        new_ip = interface.get_ip()
                        
                        if new_ip and str(new_ip) != "None":
                            backend_info = f" (via {manager})" if manager != 'manual' else ""
                            logger.info(f"Successfully connected {interface_name} with IP: {new_ip}{backend_info}")
                            self.show_info_dialog(
                                "Connection Successful", 
                                f"{interface_name} connected successfully{backend_info}\nIP: {new_ip}"
                            )
                        else:
                            logger.warning(f"Connection initiated but waiting for IP assignment on {interface_name}")
                            self.show_info_dialog(
                                "Connection Started",
                                f"{interface_name} connection initiated.\n{message}"
                            )
                    else:
                        logger.error(f"Failed to connect {interface_name}: {message}")
                        self.show_error_dialog("Connection Error", f"Failed to connect {interface_name}:\n{message}")
                        switch.set_active(False)  # Revert switch
                        
                except PermissionError:
                    logger.error(f"Permission denied when connecting {interface_name}")
                    self.show_error_dialog("Permission Error", f"Failed to connect {interface_name}: Permission denied. Please run as root or use sudo.")
                    switch.set_active(False)  # Revert switch
                except Exception as e:
                    logger.error(f"Failed to connect {interface_name}: {e}")
                    self.show_error_dialog("Connection Error", f"Failed to connect {interface_name}: {e}")
                    switch.set_active(False)  # Revert switch
            else:
                # Try to disconnect (release IP)
                try:
                    logger.info(f"Attempting to disconnect {interface_name}")
                    
                    # Use unified disconnect function
                    success, message = disconnect_interface(interface_name)
                    
                    if success:
                        logger.info(f"Successfully disconnected {interface_name}: {message}")
                        
                        # Verify disconnection
                        import time
                        time.sleep(0.5)  # Give time for IP to be cleared
                        new_ip = interface.get_ip()
                        
                        if new_ip and str(new_ip) != "None":
                            logger.warning(f"Interface still has IP after disconnect: {new_ip}")
                            self.show_info_dialog(
                                "Disconnection Partial", 
                                f"{interface_name} disconnected but may still have an IP.\nTry toggling the Status switch."
                            )
                        else:
                            self.show_info_dialog(
                                "Disconnection Successful", 
                                f"{interface_name} has been disconnected successfully."
                            )
                    else:
                        logger.error(f"Failed to disconnect {interface_name}: {message}")
                        self.show_error_dialog(
                            "Disconnection Error", 
                            f"Failed to disconnect {interface_name}:\n{message}"
                        )
                        switch.set_active(True)  # Revert switch
                    
                except PermissionError:
                    logger.error(f"Permission denied when disconnecting {interface_name}")
                    self.show_error_dialog("Permission Error", f"Failed to disconnect {interface_name}: Permission denied. Please run as root or use sudo.")
                    switch.set_active(True)  # Revert switch
                except Exception as e:
                    logger.error(f"Failed to disconnect {interface_name}: {e}")
                    self.show_error_dialog("Disconnection Error", f"Failed to disconnect {interface_name}: {e}")
                    switch.set_active(True)  # Revert switch
                    
        except IndexError:
            logger.error(f"Invalid interface index: {i}")
            self.show_error_dialog("Interface Error", f"Invalid interface index: {i}")
        except Exception as e:
            logger.error(f"Unexpected error in on_ConDiscon_activated: {e}")
            self.show_error_dialog("Unexpected Error", f"An unexpected error occurred: {e}")
