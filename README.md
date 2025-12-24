# netui-gtk

A lightweight, Python-based graphical user interface for managing network interfaces on Linux systems using GTK+ 3.

> **⚠️ Work in Progress**: This project is currently under active development. Features may change or be unstable.

## Features

*   **Interface Management**: View status, MAC, and IP addresses. Toggle interfaces UP/DOWN.
*   **DHCP & Static IP**: Easily switch between DHCP and manual configuration (IP, Subnet, Gateway).
*   **DNS Configuration**: Set primary and secondary DNS servers.
*   **Auto-Sudo**: Automatically requests privileges when needed.

## Requirements

*   Linux with Python 3.x
*   GTK+ 3.0 & PyGObject (`python3-gi`)
*   `iproute2`

## Installation

### Run from Source

```bash
git clone https://github.com/samyabdellatif/netui-gtk
cd netui-gtk

# Install dependencies (Debian/Ubuntu example)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 iproute2

# Run
python3 -m netui-gtk
```

### Method 2: Build Standalone Binary (Universal)
Create a single executable file that runs on most Linux distributions (Fedora, Arch, etc.) without requiring Python installation.

1.  **Install PyInstaller:**
    ```bash
    pip3 install pyinstaller
    ```

2.  **Build the binary:**
    ```bash
    chmod +x netui-gtk/build.sh
    ./netui-gtk/build.sh
    ```
    The executable will be located in `netui-gtk/dist/netui-gtk`.

### Method 3: Build Debian Package (.deb)
For native installation on Debian, Ubuntu, Linux Mint, and Kali Linux.

1.  **Run the build script:**
    ```bash
    chmod +x netui-gtk/build_deb.sh
    ./netui-gtk/build_deb.sh
    ```

2.  **Install the package:**
    ```bash
    sudo apt install ./netui-gtk/dist/netui-gtk_*.deb
    ```

## License

This project is licensed under the MIT License.

## Credits

Created by Samy Abdellatif. Includes code from pynetlinux.