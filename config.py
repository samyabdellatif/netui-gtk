"""
Configuration management for netui-gtk.
Follows XDG Base Directory Specification.
:Copyright: © 2020, Samy Abdellatif.
:License: MIT.
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    """Manage application configuration using XDG standards."""
    
    def __init__(self):
        # XDG Base Directory specification
        self.config_dir = os.path.join(
            os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
            'netui-gtk'
        )
        self.config_file = os.path.join(self.config_dir, 'settings.json')
        self.default_config = {
            'show_virtual_interfaces': False,
            'auto_refresh_interval': 5,
            'preferred_dhcp_client': 'auto',  # auto, dhclient, dhcpcd, udhcpc
            'show_ipv6': True,
            'window_width': 600,
            'window_height': 400,
            'confirm_on_disconnect': True,
            'theme': 'default'
        }
        self.config = self.default_config.copy()
        self._ensure_config_dir()
        self.load()
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            logger.info(f"Config directory ensured at: {self.config_dir}")
        except PermissionError:
            logger.warning(f"Cannot create config directory: {self.config_dir}")
        except Exception as e:
            logger.error(f"Error creating config directory: {e}")
    
    def load(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle new settings
                    self.config = {**self.default_config, **loaded_config}
                    logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info("No config file found, using defaults")
                self.save()  # Create default config file
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file, using defaults")
            self.config = self.default_config.copy()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self.default_config.copy()
    
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
                logger.info(f"Configuration saved to {self.config_file}")
        except PermissionError:
            logger.warning(f"Cannot save config: Permission denied for {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value and save."""
        self.config[key] = value
        self.save()
    
    def reset(self):
        """Reset configuration to defaults."""
        self.config = self.default_config.copy()
        self.save()
        logger.info("Configuration reset to defaults")


# Global config instance
_config_instance = None

def get_config():
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
