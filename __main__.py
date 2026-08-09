"""
Main routine of netui-gtk3.
:Copyright: © 2020, Samy Abdellatif.
:License: MIT.
"""
import os
import sys
import subprocess
import gi
import shutil
import argparse

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from netui import netUImainWindow


def check_dependencies() -> bool:
    """Check for required system tools."""
    required = ['ip']  # iproute2 package
    dhcp_clients = ['dhclient', 'dhcpcd', 'udhcpc']

    missing = [cmd for cmd in required if not shutil.which(cmd)]
    if missing:
        print(f"ERROR: Required commands not found: {', '.join(missing)}")
        print("Install: sudo apt install iproute2")
        return False

    if not any(shutil.which(cmd) for cmd in dhcp_clients):
        print("WARNING: No DHCP client found!")
        print("DHCP functionality will be limited.")
        print("Install one of:")
        print("  sudo apt install isc-dhcp-client (dhclient)")
        print("  sudo apt install dhcpcd")

    return True


def check_network_manager() -> bool:
    """Check if NetworkManager is running and warn user."""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'NetworkManager'],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            print("INFO: NetworkManager is running and will handle network connections.")
            print("      Interfaces managed by NetworkManager will use it automatically.")
            print("      To manage interfaces manually, stop NetworkManager:")
            print("        sudo systemctl stop NetworkManager")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return False


def check_root_privileges() -> bool:
    """Check if the application is running with root privileges."""
    return os.geteuid() == 0


def restart_with_sudo() -> None:
    """Restart the application with sudo privileges."""
    try:
        # Build the command to run
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            cmd_base = [sys.executable] + sys.argv[1:]
        else:
            # Running as Python script
            cmd_base = [sys.executable, os.path.abspath(__file__)] + sys.argv[1:]

        # Check for privilege escalation tools
        if shutil.which('sudo'):
            cmd = ['sudo', '-E'] + cmd_base
        elif shutil.which('pkexec'):
            cmd = ['pkexec'] + cmd_base
        else:
            print("ERROR: No privilege escalation tool found. Please install sudo or pkexec.")
            print("  sudo: apt install sudo")
            print("  pkexec: apt install policykit-1")
            sys.exit(1)

        print(f"Restarting with elevated privileges...")
        sys.stdout.flush()

        # Run with sudo - the '-E' flag preserves the environment automatically
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print(f"WARNING: Application exited with code {result.returncode}")

        sys.exit(result.returncode)

    except FileNotFoundError:
        print(f"ERROR: Privilege escalation tool not found. Cannot elevate privileges.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to restart with elevated privileges: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='NetUI-GTK - Network Interface Manager',
        epilog='Note: Some features require root privileges.'
    )
    parser.add_argument('--version', action='version', version='netui-gtk 1.0.0')
    parser.add_argument('--check', action='store_true',
                       help='Check system dependencies and exit')
    parser.add_argument('--list', action='store_true',
                       help='List network interfaces and exit')
    args = parser.parse_args()

    # Handle --check flag
    if args.check:
        print("Running system check...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        check_script = os.path.join(script_dir, 'check_system.py')
        if os.path.exists(check_script):
            subprocess.run([sys.executable, check_script])
        else:
            print("check_system.py not found")
        sys.exit(0)

    # Handle --list flag (requires some privileges)
    if args.list:
        print("Network Interfaces:")
        try:
            from netmanage.interface import list_ifs
            interfaces = list_ifs()
            for iface in interfaces:
                print(f"  - {iface.name}")
                try:
                    print(f"    MAC: {iface.get_mac()}")
                    ip = iface.get_ip()
                    print(f"    IP:  {ip if ip else 'None'}")
                    print(f"    UP:  {'Yes' if iface.is_up() else 'No'}")
                except Exception as e:
                    print(f"    Error: {e}")
        except Exception as e:
            print(f"Error listing interfaces: {e}")
        sys.exit(0)

    print("Starting netui-gtk application...")

    # Check dependencies first
    if not check_dependencies():
        print("\nCannot continue without required dependencies.")
        sys.exit(1)

    # Check if running with root privileges
    if not check_root_privileges():
        print("This application requires root privileges to manage network interfaces.")
        print("Requesting sudo permissions...")
        restart_with_sudo()
        # restart_with_sudo only returns on failure
        sys.exit(1)

    print("Running with root privileges.")

    # Check for NetworkManager conflicts
    check_network_manager()

    # Create and run the main window
    win = netUImainWindow()
    win.connect("destroy", Gtk.main_quit)
    print("GUI window should now be visible!")
    win.show_all()
    print("Application is running. Close the window to exit.")
    Gtk.main()
    print("Application closed.")


if __name__ == '__main__':
    main()