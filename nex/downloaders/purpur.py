import os
import requests
import json
from typing import List, Dict, Any
from tqdm import tqdm

from . import ServerDownloader

# Purpur API URLs
PURPUR_API_BASE = "https://api.purpurmc.org/v2/purpur"

class PurpurDownloader(ServerDownloader):
    """Downloader for Purpur servers."""
    
    @classmethod
    def get_versions(cls) -> List[str]:
        """Get a list of available Purpur versions."""
        try:
            response = requests.get(PURPUR_API_BASE)
            response.raise_for_status()
            data = response.json()
            
            # Return the list of available versions
            # Purpur does the same thing as paper and sends it over in reverse order, so we reverse it here
            return list(reversed(data["versions"]))
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch Purpur versions: {str(e)}")
    
    @classmethod
    def download(cls, version: str, target_dir: str) -> str:
        """Download the specified Purpur server version."""
        try:
            # Get build info for this version
            version_url = f"{PURPUR_API_BASE}/{version}"
            version_response = requests.get(version_url)
            version_response.raise_for_status()
            version_data = version_response.json()
            
            # Get the latest build number for this version
            builds = version_data["builds"]["all"]
            if not builds:
                raise ValueError(f"No builds available for Purpur version {version}")
            
            latest_build = builds[-1]  # Last build in the list is the latest
            
            # Construct the download URL
            jar_url = f"{PURPUR_API_BASE}/{version}/{latest_build}/download"
            
            # Download the file
            jar_path = os.path.join(target_dir, f"purpur-{version}-{latest_build}.jar")
            cls._download_file(jar_url, jar_path)
            
            return jar_path
            
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to download Purpur server: {str(e)}")
    
    @classmethod
    def _download_file(cls, url: str, target_path: str) -> None:
        """Download a file with progress reporting."""
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