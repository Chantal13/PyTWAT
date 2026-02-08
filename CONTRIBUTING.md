# Contributing to PyTWAT

Thank you for your interest in contributing to PyTWAT! This document provides guidelines and information to help you contribute effectively.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Areas for Contribution](#areas-for-contribution)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- **Python 3.11 or higher**
- **Poetry** for dependency management
- **Git** for version control
- Basic familiarity with:
  - Async Python (asyncio)
  - PyQt6 (for GUI contributions)
  - Trade Wars 2002 (helpful but not required)

### First Contribution?

If you're new to open source, check out:
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Timers Only](https://www.firsttimersonly.com/)

Look for issues labeled `good first issue` or `help wanted` in the issue tracker.

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone git@github.com:YOUR_USERNAME/PyTWAT.git
cd PyTWAT

# Add upstream remote
git remote add upstream git@github.com:Chantal13/PyTWAT.git
```

### 2. Install Dependencies

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 3. Verify Setup

```bash
# Run tests to verify everything works
poetry run pytest

# Run the application
poetry run python -m pytwat
```

### 4. Create a Branch

```bash
# Always create a new branch for your changes
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## How to Contribute

### Reporting Bugs

Before submitting a bug report:
1. **Check existing issues** to avoid duplicates
2. **Update to the latest version** to see if the bug persists
3. **Collect information** about your environment

Include in your bug report:
- PyTWAT version
- Python version (`python --version`)
- Operating system and version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages or logs
- Screenshots (if applicable)

### Suggesting Features

Feature suggestions are welcome! Please:
1. **Check existing issues** for similar suggestions
2. **Explain the use case** - why is this feature needed?
3. **Describe the solution** - how should it work?
4. **Consider alternatives** - are there other ways to solve this?

### Submitting Changes

1. **Make your changes** in your feature branch
2. **Write tests** for new functionality
3. **Update documentation** as needed
4. **Follow code style guidelines** (see below)
5. **Commit your changes** with clear messages
6. **Push to your fork**
7. **Open a Pull Request**

## Code Style Guidelines

### Python Style

We follow [PEP 8](https://pep8.org/) with these specific guidelines:

#### Formatting

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 88 characters (Black default)
- **Quotes**: Double quotes for strings (prefer `"hello"` over `'hello'`)
- **Imports**: Organize with:
  ```python
  # Standard library imports
  import asyncio
  import sys

  # Third-party imports
  from PyQt6.QtWidgets import QWidget

  # Local imports
  from ..network.telnet_client import TelnetClient
  ```

#### Naming Conventions

- **Classes**: `PascalCase` (e.g., `TelnetClient`)
- **Functions/Methods**: `snake_case` (e.g., `connect_to_server`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private members**: Prefix with `_` (e.g., `_internal_method`)

#### Type Hints

Use type hints for function signatures:

```python
def parse_sector(data: str) -> Sector | None:
    """Parse sector information from game output."""
    ...
```

#### Docstrings

Use Google-style docstrings:

```python
def connect(self, host: str, port: int) -> bool:
    """Connect to a telnet server.

    Args:
        host: The hostname or IP address to connect to.
        port: The port number to connect to.

    Returns:
        True if connection successful, False otherwise.

    Raises:
        ConnectionError: If connection fails after retries.
    """
    ...
```

#### Comments

- Write clear, concise comments
- Explain **why**, not **what** (code shows what)
- Update comments when changing code
- Use `#` for inline comments, `"""` for docstrings

### Async Code

- Use `async`/`await` for I/O operations
- Avoid blocking calls in async functions
- Use `asyncio.create_task()` for concurrent operations
- Handle exceptions in async code properly

### GUI Code

- Keep UI logic separate from business logic
- Use Qt signals/slots for communication
- Keep event handlers simple (delegate to other methods)
- Use the event bus for cross-component communication

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/unit/test_telnet_client.py

# Run with coverage report
poetry run pytest --cov=pytwat --cov-report=html
```

### Writing Tests

- Write tests for all new features
- Use descriptive test names: `test_connect_success_updates_status`
- Use pytest fixtures for common setup
- Mock external dependencies (network, filesystem)
- Test both success and failure cases

Example test structure:

```python
import pytest
from pytwat.network.telnet_client import TelnetClient

@pytest.mark.asyncio
async def test_connect_success():
    """Test successful connection to server."""
    client = TelnetClient()
    result = await client.connect("localhost", 23)
    assert result is True
    assert client.connected is True

@pytest.mark.asyncio
async def test_connect_invalid_host():
    """Test connection failure with invalid host."""
    client = TelnetClient()
    with pytest.raises(ConnectionError):
        await client.connect("invalid.host", 23)
```

### Test Coverage

- Aim for 80%+ coverage on new code
- Critical paths (parsers, automation) should have higher coverage
- Don't sacrifice test quality for coverage numbers

## Pull Request Process

### Before Submitting

1. **Update your branch** with latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   poetry run pytest
   ```

3. **Check code style** (if linters are configured):
   ```bash
   poetry run black src/
   poetry run flake8 src/
   ```

4. **Update documentation** if needed

### PR Description

Provide a clear description including:

- **Summary**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Changes**: What specifically changed?
- **Testing**: How was this tested?
- **Screenshots**: For UI changes
- **Related Issues**: Link to related issues (e.g., "Fixes #123")

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

- Maintainers will review your PR
- Address feedback and requested changes
- Keep discussions professional and constructive
- Be patient - reviews may take a few days

### After Merge

- Delete your feature branch (both locally and on GitHub)
- Pull the latest changes from upstream
- Celebrate your contribution! 🎉

## Issue Reporting

### Bug Reports

Use the bug report template and include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs. actual behavior
- Environment details
- Error messages/logs
- Screenshots if applicable

### Feature Requests

Use the feature request template and include:
- Clear, descriptive title
- Problem statement (what pain point does this solve?)
- Proposed solution
- Alternative solutions considered
- Additional context

### Questions

For questions about using PyTWAT:
- Check the [README](README.md) and documentation first
- Search existing issues
- Create a new issue with the "question" label

## Areas for Contribution

### High Priority

1. **Trade Wars Parsers** (Phase 2)
   - Sector information parser
   - Port data parser
   - Ship status parser
   - Combat log parser

2. **Testing**
   - Increase test coverage
   - Create fixtures with real TW output
   - Integration tests

3. **Documentation**
   - API documentation
   - User guide
   - Developer guide
   - Code examples

### Medium Priority

4. **Automation Scripts** (Phase 4+)
   - Port pair trading
   - Universe exploration
   - SST (Super Spy Tool)
   - CIM (Colonist Investment Manager)

5. **Database Layer** (Phase 3)
   - SQLAlchemy models
   - Repositories
   - Migration system

6. **UI Enhancements**
   - Keyboard shortcuts
   - Configuration dialog
   - Status indicators
   - Script controls

### Future Features

7. **Advanced Features**
   - Pathfinding algorithms
   - Universe mapping visualization
   - Session playback
   - Plugin system

## Community

### Communication

- **GitHub Issues**: Bug reports, feature requests, questions
- **Pull Requests**: Code contributions and discussions
- **Discussions**: General questions and community chat (if enabled)

### Getting Help

Stuck? Here's how to get help:
1. Check the [README](README.md) and documentation
2. Search existing issues and PRs
3. Create a new issue with the "question" label
4. Be specific about what you're trying to do and what's not working

### Recognition

Contributors are recognized in:
- Git commit history
- GitHub contributors page
- Release notes (for significant contributions)
- README acknowledgments (for major features)

## License

By contributing to PyTWAT, you agree that your contributions will be licensed under the GNU General Public License v2 or later (GPL-2.0-or-later).

---

**Thank you for contributing to PyTWAT!** Your efforts help keep Trade Wars 2002 alive for future generations of players.
