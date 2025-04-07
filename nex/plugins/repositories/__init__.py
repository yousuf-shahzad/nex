"""
Plugin repository implementations for different sources.
"""

from .spigot import SpigotRepository
from .modrinth import ModrinthRepository
from .hangar import HangarRepository
from .bukkit import BukkitRepository

__all__ = ['SpigotRepository', 'ModrinthRepository', 'HangarRepository', 'BukkitRepository'] 