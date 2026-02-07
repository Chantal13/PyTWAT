"""
Terminal Emulator - VT320/ANSI terminal emulation using pyte.

Processes ANSI escape sequences and maintains a virtual screen buffer.
"""

import pyte
from typing import List


class TerminalEmulator:
    """
    VT320 terminal emulator wrapper around pyte.

    Handles ANSI/VT escape sequences and maintains a character buffer
    for display in the GUI.
    """

    def __init__(self, columns: int = 80, lines: int = 24):
        """
        Initialize terminal emulator.

        Args:
            columns: Terminal width in characters
            lines: Terminal height in characters
        """
        self.columns = columns
        self.lines = lines
        self.screen = pyte.Screen(columns, lines)
        self.stream = pyte.ByteStream(self.screen)

    def feed(self, data: str) -> None:
        """
        Feed data to the terminal emulator.

        Args:
            data: Raw data from telnet connection (may contain ANSI codes)
        """
        self.stream.feed(data.encode('utf-8'))

    def get_display(self) -> List[str]:
        """
        Get the current screen content.

        Returns:
            List of strings, one per line
        """
        return self.screen.display

    def get_line(self, y: int) -> str:
        """
        Get a specific line from the screen.

        Args:
            y: Line number (0-indexed)

        Returns:
            Line content as string
        """
        if 0 <= y < self.lines:
            return self.screen.display[y]
        return ""

    def get_cursor_position(self) -> tuple[int, int]:
        """
        Get current cursor position.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.screen.cursor.x, self.screen.cursor.y)

    def clear(self) -> None:
        """Clear the screen."""
        self.screen.reset()

    def resize(self, columns: int, lines: int) -> None:
        """
        Resize the terminal.

        Args:
            columns: New width
            lines: New height
        """
        self.columns = columns
        self.lines = lines
        self.screen.resize(lines, columns)
