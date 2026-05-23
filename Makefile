# Makefile for NetUI-GTK
# Network Interface Manager
# Author: Samy Abdellatif
# License: MIT

.PHONY: help install uninstall install-user uninstall-user check test clean

# Default target
help:
	@echo ""
	@echo "╔════════════════════════════════════════════════╗"
	@echo "║  NetUI-GTK - Network Interface Manager        ║"
	@echo "╚════════════════════════════════════════════════╝"
	@echo ""
	@echo "Available targets:"
	@echo ""
	@echo "  make install        - Install system-wide (requires sudo)"
	@echo "  make install-user   - Install for current user only"
	@echo "  make uninstall      - Uninstall system-wide (requires sudo)"
	@echo "  make uninstall-user - Uninstall user installation"
	@echo "  make check          - Check system dependencies"
	@echo "  make test           - Run basic tests"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make run            - Run from source (requires sudo)"
	@echo ""
	@echo "Quick start:"
	@echo "  1. make check       - Verify dependencies"
	@echo "  2. make install     - Install (or make install-user)"
	@echo "  3. netui-gtk        - Launch application"
	@echo ""

# Check system dependencies
check:
	@echo "Checking system dependencies..."
	@python3 check_system.py

# Run basic tests
test:
	@echo "Running module import tests..."
	@python3 -c "from netui import *; print('✓ netui module OK')"
	@python3 -c "from manual_config import ManualConfigWindow; print('✓ manual_config module OK')"
	@python3 -c "from advanced_config import AdvancedConfigWindow; print('✓ advanced_config module OK')"
	@python3 -c "from config import get_config; print('✓ config module OK')"
	@python3 -c "from netmanage.dhcpc import lease; print('✓ dhcpc module OK')"
	@python3 -c "from netmanage.advanced import *; print('✓ advanced module OK')"
	@echo "✅ All tests passed!"

# Install system-wide (requires sudo)
install:
	@echo "Installing NetUI-GTK system-wide..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: System-wide installation requires sudo"; \
		echo "Run: sudo make install"; \
		exit 1; \
	fi
	@./install.sh

# Install for current user
install-user:
	@echo "Installing NetUI-GTK for current user..."
	@./install.sh

# Uninstall system-wide
uninstall:
	@echo "Uninstalling NetUI-GTK (system-wide)..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: System-wide uninstallation requires sudo"; \
		echo "Run: sudo make uninstall"; \
		exit 1; \
	fi
	@./uninstall.sh

# Uninstall user installation
uninstall-user:
	@echo "Uninstalling NetUI-GTK (user)..."
	@./uninstall.sh

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Clean complete"

# Run from source (development)
run:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Running with sudo..."; \
		sudo python3 __main__.py; \
	else \
		python3 __main__.py; \
	fi

# Safety check
safety:
	@./safety-check.sh

# Show version
version:
	@python3 __main__.py --version

# List interfaces
list:
	@python3 __main__.py --list
