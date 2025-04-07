# Nex - Minecraft Server Management Tool

Nex is a powerful command-line tool for managing Minecraft servers. It simplifies the process of downloading, configuring, and running Minecraft servers on Windows, macOS, and Linux.

## Features

- Download server JARs for any Minecraft version (Vanilla, Paper, or Purpur)
- Automatically set up server configuration files
- Customize server properties via command-line flags or interactive prompts
- List available versions for any server type
- Run servers with configurable memory settings
- Cross-platform support (Windows, macOS, and Linux)

## Installation

### From Source

```bash
git clone https://github.com/yousuf-shahzad/nex.git
cd nex
pip install -e .
```

## Requirements

- Python 3.9 or higher
- Java 17 or higher (for running Minecraft servers)

## Usage

### Download a Server

```bash
# Download the latest vanilla server
nex download latest vanilla

# Download a specific Paper server version
nex download 1.20.1 paper

# Download Purpur server
nex download 1.19.4 purpur
```

### List Available Versions

```bash
# List available vanilla versions
nex list-versions vanilla

# List available Paper versions
nex list-versions paper
```

### Set Up a Server

```bash
# Set up with default settings
nex setup --dir my_server --version 1.20.1 --type paper

# Set up with custom properties
nex setup --dir my_server --version 1.20.1 --type paper --difficulty hard --gamemode creative --max-players 10 --motd "My Awesome Server" --no-pvp

# Interactive setup
nex setup --interactive
```

### Run a Server

```bash
# Run with default settings (2GB RAM)
nex run

# Allocate 4GB RAM
nex run --ram 4G

# Run server without GUI
nex run --nogui
```

## Examples

### Complete Server Setup

```bash
# Create a new directory for the server
mkdir my_minecraft_server
cd my_minecraft_server

# Download and set up a Paper server
nex download 1.20.1 paper
nex setup --motd "Welcome to my server!" --max-players 20 --difficulty normal

# Run the server
nex run --ram 4G
```

### Quick Setup with One Command

```bash
# Set up and configure in one command
nex setup --dir my_server --version 1.20.1 --type paper --difficulty hard --motd "My Awesome Server" --max-players 10
```

## Plugin Management

Nex includes a powerful plugin management system that supports multiple plugin sources and handles dependencies automatically.

### Supported Plugin Sources
- SpigotMC
- Modrinth
- Hangar
- Bukkit

### Plugin Commands

#### Search for Plugins
```bash
nex plugins search <server_dir> <query> [--source SOURCE] [--category CATEGORY]
```

#### Install a Plugin
```bash
nex plugins install <server_dir> <plugin_id> <source> [--version VERSION]
```

#### List Installed Plugins
```bash
nex plugins list <server_dir>
```

#### Enable/Disable Plugins
```bash
nex plugins enable <server_dir> <plugin_name>
nex plugins disable <server_dir> <plugin_name>
```

#### Delete a Plugin
```bash
nex plugins delete <server_dir> <plugin_name>
```

#### Update a Plugin
```bash
nex plugins update <server_dir> <plugin_name>
```

#### Pin Plugin Version
```bash
nex plugins pin <server_dir> <plugin_name> <version>
nex plugins unpin <server_dir> <plugin_name>
```

#### Check Dependencies
```bash
nex plugins check-deps <server_dir> <plugin_name>
```

#### Configure Plugin
```bash
nex plugins configure <server_dir> <plugin_name> <key1>=<value1> [<key2>=<value2> ...]
```

### Features
- Automatic dependency resolution
- Version compatibility checking
- Plugin state management (enabled/disabled)
- Configuration file management
- Multiple plugin source support
- Version pinning
- Dependency tracking

## License

MIT
