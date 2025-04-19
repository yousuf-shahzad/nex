"""
Forge server downloader implementation
"""
import os
import requests
import json
import subprocess
import shutil
from typing import List, Dict, Any
from tqdm import tqdm
from packaging import version as pkg_version
from nex.utils.java_utils import find_java_executable, verify_java_version
from nex.core.server_manager import JavaNotFoundError
from . import ServerDownloader

# Forge API URLs
FORGE_API_BASE = "https://files.minecraftforge.net/net/minecraftforge/forge"
FORGE_MAVEN_BASE = "https://maven.minecraftforge.net/net/minecraftforge/forge/"

class ForgeDownloader(ServerDownloader):
    """Downloader for Forge servers"""
    
    @classmethod
    def get_versions(cls) -> List[str]:
        """Get a list of available Forge versions"""
        try:
            # Get the version manifest
            response = requests.get(f"{FORGE_API_BASE}/maven-metadata.json")
            response.raise_for_status()
            data = response.json()
            
            # Extract versions from the metadata
            versions = []
            for mc_version, forge_versions in data.items():
                # Skip non-version keys
                if not mc_version.replace(".", "").isdigit():
                    continue
                    
                # Get the latest Forge version for this Minecraft version
                if forge_versions:  # Check if there are any versions
                    # Sort versions to get the latest
                    latest_forge = sorted(forge_versions, key=lambda x: pkg_version.parse(x.split("-")[1]), reverse=True)[0]
                    versions.append(latest_forge)
            
            # Sort by Minecraft version first, then Forge version
            return sorted(versions, 
                        key=lambda x: (pkg_version.parse(x.split("-")[0]), 
                                     pkg_version.parse(x.split("-")[1])), 
                        reverse=True)
            
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch Forge versions: {str(e)}")
    
    @classmethod
    def download(cls, version: str, target_dir: str) -> str:
        """Download the specified Forge server version"""
        try:
            # First get the Minecraft version from the Forge version
            # Format is like "1.20.1-47.1.0" where first part is MC version
            mc_version = version.split("-")[0]
            
            # Get the version list for this Minecraft version
            response = requests.get(f"{FORGE_API_BASE}/maven-metadata.json")
            response.raise_for_status()
            data = response.json()
            
            # Find the latest Forge version for this Minecraft version
            forge_version = None
            if mc_version in data:
                forge_versions = data[mc_version]
                if forge_versions:
                    forge_version = sorted(forge_versions, 
                                         key=lambda x: pkg_version.parse(x.split("-")[1]), 
                                         reverse=True)[0]
            
            if not forge_version:
                raise ValueError(f"No Forge version found for Minecraft {mc_version}")
            
            # Construct the download URL
            jar_url = f"{FORGE_MAVEN_BASE}/{forge_version}/forge-{forge_version}-installer.jar"
            
            # Download the installer
            installer_path = os.path.join(target_dir, f"forge-{forge_version}-installer.jar")
            cls._download_file(jar_url, installer_path)
            
            # Run the installer to get the server jar
            server_jar = f"forge-{forge_version}-server.jar"
            server_path = os.path.join(target_dir, server_jar)
            
            # Run the installer to extract the server jar
            cls._run_forge_installer(installer_path, target_dir, forge_version)
            
            # Return the path to the server jar
            if os.path.exists(server_path):
                return server_path
            else:
                # If the server jar doesn't exist, return the installer path
                return installer_path
            
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to download Forge server: {str(e)}")
    
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
    
    @classmethod
    def _run_forge_installer(cls, installer_path: str, target_dir: str, forge_version: str) -> None:
        """Run the Forge installer to extract the server jar"""
        # Find Java executable
        java_exec = find_java_executable()
        if not java_exec:
            raise JavaNotFoundError("Java not found. Please install Java to run the Forge installer.")
        
        # Verify Java version (Forge typically requires Java 8+)
        if not verify_java_version(java_exec, min_version=8):
            raise RuntimeError("Java 8 or higher is required to run the Forge installer.")
        
        # Prepare the command to run the installer in silent mode
        # The --installServer flag runs the installer in silent mode to extract the server jar
        cmd = [
            java_exec,
            "-jar",
            installer_path,
            "--installServer",
            target_dir
        ]
        
        try:
            # Run the installer
            print(f"Running Forge installer to extract server jar...")
            process = subprocess.Popen(
                cmd,
                cwd=target_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Print the installer output
            for line in process.stdout:
                print(line.strip())
                
            process.wait()
            
            if process.returncode != 0:
                raise RuntimeError(f"Forge installer failed with exit code {process.returncode}")
                
            # The installer creates several files, find the server jar
            server_jar = f"forge-{forge_version}-server.jar"
            if not os.path.exists(os.path.join(target_dir, server_jar)):
                # Look for alternative naming patterns
                for file in os.listdir(target_dir):
                    if file.endswith("-server.jar") and "forge" in file:
                        server_jar = file
                        break
            
            print(f"Server jar extracted: {server_jar}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to run Forge installer: {str(e)}")