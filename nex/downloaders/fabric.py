"""
Fabric server downloader implementation
"""
import os
import requests
import json
from typing import List, Dict, Any
from tqdm import tqdm
from . import ServerDownloader

# Fabric API URLs
FABRIC_API_BASE = "https://meta.fabricmc.net/v2"

class FabricDownloader(ServerDownloader):
    """Downloader for Fabric servers"""
    
    @classmethod
    def get_versions(cls) -> List[str]:
        """Get a list of available Fabric versions"""
        try:
            response = requests.get(f"{FABRIC_API_BASE}/versions/game")
            response.raise_for_status()
            data = response.json()
            
            # Return the list of available versions
            return [version["version"] for version in data 
                   if version["stable"]]
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch Fabric versions: {str(e)}")
    
    @classmethod
    def download(cls, version: str, target_dir: str) -> str:
        """Download the specified Fabric server version"""
        try:
            # Get loader versions
            loader_response = requests.get(f"{FABRIC_API_BASE}/versions/loader")
            loader_response.raise_for_status()
            loader_data = loader_response.json()
            
            # Get the latest loader version
            latest_loader = loader_data[0]["version"]
            
            # Get installer version
            installer_response = requests.get(f"{FABRIC_API_BASE}/versions/installer")
            installer_response.raise_for_status()
            installer_data = installer_response.json()
            
            # Get the latest installer version
            latest_installer = installer_data[0]["version"]
            
            # Construct the download URL
            jar_url = f"{FABRIC_API_BASE}/versions/loader/{version}/{latest_loader}/{latest_installer}/server/jar"
            
            # Download the file
            jar_path = os.path.join(target_dir, f"fabric-server-{version}-{latest_loader}.jar")
            cls._download_file(jar_url, jar_path)
            
            return jar_path
            
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to download Fabric server: {str(e)}")
    
    @classmethod
    def _download_file(cls, url: str, target_path: str) -> None:
        """Download a file with progress reporting"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get total file size if available
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