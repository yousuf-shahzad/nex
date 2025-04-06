import os
import requests
import json
from typing import List, Dict, Any
import time
from tqdm import tqdm

from . import ServerDownloader

# Minecraft version manifest URL
VERSION_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"

class VanillaDownloader(ServerDownloader):
    """Downloader for vanilla Minecraft servers."""
    
    @classmethod
    def get_versions(cls) -> List[str]:
        """Get a list of available vanilla versions."""
        try:
            response = requests.get(VERSION_MANIFEST_URL)
            response.raise_for_status()
            data = response.json()
            
            # Extract and return version IDs
            return [version["id"] for version in data["versions"] 
                   if version["type"] == "release"]
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch version list: {str(e)}")
    
    @classmethod
    def download(cls, version: str, target_dir: str) -> str:
        """Download the specified vanilla server version."""
        # Get version info
        version_info = cls._get_version_info(version)
        if not version_info:
            raise ValueError(f"Version {version} not found or is not a release version")
        
        # Extract the server download URL
        server_url = cls._extract_server_url(version_info)
        if not server_url:
            raise ValueError(f"Server download URL not found for version {version}")
        
        # Download the server JAR
        jar_path = os.path.join(target_dir, f"minecraft_server.{version}.jar")
        cls._download_file(server_url, jar_path)
        
        return jar_path
    
    @classmethod
    def _get_version_info(cls, version: str) -> Dict[str, Any]:
        """Get detailed info about a specific version."""
        try:
            response = requests.get(VERSION_MANIFEST_URL)
            response.raise_for_status()
            data = response.json()
            
            # Find the version
            for ver in data["versions"]:
                if ver["id"] == version and ver["type"] == "release":
                    # Get the version details
                    version_url = ver["url"]
                    version_response = requests.get(version_url)
                    version_response.raise_for_status()
                    return version_response.json()
            
            return None
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch version info: {str(e)}")
    
    @classmethod
    def _extract_server_url(cls, version_info: Dict[str, Any]) -> str:
        """Extract the server download URL from version info."""
        try:
            return version_info["downloads"]["server"]["url"]
        except (KeyError, TypeError):
            return None
    
    @classmethod
    def _download_file(cls, url: str, target_path: str) -> None:
        """Download a file with progress reporting."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            with open(target_path, 'wb') as f, tqdm(
                desc=os.path.basename(target_path),
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=8192):
                    size = f.write(data)
                    bar.update(size)
                    
        except requests.RequestException as e:
            # Remove partial download if failed
            if os.path.exists(target_path):
                os.remove(target_path)
            raise ConnectionError(f"Download failed: {str(e)}")