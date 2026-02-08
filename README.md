# PyTWAT

**Modern Python Telnet Application for Trade Wars 2002**

PyTWAT is a secure, cross-platform replacement for the 2001 Java-based J-TWAT client, featuring a full desktop GUI with pixel-perfect terminal rendering, Trade Wars parsing capabilities, and automation features for enhanced gameplay.

## Table of Contents

- [Why PyTWAT?](#why-pytwat)
- [Features](#features)
- [Screenshots](#screenshots)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Development](#development)
- [Architecture](#architecture)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)

## Why PyTWAT?

[J-TWAT](http://www.goosemoose.com/~jtwat) (Java Telnet Application for Trade Wars) was created in 2001 as a powerful helper application for Trade Wars 2002. While the terminal still works on modern Java, the helper features are broken due to parser incompatibilities with newer JVM versions. Additionally, maintaining legacy Java applications raises security concerns.

PyTWAT solves these problems with:
- **Modern Python stack** (3.11+) with active security updates
- **Native terminal emulation** with VT320/ANSI support
- **Pixel-perfect rendering** using bitmap fonts (PT Mono) for authentic BBS display
- **Selective CP437 decoding** for proper box-drawing characters
- **Event-driven architecture** for extensibility
- **Cross-platform support** (macOS, Windows, Linux)

## Features

### Current (Phase 1 - Foundation)
- ✅ **Desktop GUI** - Built with PyQt6 for native look and feel
- ✅ **Telnet Client** - Async telnet connectivity with robust error handling
- ✅ **Terminal Emulation** - VT320/ANSI escape sequence support via pyte
- ✅ **Bitmap Font Rendering** - Pixel-perfect display using PT Mono font
- ✅ **Color Support** - Full 16-color ANSI palette with proper attributes
- ✅ **Character Encoding** - Smart ASCII/UTF-8 with selective CP437 for box drawing
- ✅ **Event Bus** - Loosely coupled component communication
- ✅ **Connection Management** - Connect/disconnect to BBS servers

### Planned (See [PYTWAT-PLAN.md](PYTWAT-PLAN.md))
- 🚧 **Trade Wars Parser** - Extract sectors, ports, ships, and game state
- 🚧 **Port Pair Analysis** - Identify profitable trading routes
- 🚧 **Automation Scripts** - Port trading, exploration, SST, CIM
- 🚧 **Persistent Database** - SQLite storage for game data
- 🚧 **Pathfinding** - Optimal route calculation
- 🚧 **Session Management** - Save and restore game sessions

## Screenshots

> **Note:** Screenshots coming soon!

## Quick Start

### Prerequisites
- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Poetry** - [Install Poetry](https://python-poetry.org/docs/#installation)

### Installation

```bash
# Clone the repository
git clone git@github.com:Chantal13/PyTWAT.git
cd PyTWAT

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running PyTWAT

```bash
# Using Poetry
poetry run python -m pytwat

# Or after activating the virtual environment
poetry shell
python -m pytwat

# Or using the installed script
poetry run pytwat
```

## Usage

### Connecting to a BBS Server

1. **Launch PyTWAT** using one of the methods above
2. **Enter connection details:**
   - Host: Your Trade Wars BBS server address (e.g., `142.44.247.204`)
   - Port: Usually `23` for telnet
3. **Click "Connect"** to establish connection
4. **Interact** with the terminal using keyboard input
5. **Disconnect** when done

### Default Connection

The GUI pre-fills with a default Trade Wars server for testing:
- Host: `142.44.247.204`
- Port: `23`

### Keyboard Shortcuts

- **Enter** - Send current input to server
- Standard text editing shortcuts work in the terminal

## Development

### Project Structure

```
pytwat/
├── src/pytwat/
│   ├── __main__.py              # Application entry point
│   ├── core/
│   │   └── event_bus.py         # Event-driven messaging
│   ├── network/
│   │   ├── telnet_client.py     # Async telnet implementation
│   │   └── terminal_emulator.py # VT320/ANSI emulation
│   ├── gui/
│   │   ├── main_window.py       # Main application window
│   │   └── widgets/
│   │       ├── bitmap_font.py           # Font rendering
│   │       ├── bitmap_terminal_widget.py # Pixel-perfect terminal
│   │       └── terminal_widget.py        # Base terminal widget
│   ├── parser/          # Game output parsers (planned)
│   ├── models/          # Data models (planned)
│   ├── storage/         # Database layer (planned)
│   ├── automation/      # Scripts (planned)
│   └── utils/           # Utilities
├── tests/
│   ├── fixtures/        # Sample TW output for testing
│   └── unit/            # Unit tests
├── docs/                # Documentation
├── pyproject.toml       # Poetry dependencies and metadata
└── README.md
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/unit/test_terminal_emulator.py

# Run with coverage
poetry run pytest --cov=pytwat
```

### Key Dependencies

- **PyQt6** (6.10.2+) - Desktop GUI framework
- **pyte** (0.8.2+) - VT320/ANSI terminal emulator
- **SQLAlchemy** (2.0.46+) - Database ORM (for future features)

### Development Dependencies

- **pytest** (9.0.2+) - Testing framework
- **pytest-qt** (4.5.0+) - PyQt testing support
- **pytest-asyncio** (1.3.0+) - Async test support

## Architecture

### Event-Driven Design

PyTWAT uses an event bus pattern for loose coupling between components:

```
┌─────────────┐     Events      ┌──────────────┐
│Telnet Client├────────────────>│  Event Bus   │
└─────────────┘                 └───────┬──────┘
                                        │
                         ┌──────────────┼──────────────┐
                         ↓              ↓              ↓
                  ┌──────────┐   ┌──────────┐  ┌──────────┐
                  │Terminal  │   │ Parser   │  │Automation│
                  │Emulator  │   │(planned) │  │(planned) │
                  └────┬─────┘   └──────────┘  └──────────┘
                       ↓
                  ┌──────────┐
                  │   GUI    │
                  └──────────┘
```

### Data Flow

```
Server → Telnet Client → Terminal Emulator → GUI Display
                              ↓
                         Parser (planned) → Universe State → Database
                              ↓
                         Automation Scripts → Commands → Telnet Client
```

### Recent Improvements

- **Bitmap font rendering** for authentic BBS appearance
- **Raw byte stream access** for proper character encoding
- **Selective CP437 decoding** for ANSI box-drawing characters
- **UTF-8 encoding** for modern BBS systems

## Project Status

### Phase 1: Foundation ✅ (In Progress)
**Goal:** Basic connectivity and display

- ✅ Project setup (Poetry, directory structure)
- ✅ Async telnet client with connection management
- ✅ Terminal widget with ANSI color support
- ✅ Bitmap font rendering for pixel-perfect display
- ✅ Character encoding (ASCII/UTF-8/CP437)
- ✅ Event bus architecture
- ✅ Main window GUI with connection controls

**Current Status:** Foundation is solid! Terminal display works great with proper ANSI rendering and character encoding.

### Phase 2: Parsing 🚧 (Next)
**Goal:** Extract game data

- Parser framework (regex patterns)
- Sector, port, ship parsers
- Prompt detection
- Mock TW server for testing

### Phase 3-6: Advanced Features (Planned)

See [PYTWAT-PLAN.md](PYTWAT-PLAN.md) for the complete implementation roadmap including:
- Data persistence (SQLAlchemy + SQLite)
- Port pair analysis
- Automation scripts (trading, exploration, SST, CIM)
- Advanced pathfinding

## Contributing

Contributions are welcome! This project is in active development.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`poetry run pytest`)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to your branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

### Areas for Contribution

- Trade Wars output parsers
- Automation scripts
- UI improvements
- Documentation
- Test coverage
- Bug fixes

## Background

**Trade Wars 2002** is a classic multiplayer BBS door game from 1986 that's still actively played today. Players explore a universe, trade commodities, battle opponents, and build trading empires.

**J-TWAT** was created by badboy in 2001 to enhance gameplay with features like:
- Automated port pair trading
- Universe mapping
- Ship status tracking
- Custom scripts (SST, CIM)

While groundbreaking for its time, J-TWAT faces challenges in 2026:
- Parser crashes on modern JVM versions
- Security concerns with Java 8 or older
- Difficult to maintain/extend

PyTWAT carries forward J-TWAT's legacy with modern technology and active development.

## FAQ

### Can I use this with any BBS server?

Yes! PyTWAT is a general-purpose telnet client with terminal emulation. While optimized for Trade Wars 2002, it works with any BBS that uses standard telnet protocol.

### Why not just fix J-TWAT?

Maintaining legacy Java code with deprecated APIs is challenging. A Python rewrite offers:
- Modern async/await patterns
- Better testing infrastructure
- Easier contributions from the community
- Active security updates

### Will this work on my operating system?

PyTWAT is cross-platform and runs on macOS, Windows, and Linux. If Python 3.11+ and PyQt6 run on your system, PyTWAT will too.

### Can I use this for other door games?

Absolutely! The terminal emulator supports standard ANSI/VT320 escape sequences used by many BBS door games.

## License

This project is licensed under the **GNU General Public License v2 or later** (GPL-2.0-or-later).

See the [LICENSE](LICENSE) file for details.

## Related Projects

- **Original J-TWAT**: http://www.goosemoose.com/~jtwat
- **Trade Wars 2002**: https://classictw.com/
- **Trade Wars Museum**: http://www.tw2002.com/

## Acknowledgments

- **badboy** - Creator of the original J-TWAT
- **Gary Martin** - Creator of Trade Wars 2002
- The Trade Wars community for keeping the game alive for 40+ years

---

**Built with ❤️ by the Trade Wars community**
