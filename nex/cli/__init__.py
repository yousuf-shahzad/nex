"""
CLI module for nex - Minecraft Server Management Tool
"""

import click

from .commands import (
    download_cmd,
    setup_cmd,
    list_versions_cmd,
    sign_eula_cmd,
    run_cmd
)

from .plugins import register_plugin_commands

@click.group()
@click.version_option()
def cli():
    """Nex: Minecraft Server Management Tool"""
    pass

# Register commands
cli.add_command(download_cmd.download)
cli.add_command(setup_cmd.setup)
cli.add_command(list_versions_cmd.list_versions)
cli.add_command(sign_eula_cmd.sign_eula)
cli.add_command(run_cmd.run)

# Register plugin commands
register_plugin_commands(cli)

def main():
    """Entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        from rich.console import Console
        console = Console()
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main() 