"""
Download command for Minecraft server JAR files
"""
import sys
import click
from rich.console import Console

from nex.core.server_manager import ServerManager
from nex.downloaders import SUPPORTED_SERVER_TYPES

console = Console()

@click.command()
@click.argument("version")
@click.argument("server_type", type=click.Choice(SUPPORTED_SERVER_TYPES))
@click.option("--dir", "-d", default=".", help="Directory to download to")
def download(version: str, server_type: str, dir: str):
    """Download a Minecraft server JAR file."""
    manager = ServerManager(dir)
    try:
        console.print(f"[bold]Downloading {server_type} server version {version}[/bold]")
        jar_path = manager.download_server(version, server_type)
        console.print(f"[green]Successfully downloaded to {jar_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1) 