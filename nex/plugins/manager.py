"""
Main plugin manager module.
"""
import os
import json
import shutil
import requests
import yaml
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from rich.console import Console
from rich.table import Table
import click
from datetime import datetime
from packaging import version

from .repositories import SpigotRepository, ModrinthRepository, HangarRepository, BukkitRepository
from .utils.dependency import DependencyResolver, DependencyError
from .utils.version import VersionManager, VersionError

console = Console()

# Supported repository types
REPO_TYPES = {
    "spigot": "https://api.spiget.org/v2",
    "bukkit": "https://dev.bukkit.org/projects",
    "modrinth": "https://api.modrinth.com/v2",
    "hangar": "https://hangar.papermc.io/api/v1"
}

class PluginManager:
    """Manager for Minecraft server plugins."""
    
    def __init__(self, server_dir: str):
        """Initialize the plugin manager for a specific server directory."""
        self.server_dir = Path(server_dir)
        self.plugins_dir = self.server_dir / "plugins"
        self.plugins_data_file = self.server_dir / "nex_plugins.json"
        self.plugins_data = self._load_plugins_data()
        
        # Initialize repositories
        self.repositories = {
            "spigot": SpigotRepository(),
            "modrinth": ModrinthRepository(),
            "hangar": HangarRepository(),
            "bukkit": BukkitRepository()
        }
        
        # Initialize utilities
        self.dependency_resolver = DependencyResolver(self.plugins_data, self.repositories)
        self.version_manager = VersionManager(self.server_dir)
        
        # Create plugins directory if it doesn't exist
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True)
    
    def _load_plugins_data(self) -> Dict[str, Any]:
        """Load plugin tracking data from file."""
        if self.plugins_data_file.exists():
            try:
                with open(self.plugins_data_file, 'r') as f:
                    data = json.load(f)
                    # Ensure the data structure includes new fields
                    if "plugins" not in data:
                        data["plugins"] = {}
                    if "repositories" not in data:
                        data["repositories"] = {
                            "spigot": True,
                            "bukkit": True,
                            "modrinth": True,
                            "hangar": True
                        }
                    if "dependency_graph" not in data:
                        data["dependency_graph"] = {}
                    if "version_pins" not in data:
                        data["version_pins"] = {}
                    return data
            except json.JSONDecodeError:
                console.print("[yellow]Warning: Plugin data file corrupted, creating new one[/yellow]")
        
        # Default structure if file doesn't exist or is corrupted
        return {
            "plugins": {},
            "repositories": {
                "spigot": True,
                "bukkit": True,
                "modrinth": True,
                "hangar": True
            },
            "dependency_graph": {},
            "version_pins": {}
        }
    
    def _save_plugins_data(self) -> None:
        """Save plugin tracking data to file."""
        with open(self.plugins_data_file, 'w') as f:
            json.dump(self.plugins_data, f, indent=2)
    
    def search_plugins(self, query: str, category: Optional[str] = None, 
                      source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for plugins matching the query."""
        results = []
        
        # Determine which repositories to search
        repos_to_search = []
        if source and source in self.repositories:
            if not self.plugins_data["repositories"].get(source, True):
                console.print(f"[yellow]Repository {source} is disabled[/yellow]")
                return []
            repos_to_search.append(source)
        else:
            # Search all enabled repositories
            repos_to_search = [
                repo for repo, enabled in self.plugins_data["repositories"].items() 
                if enabled
            ]
        
        for repo in repos_to_search:
            try:
                results.extend(self.repositories[repo].search(query, category))
            except Exception as e:
                console.print(f"[yellow]Error searching {repo}: {str(e)}[/yellow]")
        
        return results
    
    def install_plugin(self, plugin_id: str, source: str, version: Optional[str] = None) -> bool:
        """Install a plugin from a specific source with dependency resolution."""
        try:
            # Check if source is enabled
            if not self.plugins_data["repositories"].get(source, False):
                console.print(f"[red]Repository {source} is disabled[/red]")
                return False
            
            # Resolve dependencies
            console.print("[bold]Resolving dependencies...[/bold]")
            dependencies = self.dependency_resolver.resolve_dependencies(plugin_id, source, version)
            
            # Check version compatibility for all dependencies
            for dep in dependencies:
                if not self.version_manager.check_version_compatibility(dep["id"], dep["source"], dep["version"]):
                    raise VersionError(f"Plugin {dep['name']} version {dep['version']} is not compatible with your server version")
            
            # Install dependencies first
            for dep in dependencies[:-1]:  # Skip the main plugin (last in list)
                if not self._install_single_plugin(dep["id"], dep["source"], dep["version"]):
                    raise DependencyError(f"Failed to install dependency {dep['name']}")
            
            # Install the main plugin
            return self._install_single_plugin(plugin_id, source, version)
            
        except (DependencyError, VersionError) as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Error installing plugin: {str(e)}[/red]")
            return False
    
    def _install_single_plugin(self, plugin_id: str, source: str, version: Optional[str] = None) -> bool:
        """Install a single plugin without dependency resolution."""
        try:
            console.print(f"[bold]Installing plugin {plugin_id} from {source}...[/bold]")
            
            # Get plugin info
            plugin_info = self.repositories[source].get_plugin_info(plugin_id, version)
            if not plugin_info:
                console.print(f"[red]Could not find plugin {plugin_id} on {source}[/red]")
                return False
            
            # Download the plugin
            plugin_data = self.repositories[source].download_plugin(plugin_id, version)
            if not plugin_data:
                console.print(f"[red]Could not download plugin {plugin_id} from {source}[/red]")
                return False
            
            # Save the plugin file
            file_name = f"{plugin_info['name']}-{plugin_info['version']}.jar"
            plugin_path = self.plugins_dir / file_name
            
            with open(plugin_path, 'wb') as f:
                f.write(plugin_data)
            
            # Add to tracking data
            plugin_key = f"{source}:{plugin_id}"
            self.plugins_data["plugins"][plugin_key] = {
                **plugin_info,
                "file": file_name,
                "enabled": True,
                "install_date": str(datetime.now())
            }
            
            # Update dependency graph
            self._update_dependency_graph(plugin_key, plugin_info)
            
            self._save_plugins_data()
            
            console.print(f"[green]Successfully installed {plugin_info['name']} v{plugin_info['version']}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error installing plugin: {str(e)}[/red]")
            return False
    
    def _update_dependency_graph(self, plugin_key: str, plugin_info: Dict[str, Any]) -> None:
        """Update the dependency graph with the new plugin's dependencies."""
        self.plugins_data["dependency_graph"][plugin_key] = []
        
        for dep in plugin_info.get("dependencies", []):
            dep_id = dep.get("id")
            dep_source = dep.get("source", plugin_info.get("source"))
            if dep_id and dep_source:
                dep_key = f"{dep_source}:{dep_id}"
                self.plugins_data["dependency_graph"][plugin_key].append(dep_key)
    
    def pin_version(self, plugin_name: str, version: str) -> bool:
        """Pin a plugin to a specific version."""
        try:
            # Find the plugin in tracking data
            plugin_key = None
            for key, info in self.plugins_data["plugins"].items():
                if info["name"].lower() == plugin_name.lower():
                    plugin_key = key
                    break
            
            if not plugin_key:
                console.print(f"[red]Plugin {plugin_name} not found[/red]")
                return False
            
            # Check if version exists
            source, plugin_id = plugin_key.split(":", 1)
            plugin_info = self.repositories[source].get_plugin_info(plugin_id, version)
            if not plugin_info:
                console.print(f"[red]Version {version} not found for plugin {plugin_name}[/red]")
                return False
            
            # Pin the version
            self.plugins_data["version_pins"][plugin_key] = version
            self._save_plugins_data()
            
            console.print(f"[green]Pinned {plugin_name} to version {version}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error pinning version: {str(e)}[/red]")
            return False
    
    def unpin_version(self, plugin_name: str) -> bool:
        """Remove version pin for a plugin."""
        try:
            # Find the plugin in tracking data
            plugin_key = None
            for key, info in self.plugins_data["plugins"].items():
                if info["name"].lower() == plugin_name.lower():
                    plugin_key = key
                    break
            
            if not plugin_key:
                console.print(f"[red]Plugin {plugin_name} not found[/red]")
                return False
            
            # Remove the pin
            if plugin_key in self.plugins_data["version_pins"]:
                del self.plugins_data["version_pins"][plugin_key]
                self._save_plugins_data()
                console.print(f"[green]Removed version pin for {plugin_name}[/green]")
                return True
            else:
                console.print(f"[yellow]No version pin found for {plugin_name}[/yellow]")
                return False
            
        except Exception as e:
            console.print(f"[red]Error unpinning version: {str(e)}[/red]")
            return False
    
    def check_dependencies(self, plugin_name: str) -> List[Dict[str, Any]]:
        """Check and return the status of all dependencies for a plugin."""
        try:
            # Find the plugin in tracking data
            plugin_key = None
            for key, info in self.plugins_data["plugins"].items():
                if info["name"].lower() == plugin_name.lower():
                    plugin_key = key
                    break
            
            if not plugin_key:
                console.print(f"[red]Plugin {plugin_name} not found[/red]")
                return []
            
            return self.dependency_resolver.check_dependencies(plugin_key)
            
        except Exception as e:
            console.print(f"[red]Error checking dependencies: {str(e)}[/red]")
            return []
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all installed plugins."""
        plugins = []
        
        # First, get tracked plugins from our data file
        for plugin_key, plugin_info in self.plugins_data["plugins"].items():
            plugins.append(plugin_info)
        
        # Then scan the plugins directory for any untracked plugins
        for file in self.plugins_dir.glob("*.jar"):
            file_name = file.name
            
            # Check if this plugin is already tracked
            is_tracked = False
            for plugin in plugins:
                if plugin.get("file") == file_name:
                    is_tracked = True
                    break
            
            if not is_tracked:
                # Add untracked plugin
                plugins.append({
                    "name": os.path.splitext(file_name)[0],
                    "version": "Unknown",
                    "source": "untracked",
                    "enabled": True,
                    "file": file_name
                })
        
        return plugins
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        return self._set_plugin_state(plugin_name, True)
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        return self._set_plugin_state(plugin_name, False)
    
    def _set_plugin_state(self, plugin_name: str, enabled: bool) -> bool:
        """Set the enabled state of a plugin."""
        # First try to find the plugin in our tracking data
        plugin_key = None
        for key, info in self.plugins_data["plugins"].items():
            if info["name"].lower() == plugin_name.lower() or (
                info.get("file", "").lower() == plugin_name.lower() or
                info.get("file", "").lower() == f"{plugin_name.lower()}.jar"
            ):
                plugin_key = key
                break
        
        if plugin_key:
            # Found in tracking data
            plugin_info = self.plugins_data["plugins"][plugin_key]
            
            # Get the file name
            file_name = plugin_info.get("file")
            if not file_name:
                file_name = f"{plugin_info['name']}.jar"
            
            # Check if the file exists
            jar_path = self.plugins_dir / file_name
            disabled_path = self.plugins_dir / f"{file_name}.disabled"
            
            try:
                if enabled:
                    # Enable: rename .jar.disabled to .jar
                    if disabled_path.exists():
                        shutil.move(str(disabled_path), str(jar_path))
                    elif not jar_path.exists():
                        console.print(f"[yellow]Warning: Plugin file {file_name} not found[/yellow]")
                        return False
                else:
                    # Disable: rename .jar to .jar.disabled
                    if jar_path.exists():
                        shutil.move(str(jar_path), str(disabled_path))
                    elif not disabled_path.exists():
                        console.print(f"[yellow]Warning: Plugin file {file_name} not found[/yellow]")
                        return False
                
                # Update tracking data
                self.plugins_data["plugins"][plugin_key]["enabled"] = enabled
                self._save_plugins_data()
                
                console.print(f"[green]Plugin {plugin_name} {'enabled' if enabled else 'disabled'}[/green]")
                return True
                
            except Exception as e:
                console.print(f"[red]Error {'enabling' if enabled else 'disabling'} plugin: {str(e)}[/red]")
                return False
        else:
            # Try to find by filename in the plugins directory
            for file in self.plugins_dir.glob("*.jar"):
                file_name = file.name
                name_without_ext = os.path.splitext(file_name)[0]
                
                if name_without_ext.lower() == plugin_name.lower():
                    # Found by filename
                    jar_path = file
                    disabled_path = self.plugins_dir / f"{file_name}.disabled"
                    
                    try:
                        if enabled:
                            # Already enabled
                            console.print(f"[green]Plugin {plugin_name} is already enabled[/green]")
                            return True
                        else:
                            # Disable: rename .jar to .jar.disabled
                            shutil.move(str(jar_path), str(disabled_path))
                            
                            # Add to tracking data
                            plugin_key = f"untracked:{file_name}"
                            self.plugins_data["plugins"][plugin_key] = {
                                "name": name_without_ext,
                                "version": "Unknown",
                                "source": "untracked",
                                "enabled": False,
                                "file": file_name
                            }
                            self._save_plugins_data()
                            
                            console.print(f"[green]Plugin {plugin_name} disabled[/green]")
                            return True
                            
                    except Exception as e:
                        console.print(f"[red]Error disabling plugin: {str(e)}[/red]")
                        return False
            
            # Check disabled plugins
            for file in self.plugins_dir.glob("*.jar.disabled"):
                file_name = file.name[:-9]  # Remove .disabled
                name_without_ext = os.path.splitext(file_name)[0]
                
                if name_without_ext.lower() == plugin_name.lower():
                    # Found by filename
                    jar_path = self.plugins_dir / file_name
                    disabled_path = file
                    
                    try:
                        if enabled:
                            # Enable: rename .jar.disabled to .jar
                            shutil.move(str(disabled_path), str(jar_path))
                            
                            # Add to tracking data
                            plugin_key = f"untracked:{file_name}"
                            self.plugins_data["plugins"][plugin_key] = {
                                "name": name_without_ext,
                                "version": "Unknown",
                                "source": "untracked",
                                "enabled": True,
                                "file": file_name
                            }
                            self._save_plugins_data()
                            
                            console.print(f"[green]Plugin {plugin_name} enabled[/green]")
                            return True
                        else:
                            # Already disabled
                            console.print(f"[green]Plugin {plugin_name} is already disabled[/green]")
                            return True
                            
                    except Exception as e:
                        console.print(f"[red]Error enabling plugin: {str(e)}[/red]")
                        return False
        
        console.print(f"[red]Plugin {plugin_name} not found[/red]")
        return False
    
    def delete_plugin(self, plugin_name: str) -> bool:
        """Delete a plugin."""
        # Find the plugin in our tracking data or by filename
        plugin_path = None
        plugin_key = None
        
        # First try to find in tracking data
        for key, info in self.plugins_data["plugins"].items():
            if info["name"].lower() == plugin_name.lower() or (
                info.get("file", "").lower() == plugin_name.lower() or
                info.get("file", "").lower() == f"{plugin_name.lower()}.jar"
            ):
                plugin_key = key
                file_name = info.get("file")
                if file_name:
                    plugin_path = self.plugins_dir / file_name
                    disabled_path = self.plugins_dir / f"{file_name}.disabled"
                    if disabled_path.exists():
                        plugin_path = disabled_path
                break
        
        # If not found in tracking data, try to find by filename
        if not plugin_path:
            for ext in [".jar", ".jar.disabled"]:
                test_path = self.plugins_dir / f"{plugin_name}{ext}"
                if test_path.exists():
                    plugin_path = test_path
                    break
                
                # Try without exact match
                for file in self.plugins_dir.glob(f"*{ext}"):
                    name_without_ext = os.path.splitext(file.name.replace('.disabled', ''))[0]
                    if name_without_ext.lower() == plugin_name.lower():
                        plugin_path = file
                        break
                
                if plugin_path:
                    break
        
        if not plugin_path:
            console.print(f"[red]Plugin {plugin_name} not found[/red]")
            return False
        
        try:
            # Delete the file
            os.remove(plugin_path)
            
            # Remove from tracking data if present
            if plugin_key:
                del self.plugins_data["plugins"][plugin_key]
                self._save_plugins_data()
            
            console.print(f"[green]Plugin {plugin_name} deleted[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error deleting plugin: {str(e)}[/red]")
            return False
    
    def update_plugin(self, plugin_name: str) -> bool:
        """Update a plugin to the latest version."""
        # Find the plugin in our tracking data
        plugin_key = None
        for key, info in self.plugins_data["plugins"].items():
            if info["name"].lower() == plugin_name.lower():
                plugin_key = key
                break
        
        if not plugin_key:
            console.print(f"[red]Plugin {plugin_name} not found in tracking data[/red]")
            console.print("[yellow]Only plugins installed through nex can be updated automatically[/yellow]")
            return False
        
        plugin_info = self.plugins_data["plugins"][plugin_key]
        source = plugin_info["source"]
        plugin_id = plugin_info.get("id")
        
        if not plugin_id:
            console.print(f"[red]Cannot update plugin: missing plugin ID[/red]")
            return False
        
        if source not in self.repositories:
            console.print(f"[red]Cannot update plugins from source: {source}[/red]")
            return False
        
        # Backup the old plugin file
        old_file = plugin_info.get("file")
        if old_file:
            old_path = self.plugins_dir / old_file
            if old_path.exists():
                backup_path = self.plugins_dir / f"{old_file}.bak"
                shutil.copy2(old_path, backup_path)
        
        # Try to install the latest version
        success = self.install_plugin(plugin_id, source)
        
        if success:
            console.print(f"[green]Plugin {plugin_name} updated successfully[/green]")
            
            # Clean up the backup if successful
            if old_file and (self.plugins_dir / f"{old_file}.bak").exists():
                os.remove(self.plugins_dir / f"{old_file}.bak")
                
            return True
        else:
            console.print(f"[red]Failed to update plugin {plugin_name}[/red]")
            
            # Restore from backup if update failed
            if old_file:
                backup_path = self.plugins_dir / f"{old_file}.bak"
                if backup_path.exists():
                    shutil.move(str(backup_path), str(self.plugins_dir / old_file))
                    console.print("[yellow]Restored previous version from backup[/yellow]")
            
            return False
    
    def configure_plugin(self, plugin_name: str, config_values: Dict[str, Any] = None) -> bool:
        """Configure a plugin by modifying its config files."""
        # Find the plugin
        plugin_found = False
        for info in self.list_plugins():
            if info["name"].lower() == plugin_name.lower():
                plugin_found = True
                break
        
        if not plugin_found:
            console.print(f"[red]Plugin {plugin_name} not found[/red]")
            return False
        
        # Look for config files in common locations
        config_paths = [
            self.plugins_dir / plugin_name / "config.yml",
            self.plugins_dir / f"{plugin_name}.yml",
            self.plugins_dir / "config" / f"{plugin_name}.yml",
            self.server_dir / "plugins" / plugin_name / "config.yml",
            self.server_dir / "config" / f"{plugin_name}.yml"
        ]
        
        config_file = None
        for path in config_paths:
            if path.exists():
                config_file = path
                break
        
        if not config_file:
            console.print(f"[red]No config file found for plugin {plugin_name}[/red]")
            return False
        
        try:
            # Make a backup
            backup_path = str(config_file) + ".bak"
            shutil.copy2(config_file, backup_path)
            
            # Load the config
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                config_data = {}
            
            # Update config values
            if config_values:
                for key, value in config_values.items():
                    keys = key.split('.')
                    current = config_data
                    for k in keys[:-1]:
                        if k not in current:
                            current[k] = {}
                        current = current[k]
                    current[keys[-1]] = value
            
            # Save the updated config
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            console.print(f"[green]Successfully configured plugin {plugin_name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error configuring plugin: {str(e)}[/red]")
            # Restore from backup if available
            if 'backup_path' in locals() and os.path.exists(backup_path):
                shutil.move(backup_path, str(config_file))
                console.print("[yellow]Restored original config from backup[/yellow]")
            return False