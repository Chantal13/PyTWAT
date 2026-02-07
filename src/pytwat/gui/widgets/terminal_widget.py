"""
Terminal Widget - PyQt6 widget for displaying terminal output.

Provides a text display area with ANSI color support and input handling.
"""

from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QPalette
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
        Append content to the terminal.

        Args:
            content: Content to append
        """
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(content)
        self.text_edit.setTextCursor(cursor)

    def clear(self):
        """Clear the terminal."""
        self.text_edit.clear()

    def _handle_key_press(self, event):
        """
        Handle key press events.

        Captures input and sends it when Enter is pressed.
        """
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Get the current line
            cursor = self.text_edit.textCursor()
            cursor.select(cursor.SelectionType.LineUnderCursor)
            line = cursor.selectedText()

            # Send the line
            self.data_entered.emit(line + "\r\n")

            # Let the base class handle the key press (add newline)
            QTextEdit.keyPressEvent(self.text_edit, event)
        else:
            # Normal key handling
            QTextEdit.keyPressEvent(self.text_edit, event)

    def setFocus(self):
        """Set focus to the text edit."""
        self.text_edit.setFocus()
