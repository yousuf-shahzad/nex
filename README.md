# Nex - Minecraft Server Management Tool

Nex is a powerful command-line tool for managing Minecraft servers. It simplifies the process of downloading, configuring, and running Minecraft servers on Windows, macOS, and Linux.

## Features

- Download server JARs for any Minecraft version (Vanilla, Paper, or Purpur)
- Automatically set up server configuration files
- Customize server properties via command-line flags or interactive prompts
- List available versions for any server type
- Run servers with configurable memory settings
- Cross-platform support (Windows, macOS, and Linux)
- Comprehensive plugin management system

## Installation

### Prerequisites

- Python 3.9 or higher
- Java 17 or higher (for running Minecraft servers)

### Installation Methods

#### From Source
```bash
git clone https://github.com/yousuf-shahzad/nex.git
cd nex
pip install -e .
```

## Project Structure

```
nex/
├── cli/           # Command-line interface implementation
├── core/          # Core functionality
├── plugins/       # Plugin management system
├── utils/         # Utility functions
├── config/        # Configuration handling
└── downloaders/   # Server download implementations
```

## Usage

### Server Management

#### Download a Server
```bash
# Download the latest vanilla server
nex download latest vanilla

# Download a specific Paper server version
nex download 1.20.1 paper

# Download Purpur server
nex download 1.19.4 purpur
```

#### List Available Versions
```bash
# List available vanilla versions
nex list-versions vanilla

# List available Paper versions
nex list-versions paper
```

#### Server Setup
```bash
# Set up with default settings
nex setup --dir my_server --version 1.20.1 --type paper

# Set up with custom properties
nex setup --dir my_server --version 1.20.1 --type paper \
    --difficulty hard \
    --gamemode creative \
    --max-players 10 \
    --motd "My Awesome Server" \
    --no-pvp

# Interactive setup
nex setup --interactive
```

#### Run a Server
```bash
# Run with default settings (2GB RAM)
nex run

# Allocate 4GB RAM
nex run --ram 4G

# Run server without GUI
nex run --nogui
```

### Plugin Management

Nex provides a comprehensive plugin management system with support for multiple sources and automatic dependency handling.

#### Supported Plugin Sources
- SpigotMC
- Modrinth

#### Plugin Commands

```bash
# Search for plugins
nex plugins search <server_dir> <query> [--source SOURCE] [--category CATEGORY]

# Install a plugin
nex plugins install <server_dir> <plugin_id> <source> [--version VERSION]

# List installed plugins
nex plugins list <server_dir>

# Enable/disable plugins
nex plugins enable <server_dir> <plugin_name>
nex plugins disable <server_dir> <plugin_name>

# Delete a plugin
nex plugins delete <server_dir> <plugin_name>

# Update a plugin
nex plugins update <server_dir> <plugin_name>

# Pin plugin version
nex plugins pin <server_dir> <plugin_name> <version>
nex plugins unpin <server_dir> <plugin_name>

# Check dependencies
nex plugins check-deps <server_dir> <plugin_name>

# Configure plugin
nex plugins configure <server_dir> <plugin_name> <key1>=<value1> [<key2>=<value2> ...]
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
nex setup --dir my_server \
    --version 1.20.1 \
    --type paper \
    --difficulty hard \
    --motd "My Awesome Server" \
    --max-players 10
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
