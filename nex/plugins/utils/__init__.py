"""
Utility functions for plugin management.
"""

from .dependency import DependencyResolver, DependencyError
from .version import VersionManager, VersionError

__all__ = ['DependencyResolver', 'DependencyError', 'VersionManager', 'VersionError'] 