#!/bin/bash
# Build wrapper script for netui-gtk

echo "Running syntax check..."
# Compile to check for syntax errors, but don't keep the __pycache__
python3 -m compileall -q .

if [ $? -eq 0 ]; then
    echo "Syntax check passed."
    chmod +x build_deb.sh
    ./build_deb.sh
else
    echo "Syntax check failed. Aborting build."
    exit 1
fi