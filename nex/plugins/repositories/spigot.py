"""
SpigotMC repository implementation.
"""
from typing import Dict, List, Any, Optional
from .base import BaseRepository
import requests

class SpigotRepository(BaseRepository):
    """Repository implementation for SpigotMC."""
    
    def __init__(self):
        """Initialize with SpigotMC API base URL."""
        super().__init__("https://api.spiget.org/v2")
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for plugins on SpigotMC."""
        url = f"{self.base_url}/search/resources/{query}"
        params = {
            "field": "name",
            "size": 20,
            "sort": "-downloads"
        }
        
        if category:
            # Note: category parameter would need to be handled separately
            # as it's not shown in the API documentation you provided
            pass
            
        data = self._make_request(url, params)
        if not data:
            return []
        
        results = []
        for item in data:
            results.append({
                "id": str(item["id"]),
                "name": item["name"],
                "description": item.get("tag", ""),
                "downloads": item.get("downloads", 0),
                "version": item.get("version", "Unknown"),
                "source": "spigot",
                "author": item.get("author", {}).get("id", "Unknown"),
                "url": f"https://spigotmc.org/resources/{item['id']}"
            })
        
        return results
    
    def get_plugin_info(self, plugin_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get plugin information from SpigotMC."""
        url = f"{self.base_url}/resources/{plugin_id}"
        data = self._make_request(url)
        author = data['author']['id']
        if not data:
            return None
        
        return {
            "id": str(data["id"]),
            "name": data["name"],
            "description": data.get("tag", ""),
            "version": data.get("version", "Unknown"),
            "downloads": data.get("downloads", 0),
            "author": data.get("author", {}).get("name", "Unknown"),
            "dependencies": data.get("dependencies", []),
            "min_server_version": data.get("min_server_version"),
            "max_server_version": data.get("max_server_version")
        }
    
    def get_versions(self, plugin_id: str) -> List[str]:
        """Get available versions for a plugin."""
        url = f"{self.base_url}/resources/{plugin_id}/versions"
        data = self._make_request(url)
        if not data:
            return []
        
        versions = []
        for version in data:
            versions.append(version.get("name", "Unknown"))
        return versions
    
    def download_plugin(self, plugin_id: str, version: Optional[str] = None) -> Optional[bytes]:
        """Download a plugin from SpigotMC."""
        # Get plugin info
        plugin_info = self.get_plugin_info(plugin_id)
        if not plugin_info:
            return None
        
        # Get download URL
        download_url = f"{self.base_url}/resources/{plugin_id}/download"
        
        # Download the file
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            return response.content
        except requests.RequestException:
            return None