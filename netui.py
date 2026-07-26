"""
Main code of netui-gtk.
:Copyright: © 2020, Samy Abdellatif.
:License: MIT.

ifconfig,route are forked from https://github.com/rlisagor/pynetlinux under the MIT licence
thanks for developers rlisagor Roman Lisagor, Robert Grant, and williamjoy williamjoy
"""
from netmanage.ifconfig import list_ifs
from netmanage.route import get_default_if, get_default_gw
from netmanage.dhcpc import lease as dhcp_lease
from netmanage.network_service import connect_interface_dhcp, disconnect_interface, NetworkService
from config import get_config, Config

import gi
import logging
import os
from typing import List, Optional, Any

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
from manual_config import ManualConfigWindow
from advanced_config import AdvancedConfigWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# CSS styling for modern UI
CSS_STYLESHEET = """
/* Main window */
window {
    background-color: #f5f5f5;
}
listbox { background-color: transparent; }
listbox row { background-color: white; border: 1px solid #e0e0e0; border-top: none; padding: 4px; }
listbox row:first-child {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    border: 1px solid #2c3e50;
    border-radius: 8px 8px 0 0;
    padding: 8px;
}
listbox row:first-child label { color: #ecf0f1; font-weight: bold; }
listbox row:hover { background-color: #f0f7ff; }
listbox row:last-child { border-radius: 0 0 8px 8px; }
listbox row label { color: #2c3e50; }
button {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white; border: none; border-radius: 4px;
    padding: 4px 10px; font-size: 11px; font-weight: bold;
}
button:hover { background: linear-gradient(135deg, #2980b9 0%, #2471a3 100%); }
switch:checked { background-color: #27ae60; }
"""


