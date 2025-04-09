"""
Plugin management integration for the CLI
"""
import click
from rich.console import Console
import sys
from typing import Optional, List, Dict, Any

from nex.plugins.manager import PluginManager

console = Console()

def register_plugin_commands(cli_group):
    """
    Register plugin-related commands to the CLI group
    
    Args:
        cli_group: The Click group to register commands to
    """
    @cli_group.group("plugin")
    def plugin():
        """Manage server plugins."""
        pass
    
    @plugin.command("install")
    @click.argument("plugin_id", required=False)
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    @click.option("--version", "-v", help="Plugin version to install")
    @click.option("--source", "-s", default="spigot", 
                 help="Plugin source (e.g., spigot, modrinth)")
    @click.option("--interactive", "-i", is_flag=True, help="Use interactive mode")
    def install_plugin(plugin_id: Optional[str], server_dir: str, version: Optional[str], 
                      source: str, interactive: bool):
        """Install a plugin to your server.
        
        You can install plugins in two ways:
        1. Direct installation: nex plugin install <plugin_id> --source <source>
        2. Interactive mode: nex plugin install -i
        
        In interactive mode, you'll be guided through the installation process.
        """
        manager = PluginManager(server_dir)
        
        try:
            if interactive:
                return _install_interactive(manager)
            
            if not plugin_id:
                console.print("[red]Error: Plugin ID is required unless using interactive mode (-i)[/red]")
                console.print("\nTry one of these:")
                console.print("  • nex plugin install <plugin_id> --source <source>")
                console.print("  • nex plugin install -i  (for interactive mode)")
                sys.exit(1)
            
            # Validate source
            source = source.lower()
            if source not in ["spigot", "modrinth"]:
                console.print("[red]Invalid source. Choose from: spigot or modrinth[/red]")
                sys.exit(1)
            
            # Show available versions if version not specified
            if not version:
                console.print(f"[bold]Fetching available versions for {plugin_id}...[/bold]")
                versions = manager.repositories[source].get_versions(plugin_id)
                if versions:
                    console.print("\n[green]Available versions:[/green]")
                    for v in versions[:10]:  # Show latest 10 versions
                        console.print(f"  • {v}")
                    if len(versions) > 10:
                        console.print(f"...and {len(versions) - 10} more versions")
                    console.print("\n[yellow]Tip: Use --version to specify a version[/yellow]")
                    sys.exit(0)
            
            # Install the plugin
            console.print(f"[bold]Installing plugin: {plugin_id}[/bold]")
            success = manager.install_plugin(plugin_id, source, version)
            
            if success:
                console.print(f"[green]Successfully installed plugin: {plugin_id}[/green]")
            else:
                console.print("[red]Failed to install plugin[/red]")
                sys.exit(1)
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    def _install_interactive(manager: PluginManager) -> None:
        """Interactive plugin installation process."""
        try:
            # Step 1: Choose source
            console.print("\n[bold]Step 1: Choose plugin source[/bold]")
            console.print("Available sources:")
            for i, source in enumerate(["spigot", "modrinth"], 1):
                console.print(f"  {i}. {source}")
            
            source_choice = click.prompt("\nEnter source number", type=int)
            if not 1 <= source_choice <= 4:
                console.print("[red]Invalid choice[/red]")
                sys.exit(1)
            source = ["spigot", "modrinth"][source_choice - 1]
            
            # Step 2: Search for plugin
            console.print("\n[bold]Step 2: Search for plugin[/bold]")
            search_term = click.prompt("Enter search term")
            console.print(f"[bold]Searching for plugins matching '{search_term}'...[/bold]")
            
            results = manager.search_plugins(search_term, source=source)
            if not results:
                console.print("[yellow]No plugins found matching your query.[/yellow]")
                sys.exit(1)
            
            # Display results
            console.print(f"\n[green]Found {len(results)} plugins:[/green]")
            for i, plugin in enumerate(results[:10], 1):
                console.print(f"  {i}. {plugin['name']} ({plugin['author']})")
                console.print(f"     ID: {plugin['id']}")
                console.print(f"     {plugin['description'][:60]}...")
            
            if len(results) > 10:
                console.print(f"...and {len(results) - 10} more results")
            
            # Step 3: Choose plugin
            plugin_choice = click.prompt("\nEnter plugin number", type=int)
            if not 1 <= plugin_choice <= min(10, len(results)):
                console.print("[red]Invalid choice[/red]")
                sys.exit(1)
            
            selected_plugin = results[plugin_choice - 1]
            
            # Step 4: Choose version
            console.print(f"\n[bold]Step 3: Choose version for {selected_plugin['name']}[/bold]")
            try:
                versions = manager.repositories[source].get_versions(selected_plugin['id'])
                if versions:
                    console.print("\n[green]Available versions:[/green]")
                    for i, v in enumerate(versions[:10], 1):
                        console.print(f"  {i}. {v}")
                    if len(versions) > 10:
                        console.print(f"...and {len(versions) - 10} more versions")
                    
                    version_choice = click.prompt("\nEnter version number (or press Enter for latest)", 
                                                default="1", type=str)
                    version = versions[int(version_choice) - 1] if version_choice else None
                else:
                    version = None
            except Exception as e:
                console.print(f"[yellow]Could not fetch versions: {str(e)}[/yellow]")
                console.print("[yellow]Proceeding with latest version...[/yellow]")
                version = None
            
            # Step 5: Confirm installation
            console.print("\n[bold]Step 4: Confirm installation[/bold]")
            console.print(f"Plugin: {selected_plugin['name']}")
            console.print(f"Source: {source}")
            console.print(f"Version: {version or 'latest'}")
            
            if not click.confirm("\nDo you want to proceed with installation?"):
                console.print("[yellow]Installation cancelled[/yellow]")
                sys.exit(0)
            
            # Install the plugin
            console.print(f"\n[bold]Installing {selected_plugin['name']}...[/bold]")
            success = manager.install_plugin(selected_plugin['id'], source, version)
            
            if success:
                console.print(f"[green]Successfully installed {selected_plugin['name']}[/green]")
            else:
                console.print("[red]Failed to install plugin[/red]")
                sys.exit(1)
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("list")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    def list_plugins(server_dir):
        """List installed plugins in your server."""
        manager = PluginManager(server_dir)
        try:
            console.print("[bold]Installed plugins:[/bold]")
            plugins = manager.list_plugins()
            
            if not plugins:
                console.print("[yellow]No plugins installed.[/yellow]")
                return
                
            for plugin in plugins:
                console.print(f"  • {plugin['name']} (v{plugin['version']})")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("search")
    @click.argument("query", nargs=-1)
    @click.option("--source", "-s", default="spigot", 
                 help="Plugin source to search (e.g., spigot, bukkit)")
    def search_plugins(query, source):
        """Search for available plugins."""
        search_term = " ".join(query)
        source = source.lower()
        manager = PluginManager(".")
        try:
            console.print(f"[bold]Searching for plugins matching '{search_term}' on {source}...[/bold]")
            if source not in ["spigot", "modrinth"]:
                console.print("[red]Invalid source. Choose from: spigot or modrinth[/red]")
                return
            
            results = manager.search_plugins(search_term, source=source)
            
            if not results:
                console.print("[yellow]No plugins found matching your query.[/yellow]")
                return
                
            console.print(f"[green]Found {len(results)} plugins:[/green]")
            for plugin in results[:10]:  # Show top 10 results
                console.print(f"\t• {plugin['name']} ({plugin['author']}), [bold]ID:[/bold] [blue]{plugin['id']}[/blue] - {plugin['description'][:60]}...")
                
            if len(results) > 10:
                console.print(f"...and {len(results) - 10} more results.")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("remove")
    @click.argument("plugin_name")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    def remove_plugin(plugin_name, server_dir):
        """Remove a plugin from your server."""
        manager = PluginManager(server_dir)
        try:
            console.print(f"[bold]Removing plugin: {plugin_name}[/bold]")
            manager.delete_plugin(plugin_name)
            console.print(f"[green]Successfully removed plugin: {plugin_name}[/green]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("enable")
    @click.argument("plugin_name")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    def enable_plugin(plugin_name, server_dir):
        """Enable a plugin."""
        manager = PluginManager(server_dir)
        try:
            success = manager.enable_plugin(plugin_name)
            if not success:
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("disable")
    @click.argument("plugin_name")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    def disable_plugin(plugin_name, server_dir):
        """Disable a plugin."""
        manager = PluginManager(server_dir)
        try:
            success = manager.disable_plugin(plugin_name)
            if not success:
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("update")
    @click.argument("plugin_name")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    def update_plugin(plugin_name, server_dir):
        """Update a plugin to the latest version."""
        manager = PluginManager(server_dir)
        try:
            success = manager.update_plugin(plugin_name)
            if not success:
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("configure")
    @click.argument("plugin_name")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    @click.option("--set", "-s", multiple=True, help="Set config values (format: key=value)")
    def configure_plugin(plugin_name, server_dir, set):
        """Configure a plugin's settings."""
        manager = PluginManager(server_dir)
        try:
            # Parse config values
            config_values = {}
            for item in set:
                try:
                    key, value = item.split("=", 1)
                    # Try to convert to appropriate type
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            if value.lower() in ["true", "false"]:
                                value = value.lower() == "true"
                    config_values[key] = value
                except ValueError:
                    console.print(f"[red]Invalid config format: {item}. Use key=value format.[/red]")
                    sys.exit(1)
            
            success = manager.configure_plugin(plugin_name, config_values)
            if not success:
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("pin-version")
    @click.argument("plugin_name")
    @click.argument("version")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    def pin_version(plugin_name, version, server_dir):
        """Pin a plugin to a specific version."""
        manager = PluginManager(server_dir)
        try:
            success = manager.pin_version(plugin_name, version)
            if not success:
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("unpin-version")
    @click.argument("plugin_name")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    def unpin_version(plugin_name, server_dir):
        """Remove version pin from a plugin."""
        manager = PluginManager(server_dir)
        try:
            success = manager.unpin_version(plugin_name)
            if not success:
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("check-dependencies")
    @click.argument("plugin_name")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    def check_dependencies(plugin_name, server_dir):
        """Check dependencies for a plugin."""
        manager = PluginManager(server_dir)
        try:
            dependencies = manager.check_dependencies(plugin_name)
            if not dependencies:
                console.print(f"[yellow]No dependencies found for plugin: {plugin_name}[/yellow]")
                return
            
            console.print(f"[bold]Dependencies for {plugin_name}:[/bold]")
            for dep in dependencies:
                status_color = {
                    "installed": "green",
                    "available": "yellow",
                    "unavailable": "red"
                }.get(dep["status"], "white")
                
                console.print(f"  • {dep['name']} (v{dep['version']}) - [{status_color}]{dep['status']}[/{status_color}]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    return plugin 