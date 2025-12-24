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
mkdir -p $STAGING_DIR/usr/bin
mkdir -p $STAGING_DIR/usr/share/applications
mkdir -p $STAGING_DIR/DEBIAN

# Copy application files
# We only copy necessary source files, excluding build artifacts and git files
echo "Copying files..."
cp netui.py $STAGING_DIR/usr/share/$APP_NAME/
cp manual_config.py $STAGING_DIR/usr/share/$APP_NAME/
cp -r netmanage $STAGING_DIR/usr/share/$APP_NAME/
# Remove __pycache__ directories to minimize package size
find "$STAGING_DIR" -name "__pycache__" -type d -exec rm -rf {} +

# Copy icon if it exists
if [ -f "iplinkgui.ico" ]; then
    cp iplinkgui.ico $STAGING_DIR/usr/share/$APP_NAME/
fi

# Create executable wrapper script
echo "Creating launcher..."
cat > $STAGING_DIR/usr/bin/$APP_NAME << EOF
#!/bin/sh
cd /usr/share/$APP_NAME
exec python3 netui.py "\$@"
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
Depends: python3, python3-gi, gir1.2-gtk-3.0, net-tools
Maintainer: Samy Abdellatif
Installed-Size: $INSTALLED_SIZE
Description: Network Interface Management GUI
 A lightweight GTK+ utility to manage network interfaces, routes, and DHCP.
EOF

# Build the package
echo "Building .deb package..."
dpkg-deb --build $STAGING_DIR $DEB_NAME

# Cleanup staging
rm -rf $STAGING_DIR

echo "Build complete: $DEB_NAME"