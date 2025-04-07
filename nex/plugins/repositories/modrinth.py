"""
Modrinth repository implementation.
"""
from typing import Dict, List, Any, Optional
from .base import BaseRepository
import requests

class ModrinthRepository(BaseRepository):
    """Repository implementation for Modrinth."""
    
    def __init__(self):
        """Initialize with Modrinth API base URL."""
        super().__init__("https://api.modrinth.com/v2")
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for plugins on Modrinth."""
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "limit": 20,
            "facets": [["categories:bukkit"]],
            "index": "downloads"
        }
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        results = []
        for item in data["hits"]:
            results.append({
                "id": item["project_id"],
                "name": item["title"],
                "description": item["description"],
                "downloads": item.get("downloads", 0),
                "version": "Latest",  # Would need another API call for specific version
                "source": "modrinth",
                "author": item.get("author", "Unknown"),
                "url": f"https://modrinth.com/plugin/{item['project_id']}"
            })
        
        return results
    
    def get_plugin_info(self, plugin_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get plugin information from Modrinth."""
        url = f"{self.base_url}/project/{plugin_id}"
        data = self._make_request(url)
        if not data:
            return None
        
        return {
            "id": data["id"],
            "name": data["title"],
            "description": data["description"],
            "version": "Latest",  # Would need another API call for specific version
            "downloads": data.get("downloads", 0),
            "author": data.get("author", "Unknown"),
            "dependencies": data.get("dependencies", []),
            "min_server_version": data.get("min_server_version"),
            "max_server_version": data.get("max_server_version")
        }
    
    def download_plugin(self, plugin_id: str, version: Optional[str] = None) -> Optional[bytes]:
        """Download a plugin from Modrinth."""
        # Get version info
        versions_url = f"{self.base_url}/project/{plugin_id}/version"
        versions_data = self._make_request(versions_url)
        if not versions_data:
            return None
        
        # Find the appropriate version
        target_version = None
        if version:
            for ver in versions_data:
                if ver["version_number"] == version:
                    target_version = ver
                    break
        else:
            # Get latest version
            target_version = versions_data[0]
        
        if not target_version:
            return None
        
        # Find the right file (JAR)
        download_url = None
        for file in target_version["files"]:
            if file["filename"].endswith(".jar"):
                download_url = file["url"]
                break
        
        if not download_url:
            return None
        
        # Download the file
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            return response.content
        except requests.RequestException:
            return None 