from typing import List, Dict, Any, Type
import importlib

# List of supported server types
SUPPORTED_SERVER_TYPES = ["vanilla", "paper", "purpur", "fabric", "forge"]

# Base Downloader class that all specific downloaders will inherit from
class ServerDownloader:
    """Base class for server downloaders."""
    
    @classmethod
    def get_versions(cls) -> List[str]:
        """Get a list of available versions."""
        raise NotImplementedError
    
    @classmethod
    def download(cls, version: str, target_dir: str) -> str:
        """Download the specified version to the target directory."""
        raise NotImplementedError


def get_downloader_for_type(server_type: str) -> Type[ServerDownloader]:
    """Get the appropriate downloader for the server type."""
    if server_type not in SUPPORTED_SERVER_TYPES:
        raise ValueError(f"Unsupported server type: {server_type}")
    
    # Import the appropriate module
    module_name = f".{server_type}"
    module = importlib.import_module(module_name, package=__name__)
    
    # Get the downloader class from the module
    class_name = f"{server_type.capitalize()}Downloader"
    downloader_class = getattr(module, class_name)
    
    return downloader_class