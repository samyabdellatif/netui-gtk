"""
Compatibility shim for the old ifconfig module.
Re-exports from the new interface module.
"""
from .interface import (
    Interface,
    InterfaceError,
    InterfaceNotFoundError,
    InvalidInterfaceNameError,
    InterfacePermissionError,
    iterifs,
    list_ifs,
    findif,
    shutdown,
)

__all__ = [
    'Interface',
    'InterfaceError',
    'InterfaceNotFoundError',
    'InvalidInterfaceNameError',
    'InterfacePermissionError',
    'iterifs',
    'list_ifs',
    'findif',
    'shutdown',
]