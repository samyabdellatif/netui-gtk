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

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from netui import *

def check_root_privileges():
    """Check if the application is running with root privileges"""
    return os.geteuid() == 0

def restart_with_sudo():
    """Restart the application with sudo privileges"""
    try:
        # Preserve environment variables needed for GUI display
        env = os.environ.copy()
        display_vars = ['DISPLAY', 'XAUTHORITY', 'DBUS_SESSION_BUS_ADDRESS', 'XDG_RUNTIME_DIR']
        sudo_env = ['-E']
        for var in display_vars:
            if var in env:
                sudo_env.append(f'{var}={env[var]}')
        
        # Determine command based on execution mode (frozen or script)
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            cmd_base = [sys.executable] + sys.argv[1:]
        else:
            # Running as Python script
            cmd_base = [sys.executable, os.path.abspath(__file__)] + sys.argv[1:]

        # Check for sudo or pkexec availability
        if shutil.which('sudo'):
            cmd = ['sudo'] + sudo_env + cmd_base
        elif shutil.which('pkexec'):
            # pkexec clears env, so we use 'env' to restore them
            cmd = ['pkexec', 'env'] + sudo_env + cmd_base
        else:
            raise RuntimeError("No privilege escalation tool (sudo or pkexec) found.")

        print(f"Restarting with command: {cmd}")
        subprocess.call(cmd)
        sys.exit(0)
    except Exception as e:
        print(f"Failed to restart with sudo: {e}")
        sys.exit(1)

def main():
    print("Starting netui-gtk application...")
    
    # Check if running with root privileges
    if not check_root_privileges():
        print("This application requires root privileges to manage network interfaces.")
        print("Requesting sudo permissions...")
        restart_with_sudo()
    
    print("Running with root privileges.")
    
    win = netUImainWindow()
    win.connect("destroy", Gtk.main_quit)
    print("GUI window should now be visible!")
    win.show_all()
    print("Application is running. Close the window to exit.")
    Gtk.main()
    print("Application closed.")

if __name__ == '__main__':
    main()
