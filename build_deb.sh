#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Configuration
APP_NAME="netui-gtk"
VERSION="0.0.1"
ARCH="amd64"
DEB_NAME="${APP_NAME}_${VERSION}_${ARCH}"
BUILD_DIR="dist/deb_build"

# 1. Build the binary if it doesn't exist
if [ ! -f "dist/$APP_NAME" ]; then
    echo "Binary not found. Running build.sh..."
    if [ -f "./build.sh" ]; then
        chmod +x ./build.sh
        ./build.sh
    else
        echo "Error: build.sh not found!"
        exit 1
    fi
fi

# 2. Prepare directory structure
echo "Creating directory structure..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"

# 3. Copy files
echo "Copying files..."
cp "dist/$APP_NAME" "$BUILD_DIR/usr/bin/"
chmod 755 "$BUILD_DIR/usr/bin/$APP_NAME"

# Check for desktop file, create if missing
if [ -f "$APP_NAME.desktop" ]; then
    cp "$APP_NAME.desktop" "$BUILD_DIR/usr/share/applications/"
else
    echo "Warning: $APP_NAME.desktop not found. Please create it for full integration."
fi

# Check for icon
if [ -f "$APP_NAME.svg" ]; then
    cp "$APP_NAME.svg" "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps/"
fi

# 4. Create Control File
echo "Creating control file..."
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $VERSION
Architecture: $ARCH
Maintainer: Samy Abdellatif <samiahmed086@gmail.com>
Depends: libgtk-3-0, libgirepository-1.0-1, iproute2
Section: net
Priority: optional
Description: GTK3 GUI for managing network interfaces
 A lightweight, Python-based graphical user interface for managing 
 network interfaces on Linux systems using GTK+ 3.
EOF

# 5. Build .deb
echo "Building .deb package..."
dpkg-deb --build "$BUILD_DIR" "dist/${DEB_NAME}.deb"

echo "Done! Package saved to dist/${DEB_NAME}.deb"