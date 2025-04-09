"""
Modrinth repository implementation.
"""
from typing import Dict, List, Any, Optional
from .base import BaseRepository
import requests
import json

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
            "facets": json.dumps([["categories:bukkit"]]),
            "index": "downloads"
        }
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        results = []
        for item in data["hits"]:
            results.append({
                "id": item["slug"],
                "name": item["title"],
                "description": item["description"],
                "downloads": item.get("downloads", 0),
                "version": "Latest",  # Would need another API call for specific version
                "source": "modrinth",
                "author": item.get("author", "Unknown"),
                "url": f"https://modrinth.com/plugin/{item['slug']}"
            })
        
        return results
    
    def get_plugin_info(self, plugin_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get plugin information from Modrinth."""
        # First try with slug
        url = f"{self.base_url}/project/{plugin_id}"
        data = self._make_request(url)
        
        # If that fails, try searching for it
        if not data:
            search_url = f"{self.base_url}/search"
            search_params = {
                "query": plugin_id,
                "limit": 1,
                "facets": json.dumps([["categories:bukkit"]])
            }
            search_data = self._make_request(search_url, search_params)
            if search_data and search_data["hits"]:
                data = search_data["hits"][0]
        
        if not data:
            return None
        
        # Get version info if specific version requested
        version_info = None
        if version:
            versions_url = f"{self.base_url}/project/{plugin_id}/version"
            versions_data = self._make_request(versions_url)
            if versions_data:
                for ver in versions_data:
                    if ver["version_number"] == version:
                        version_info = ver
                        break
        
        return {
            "id": data.get("slug", data.get("id")),
            "name": data.get("title"),
            "description": data.get("description"),
            "version": version_info["version_number"] if version_info else "Latest",
            "downloads": data.get("downloads", 0),
            "author": data.get("team", "Unknown"),
            "dependencies": data.get("dependencies", []),
            "min_server_version": data.get("game_versions", [])[0] if data.get("game_versions") else None,
            "max_server_version": data.get("game_versions", [])[-1] if data.get("game_versions") else None
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
    
    def get_versions(self, plugin_id: str) -> List[str]:
        """Get available versions for a plugin."""
        url = f"{self.base_url}/project/{plugin_id}/version"
        data = self._make_request(url)
        if not data:
            return []
        
        versions = []
        for version in data:
            versions.append(version.get("version_number", "Unknown"))
        return versions 