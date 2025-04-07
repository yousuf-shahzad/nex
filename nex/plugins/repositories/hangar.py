"""
Hangar repository implementation.
"""
from typing import Dict, List, Any, Optional
from .base import BaseRepository
import requests

class HangarRepository(BaseRepository):
    """Repository implementation for Hangar."""
    
    def __init__(self):
        """Initialize with Hangar API base URL."""
        super().__init__("https://hangar.papermc.io/api/v1")
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for plugins on Hangar."""
        url = f"{self.base_url}/projects"
        params = {
            "q": query,
            "limit": 20,
            "platforms": "paper"
        }
        
        if category:
            params["categories"] = category
            
        data = self._make_request(url, params)
        if not data:
            return []
        
        results = []
        for item in data.get("result", []):
            results.append({
                "id": f"{item['owner']}:{item['name']}",
                "name": item["name"],
                "description": item.get("description", ""),
                "downloads": item.get("stats", {}).get("downloads", 0),
                "version": "Latest",  # Would need another API call for specific version
                "source": "hangar",
                "author": item.get("owner", "Unknown"),
                "url": f"https://hangar.papermc.io/projects/{item['owner']}/{item['name']}"
            })
        
        return results
    
    def get_plugin_info(self, plugin_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get plugin information from Hangar."""
        owner, name = plugin_id.split(":", 1)
        url = f"{self.base_url}/projects/{owner}/{name}"
        data = self._make_request(url)
        if not data:
            return None
        
        return {
            "id": plugin_id,
            "name": data["name"],
            "description": data.get("description", ""),
            "version": "Latest",  # Would need another API call for specific version
            "downloads": data.get("stats", {}).get("downloads", 0),
            "author": data.get("owner", "Unknown"),
            "dependencies": data.get("dependencies", []),
            "min_server_version": data.get("min_server_version"),
            "max_server_version": data.get("max_server_version")
        }
    
    def download_plugin(self, plugin_id: str, version: Optional[str] = None) -> Optional[bytes]:
        """Download a plugin from Hangar."""
        owner, name = plugin_id.split(":", 1)
        
        # Get versions
        versions_url = f"{self.base_url}/projects/{owner}/{name}/versions"
        versions_data = self._make_request(versions_url)
        if not versions_data:
            return None
        
        # Find the appropriate version
        target_version = None
        platform_versions = versions_data.get("paper", [])
        
        if version:
            for ver in platform_versions:
                if ver["name"] == version:
                    target_version = ver
                    break
        else:
            # Get latest version
            if platform_versions:
                target_version = platform_versions[0]
        
        if not target_version:
            return None
        
        # Get download URL
        download_url = f"{self.base_url}/projects/{owner}/{name}/versions/{target_version['name']}/downloads/paper"
        
        # Download the file
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            return response.content
        except requests.RequestException:
            return None 