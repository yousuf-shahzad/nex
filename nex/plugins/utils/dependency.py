"""
Dependency management utilities for plugins.
"""
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from rich.console import Console

console = Console()

class DependencyError(Exception):
    """Exception raised for dependency-related errors."""
    pass

class DependencyResolver:
    """Handles plugin dependency resolution and management."""
    
    def __init__(self, plugins_data: Dict[str, Any]):
        """Initialize with plugin tracking data."""
        self.plugins_data = plugins_data
    
    def resolve_dependencies(self, plugin_id: str, source: str, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Resolve and return a list of all dependencies for a plugin."""
        dependencies = []
        visited = set()
        
        def resolve(plugin_id: str, source: str, version: Optional[str] = None):
            if (plugin_id, source) in visited:
                return
            
            visited.add((plugin_id, source))
            
            # Get plugin info and dependencies
            plugin_info = self._get_plugin_info(plugin_id, source, version)
            if not plugin_info:
                raise DependencyError(f"Could not find plugin {plugin_id} from {source}")
            
            # Add to dependencies list
            dependencies.append({
                "id": plugin_id,
                "source": source,
                "version": version or plugin_info.get("version", "latest"),
                "name": plugin_info.get("name", plugin_id)
            })
            
            # Get dependencies from plugin info
            plugin_deps = plugin_info.get("dependencies", [])
            for dep in plugin_deps:
                dep_id = dep.get("id")
                dep_source = dep.get("source", source)
                dep_version = dep.get("version")
                
                if dep_id and dep_source:
                    resolve(dep_id, dep_source, dep_version)
        
        resolve(plugin_id, source, version)
        return dependencies
    
    def check_dependencies(self, plugin_key: str) -> List[Dict[str, Any]]:
        """Check and return the status of all dependencies for a plugin."""
        dependencies = []
        visited = set()
        
        def check_dep(dep_key: str):
            if dep_key in visited:
                return
            visited.add(dep_key)
            
            dep_info = self.plugins_data["plugins"].get(dep_key)
            if dep_info:
                dependencies.append({
                    "name": dep_info["name"],
                    "version": dep_info["version"],
                    "status": "installed"
                })
            else:
                source, dep_id = dep_key.split(":", 1)
                dep_info = self._get_plugin_info(dep_id, source)
                if dep_info:
                    dependencies.append({
                        "name": dep_info["name"],
                        "version": dep_info.get("version", "unknown"),
                        "status": "available"
                    })
                else:
                    dependencies.append({
                        "name": dep_id,
                        "version": "unknown",
                        "status": "unavailable"
                    })
            
            # Check sub-dependencies
            for sub_dep in self.plugins_data["dependency_graph"].get(dep_key, []):
                check_dep(sub_dep)
        
        for dep_key in self.plugins_data["dependency_graph"].get(plugin_key, []):
            check_dep(dep_key)
        
        return dependencies
    
    def _get_plugin_info(self, plugin_id: str, source: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin from its source."""
        # This would be implemented by the repository classes
        # For now, return None as a placeholder
        return None 