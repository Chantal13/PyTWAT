# PyTWAT

**Modern Python Telnet Application for Trade Wars 2002**

PyTWAT is a secure, cross-platform replacement for the 2001 Java-based J-TWAT client, featuring a full desktop GUI, Trade Wars parsing, and automation capabilities.

## Features

- 🖥️ **Desktop GUI** - Built with PyQt6 for native look and feel
- 🔌 **Telnet Client** - Async telnet with VT320 terminal emulation
- 🎮 **Trade Wars Parser** - Extract sectors, ports, ships, and game state
- 🤖 **Automation** - Port pair trading, exploration, SST, CIM scripts
- 💾 **Persistent Database** - SQLite storage for game data
- 🔒 **Modern & Secure** - Python 3.11+ with regular security updates
- 🌐 **Cross-Platform** - Works on macOS, Windows, and Linux

## Project Status

🚧 **Phase 1: Foundation** - Setting up basic connectivity and display

See [PYTWAT-PLAN.md](PYTWAT-PLAN.md) for the complete implementation plan.

## Requirements

- Python 3.11 or higher
- Poetry (for dependency management)

## Installation

```bash
# Clone the repository
git clone git@github.com:Chantal13/PyTWAT.git
cd PyTWAT

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Development

### Project Structure

```
pytwat/
├── src/pytwat/
│   ├── core/          # Event bus, config
│   ├── network/       # Telnet, terminal
│   ├── parser/        # Game parsers
│   ├── models/        # Data models
│   ├── storage/       # Database
│   ├── automation/    # Scripts
│   ├── gui/           # PyQt6 interface
│   └── utils/         # Utilities
├── tests/
│   ├── fixtures/      # Sample TW output
│   └── unit/          # Test files
└── docs/              # Documentation
```

### Running Tests

```bash
poetry run pytest
```

## Background

PyTWAT is a complete rewrite of J-TWAT (Java Telnet Application for Trade Wars), originally created by badboy in 2001. While J-TWAT still functions as a telnet terminal on modern Java, its helper features are broken due to parser incompatibilities with newer Java versions. PyTWAT addresses these issues with a modern, maintainable codebase.

See [AGENTS.md](AGENTS.md) for documentation on the original J-TWAT project.

## License

This project is licensed under the GNU General Public License v2 or later.

## Related Projects

- Original J-TWAT: http://www.goosemoose.com/~jtwat
- Trade Wars 2002: https://classictw.com/
