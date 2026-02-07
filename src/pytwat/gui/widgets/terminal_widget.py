"""
Terminal Widget - PyQt6 widget for displaying terminal output.

Provides a text display area with ANSI color support and input handling.
"""

import re
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QPalette, QTextCursor
from PyQt6.QtCore import pyqtSignal, Qt


class TerminalWidget(QWidget):
    """
    Terminal display widget with input capture.

    Displays terminal output and captures user input.
    """

    # Signal emitted when user presses Enter
    data_entered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._input_buffer = ""
        self._ansi_colors = self._setup_ansi_colors()
        self._screen_mode = False  # Track if we're in screen positioning mode

    def _init_ui(self):
        """Initialize the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Text display area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(False)  # Allow input
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Set monospace font - Monaco for better box-drawing alignment
        font = QFont("Monaco", 13)  # Try 13pt for better alignment
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        font.setKerning(False)  # Disable kerning for exact monospace
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0)  # No extra letter spacing
        self.text_edit.setFont(font)

        # Set tab stop width (8 characters, standard for BBS)
        metrics = self.text_edit.fontMetrics()
        self.text_edit.setTabStopDistance(metrics.horizontalAdvance(' ') * 8)

        # Set document to use fixed line height
        self.text_edit.document().setDocumentMargin(0)

        # Set colors (white on black, like J-TWAT)
        palette = self.text_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
        self.text_edit.setPalette(palette)

        # Hide the Qt cursor (BBS shows its own cursor)
        self.text_edit.setCursorWidth(0)

        # Capture key presses
        self.text_edit.keyPressEvent = self._handle_key_press

        layout.addWidget(self.text_edit)

    def _setup_ansi_colors(self):
        """Set up ANSI colour mapping using SyncTerm's exact palette (including iCE colours)."""
        colors = {
            # Standard foreground colours (30-37) - SyncTerm palette
            '30': QColor(0, 0, 0),           # 0: Black
            '31': QColor(168, 0, 0),         # 1: Red
            '32': QColor(0, 168, 0),         # 2: Green
            '33': QColor(168, 84, 0),        # 3: Brown
            '34': QColor(0, 0, 168),         # 4: Blue
            '35': QColor(168, 0, 168),       # 5: Magenta
            '36': QColor(0, 168, 168),       # 6: Cyan
            '37': QColor(168, 168, 168),     # 7: Light Gray

            # Standard background colours (40-47) - SyncTerm palette
            '40': QColor(0, 0, 0),           # Black background
            '41': QColor(168, 0, 0),         # Red background
            '42': QColor(0, 168, 0),         # Green background
            '43': QColor(168, 84, 0),        # Brown background
            '44': QColor(0, 0, 168),         # Blue background
            '45': QColor(168, 0, 168),       # Magenta background
            '46': QColor(0, 168, 168),       # Cyan background
            '47': QColor(168, 168, 168),     # Light Gray background

            # Bright foreground colours (90-97) - SyncTerm palette
            '90': QColor(84, 84, 84),        # 8: Dark Gray
            '91': QColor(255, 84, 84),       # 9: Light Red
            '92': QColor(84, 255, 84),       # 10: Light Green
            '93': QColor(255, 255, 84),      # 11: Yellow
            '94': QColor(84, 84, 255),       # 12: Light Blue
            '95': QColor(255, 84, 255),      # 13: Light Magenta
            '96': QColor(84, 255, 255),      # 14: Light Cyan
            '97': QColor(255, 255, 255),     # 15: White

            # Bright background colours (100-107) - iCE colour support
            '100': QColor(84, 84, 84),       # Dark Gray background
            '101': QColor(255, 84, 84),      # Light Red background
            '102': QColor(84, 255, 84),      # Light Green background
            '103': QColor(255, 255, 84),     # Yellow background
            '104': QColor(84, 84, 255),      # Light Blue background
            '105': QColor(255, 84, 255),     # Light Magenta background
            '106': QColor(84, 255, 255),     # Light Cyan background
            '107': QColor(255, 255, 255),    # White background
        }
        return colors

    def set_content(self, content: str):
        """
        Set the terminal content.

        Args:
            content: Terminal content to display
        """
        # Save cursor position
        cursor = self.text_edit.textCursor()
        scroll_pos = self.text_edit.verticalScrollBar().value()
        at_bottom = scroll_pos == self.text_edit.verticalScrollBar().maximum()

        # Update content
        self.text_edit.setPlainText(content)

        # Restore scroll position (or scroll to bottom if we were at bottom)
        if at_bottom:
            self.text_edit.verticalScrollBar().setValue(
                self.text_edit.verticalScrollBar().maximum()
            )
        else:
            self.text_edit.verticalScrollBar().setValue(scroll_pos)

    def append_content(self, content: str):
        """
        Append content to the terminal with ANSI color support.

        Args:
            content: Content to append (may contain ANSI codes)
        """
        # Disable updates during append for better performance
        self.text_edit.setUpdatesEnabled(False)

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Parse and render ANSI codes
        self._append_with_ansi(cursor, content)

        # Auto-scroll to bottom
        self.text_edit.setTextCursor(cursor)

        # Re-enable updates and refresh once
        self.text_edit.setUpdatesEnabled(True)
        self.text_edit.ensureCursorVisible()

    def _append_with_ansi(self, cursor, text):
        """
        Append text with ANSI escape codes (colors and control sequences).

        Args:
            cursor: QTextCursor to append to
            text: Text with ANSI escape sequences
        """
        # Comprehensive ANSI escape sequence pattern
        # Matches: colors (\x1b[...m), cursor ops (\x1b[...H/J/K), etc.
        ansi_pattern = re.compile(r'\x1b\[([0-9;]*)(m|H|J|K|A|B|C|D|s|u|f)?')

        current_format = QTextCharFormat()
        current_format.setForeground(QColor("#ffffff"))  # Default white

        last_end = 0
        for match in ansi_pattern.finditer(text):
            # Insert text before this ANSI code
            if match.start() > last_end:
                plain_text = text[last_end:match.start()]
                cursor.insertText(plain_text, current_format)

            command = match.group(2)
            params = match.group(1)

            if command == 'm':
                # Color/style codes
                codes = params.split(';') if params else ['0']
                for code in codes:
                    if code == '0' or code == '':
                        # Reset
                        current_format = QTextCharFormat()
                        current_format.setForeground(QColor("#ffffff"))
                    elif code == '1':
                        # Bold
                        current_format.setFontWeight(700)
                    elif code in self._ansi_colors:
                        # Set foreground color
                        current_format.setForeground(self._ansi_colors[code])
                    # Background colors (40-47, 100-107)
                    elif code.startswith('4') and len(code) == 2:
                        bg_code = str(int(code) - 10)  # Convert 40->30, etc.
                        if bg_code in self._ansi_colors:
                            current_format.setBackground(self._ansi_colors[bg_code])
            elif command == 'J':
                # Clear screen commands
                if params == '2' or params == '':
                    # Clear entire screen
                    self.text_edit.clear()
            elif command == 'K':
                # Erase to end of line (we'll just ignore for now in scrolling mode)
                pass
            # Cursor movement commands (H, A, B, C, D, f) are ignored in scrolling mode

            last_end = match.end()

        # Insert remaining text
        if last_end < len(text):
            cursor.insertText(text[last_end:], current_format)

    def clear(self):
        """Clear the terminal."""
        self.text_edit.clear()

    def render_screen(self, screen) -> None:
        """
        Render a pyte Screen object with proper colors and formatting.

        Args:
            screen: pyte.Screen object with character buffer and attributes
        """
        # Disable updates during render for better performance
        self.text_edit.setUpdatesEnabled(False)

        # Check if we should scroll to bottom after update
        scroll_bar = self.text_edit.verticalScrollBar()
        was_at_bottom = scroll_bar.value() >= scroll_bar.maximum() - 10

        # Clear and rebuild
        self.text_edit.clear()
        cursor = self.text_edit.textCursor()

        # Map pyte color names/numbers to ANSI codes
        def get_color_code(color, is_bg=False):
            """Convert pyte color to ANSI code."""
            if isinstance(color, str):
                color_map = {
                    'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
                    'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7,
                    'default': 7
                }
                color_num = color_map.get(color, 7)
            else:
                color_num = color if color is not None else 7

            # Map to ANSI codes (30-37 for fg, 40-47 for bg, 90-97 for bright fg)
            if is_bg:
                return str(40 + (color_num % 8))
            else:
                # Use bright colors (90-97) if color_num >= 8
                if color_num >= 8:
                    return str(90 + (color_num % 8))
                else:
                    return str(30 + color_num)

        # Debug: Print character attributes for first few chars
        debug_printed = False

        # Render each line character-by-character for exact alignment
        for line_num in range(screen.lines):
            for col_num in range(screen.columns):
                char_obj = screen.buffer[line_num][col_num]

                # Get character data
                char = char_obj.data

                # Debug: Print attributes for characters with backgrounds or blink
                if not debug_printed and (char_obj.blink or (char_obj.bg != 'default' and char_obj.bg != 'black')):
                    print(f"DEBUG Char: '{char}' fg={char_obj.fg} bg={char_obj.bg} bold={char_obj.bold} blink={char_obj.blink} reverse={char_obj.reverse}")
                    debug_printed = True

                # Build format for this character
                char_format = QTextCharFormat()

                # Set foreground colour
                # In ANSI terminals, bold makes colors bright (adds 8 to color number)
                fg_color_num = get_color_code(char_obj.fg, is_bg=False)
                if char_obj.bold and fg_color_num.startswith('3'):
                    # Convert normal color (30-37) to bright (90-97) when bold
                    color_num = int(fg_color_num) - 30
                    fg_code = str(90 + color_num)
                else:
                    fg_code = fg_color_num

                if fg_code in self._ansi_colors:
                    char_format.setForeground(self._ansi_colors[fg_code])

                # Set background colour (iCE colour support - 16 background colours)
                if char_obj.bg != 'default':
                    # Get the numeric colour value
                    if isinstance(char_obj.bg, str):
                        color_map = {
                            'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
                            'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7
                        }
                        bg_num = color_map.get(char_obj.bg, 0)
                    else:
                        bg_num = char_obj.bg if char_obj.bg is not None else 0

                    # iCE colour: Use blink attribute as high-intensity bit for background
                    # When blink is set, add 8 to background colour for bright backgrounds
                    if hasattr(char_obj, 'blink') and char_obj.blink:
                        bg_num += 8

                    # Map to background ANSI code (40-47 for normal, 100-107 for bright)
                    if bg_num >= 8:
                        bg_code = str(100 + (bg_num % 8))  # Bright background (iCE)
                    else:
                        bg_code = str(40 + bg_num)  # Normal background

                    if bg_code in self._ansi_colors:
                        char_format.setBackground(self._ansi_colors[bg_code])

                # Set bold
                if char_obj.bold:
                    char_format.setFontWeight(700)

                # Insert character
                cursor.insertText(char, char_format)

            # Add newline except for last line
            if line_num < screen.lines - 1:
                cursor.insertText('\n')

        # Restore scroll position or scroll to bottom
        if was_at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())

        # Re-enable updates
        self.text_edit.setUpdatesEnabled(True)

    def _formats_equal(self, fmt1, fmt2):
        """Check if two QTextCharFormats are equal."""
        return (fmt1.foreground().color() == fmt2.foreground().color() and
                fmt1.background().color() == fmt2.background().color() and
                fmt1.fontWeight() == fmt2.fontWeight())

    def _handle_key_press(self, event):
        """
        Handle key press events.

        Sends characters as they're typed (telnet-style).
        """
        # Handle special keys
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.data_entered.emit("\r\n")
            return
        elif event.key() == Qt.Key.Key_Backspace:
            self.data_entered.emit("\b")
            return
        elif event.key() == Qt.Key.Key_Tab:
            self.data_entered.emit("\t")
            return
        elif event.key() == Qt.Key.Key_Escape:
            self.data_entered.emit("\x1b")
            return

        # Regular character input
        text = event.text()
        if text:
            self.data_entered.emit(text)

        # Let Qt handle the display (but server echo will overwrite)
        # We don't call the base class to avoid double-display
        # The server will echo back what we type

    def setFocus(self):
        """Set focus to the text edit."""
        self.text_edit.setFocus()
