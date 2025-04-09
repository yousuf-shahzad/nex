"""
Command to list available Minecraft server versions
"""
import sys
import click
from rich.console import Console

from nex.core.server_manager import ServerManager
from nex.downloaders import SUPPORTED_SERVER_TYPES

console = Console()

@click.command("list-versions")
@click.argument("server_type", type=click.Choice(SUPPORTED_SERVER_TYPES))
def list_versions(server_type: str):
    """List available versions for a server type."""
    manager = ServerManager(".")
    try:
        console.print(f"[bold]Fetching available {server_type} versions...[/bold]")
        versions = manager.list_versions(server_type)
        
        console.print(f"[green]Available {server_type} versions:[/green]")
        # Show the latest 10 versions by default
        for version in versions[:10]:
            console.print(f"  • {version}")
        
        if len(versions) > 10:
            console.print(f"...and {len(versions) - 10} more versions available.")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1) 