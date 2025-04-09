"""
Version management utilities for plugins.
"""
from typing import Dict, Any, Optional
from pathlib import Path
from packaging import version
from rich.console import Console

console = Console()

class VersionError(Exception):
    """Exception raised for version-related errors."""
    pass

class VersionManager:
    """Handles plugin version management and compatibility checking."""
    
    def __init__(self, server_dir: Path):
        """Initialize with server directory path."""
        self.server_dir = server_dir
    
    def check_version_compatibility(self, plugin_id: str, source: str, plugin_version: str) -> bool:
        """Check if a plugin version is compatible with the server version."""
        # Get server version from server.properties
        server_props = self.server_dir / "server.properties"
        if not server_props.exists():
            return True  # If no server.properties, assume compatibility
        
        with open(server_props, 'r') as f:
            for line in f:
                if line.startswith("version="):
                    server_version = line.split("=")[1].strip()
                    break
            else:
                return True  # If no version found, assume compatibility
        
        # Get plugin version info
        plugin_info = self._get_plugin_info(plugin_id, source, plugin_version)
        if not plugin_info:
            return True  # If can't get plugin info, assume compatibility
        
        # Check version compatibility
        min_version = plugin_info.get("min_server_version")
        max_version = plugin_info.get("max_server_version")
        
        if min_version and version.parse(server_version) < version.parse(min_version):
            return False
        if max_version and version.parse(server_version) > version.parse(max_version):
            return False
        
        return True
    
    def _get_plugin_info(self, plugin_id: str, source: str, plugin_version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin from its source."""
        # This would be implemented by the repository classes
        # For now, return None as a placeholder
        return None 