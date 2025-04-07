"""
Command to run the Minecraft server
"""
import sys
from typing import Optional
import click
from rich.console import Console

from nex.core.server_manager import ServerManager

console = Console()

@click.command()
@click.option("--ram", "-r", default="2G", help="RAM allocation (e.g., 2G, 4G)")
@click.option("--dir", "-d", default=".", help="Server directory")
@click.option("--java-path", help="Custom Java executable path")
@click.option("--nogui", is_flag=True, help="Start server without GUI")
def run(ram: str, dir: str, java_path: Optional[str], nogui: bool):
    """Run the Minecraft server."""
    manager = ServerManager(dir)
    try:
        console.print(f"[bold]Starting Minecraft server with {ram} RAM[/bold]")
        manager.run_server(ram, java_path, nogui)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1) 