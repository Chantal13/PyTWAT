"""
Terminal Emulator - VT320/ANSI terminal emulation using pyte.

Processes ANSI escape sequences and maintains a virtual screen buffer.
"""

import re
import pyte
from typing import List


class TerminalEmulator:
    # Pre-compiled regex pattern for ANSI SGR sequences (class-level constant)
    _ANSI_PATTERN = re.compile(r'(\x1b\[([0-9;]*)m)')
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
        # Convert iCE colors (ESC[5m + background) to bright backgrounds for pyte
        # This is needed because pyte doesn't preserve the blink attribute
        data = self._convert_ice_colors(data)

        self.stream.feed(data.encode('utf-8'))

    def _convert_ice_colors(self, data: str) -> str:
        """
        Convert iCE colour sequences to bright backgrounds.

        In iCE colour mode, ESC[5m (blink) combined with a background colour
        means bright background. We convert these to ESC[10Xm codes that
        pyte can render directly.

        Args:
            data: Raw terminal data with ANSI codes

        Returns:
            Data with iCE colours converted to bright backgrounds
        """
        # Early exit if no ANSI escape sequences present
        if '\x1b[' not in data:
            return data

        # Track current state
        result = []
        has_blink = False
        current_bg = None

        last_end = 0
        for match in self._ANSI_PATTERN.finditer(data):
            # Add text before this code
            result.append(data[last_end:match.start()])

            codes = match.group(2).split(';') if match.group(2) else ['0']
            new_codes = []

            for code in codes:
                if code == '0' or code == '':
                    # Reset - clear blink state
                    has_blink = False
                    current_bg = None
                    new_codes.append(code)
                elif code == '5':
                    # Blink - set flag but don't add to output
                    has_blink = True
                elif code.startswith('4') and len(code) == 2 and code[1].isdigit():
                    # Background colour (40-47)
                    bg_colour_num = int(code[1])
                    current_bg = bg_colour_num
                    if has_blink:
                        # Convert to bright background (100-107)
                        new_codes.append(f'10{bg_colour_num}')
                    else:
                        new_codes.append(code)
                else:
                    new_codes.append(code)

            # Reconstruct the ANSI sequence
            if new_codes:
                result.append(f'\x1b[{";".join(new_codes)}m')

            last_end = match.end()

        # Add remaining text
        result.append(data[last_end:])

        return ''.join(result)

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
