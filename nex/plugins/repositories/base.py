"""
Base class for plugin repositories.
"""
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import requests
from rich.console import Console

console = Console()

class BaseRepository(ABC):
    """Base class for plugin repositories."""
    
    def __init__(self, base_url: str):
        """Initialize with repository base URL."""
        self.base_url = base_url
    
    @abstractmethod
    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for plugins matching the query."""
        pass
    
    @abstractmethod
    def get_plugin_info(self, plugin_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin."""
        pass
    
    @abstractmethod
    def download_plugin(self, plugin_id: str, version: Optional[str] = None) -> Optional[bytes]:
        """Download a plugin file."""
        pass
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make an HTTP request to the repository API."""
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            console.print(f"[yellow]Error making request to {url}: {str(e)}[/yellow]")
            return None 