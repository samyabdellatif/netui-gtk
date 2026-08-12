#!/bin/bash
set -e

# Configuration
APP_NAME="netui-gtk"
VERSION="1.0.0"
ARCH="all"
STAGING_DIR="deb_staging"
DEB_NAME="${APP_NAME}_${VERSION}_${ARCH}.deb"

echo "Starting build process for $APP_NAME..."

# Clean up previous builds
rm -rf $STAGING_DIR
rm -f $DEB_NAME

# Create directory structure
mkdir -p $STAGING_DIR/usr/share/$APP_NAME
mkdir -p $STAGING_DIR/usr/share/$APP_NAME/styles
mkdir -p $STAGING_DIR/usr/share/$APP_NAME/netmanage
mkdir -p $STAGING_DIR/usr/bin
mkdir -p $STAGING_DIR/usr/share/applications
mkdir -p $STAGING_DIR/usr/share/pixmaps
mkdir -p $STAGING_DIR/usr/share/polkit-1/actions
mkdir -p $STAGING_DIR/DEBIAN

# Copy application files
echo "Copying files..."
cp __main__.py $STAGING_DIR/usr/share/$APP_NAME/
cp __init__.py $STAGING_DIR/usr/share/$APP_NAME/
cp netui.py $STAGING_DIR/usr/share/$APP_NAME/
cp config.py $STAGING_DIR/usr/share/$APP_NAME/
cp manual_config.py $STAGING_DIR/usr/share/$APP_NAME/
cp advanced_config.py $STAGING_DIR/usr/share/$APP_NAME/
cp -r netmanage/* $STAGING_DIR/usr/share/$APP_NAME/netmanage/
cp styles/style.css $STAGING_DIR/usr/share/$APP_NAME/styles/

# Copy icon
if [ -f "netui.ico" ]; then
    cp netui.ico $STAGING_DIR/usr/share/$APP_NAME/
    cp netui.ico $STAGING_DIR/usr/share/pixmaps/$APP_NAME.ico
fi

# Copy desktop file
if [ -f "$APP_NAME.desktop" ]; then
    cp $APP_NAME.desktop $STAGING_DIR/usr/share/applications/
fi

# Copy polkit policy
if [ -f "com.github.netui-gtk.policy" ]; then
    cp com.github.netui-gtk.policy $STAGING_DIR/usr/share/polkit-1/actions/
fi

# Remove __pycache__ directories to minimize package size
find "$STAGING_DIR" -name "__pycache__" -type d -exec rm -rf {} +

# Create executable wrapper script
echo "Creating launcher..."
cat > $STAGING_DIR/usr/bin/$APP_NAME << EOF
#!/bin/sh
exec python3 /usr/share/$APP_NAME/__main__.py "\$@"
EOF
chmod 755 $STAGING_DIR/usr/bin/$APP_NAME

# Calculate installed size (in KB)
INSTALLED_SIZE=$(du -s $STAGING_DIR/usr | cut -f1)

# Create control file
echo "Creating control file..."
cat > $STAGING_DIR/DEBIAN/control << EOF
Package: $APP_NAME
Version: $VERSION
Section: net
Priority: optional
Architecture: $ARCH
Depends: python3, python3-gi, gir1.2-gtk-3.0, iproute2
Recommends: dhcpcd | dhclient | udhcpc, networkmanager, systemd
Maintainer: Samy Abdellatif
Installed-Size: $INSTALLED_SIZE
Description: Network Interface Management GUI
 A lightweight GTK+ utility to manage network interfaces, routes, and DHCP.
 .
 Features:
  - Interface management (up/down, DHCP, static IP)
  - Advanced settings (MTU, MAC cloning, promiscuous mode)
  - Real-time statistics monitoring
  - Automatic network manager detection (NetworkManager, systemd-networkd,
    netctl, wpa_supplicant, dhcpcd, dhclient, Wicd)
  - Modern professional GTK+ 3 interface
EOF

# Create postinst script
echo "Creating postinst script..."
cat > $STAGING_DIR/DEBIAN/postinst << 'EOF'
#!/bin/sh
set -e

# Update desktop database if available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi

# Update icon cache if available
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f /usr/share/pixmaps 2>/dev/null || true
fi

exit 0
EOF
chmod 755 $STAGING_DIR/DEBIAN/postinst

# Create prerm script
echo "Creating prerm script..."
cat > $STAGING_DIR/DEBIAN/prerm << 'EOF'
#!/bin/sh
set -e
exit 0
EOF
chmod 755 $STAGING_DIR/DEBIAN/prerm

# Build the package
echo "Building .deb package..."
dpkg-deb --build $STAGING_DIR $DEB_NAME

# Cleanup staging
rm -rf $STAGING_DIR

echo "Build complete: $DEB_NAME"
echo ""
echo "Package contents:"
dpkg-deb --contents $DEB_NAME
echo ""
echo "Install with: sudo dpkg -i $DEB_NAME"