class netUImainWindow(Gtk.Window):
    """Main application window for NetUI GTK network interface manager."""
    
    def __init__(self) -> None:
        Gtk.Window.__init__(self, title="NetUI - Network Interface Manager")
        self.config: Config = get_config()
        
        # Initialize interface list
        self.intF_list: List[Any] = []
        self._load_interfaces()
        
        # Window setup
        self.set_border_width(10)
        window_width = self.config.get('window_width', 700)
        window_height = self.config.get('window_height', 500)
        self.set_default_size(window_width, window_height)
        self.set_position(Gtk.WindowPosition.CENTER)
        # Don't use set_keep_above - it's intrusive to the user's workflow
        
        # Polling state containers (isolated per poll operation)
        self._poll_data = {}  # Stores poll callbacks/state keyed by unique IDs
        
        # Save window size before closing
        self.connect("delete-event", self.on_window_delete)
        
        # Load CSS stylesheet
        self._load_css()
        
        try:
            self.create_ui()
            logger.info("UI created successfully")
        except Exception as e:
            logger.error(f"Failed to create UI: {e}")
            self.show_error_dialog("UI Creation Error", f"Failed to create user interface: {e}")
    
    def _load_css(self) -> None:
        """Load CSS styling for modern UI."""
        try:
            screen = Gdk.Screen.get_default()
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(CSS_STYLESHEET.encode('utf-8'))
            Gtk.StyleContext.add_provider_for_screen(
                screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            logger.warning(f"Could not load CSS stylesheet: {e}")
    
    def _load_interfaces(self) -> None:
        """Load network interfaces with error handling."""
        try:
            self.intF_list = list_ifs()
            logger.info(f"Found {len(self.intF_list)} interfaces")
            for iface in self.intF_list:
                if iface.is_up():
                    ip = iface.get_ip()
                    logger.info(f"Interface {iface.name} is UP - IP: {ip}")
                else:
                    logger.info(f"Interface {iface.name} is DOWN")
        except Exception as e:
            logger.error(f"Failed to initialize interface list: {e}")
            self.intF_list = []
    
    def on_window_delete(self, widget: Gtk.Widget, event: object) -> bool:
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
    
    def show_error_dialog(self, title: str, message: str) -> None:
        """Display an error dialog to user."""
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
    
    def show_info_dialog(self, title: str, message: str) -> None:
        """Display an info dialog to the user."""
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
    
    def create_ui(self) -> None:
        """Create the main user interface."""
        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        # Header label
        header_label = Gtk.Label(
            label="<b>Network Interface Manager</b>",
            use_markup=True,
            xalign=0.5
        )
        vbox.pack_start(header_label, False, False, 6)
        
        # Scrolled window for interface list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)
        
        # Listbox for interfaces
        lbox = Gtk.ListBox()
        lbox.set_selection_mode(Gtk.SelectionMode.NONE)
        lbox.set_margin_top(10)
        lbox.set_margin_bottom(10)
        lbox.set_margin_start(10)
        lbox.set_margin_end(10)
        scrolled.add(lbox)
        
        # Header Row
        header_row = Gtk.ListBoxRow()
        header_row.set_activatable(False)
        header_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_row.add(header_hbox)
        
        # Header labels
        headers = [
            ("<b>Interface Details</b>", 35, 0),
            ("<b>Status</b>", 8, 0.5),
            ("<b>Connection</b>", 10, 0.5),
            ("<b>Configuration</b>", 12, 0.5),
            ("<b>Advanced</b>", 10, 0.5),
        ]
        for text, width_chars, xalign in headers:
            label = Gtk.Label(
                label=text, use_markup=True,
                width_chars=width_chars, xalign=xalign
            )
            header_hbox.pack_start(label, True, True, 6)
        lbox.add(header_row)
        
        # Iterate through interfaces and add one row for each
        for iface_index, interface in enumerate(self.intF_list):
            try:
                self._create_interface_row(lbox, interface, iface_index)
            except Exception as e:
                logger.error(f"Error creating UI row for interface {iface_index}: {e}")
                self._create_error_row(lbox, iface_index, str(e))
        
        # Footer with refresh button
        footer_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_refresh = Gtk.Button(label="🔄 Refresh")
        btn_refresh.connect("clicked", self._on_refresh_clicked)
        footer_hbox.pack_end(btn_refresh, False, False, 6)
        vbox.pack_start(footer_hbox, False, False, 0)
        
        logger.info("Window and UI components created successfully")
    
    def _create_interface_row(self, lbox: Gtk.ListBox, interface: Any, iface_index: int) -> None:
        """Create a row for a single network interface."""
        # Get interface details with error handling
        try:
            mac_addr = interface.get_mac() or "N/A"
            ip_addr = interface.get_ip() or "No IP"
            interface_details = f"{interface.name} | {mac_addr} | {ip_addr}"
        except Exception as e:
            logger.error(f"Error getting details for {interface.name}: {e}")
            interface_details = f"{interface.name} | Error getting details"
        
        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.add(hbox)
        
        # Interface details label
        label = Gtk.Label(label=interface_details, width_chars=35, xalign=0)
        hbox.pack_start(label, True, True, 6)
        
        # Up/Down switch
        up_switch = Gtk.Switch()
        up_switch.connect("notify::active", self.on_UpDown_activated, iface_index)
        up_switch.props.valign = Gtk.Align.CENTER
        try:
            up_switch.set_active(interface.is_up())
        except Exception as e:
            logger.error(f"Error checking interface status: {e}")
            up_switch.set_sensitive(False)
        hbox.pack_start(up_switch, False, False, 0)
        
        # Connect/Disconnect switch
        conn_switch = Gtk.Switch()
        conn_switch.connect("notify::active", self.on_ConDiscon_activated, iface_index)
        conn_switch.props.valign = Gtk.Align.CENTER
        try:
            ip_addr = interface.get_ip()
            conn_switch.set_active(ip_addr is not None and str(ip_addr) != "None")
        except Exception as e:
            logger.error(f"Error checking IP: {e}")
            conn_switch.set_sensitive(False)
        hbox.pack_start(conn_switch, False, False, 0)
        
        # Manual Config Button
        btn_config = Gtk.Button(label="Config")
        btn_config.connect("clicked", self.on_config_clicked, interface)
        hbox.pack_start(btn_config, False, False, 0)
        
        # Advanced Button
        btn_advanced = Gtk.Button(label="Advanced")
        btn_advanced.connect("clicked", self.on_advanced_clicked, interface)
        hbox.pack_start(btn_advanced, False, False, 0)
        
        lbox.add(row)
    
    def _create_error_row(self, lbox: Gtk.ListBox, iface_index: int, error_msg: str) -> None:
        """Create an error row for a failed interface load."""
        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.add(hbox)
        label = Gtk.Label(
            label=f"Error loading interface {iface_index}: {error_msg}",
            width_chars=40, xalign=0
        )
        hbox.pack_start(label, True, True, 10)
        lbox.add(row)
    
    def _on_refresh_clicked(self, widget: Gtk.Button) -> None:
        """Handle refresh button click - reload all interfaces."""
        logger.info("Refreshing interface list...")
        self.intF_list = list_ifs()
        # Remove old UI and recreate
        for child in self.get_children():
            self.remove(child)
        self.create_ui()
        self.show_all()
    
    def on_config_clicked(self, widget: Gtk.Button, interface: Any) -> None:
        """Handle manual config button click."""
        try:
            win = ManualConfigWindow(interface=interface)
            win.set_transient_for(self)
            win.set_modal(True)
            win.show_all()
        except Exception as e:
            logger.error(f"Failed to open manual config window: {e}")
            self.show_error_dialog("Configuration Error", f"Failed to open configuration window: {e}")
    
    def on_advanced_clicked(self, widget: Gtk.Button, interface: Any) -> None:
        """Handle advanced button click."""
        try:
            win = AdvancedConfigWindow(interface=interface)
            win.set_transient_for(self)
            win.set_modal(False)  # Non-modal so statistics can update
            win.show_all()
        except Exception as e:
            logger.error(f"Failed to open advanced window: {e}")
            self.show_error_dialog("Advanced Error", f"Failed to open advanced window: {e}")
    
    def on_UpDown_activated(self, switch: Gtk.Switch, gparam: object, iface_index: int) -> None:
        """Handle interface up/down switch activation."""
        try:
            interface = self.intF_list[iface_index]
            interface_name = interface.name
        except IndexError:
            logger.error(f"Invalid interface index: {iface_index}")
            self.show_error_dialog("Interface Error", f"Invalid interface index: {iface_index}")
            return
        
        try:
            if switch.get_active():
                if not interface.is_up():
                    interface.up()
                    logger.info(f"Brought up interface {interface_name}")
                    self.show_info_dialog("Interface Up", f"{interface_name} is now UP.")
                else:
                    logger.info(f"Interface {interface_name} was already up")
            else:
                if interface.is_up():
                    interface.down()
                    logger.info(f"Brought down interface {interface_name}")
                    self.show_info_dialog("Interface Down", f"{interface_name} is now DOWN.")
                else:
                    logger.info(f"Interface {interface_name} was already down")
        except PermissionError:
            logger.error(f"Permission denied for {interface_name}")
            self.show_error_dialog("Permission Error", "Permission denied. Please run as root or use sudo.")
            switch.set_active(not switch.get_active())  # Revert
        except Exception as e:
            logger.error(f"Failed to toggle {interface_name}: {e}")
            self.show_error_dialog("Interface Error", f"Failed to toggle {interface_name}: {e}")
            switch.set_active(not switch.get_active())  # Revert
    
    def _on_connect_complete(self, success: bool, result, interface: Any, switch: Gtk.Switch, manager: str) -> None:
        """Called on GTK main thread when async connect completes."""
        if success:
            logger.info(f"Connect succeeded for {interface.name}, polling for IP...")
            self._poll_for_ip(interface, switch, max_attempts=15)
        else:
            error_msg = result  # result is the error string when success=False
            logger.error(f"Failed to connect {interface.name}: {error_msg}")
            self.show_error_dialog("Connection Error", f"Failed to connect {interface.name}:\n{error_msg}")
            switch.set_active(False)
    
    def _on_disconnect_complete(self, success: bool, result, interface: Any, switch: Gtk.Switch) -> None:
        """Called on GTK main thread when async disconnect completes."""
        if success:
            logger.info(f"Disconnect succeeded for {interface.name}, polling IP removal...")
            self._poll_for_disconnect(interface, switch, max_attempts=10)
        else:
            error_msg = result  # result is the error string when success=False
            logger.error(f"Failed to disconnect {interface.name}: {error_msg}")
            self.show_error_dialog("Disconnection Error", f"Failed to disconnect {interface.name}:\n{error_msg}")
            switch.set_active(True)
    
    def on_ConDiscon_activated(self, switch: Gtk.Switch, gparam: object, iface_index: int) -> None:
        """Handle interface connect/disconnect switch activation (non-blocking)."""
        try:
            interface = self.intF_list[iface_index]
            interface_name = interface.name
        except IndexError:
            logger.error(f"Invalid interface index: {iface_index}")
            self.show_error_dialog("Interface Error", f"Invalid interface index: {iface_index}")
            return
        
        if switch.get_active():
            # Connect using async worker to avoid GUI freeze
            manager = NetworkService.detect_interface_manager(interface_name)
            logger.info(f"Interface {interface_name} is managed by: {manager}")
            logger.info(f"Connecting {interface_name} via DHCP (async)...")
            
            from netmanage.async_worker import AsyncWorker
            # NOTE: callback signature is callback(success, result) - matches our _on_connect_complete
            AsyncWorker.run_async(
                connect_interface_dhcp,
                lambda success, data, iface=interface, sw=switch, mgr=manager:
                    self._on_connect_complete(success, data, iface, sw, mgr),
                interface_name=interface_name
            )
        else:
            # Disconnect using async worker to avoid GUI freeze
            logger.info(f"Disconnecting {interface_name} (async)...")
            
            from netmanage.async_worker import AsyncWorker
            # NOTE: callback signature is callback(success, result) - matches our _on_disconnect_complete
            AsyncWorker.run_async(
                disconnect_interface,
                lambda success, data, iface=interface, sw=switch:
                    self._on_disconnect_complete(success, data, iface, sw),
                interface_name=interface_name
            )
    
    def _poll_for_ip(self, interface: Any, switch: Gtk.Switch, max_attempts: int = 15) -> None:
        """Poll for IP assignment without blocking the GUI."""
        poll_id = f"ip_poll_{id(interface)}"
        poll_data = {
            'count': 0,
            'max': max_attempts,
            'interface': interface,
            'switch': switch,
        }
        self._poll_data[poll_id] = poll_data
        
        def poll_check() -> bool:
            """Called every second to check if IP has been assigned."""
            data = self._poll_data.get(poll_id)
            if not data:
                return False  # Polling cancelled
            
            data['count'] += 1
            try:
                new_ip = data['interface'].get_ip()
                if new_ip and str(new_ip) != "None":
                    manager = NetworkService.detect_interface_manager(data['interface'].name)
                    backend_info = f" (via {manager})" if manager != 'manual' else ""
                    logger.info(f"Connected {data['interface'].name} with IP: {new_ip}{backend_info}")
                    self.show_info_dialog(
                        "Connection Successful",
                        f"{data['interface'].name} connected successfully{backend_info}\nIP: {new_ip}"
                    )
                    self._poll_data.pop(poll_id, None)
                    return False
            except Exception as e:
                logger.error(f"Error checking IP: {e}")
            
            if data['count'] >= data['max']:
                logger.warning(f"IP not assigned after {data['max']} seconds")
                self.show_info_dialog(
                    "Connection Started",
                    f"{data['interface'].name} connection initiated.\nIP assignment may still be in progress."
                )
                self._poll_data.pop(poll_id, None)
                return False
            return True
        
        GLib.timeout_add(1000, poll_check)
    
    def _poll_for_disconnect(self, interface: Any, switch: Gtk.Switch, max_attempts: int = 10) -> None:
        """Poll for IP removal without blocking the GUI."""
        poll_id = f"disconnect_poll_{id(interface)}"
        poll_data = {
            'count': 0,
            'max': max_attempts,
            'interface': interface,
            'switch': switch,
        }
        self._poll_data[poll_id] = poll_data
        
        def poll_check() -> bool:
            """Called every 0.5 seconds to check if IP has been cleared."""
            data = self._poll_data.get(poll_id)
            if not data:
                return False  # Polling cancelled
            
            data['count'] += 1
            try:
                new_ip = data['interface'].get_ip()
                if not new_ip or str(new_ip) == "None":
                    logger.info(f"Disconnected {data['interface'].name}")
                    self.show_info_dialog(
                        "Disconnection Successful",
                        f"{data['interface'].name} has been disconnected successfully."
                    )
                    self._poll_data.pop(poll_id, None)
                    return False
            except Exception as e:
                logger.error(f"Error checking IP: {e}")
            
            if data['count'] >= data['max']:
                logger.warning(f"IP not cleared after {data['max'] * 0.5} seconds")
                self.show_info_dialog(
                    "Disconnection Partial",
                    f"{data['interface'].name} disconnected but may still have an IP.\nTry toggling the Status switch."
                )
                self._poll_data.pop(poll_id, None)
                return False
            return True
        
        GLib.timeout_add(500, poll_check)