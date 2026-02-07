# Plan: PyTWAT - Modern Python Rewrite of J-TWAT

## Context
J-TWAT is a 2001 Java telnet client for Trade Wars 2002 with automation features. While the terminal works on Java 25, helper features are broken (parser crash: `ArrayIndexOutOfBoundsException`). User has security concerns about using old Java versions and wants a modern, secure Python replacement.

## User Requirements
- Full desktop GUI (like J-TWAT)
- Telnet client with VT320 terminal emulation
- Trade Wars parser (sectors, ports, ships)
- Port pair analysis
- Ship exploration automation
- All helper scripts (SST, CIM, etc.)

## Technology Stack
**Python 3.11+ with:**
- **PyQt6** - Desktop GUI framework
- **asyncio + telnetlib3** - Async telnet client
- **pyte** - VT320 terminal emulator
- **SQLAlchemy + SQLite** - Data persistence
- **networkx** - Pathfinding algorithms

## Architecture Overview

### Core Components
1. **Network Layer** (`network/`)
   - Async telnet client
   - Terminal emulator (VT320/ANSI)
   - Stream buffering and prompt detection

2. **Parser Layer** (`parser/`)
   - Game output parser (sectors, ports, ships)
   - Regex pattern library
   - Prompt detector (critical for automation)

3. **Data Models** (`models/`)
   - Sector, Port, Ship, Planet, Universe
   - Dataclasses with validation

4. **Storage Layer** (`storage/`)
   - SQLAlchemy ORM
   - Repository pattern
   - Session tracking

5. **Automation Layer** (`automation/`)
   - Script base class
   - SST, CIM, port pair trade scripts
   - Port pair analyzer

6. **GUI Layer** (`gui/`)
   - Main window (PyQt6)
   - Terminal widget
   - Status widget
   - Script controls

7. **Event Bus** (`core/`)
   - Event-driven communication
   - Loose coupling between components

### Data Flow
```
Telnet → Terminal Emulator → Parser → Universe State → Database
                           ↓                    ↓
                        GUI Display        Script Logic → Commands → Telnet
```

## Implementation Phases

### Phase 1: Foundation (MVP)
**Goal:** Basic connectivity and display
- Project setup (Poetry, directory structure)
- Async telnet client
- Terminal widget with ANSI colors
- Connection dialog

**Deliverable:** Connect to TW server, see colored output, type commands

### Phase 2: Parsing
**Goal:** Extract game data
- Parser framework (regex patterns)
- Sector, port, ship parsers
- Prompt detection
- Event bus integration
- Mock TW server for testing

**Deliverable:** Parse sectors, ports, ship status; display in GUI

### Phase 3: Persistence
**Goal:** Save game data
- SQLAlchemy models (sectors, ports, sessions)
- Repositories
- Session management

**Deliverable:** Game state persists between sessions

### Phase 4: Basic Automation
**Goal:** First working script
- Script base class
- Port pair trade script
- Port pair analyzer
- Start/stop controls

**Deliverable:** Run basic port pair trading script

### Phase 5: Full Automation
**Goal:** Feature parity with J-TWAT
- SST script
- CIM script
- Exploration automation
- Advanced analysis
- Script parameter dialogs

**Deliverable:** All J-TWAT features replicated

### Phase 6: Polish
**Goal:** Production ready
- Universe map visualization
- Analysis dialogs
- Preferences
- Comprehensive testing
- Documentation
- Packaging (PyInstaller)

**Deliverable:** v1.0 release

## Critical Files

**Phase 1 (Start here):**
- `src/pytwat/core/event_bus.py` - Central event system
- `src/pytwat/network/telnet_client.py` - Telnet connection
- `src/pytwat/network/terminal_emulator.py` - ANSI processing
- `src/pytwat/gui/main_window.py` - Main UI
- `src/pytwat/gui/widgets/terminal_widget.py` - Terminal display

**Phase 2:**
- `src/pytwat/parser/game_parser.py` - Parser orchestrator
- `src/pytwat/parser/patterns.py` - Regex patterns
- `src/pytwat/parser/sector_parser.py` - Sector parsing
- `src/pytwat/parser/prompt_detector.py` - Prompt detection
- `src/pytwat/models/universe.py` - Game state container

**Phase 3:**
- `src/pytwat/storage/database.py` - SQLAlchemy setup
- `src/pytwat/storage/repositories/sector_repository.py` - Data access

**Phase 4:**
- `src/pytwat/automation/script_base.py` - Base script class
- `src/pytwat/automation/scripts/port_pair_trade.py` - Trading script
- `src/pytwat/automation/analyzers/port_pair_analyzer.py` - Analysis

## Testing Strategy
- **Unit tests:** Parser, models, analyzers (pytest)
- **Integration tests:** Mock TW server
- **GUI tests:** pytest-qt
- **Fixtures:** Real TW output samples

## Verification Plan
After each phase:
1. Run unit tests: `pytest tests/`
2. Manual testing: Connect to real TW server
3. Verify phase deliverable works as specified

## Project Structure
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

## Estimated Timeline
- Phase 1: 1-2 weeks
- Phase 2: 1-2 weeks
- Phase 3: 1 week
- Phase 4: 1-2 weeks
- Phase 5: 2-3 weeks
- Phase 6: 1-2 weeks
**Total: ~10-13 weeks** for full implementation

## Success Criteria
- ✅ Connects to Trade Wars servers
- ✅ Displays ANSI colored terminal
- ✅ Parses sectors, ports, ship data
- ✅ Stores data persistently
- ✅ Runs port pair trading automation
- ✅ All J-TWAT scripts replicated
- ✅ No security vulnerabilities
- ✅ Cross-platform (macOS, Windows, Linux)
