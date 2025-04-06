import os
import requests
import json
from typing import List, Dict, Any
from tqdm import tqdm

from . import ServerDownloader

# PaperMC API URLs
PAPER_API_BASE = "https://api.papermc.io/v2/projects/paper"

class PaperDownloader(ServerDownloader):
    """Downloader for PaperMC servers."""
    
    @classmethod
    def get_versions(cls) -> List[str]:
        """Get a list of available Paper versions."""
        try:
            response = requests.get(PAPER_API_BASE)
            response.raise_for_status()
            data = response.json()
            
            # Return the list of available versions
            # Paper weirdly sends it over in reverse order, so we reverse it here
            return list(reversed(data["versions"]))
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch Paper versions: {str(e)}")
    
    @classmethod
    def download(cls, version: str, target_dir: str) -> str:
        """Download the specified Paper server version."""
        try:
            # Get build info for this version
            builds_url = f"{PAPER_API_BASE}/versions/{version}"
            builds_response = requests.get(builds_url)
            builds_response.raise_for_status()
            builds_data = builds_response.json()
            
            # Get the latest build number for this version
            builds = builds_data["builds"]
            if not builds:
                raise ValueError(f"No builds available for Paper version {version}")
            
            latest_build = builds[-1]  # Last build in the list is the latest
            
            # Get download info for this build
            download_url = f"{PAPER_API_BASE}/versions/{version}/builds/{latest_build}"
            download_response = requests.get(download_url)
            download_response.raise_for_status()
            download_data = download_response.json()
            
            # Construct the download URL for the JAR
            jar_name = download_data["downloads"]["application"]["name"]
            jar_url = f"{PAPER_API_BASE}/versions/{version}/builds/{latest_build}/downloads/{jar_name}"
            
            # Download the file
            jar_path = os.path.join(target_dir, f"paper-{version}-{latest_build}.jar")
            cls._download_file(jar_url, jar_path)
            
            return jar_path
            
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to download Paper server: {str(e)}")
    
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