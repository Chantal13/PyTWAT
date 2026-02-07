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

    def _init_ui(self):
        """Initialize the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Text display area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(False)  # Allow input
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Set monospace font (like J-TWAT)
        font = QFont("Courier", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(font)

        # Set colors (white on black, like J-TWAT)
        palette = self.text_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
        self.text_edit.setPalette(palette)

        # Capture key presses
        self.text_edit.keyPressEvent = self._handle_key_press

        layout.addWidget(self.text_edit)

    def _setup_ansi_colors(self):
        """Set up ANSI color mapping."""
        return {
            '30': QColor(0, 0, 0),        # Black
            '31': QColor(205, 49, 49),    # Red
            '32': QColor(13, 188, 121),   # Green
            '33': QColor(229, 229, 16),   # Yellow
            '34': QColor(36, 114, 200),   # Blue
            '35': QColor(188, 63, 188),   # Magenta
            '36': QColor(17, 168, 205),   # Cyan
            '37': QColor(229, 229, 229),  # White
            '90': QColor(102, 102, 102),  # Bright Black (Gray)
            '91': QColor(241, 76, 76),    # Bright Red
            '92': QColor(35, 209, 139),   # Bright Green
            '93': QColor(245, 245, 67),   # Bright Yellow
            '94': QColor(59, 142, 234),   # Bright Blue
            '95': QColor(214, 112, 214),  # Bright Magenta
            '96': QColor(41, 184, 219),   # Bright Cyan
            '97': QColor(255, 255, 255),  # Bright White
        }

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
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Parse and render ANSI codes
        self._append_with_ansi(cursor, content)

        # Auto-scroll to bottom
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def _append_with_ansi(self, cursor, text):
        """
        Append text with ANSI color codes.

        Args:
            cursor: QTextCursor to append to
            text: Text with ANSI escape sequences
        """
        # ANSI escape sequence pattern
        ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')

        current_format = QTextCharFormat()
        current_format.setForeground(QColor("#ffffff"))  # Default white

        last_end = 0
        for match in ansi_pattern.finditer(text):
            # Insert text before this ANSI code
            if match.start() > last_end:
                plain_text = text[last_end:match.start()]
                cursor.insertText(plain_text, current_format)

            # Parse ANSI code
            codes = match.group(1).split(';') if match.group(1) else ['0']
            for code in codes:
                if code == '0' or code == '':
                    # Reset
                    current_format = QTextCharFormat()
                    current_format.setForeground(QColor("#ffffff"))
                elif code in self._ansi_colors:
                    # Set foreground color
                    current_format.setForeground(self._ansi_colors[code])

            last_end = match.end()

        # Insert remaining text
        if last_end < len(text):
            cursor.insertText(text[last_end:], current_format)

    def clear(self):
        """Clear the terminal."""
        self.text_edit.clear()

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
