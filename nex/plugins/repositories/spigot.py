"""
SpigotMC repository implementation.
"""
from typing import Dict, List, Any, Optional
from .base import BaseRepository

class SpigotRepository(BaseRepository):
    """Repository implementation for SpigotMC."""
    
    def __init__(self):
        """Initialize with SpigotMC API base URL."""
        super().__init__("https://api.spiget.org/v2")
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for plugins on SpigotMC."""
        url = f"{self.base_url}/resources/search"
        params = {
            "size": 20,
            "sort": "downloads",
            "query": query
        }
        
        if category:
            params["category"] = category
            
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
                "author": item.get("author", {}).get("name", "Unknown"),
                "url": f"https://spigotmc.org/resources/{item['id']}"
            })
        
        return results
    
    def get_plugin_info(self, plugin_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get plugin information from SpigotMC."""
        url = f"{self.base_url}/resources/{plugin_id}"
        data = self._make_request(url)
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
    
    def download_plugin(self, plugin_id: str, version: Optional[str] = None) -> Optional[bytes]:
        """Download a plugin from SpigotMC."""
        # Note: SpigotMC doesn't provide direct downloads via API
        # This would need to be implemented using web scraping or a third-party API
        return None 