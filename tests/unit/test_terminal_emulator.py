"""Tests for the terminal emulator."""

import pytest
from pytwat.network.terminal_emulator import TerminalEmulator


def test_terminal_emulator_init():
    """Test terminal emulator initialization."""
    emulator = TerminalEmulator(80, 24)
    assert emulator.columns == 80
    assert emulator.lines == 24


def test_terminal_emulator_feed():
    """Test feeding data to the emulator."""
    emulator = TerminalEmulator(80, 24)
    emulator.feed("Hello World")
    display = emulator.get_display()
    assert "Hello World" in display[0]


def test_terminal_emulator_clear():
    """Test clearing the terminal."""
    emulator = TerminalEmulator(80, 24)
    emulator.feed("Test data")
    emulator.clear()
    display = emulator.get_display()
    assert all(line.strip() == "" for line in display)


def test_terminal_emulator_resize():
    """Test resizing the terminal."""
    emulator = TerminalEmulator(80, 24)
    emulator.resize(100, 30)
    assert emulator.columns == 100
    assert emulator.lines == 30
