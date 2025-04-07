"""
Plugin management integration for the CLI
"""
import click
from rich.console import Console
import sys

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
    @click.argument("plugin_name")
    @click.option("--server-dir", "-d", default=".", help="Server directory")
    @click.option("--version", "-v", help="Plugin version to install")
    @click.option("--source", "-s", default="spigotmc", 
                 help="Plugin source (e.g., spigotmc, bukkit)")
    def install_plugin(plugin_name, server_dir, version, source):
        """Install a plugin to your server."""
        manager = PluginManager(server_dir)
        try:
            console.print(f"[bold]Installing plugin: {plugin_name}[/bold]")
            plugin_path = manager.install_plugin(plugin_name, version, source)
            console.print(f"[green]Successfully installed plugin to {plugin_path}[/green]")
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
            plugins = manager.list_installed_plugins()
            
            if not plugins:
                console.print("[yellow]No plugins installed.[/yellow]")
                return
                
            for plugin in plugins:
                console.print(f"  • {plugin['name']} (v{plugin['version']})")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    @plugin.command("search")
    @click.argument("query")
    @click.option("--source", "-s", default="spigotmc", 
                 help="Plugin source to search (e.g., spigotmc, bukkit)")
    def search_plugins(query, source):
        """Search for available plugins."""
        manager = PluginManager(".")
        try:
            console.print(f"[bold]Searching for plugins matching '{query}'...[/bold]")
            results = manager.search_plugins(query, source)
            
            if not results:
                console.print("[yellow]No plugins found matching your query.[/yellow]")
                return
                
            console.print(f"[green]Found {len(results)} plugins:[/green]")
            for plugin in results[:10]:  # Show top 10 results
                console.print(f"  • {plugin['name']} - {plugin['description'][:60]}...")
                
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
            manager.remove_plugin(plugin_name)
            console.print(f"[green]Successfully removed plugin: {plugin_name}[/green]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
    
    return plugin 