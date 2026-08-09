"""
NetManage package - Network interface management backend.
"""
from . import interface
from . import route
from . import dhcpc
# Import commonly used items for convenience
from .interface import Interface, list_ifs, iterifs, findif, shutdown
from .route import get_default_if, get_default_gw

__all__ = [
    'Interface', 'list_ifs', 'iterifs', 'findif', 'shutdown',
    'get_default_if', 'get_default_gw',
    'interface', 'route', 'dhcpc',
]