"""
NetUI-GTK: A lightweight, Python-based graphical user interface for managing
network interfaces on Linux systems using GTK+ 3.
"""
from netmanage import ifconfig, route, dhcpc
from . import netui

__title__ = 'netui-gtk'
__version__ = '1.0.0'
__author__ = 'Samy Abdellatif'
__license__ = 'MIT'
__docformat__ = 'restructuredtext en'