#!/usr/bin/env python3
import os
import sys
import click
from typing import Optional

from .server_manager import ServerManager
from .downloaders import SUPPORTED_SERVER_TYPES
from .config.properties import ServerProperties, validate_property
from rich.console import Console
from rich import print as rprint

console = Console()

@click.group()
@click.version_option()
def cli():
    """Nex: Minecraft Server Management Tool"""
    pass


@cli.command()
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


@cli.command()
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


@cli.command("list-versions")
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


@cli.command("sign")
def sign_eula():
    """Sign the EULA by creating eula.txt."""
    try:
        with open("eula.txt", "w") as f:
            f.write("# Generated by Nex\n")
            f.write("eula=true\n")
        console.print("[green]EULA signed successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
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


def main():
    try:
        cli()
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()