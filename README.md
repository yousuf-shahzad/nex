# Nex - Minecraft Server Management Tool

<div align="center">

![Nex Banner](https://img.shields.io/badge/NEX-Minecraft%20Server%20Management-brightgreen?style=for-the-badge)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Java 17+](https://img.shields.io/badge/java-17%2B-orange.svg)](https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html)
[![GitHub issues](https://img.shields.io/github/issues/yousuf-shahzad/nex)](https://github.com/yousuf-shahzad/nex/issues)

**Simplify Minecraft server management with one powerful command-line tool**

[Installation](#-installation) • [Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-usage) • [Contributing](#-contributing)

</div>

## ✨ Features

- 🚀 **Multi-Server Support**: Download and manage Vanilla, Paper, or Purpur servers
- ⚙️ **Effortless Configuration**: Set up server properties via CLI flags or interactive wizard
- 🔌 **Plugin Management**: Search, install, and manage plugins from multiple sources
- 🛠️ **Version Control**: Easily switch between Minecraft versions with proper Java compatibility
- 📊 **Performance Optimization**: Configure memory settings and server properties for optimal performance
- 💻 **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux

## 📋 Installation

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

## 🚀 Quick Start

```bash
# Download and set up a Paper server in one command
nex setup --dir my_server --version 1.20.1 --type paper --difficulty normal --motd "My Awesome Server"

# Start your server
cd my_server
nex run --ram 4G
```

## 📁 Project Structure

```
nex/
├── cli/           # Command-line interface implementation
├── core/          # Core functionality
├── plugins/       # Plugin management system
├── utils/         # Utility functions
├── config/        # Configuration handling
└── downloaders/   # Server download implementations
```

## 💻 Usage

### Server Management

### Sign EULA
```bash
# Sign the EULA
nex sign
```

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

## 📊 Minecraft Server Version and Java Compatibility Matrix

Below is a compatibility matrix for Minecraft server versions and their corresponding Java version requirements:

| **Minecraft Version** | **Minimum Java Version** | **Recommended Java Version** | **Notes**                                                                 |
|-----------------------|--------------------------|------------------------------|---------------------------------------------------------------------------|
| 1.2.5 - 1.7.10        | Java 6                   | Java 8                       | Older versions work with Java 6 or 7, but Java 8 is widely recommended for stability. |
| 1.8 - 1.12.2          | Java 8                   | Java 8                       | Java 8 is the standard; later versions may cause compatibility issues with mods/plugins. |
| 1.13 - 1.16.5         | Java 8                   | Java 11 or 16                | Java 8 works, but Java 11 or 16 can improve performance; some mods require Java 16. |
| 1.17 - 1.17.1         | Java 16                  | Java 17                      | Java 16 is required; Java 17 is recommended for better performance.        |
| 1.18 - 1.20.4         | Java 17                  | Java 17                      | Java 17 is the minimum and recommended version.                           |
| 1.20.5 - 1.21.4       | Java 21                  | Java 21                      | Java 21 is required starting with 1.20.5 due to updated class file versions. |

## 📚 Examples

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

## 📝 Roadmap

Here are some features planned for future releases:

- **Backup and Restore**: Backup and restore functionality
- **Forge & Fabric Support**: Download and manage modded server types
- **Mod Management**: Install and configure mods similar to plugins
- **Additional Plugin Sources**: Integration with Bukkit and other repositories
- **Scheduled Backups**: Automated backup scheduling
- **Web Interface**: Easy server management through a browser

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The Minecraft community
- [Paper](https://papermc.io/) and [Purpur](https://purpurmc.org/) projects