"""
NetManage package - Network interface management backend.
"""
from . import ifconfig
from . import route
from . import dhcpc
# Import commonly used items for convenience
from .ifconfig import Interface, list_ifs, iterifs, findif
from .route import get_default_if, get_default_gw

__all__ = [
    'Interface', 'list_ifs', 'iterifs', 'findif',
    'get_default_if', 'get_default_gw',
    'ifconfig', 'route', 'dhcpc',
]