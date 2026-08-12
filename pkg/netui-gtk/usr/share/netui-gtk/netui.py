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
    background-color: #f0f2f5;
    color: #1e293b;
}

/* Header bar */
headerbar {
    background-color: #1e293b;
    color: #f1f5f9;
    border: none;
    padding: 4px 8px;
    min-height: 44px;
}

headerbar label {
    color: #f1f5f9;
}

headerbar button {
    background-color: transparent;
    color: #f1f5f9;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 4px 10px;
    font-weight: 500;
}

headerbar button:hover {
    background-color: #334155;
}

.app-title {
    font-size: 15px;
    font-weight: 700;
    color: #f1f5f9;
}

.app-subtitle {
    font-size: 11px;
    color: rgba(241, 245, 249, 0.7);
}

/* Stats bar */
.stats-bar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 12px;
}

.stat-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 6px 12px;
    margin: 0 4px;
}

.stat-value {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
}

.stat-label {
    font-size: 10px;
    color: #64748b;
}

.stat-value.up { color: #10b981; }
.stat-value.down { color: #ef4444; }
.stat-value.connected { color: #06b6d4; }
.stat-value.total { color: #3b82f6; }

/* Search bar */
.search-bar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 12px;
}

.search-bar entry {
    background-color: #f0f2f5;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 6px 10px;
    color: #1e293b;
}

.search-bar entry:focus {
    border-color: #3b82f6;
}

/* Interface cards */
.interface-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin: 4px 8px;
    padding: 10px 12px;
}

.interface-card:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
}

.interface-card.up {
    border-left: 3px solid #10b981;
}

.interface-card.down {
    border-left: 3px solid #ef4444;
}

.interface-card.connected {
    border-left: 3px solid #06b6d4;
}

.iface-name {
    font-family: 'Monospace', 'Courier New', monospace;
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
}

.iface-detail {
    font-size: 11px;
    color: #64748b;
}

.iface-ip {
    font-family: 'Monospace', 'Courier New', monospace;
    font-size: 12px;
    color: #3b82f6;
    font-weight: 600;
}

/* Badges */
.badge {
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 600;
}

.badge-ethernet {
    background-color: #dbeafe;
    color: #1d4ed8;
}

.badge-wifi {
    background-color: #fef3c7;
    color: #b45309;
}

.badge-loopback {
    background-color: #f3e8ff;
    color: #7e22ce;
}

.badge-virtual {
    background-color: #f1f5f9;
    color: #475569;
}

.badge-bridge {
    background-color: #cffafe;
    color: #0e7490;
}

.badge-unknown {
    background-color: #f1f5f9;
    color: #64748b;
}

/* Status indicators */
.status-dot {
    min-width: 10px;
    min-height: 10px;
    border-radius: 50%;
    margin: 0 4px;
}

.status-dot.up {
    background-color: #10b981;
}

.status-dot.down {
    background-color: #ef4444;
}

.status-dot.connected {
    background-color: #06b6d4;
}

.status-text {
    font-size: 11px;
    font-weight: 600;
}

.status-text.up { color: #10b981; }
.status-text.down { color: #ef4444; }
.status-text.connected { color: #06b6d4; }

/* Backend badge */
.backend-badge {
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 9px;
    font-weight: 600;
}

.backend-nm {
    background-color: #dcfce7;
    color: #166534;
}

.backend-networkd {
    background-color: #e0e7ff;
    color: #3730a3;
}

.backend-manual {
    background-color: #fef3c7;
    color: #92400e;
}

/* Buttons */
button {
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
}

button.primary {
    background-color: #3b82f6;
    color: white;
    border: none;
}

button.primary:hover {
    background-color: #2563eb;
}

button.success {
    background-color: #10b981;
    color: white;
    border: none;
}

button.success:hover {
    background-color: #059669;
}

button.danger {
    background-color: #ef4444;
    color: white;
    border: none;
}

button.danger:hover {
    background-color: #dc2626;
}

button.ghost {
    background-color: transparent;
    color: #1e293b;
    border: 1px solid #e2e8f0;
}

button.ghost:hover {
    background-color: #e8f0fe;
    border-color: #cbd5e1;
}

button.flat {
    background-color: transparent;
    color: #64748b;
    border: none;
}

button.flat:hover {
    background-color: #e8f0fe;
    color: #1e293b;
}

button:disabled {
    opacity: 0.5;
}

/* Switches */
switch {
    min-width: 44px;
    min-height: 22px;
    border-radius: 11px;
    background-color: #cbd5e1;
}

switch:checked {
    background-color: #10b981;
}

switch slider {
    background-color: white;
    border-radius: 50%;
    min-width: 18px;
    min-height: 18px;
    margin: 2px;
}

/* Labels */
label {
    color: #1e293b;
}

label.info {
    color: #64748b;
    font-style: italic;
    font-size: 11px;
}

label.warning {
    color: #f59e0b;
    font-weight: 600;
}

label.error {
    color: #ef4444;
    font-weight: 600;
}

label.success {
    color: #10b981;
    font-weight: 600;
}

label.muted {
    color: #94a3b8;
    font-size: 11px;
}

/* Scrolled window */
scrolledwindow {
    background-color: #f0f2f5;
}

scrolledwindow viewport {
    background-color: #f0f2f5;
}

/* List box */
listbox {
    background-color: transparent;
}

listbox row {
    background-color: transparent;
    border: none;
    padding: 2px;
}

listbox row:hover {
    background-color: transparent;
}

/* Footer */
.footer-bar {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    padding: 6px 12px;
}

.footer-bar label {
    font-size: 10px;
    color: #94a3b8;
}

/* Empty state */
.empty-state {
    padding: 40px;
}

.empty-state .empty-title {
    font-size: 16px;
    font-weight: 600;
    color: #64748b;
    margin-top: 8px;
}

.empty-state .empty-subtitle {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 4px;
}
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
        self.set_border_width(0)
        window_width = self.config.get('window_width', 800)
        window_height = self.config.get('window_height', 600)
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

            # Try to load from external file first (more maintainable)
            css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styles', 'style.css')
            css_loaded = False
            if os.path.exists(css_file):
                try:
                    css_provider.load_from_path(css_file)
                    css_loaded = True
                except Exception as e:
                    logger.warning(f"Could not load external CSS file: {e}")

            # Fall back to inline CSS if external file failed
            if not css_loaded:
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

    def _get_interface_type(self, name: str) -> str:
        """Determine interface type from its name."""
        name_lower = name.lower()
        if name_lower == 'lo':
            return 'loopback'
        if name_lower.startswith(('eth', 'enp', 'ens', 'eno', 'enx')):
            return 'ethernet'
        if name_lower.startswith(('wl', 'wlan', 'wlp')):
            return 'wifi'
        if name_lower.startswith(('br', 'bridge')):
            return 'bridge'
        if name_lower.startswith(('virbr', 'veth', 'docker', 'tap', 'tun')):
            return 'virtual'
        return 'unknown'

    def _get_type_badge_class(self, iface_type: str) -> str:
        """Get CSS class for interface type badge."""
        return f"badge badge-{iface_type}"

    def _get_type_label(self, iface_type: str) -> str:
        """Get display label for interface type."""
        labels = {
            'ethernet': 'Ethernet',
            'wifi': 'Wi-Fi',
            'loopback': 'Loopback',
            'virtual': 'Virtual',
            'bridge': 'Bridge',
            'unknown': 'Interface',
        }
        return labels.get(iface_type, 'Interface')

    def _get_backend_badge_class(self, manager: str) -> str:
        """Get CSS class for backend badge."""
        class_map = {
            'networkmanager': 'backend-nm',
            'systemd-networkd': 'backend-networkd',
            'netctl': 'backend-netctl',
            'wpa_supplicant': 'backend-wpa',
            'dhcpcd': 'backend-dhcpcd',
            'dhclient': 'backend-dhclient',
            'wicd': 'backend-wicd',
        }
        css_class = class_map.get(manager, 'backend-manual')
        return f"backend-badge {css_class}"

    def _get_backend_label(self, manager: str) -> str:
        """Get display label for backend manager."""
        labels = {
            'networkmanager': 'NetworkManager',
            'systemd-networkd': 'systemd-networkd',
            'netctl': 'netctl',
            'wpa_supplicant': 'wpa_supplicant',
            'dhcpcd': 'dhcpcd',
            'dhclient': 'dhclient',
            'wicd': 'wicd',
            'manual': 'Manual',
        }
        return labels.get(manager, manager)

    def create_ui(self) -> None:
        """Create the main user interface."""
        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "NetUI"
        header.props.subtitle = "Network Interface Manager"
        self.set_titlebar(header)

        # Refresh button in header
        btn_refresh = Gtk.Button(label="🔄 Refresh")
        btn_refresh.get_style_context().add_class("flat")
        btn_refresh.connect("clicked", self._on_refresh_clicked)
        header.pack_end(btn_refresh)

        # Store the main container for targeted updates on refresh
        self._vbox = vbox

        # Build the content area
        self._create_content(vbox)

        logger.info("Window and UI components created successfully")

    def _create_content(self, vbox: Gtk.Box) -> None:
        """Create the main content area (stats, search, interface list, footer)."""
        # Summary stats bar
        stats_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        stats_bar.get_style_context().add_class("stats-bar")
        vbox.pack_start(stats_bar, False, False, 0)
        self._stats_bar = stats_bar
        self._stats_bar_labels = {}
        
        # Detect installed network managers for stats row
        try:
            self._network_managers = NetworkService.detect_installed_managers()
            running_managers = [m for m in self._network_managers if m['running']]
            installed_managers = [m for m in self._network_managers if m['installed'] and not m['running']]
            self._running_managers_text = ", ".join([m['name'] for m in running_managers]) if running_managers else "None"
            self._installed_managers_text = ", ".join([m['name'] for m in installed_managers]) if installed_managers else "None"
        except Exception as e:
            logger.warning(f"Error detecting network managers: {e}")
            self._network_managers = []
            self._running_managers_text = "Unknown"
            self._installed_managers_text = "Unknown"

        # Calculate stats
        total = len(self.interfaces)
        up_count = 0
        down_count = 0
        connected_count = 0
        for iface in self.interfaces:
            try:
                if iface.is_up():
                    up_count += 1
                else:
                    down_count += 1
                ip = iface.get_ip()
                if ip and str(ip) != "None":
                    connected_count += 1
            except Exception:
                pass

        # Total interfaces stat
        self._create_stat_card(stats_bar, "Total", str(total), "total")
        # Up interfaces stat
        self._create_stat_card(stats_bar, "Up", str(up_count), "up")
        # Down interfaces stat
        self._create_stat_card(stats_bar, "Down", str(down_count), "down")
        # Connected stat
        self._create_stat_card(stats_bar, "Connected", str(connected_count), "connected")

        # Search bar
        search_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        search_bar.get_style_context().add_class("search-bar")
        vbox.pack_start(search_bar, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search interfaces...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        search_bar.pack_start(self.search_entry, True, True, 0)

        # Managed-by info bar (shows which network managers are in control)
        managers_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        managers_bar.get_style_context().add_class("search-bar")
        vbox.pack_start(managers_bar, False, False, 0)

        managers_label = Gtk.Label(
            label=f"🔧 Running: {self._running_managers_text} | Installed: {self._installed_managers_text}",
            xalign=0
        )
        managers_label.get_style_context().add_class("iface-detail")
        managers_bar.pack_start(managers_label, True, True, 0)

        # Details button
        btn_managers_info = Gtk.Button(label="Details")
        btn_managers_info.get_style_context().add_class("ghost")
        btn_managers_info.connect("clicked", self._on_managers_info_clicked)
        managers_bar.pack_end(btn_managers_info, False, False, 0)

        # Scrolled window for interface list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)

        # Listbox for interfaces
        self.lbox = Gtk.ListBox()
        self.lbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.lbox.set_margin_top(4)
        self.lbox.set_margin_bottom(4)
        scrolled.add(self.lbox)

        # Add interface cards
        self._populate_interface_list()

        # Footer
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        footer.get_style_context().add_class("footer-bar")
        vbox.pack_start(footer, False, False, 0)

        footer_label = Gtk.Label(
            label=f"{total} interface(s) detected | Requires root privileges for changes"
        )
        footer.pack_start(footer_label, False, False, 0)

    def _create_stat_card(self, parent: Gtk.Box, label: str, value: str, css_class: str) -> None:
        """Create a stat card in the stats bar."""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.get_style_context().add_class("stat-card")

        value_label = Gtk.Label(label=value)
        value_label.get_style_context().add_class("stat-value")
        value_label.get_style_context().add_class(css_class)
        card.pack_start(value_label, False, False, 0)

        label_widget = Gtk.Label(label=label)
        label_widget.get_style_context().add_class("stat-label")
        card.pack_start(label_widget, False, False, 0)

        parent.pack_start(card, False, False, 0)

    def _populate_interface_list(self) -> None:
        """Populate the interface list with cards."""
        # Clear existing rows
        for child in self.lbox.get_children():
            self.lbox.remove(child)

        if not self.interfaces:
            # Empty state
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            empty_box.get_style_context().add_class("empty-state")

            empty_title = Gtk.Label(label="No interfaces found")
            empty_title.get_style_context().add_class("empty-title")
            empty_box.pack_start(empty_title, False, False, 0)

            empty_subtitle = Gtk.Label(label="Check that the system has network interfaces available")
            empty_subtitle.get_style_context().add_class("empty-subtitle")
            empty_box.pack_start(empty_subtitle, False, False, 0)

            row = Gtk.ListBoxRow()
            row.set_activatable(False)
            row.add(empty_box)
            self.lbox.add(row)
            return

        # Get search filter
        search_text = ""
        if hasattr(self, 'search_entry'):
            search_text = self.search_entry.get_text().strip().lower()

        # Add interface cards
        matching_count = 0
        for interface in self.interfaces:
            # Apply search filter
            if search_text and search_text not in interface.name.lower():
                continue

            matching_count += 1
            try:
                self._create_interface_card(interface)
            except Exception as e:
                logger.error(f"Error creating UI row for {interface.name}: {e}")
                self._create_error_row(interface.name, str(e))

        # Show "no results" message if search filter matches nothing
        if matching_count == 0 and search_text:
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            empty_box.get_style_context().add_class("empty-state")

            empty_title = Gtk.Label(label=f"No interfaces matching '{search_text}'")
            empty_title.get_style_context().add_class("empty-title")
            empty_box.pack_start(empty_title, False, False, 0)

            empty_subtitle = Gtk.Label(label="Try a different search term or clear the search")
            empty_subtitle.get_style_context().add_class("empty-subtitle")
            empty_box.pack_start(empty_subtitle, False, False, 0)

            row = Gtk.ListBoxRow()
            row.set_activatable(False)
            row.add(empty_box)
            self.lbox.add(row)

        self.lbox.show_all()

    def _create_interface_card(self, interface: Interface) -> None:
        """Create a card for a single network interface."""
        # Get interface details with error handling
        try:
            mac_addr = interface.get_mac() or "N/A"
            ip_addr = interface.get_ip() or "No IP"
        except Exception as e:
            logger.error(f"Error getting details for {interface.name}: {e}")
            mac_addr = "N/A"
            ip_addr = "Error"

        # Determine interface type
        iface_type = self._get_interface_type(interface.name)
        type_badge_class = self._get_type_badge_class(iface_type)
        type_label = self._get_type_label(iface_type)

        # Check status
        try:
            is_up = interface.is_up()
        except Exception:
            is_up = False

        has_ip = ip_addr not in ("No IP", "Error", "None")

        # Detect backend manager
        try:
            manager = NetworkService.detect_interface_manager(interface.name)
        except Exception:
            manager = 'manual'

        # Create card container
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card.get_style_context().add_class("interface-card")
        if is_up:
            card.get_style_context().add_class("up")
        else:
            card.get_style_context().add_class("down")
        if has_ip:
            card.get_style_context().add_class("connected")

        # Row 1: Name + type badge + status + backend
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Interface name
        name_label = Gtk.Label(label=interface.name)
        name_label.get_style_context().add_class("iface-name")
        name_label.set_xalign(0)
        row1.pack_start(name_label, False, False, 0)

        # Type badge
        type_badge = Gtk.Label(label=type_label)
        type_badge.get_style_context().add_class(type_badge_class)
        row1.pack_start(type_badge, False, False, 0)

        # Spacer
        row1.pack_start(Gtk.Label(), True, True, 0)

        # Status dot + text
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        status_dot = Gtk.Label(label="●")
        status_dot.get_style_context().add_class("status-dot")
        if is_up:
            status_dot.get_style_context().add_class("up")
        else:
            status_dot.get_style_context().add_class("down")
        status_box.pack_start(status_dot, False, False, 0)

        status_text = Gtk.Label(label="UP" if is_up else "DOWN")
        status_text.get_style_context().add_class("status-text")
        if is_up:
            status_text.get_style_context().add_class("up")
        else:
            status_text.get_style_context().add_class("down")
        status_box.pack_start(status_text, False, False, 0)
        row1.pack_start(status_box, False, False, 0)

        # Backend badge
        backend_badge = Gtk.Label(label=self._get_backend_label(manager))
        backend_badge.get_style_context().add_class(self._get_backend_badge_class(manager))
        row1.pack_start(backend_badge, False, False, 0)

        card.pack_start(row1, False, False, 0)

        # Row 2: MAC + IP details
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        mac_label = Gtk.Label(label=f"MAC: {mac_addr}")
        mac_label.get_style_context().add_class("iface-detail")
        mac_label.set_xalign(0)
        row2.pack_start(mac_label, False, False, 0)

        ip_label = Gtk.Label(label=f"IP: {ip_addr}")
        ip_label.get_style_context().add_class("iface-ip")
        ip_label.set_xalign(0)
        row2.pack_start(ip_label, False, False, 0)

        card.pack_start(row2, False, False, 0)

        # Row 3: Controls
        row3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Up/Down switch with label
        up_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        up_label = Gtk.Label(label="Status:")
        up_label.get_style_context().add_class("iface-detail")
        up_box.pack_start(up_label, False, False, 0)

        up_switch = Gtk.Switch()
        up_switch.props.valign = Gtk.Align.CENTER
        try:
            up_switch.set_active(is_up)
        except Exception as e:
            logger.error(f"Error checking interface status: {e}")
            up_switch.set_sensitive(False)
        # Connect signal AFTER setting state to avoid triggering during init
        up_switch.connect("notify::active", self.on_UpDown_activated, interface.name)
        up_box.pack_start(up_switch, False, False, 0)
        row3.pack_start(up_box, False, False, 0)

        # Connect/Disconnect switch with label
        conn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        conn_label = Gtk.Label(label="Connection:")
        conn_label.get_style_context().add_class("iface-detail")
        conn_box.pack_start(conn_label, False, False, 0)

        conn_switch = Gtk.Switch()
        conn_switch.props.valign = Gtk.Align.CENTER
        try:
            conn_switch.set_active(has_ip)
        except Exception as e:
            logger.error(f"Error checking IP: {e}")
            conn_switch.set_sensitive(False)
        # Connect signal AFTER setting state to avoid triggering during init
        conn_switch.connect("notify::active", self.on_ConDiscon_activated, interface.name)
        conn_box.pack_start(conn_switch, False, False, 0)
        row3.pack_start(conn_box, False, False, 0)

        # Spacer
        row3.pack_start(Gtk.Label(), True, True, 0)

        # Config button
        btn_config = Gtk.Button(label="⚙ Config")
        btn_config.get_style_context().add_class("ghost")
        btn_config.connect("clicked", self.on_config_clicked, interface)
        row3.pack_start(btn_config, False, False, 0)

        # Advanced button
        btn_advanced = Gtk.Button(label="📊 Advanced")
        btn_advanced.get_style_context().add_class("ghost")
        btn_advanced.connect("clicked", self.on_advanced_clicked, interface)
        row3.pack_start(btn_advanced, False, False, 0)

        card.pack_start(row3, False, False, 0)

        # Add card to list
        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        row.add(card)
        self.lbox.add(row)

    def _create_error_row(self, iface_name: str, error_msg: str) -> None:
        """Create an error row for a failed interface load."""
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        card.get_style_context().add_class("interface-card")
        card.get_style_context().add_class("down")

        label = Gtk.Label(
            label=f"Error loading interface {iface_name}: {error_msg}",
            xalign=0
        )
        label.get_style_context().add_class("error")
        card.pack_start(label, True, True, 0)

        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        row.add(card)
        self.lbox.add(row)

    def _on_managers_info_clicked(self, widget: Gtk.Button) -> None:
        """Show detailed network managers information dialog."""
        lines = []
        for mgr in self._network_managers:
            status = "● Running" if mgr['running'] else ("○ Installed" if mgr['installed'] else "✗ Not found")
            lines.append(f"{mgr['display_name']}: {status}")
            lines.append(f"    {mgr['description']}")

        if not lines:
            lines.append("No network managers detected on this system.")

        dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format="Network Management Tools"
        )
        dialog.format_secondary_text("\n".join(lines))
        dialog.run()
        dialog.destroy()

    def _on_search_changed(self, entry: Gtk.SearchEntry) -> None:
        """Handle search text changes - filter interface list."""
        self._populate_interface_list()

    def _on_refresh_clicked(self, widget: Gtk.Button) -> None:
        """Handle refresh button click - reload all interfaces."""
        logger.info("Refreshing interface list...")
        # Cancel any pending polls
        self._cancel_all_polls()
        # Reload interfaces and rebuild the entire UI
        self._load_interfaces()
        self._update_stats()

    def _update_stats(self) -> None:
        """Update the summary stats bar by rebuilding the inner UI."""
        if hasattr(self, '_vbox'):
            # Remove all children from the inner vbox (keeps titlebar intact)
            for child in self._vbox.get_children():
                self._vbox.remove(child)
            self._create_content(self._vbox)
        else:
            # Fallback: rebuild everything
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
