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

### Current (Phase 1 - Foundation) ✅ Complete!
- ✅ **Desktop GUI** - Built with PyQt6 for native look and feel
- ✅ **Telnet Client** - Async telnet connectivity with robust error handling
- ✅ **Terminal Emulation** - VT320/ANSI escape sequence support via pyte
- ✅ **Bitmap Font Rendering** - Pixel-perfect display using PT Mono font
- ✅ **Dynamic Text Scaling** - Terminal scales smoothly with window resize
- ✅ **Centered Display** - Content centered when maximized
- ✅ **Mouse Support** - SGR mouse protocol for BBS menu navigation
- ✅ **Colour Support** - Full 16-colour ANSI palette with iCE colour support
- ✅ **Character Encoding** - Smart CP437 decoding for authentic BBS display
- ✅ **Event Bus** - Loosely coupled component communication
- ✅ **Connection Management** - Connect/disconnect to BBS servers
- ✅ **60 FPS Rendering** - Throttled updates for smooth performance

### Planned (See [Milestones](https://github.com/Chantal13/PyTWAT/milestones))
- 📋 **Phase 2: Parsing** - Extract sectors, ports, ships, and game state ([7 issues](https://github.com/Chantal13/PyTWAT/milestone/1))
- 📋 **Phase 3: Persistence** - SQLite storage with SQLAlchemy ORM ([5 issues](https://github.com/Chantal13/PyTWAT/milestone/2))
- 📋 **Phase 4: Basic Automation** - Port pair trading script ([5 issues](https://github.com/Chantal13/PyTWAT/milestone/3))
- 📋 **Phase 5: Full Automation** - SST, CIM, exploration scripts ([5 issues](https://github.com/Chantal13/PyTWAT/milestone/4))
- 📋 **Phase 6: Polish & Release** - Map visualization, packaging, v1.0 ([7 issues](https://github.com/Chantal13/PyTWAT/milestone/5))

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

### Controls

**Keyboard:**
- **Enter** - Send current input to server
- **Arrow Keys** - Navigation (sent as VT320 escape sequences)
- **Backspace** - Delete character
- Standard text editing works in the terminal

**Mouse:**
- **Click** - Interact with BBS menus (SGR mouse protocol)
- Works with menu systems that support mouse input

**Window:**
- **Resize** - Text scales dynamically to fit window
- **Maximize** - Terminal content centers automatically

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

### Recent Improvements (Latest First)

- **Centered terminal display** - Content centers properly when window is maximized
- **Dynamic text scaling** - Text size adjusts smoothly with window resize, maintaining aspect ratio
- **Mouse support** - Full SGR mouse protocol for clicking BBS menus
- **60 FPS rendering** - Throttled updates for smooth display performance
- **Bitmap font rendering** - Authentic BBS appearance with PT Mono font
- **iCE colour support** - Proper bright backgrounds for ANSI art
- **CP437 character decoding** - Correct box-drawing characters and symbols

## Project Status

PyTWAT is under active development with **29 tracked issues** across **5 development phases**.

### Phase 1: Foundation ✅ **COMPLETE!**
**Deliverable:** Connect to TW server, see coloured output, type commands

- ✅ Project setup (Poetry, directory structure)
- ✅ Async telnet client with connection management
- ✅ Terminal widget with ANSI colour support
- ✅ Bitmap font rendering for pixel-perfect display
- ✅ Dynamic scaling with window resize
- ✅ Mouse support (SGR protocol)
- ✅ Character encoding (CP437/UTF-8)
- ✅ Event bus architecture
- ✅ Main window GUI with connection controls
- ✅ Centered display when maximized

**Status:** ✨ Foundation complete and working excellently! Terminal emulation is professional-grade.

### Phase 2: Parsing 📋 **UP NEXT**
**Deliverable:** Parse sectors, ports, ship status; display in GUI

[**View 7 issues →**](https://github.com/Chantal13/PyTWAT/milestone/1)
- Parser Framework (#1)
- Prompt Detection (#2) ⚠️ Critical
- Sector Parser (#3)
- Port Parser (#4)
- Ship Status Parser (#5)
- Mock TW Server (#6)
- Parser-EventBus Integration (#7)

### Phases 3-6: Advanced Features

**Phase 3: Persistence** ([5 issues](https://github.com/Chantal13/PyTWAT/milestone/2)) - Save game data
**Phase 4: Basic Automation** ([5 issues](https://github.com/Chantal13/PyTWAT/milestone/3)) - Port pair trading
**Phase 5: Full Automation** ([5 issues](https://github.com/Chantal13/PyTWAT/milestone/4)) - SST, CIM, exploration
**Phase 6: Polish & Release** ([7 issues](https://github.com/Chantal13/PyTWAT/milestone/5)) - v1.0 release

**Track Progress:**
- 📊 [View All Milestones](https://github.com/Chantal13/PyTWAT/milestones)
- 📝 [View All Issues](https://github.com/Chantal13/PyTWAT/issues)
- 📋 [Development Plan](PYTWAT-PLAN.md)

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

Check out our [open issues](https://github.com/Chantal13/PyTWAT/issues) for ways to contribute:

- **Good First Issues**: Look for `enhancement` label
- **High Priority**: Issues marked `critical`
- **Current Focus**: Phase 2 (Parsing) issues
- **Documentation**: Help improve docs and tutorials
- **Testing**: Add test coverage for existing features
- **Bug Fixes**: Fix reported bugs

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

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
