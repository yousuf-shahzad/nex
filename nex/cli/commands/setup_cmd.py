"""
Setup command for Minecraft server configuration
"""
import os
import sys
from typing import Optional
import click
from rich.console import Console

from nex.core.server_manager import ServerManager
from nex.downloaders import SUPPORTED_SERVER_TYPES

console = Console()

@click.command()
@click.option("--dir", "-d", default=".", help="Directory to set up the server in")
@click.option("--version", "-v", help="Minecraft version to use")
@click.option("--type", "-t", "server_type", 
              type=click.Choice(SUPPORTED_SERVER_TYPES), 
              default="vanilla", help="Server type")
@click.option("--difficulty", type=click.Choice(["peaceful", "easy", "normal", "hard"]), 
              default="easy", help="Server difficulty")
@click.option("--gamemode", type=click.Choice(["survival", "creative", "adventure", "spectator"]), 
              default="survival", help="Default game mode")
@click.option("--max-players", type=int, default=20, help="Maximum number of players")
@click.option("--motd", default="Welcome to Nex Server", help="Message of the day")
@click.option("--pvp/--no-pvp", default=True, help="Enable or disable PvP")
@click.option("--online-mode/--offline-mode", default=True, 
              help="Enable or disable online mode (authentication)")
@click.option("--interactive", "-i", is_flag=True, help="Use interactive mode for configuration")
def setup(dir: str, version: Optional[str], server_type: str, difficulty: str, 
          gamemode: str, max_players: int, motd: str, pvp: bool, 
          online_mode: bool, interactive: bool):
    """Set up a Minecraft server with the specified configuration."""
    manager = ServerManager(dir)

    # Interactive mode
    if interactive:
        server_type = click.prompt("Server type", type=click.Choice(SUPPORTED_SERVER_TYPES), 
                                  default=server_type)
        version = click.prompt("Minecraft version", default=version if version else "latest")
        difficulty = click.prompt("Difficulty", type=click.Choice(["peaceful", "easy", "normal", "hard"]), 
                                 default=difficulty)
        gamemode = click.prompt("Default gamemode", 
                              type=click.Choice(["survival", "creative", "adventure", "spectator"]), 
                              default=gamemode)
        max_players = click.prompt("Max players", type=int, default=max_players)
        motd = click.prompt("Server message (MOTD)", default=motd)
        pvp = click.confirm("Enable PvP?", default=pvp)
        online_mode = click.confirm("Enable online mode (authentication)?", default=online_mode)

    try:
        # First, download the server if version is specified
        if version:
            console.print(f"[bold]Downloading {server_type} server version {version}[/bold]")
            jar_path = manager.download_server(version, server_type)
            console.print(f"[green]Successfully downloaded to {jar_path}[/green]")
        
        # Set up the server configuration
        properties = {
            "difficulty": difficulty,
            "gamemode": gamemode,
            "max-players": max_players,
            "motd": motd,
            "pvp": pvp,
            "online-mode": online_mode
        }
        
        console.print("[bold]Setting up server configuration...[/bold]")
        manager.setup_server(properties)
        console.print(f"[green]Server successfully set up in {os.path.abspath(dir)}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1) 