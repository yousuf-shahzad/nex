"""
Plugin repository implementations for different sources.
"""

from .spigot import SpigotRepository
from .modrinth import ModrinthRepository

__all__ = ['SpigotRepository', 'ModrinthRepository'] 