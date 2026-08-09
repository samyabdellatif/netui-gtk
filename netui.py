"""
Main application window for NetUI GTK network interface manager.
:Copyright: © 2020, Samy Abdellatif.
:License: MIT.
"""
import gi
import logging
import os
from typing import List, Optional, Any, Dict

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

from netmanage.interface import Interface, list_ifs, InterfaceError, InterfacePermissionError
from netmanage.network_service import (
    connect_interface_dhcp,
    disconnect_interface,
    NetworkService,
)
from netmanage.async_worker import AsyncWorker
from config import get_config, Config
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
        self.interfaces: List[Interface] = []
        self._load_interfaces()

        # Window setup
        self.set_border_width(10)
        window_width = self.config.get('window_width', 700)
        window_height = self.config.get('window_height', 500)
        self.set_default_size(window_width, window_height)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Polling state containers (isolated per poll operation)
        self._poll_data: Dict[str, Dict[str, Any]] = {}

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
            self.interfaces = list_ifs()
            logger.info(f"Found {len(self.interfaces)} interfaces")
            for iface in self.interfaces:
                try:
                    if iface.is_up():
                        ip = iface.get_ip()
                        logger.info(f"Interface {iface.name} is UP - IP: {ip}")
                    else:
                        logger.info(f"Interface {iface.name} is DOWN")
                except InterfaceError as e:
                    logger.warning(f"Error checking interface {iface.name}: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize interface list: {e}")
            self.interfaces = []

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
        for interface in self.interfaces:
            try:
                self._create_interface_row(lbox, interface)
            except Exception as e:
                logger.error(f"Error creating UI row for {interface.name}: {e}")
                self._create_error_row(lbox, interface.name, str(e))

        # Footer with refresh button
        footer_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_refresh = Gtk.Button(label="🔄 Refresh")
        btn_refresh.connect("clicked", self._on_refresh_clicked)
        footer_hbox.pack_end(btn_refresh, False, False, 6)
        vbox.pack_start(footer_hbox, False, False, 0)

        logger.info("Window and UI components created successfully")

    def _create_interface_row(self, lbox: Gtk.ListBox, interface: Interface) -> None:
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
        up_switch.connect("notify::active", self.on_UpDown_activated, interface.name)
        up_switch.props.valign = Gtk.Align.CENTER
        try:
            up_switch.set_active(interface.is_up())
        except Exception as e:
            logger.error(f"Error checking interface status: {e}")
            up_switch.set_sensitive(False)
        hbox.pack_start(up_switch, False, False, 0)

        # Connect/Disconnect switch
        conn_switch = Gtk.Switch()
        conn_switch.connect("notify::active", self.on_ConDiscon_activated, interface.name)
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

    def _create_error_row(self, lbox: Gtk.ListBox, iface_name: str, error_msg: str) -> None:
        """Create an error row for a failed interface load."""
        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.add(hbox)
        label = Gtk.Label(
            label=f"Error loading interface {iface_name}: {error_msg}",
            width_chars=40, xalign=0
        )
        hbox.pack_start(label, True, True, 10)
        lbox.add(row)

    def _on_refresh_clicked(self, widget: Gtk.Button) -> None:
        """Handle refresh button click - reload all interfaces."""
        logger.info("Refreshing interface list...")
        # Cancel any pending polls
        self._cancel_all_polls()
        # Reload interfaces
        self._load_interfaces()
        # Remove old UI and recreate
        for child in self.get_children():
            self.remove(child)
        self.create_ui()
        self.show_all()

    def _cancel_all_polls(self) -> None:
        """Cancel all pending polling operations."""
        self._poll_data.clear()
        logger.info("Cancelled all pending poll operations")

    def _find_interface(self, name: str) -> Optional[Interface]:
        """Find an interface by name in the current list."""
        for iface in self.interfaces:
            if iface.name == name:
                return iface
        return None

    def on_config_clicked(self, widget: Gtk.Button, interface: Interface) -> None:
        """Handle manual config button click."""
        try:
            win = ManualConfigWindow(interface=interface)
            win.set_transient_for(self)
            win.set_modal(True)
            win.show_all()
        except Exception as e:
            logger.error(f"Failed to open manual config window: {e}")
            self.show_error_dialog("Configuration Error", f"Failed to open configuration window: {e}")

    def on_advanced_clicked(self, widget: Gtk.Button, interface: Interface) -> None:
        """Handle advanced button click."""
        try:
            win = AdvancedConfigWindow(interface=interface)
            win.set_transient_for(self)
            win.set_modal(False)  # Non-modal so statistics can update
            win.show_all()
        except Exception as e:
            logger.error(f"Failed to open advanced window: {e}")
            self.show_error_dialog("Advanced Error", f"Failed to open advanced window: {e}")

    def on_UpDown_activated(self, switch: Gtk.Switch, gparam: object, iface_name: str) -> None:
        """Handle interface up/down switch activation."""
        interface = self._find_interface(iface_name)
        if interface is None:
            logger.error(f"Interface not found: {iface_name}")
            self.show_error_dialog("Interface Error", f"Interface {iface_name} not found")
            switch.set_active(not switch.get_active())
            return

        try:
            if switch.get_active():
                if not interface.is_up():
                    interface.up()
                    logger.info(f"Brought up interface {iface_name}")
                    self.show_info_dialog("Interface Up", f"{iface_name} is now UP.")
                else:
                    logger.info(f"Interface {iface_name} was already up")
            else:
                if interface.is_up():
                    interface.down()
                    logger.info(f"Brought down interface {iface_name}")
                    self.show_info_dialog("Interface Down", f"{iface_name} is now DOWN.")
                else:
                    logger.info(f"Interface {iface_name} was already down")
        except InterfacePermissionError:
            logger.error(f"Permission denied for {iface_name}")
            self.show_error_dialog("Permission Error", "Permission denied. Please run as root or use sudo.")
            switch.set_active(not switch.get_active())  # Revert
        except Exception as e:
            logger.error(f"Failed to toggle {iface_name}: {e}")
            self.show_error_dialog("Interface Error", f"Failed to toggle {iface_name}: {e}")
            switch.set_active(not switch.get_active())  # Revert

    def _on_connect_complete(self, success: bool, result, iface_name: str, switch: Gtk.Switch, manager: str) -> None:
        """Called on GTK main thread when async connect completes."""
        if success:
            logger.info(f"Connect succeeded for {iface_name}, polling for IP...")
            self._poll_for_ip(iface_name, switch, max_attempts=15)
        else:
            error_msg = result  # result is the error string when success=False
            logger.error(f"Failed to connect {iface_name}: {error_msg}")
            self.show_error_dialog("Connection Error", f"Failed to connect {iface_name}:\n{error_msg}")
            switch.set_active(False)

    def _on_disconnect_complete(self, success: bool, result, iface_name: str, switch: Gtk.Switch) -> None:
        """Called on GTK main thread when async disconnect completes."""
        if success:
            logger.info(f"Disconnect succeeded for {iface_name}, polling IP removal...")
            self._poll_for_disconnect(iface_name, switch, max_attempts=10)
        else:
            error_msg = result  # result is the error string when success=False
            logger.error(f"Failed to disconnect {iface_name}: {error_msg}")
            self.show_error_dialog("Disconnection Error", f"Failed to disconnect {iface_name}:\n{error_msg}")
            switch.set_active(True)

    def on_ConDiscon_activated(self, switch: Gtk.Switch, gparam: object, iface_name: str) -> None:
        """Handle interface connect/disconnect switch activation (non-blocking)."""
        interface = self._find_interface(iface_name)
        if interface is None:
            logger.error(f"Interface not found: {iface_name}")
            self.show_error_dialog("Interface Error", f"Interface {iface_name} not found")
            switch.set_active(not switch.get_active())
            return

        if switch.get_active():
            # Connect using async worker to avoid GUI freeze
            manager = NetworkService.detect_interface_manager(iface_name)
            logger.info(f"Interface {iface_name} is managed by: {manager}")
            logger.info(f"Connecting {iface_name} via DHCP (async)...")

            AsyncWorker.run_async(
                connect_interface_dhcp,
                lambda success, data, name=iface_name, sw=switch, mgr=manager:
                    self._on_connect_complete(success, data, name, sw, mgr),
                interface_name=iface_name
            )
        else:
            # Disconnect using async worker to avoid GUI freeze
            logger.info(f"Disconnecting {iface_name} (async)...")

            AsyncWorker.run_async(
                disconnect_interface,
                lambda success, data, name=iface_name, sw=switch:
                    self._on_disconnect_complete(success, data, name, sw),
                interface_name=iface_name
            )

    def _poll_for_ip(self, iface_name: str, switch: Gtk.Switch, max_attempts: int = 15) -> None:
        """Poll for IP assignment without blocking the GUI."""
        poll_id = f"ip_poll_{iface_name}"
        poll_data = {
            'count': 0,
            'max': max_attempts,
            'iface_name': iface_name,
            'switch': switch,
        }
        self._poll_data[poll_id] = poll_data

        def poll_check() -> bool:
            """Called every second to check if IP has been assigned."""
            data = self._poll_data.get(poll_id)
            if not data:
                return False  # Polling cancelled

            data['count'] += 1
            interface = self._find_interface(data['iface_name'])
            if interface is None:
                self._poll_data.pop(poll_id, None)
                return False

            try:
                new_ip = interface.get_ip()
                if new_ip and str(new_ip) != "None":
                    manager = NetworkService.detect_interface_manager(data['iface_name'])
                    backend_info = f" (via {manager})" if manager != 'manual' else ""
                    logger.info(f"Connected {data['iface_name']} with IP: {new_ip}{backend_info}")
                    self.show_info_dialog(
                        "Connection Successful",
                        f"{data['iface_name']} connected successfully{backend_info}\nIP: {new_ip}"
                    )
                    self._poll_data.pop(poll_id, None)
                    return False
            except Exception as e:
                logger.error(f"Error checking IP: {e}")

            if data['count'] >= data['max']:
                logger.warning(f"IP not assigned after {data['max']} seconds")
                self.show_info_dialog(
                    "Connection Started",
                    f"{data['iface_name']} connection initiated.\nIP assignment may still be in progress."
                )
                self._poll_data.pop(poll_id, None)
                return False
            return True

        GLib.timeout_add(1000, poll_check)

    def _poll_for_disconnect(self, iface_name: str, switch: Gtk.Switch, max_attempts: int = 10) -> None:
        """Poll for IP removal without blocking the GUI."""
        poll_id = f"disconnect_poll_{iface_name}"
        poll_data = {
            'count': 0,
            'max': max_attempts,
            'iface_name': iface_name,
            'switch': switch,
        }
        self._poll_data[poll_id] = poll_data

        def poll_check() -> bool:
            """Called every 0.5 seconds to check if IP has been cleared."""
            data = self._poll_data.get(poll_id)
            if not data:
                return False  # Polling cancelled

            data['count'] += 1
            interface = self._find_interface(data['iface_name'])
            if interface is None:
                self._poll_data.pop(poll_id, None)
                return False

            try:
                new_ip = interface.get_ip()
                if not new_ip or str(new_ip) == "None":
                    logger.info(f"Disconnected {data['iface_name']}")
                    self.show_info_dialog(
                        "Disconnection Successful",
                        f"{data['iface_name']} has been disconnected successfully."
                    )
                    self._poll_data.pop(poll_id, None)
                    return False
            except Exception as e:
                logger.error(f"Error checking IP: {e}")

            if data['count'] >= data['max']:
                logger.warning(f"IP not cleared after {data['max'] * 0.5} seconds")
                self.show_info_dialog(
                    "Disconnection Partial",
                    f"{data['iface_name']} disconnected but may still have an IP.\nTry toggling the Status switch."
                )
                self._poll_data.pop(poll_id, None)
                return False
            return True

        GLib.timeout_add(500, poll_check)