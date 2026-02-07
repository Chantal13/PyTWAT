"""
Bitmap Terminal Widget - Pixel-perfect terminal rendering using bitmap fonts.

Renders terminal output using bitmap fonts for exact ANSI art alignment.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QImage, QColor, QPalette, QFont
from PyQt6.QtCore import pyqtSignal, Qt, QRect, QSize


class BitmapTerminalWidget(QWidget):
    """
    Terminal display widget using bitmap font rendering.

    Provides pixel-perfect character rendering for ANSI/ASCII art using
    fixed-pitch fonts with exact positioning.
    """

    # Signal emitted when user presses a key
    data_entered = pyqtSignal(str)

    def __init__(self, parent=None, columns: int = 80, lines: int = 24):
        super().__init__(parent)

        self.columns = columns
        self.lines = lines

        # Character dimensions (scaled up for modern displays)
        self.char_width = 11
        self.char_height = 22

        # Set up font (larger for better readability)
        # PT Mono for better BBS display
        self.font = QFont("PT Mono", 16)
        self.font.setStyleHint(QFont.StyleHint.Monospace)
        self.font.setFixedPitch(True)
        self.font.setKerning(False)
        self.font.setStyleStrategy(QFont.StyleStrategy.NoAntialias)  # Disable anti-aliasing for crisp text

        # Create back buffer for rendering
        self._create_back_buffer()

        # Set up ANSI colour palette (SyncTerm colours)
        self._ansi_colors = self._setup_ansi_colors()

        # Widget configuration
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(
            self.columns * self.char_width,
            self.lines * self.char_height
        )

        # Set background colour to black
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def _create_back_buffer(self) -> None:
        """Create the back buffer image for rendering."""
        width = self.columns * self.char_width
        height = self.lines * self.char_height

        self.back_buffer = QImage(width, height, QImage.Format.Format_ARGB32)
        self.back_buffer.fill(QColor(0, 0, 0))  # Black background

    def _setup_ansi_colors(self) -> dict:
        """Set up ANSI colour mapping using SyncTerm's exact palette."""
        colors = {
            # Standard colours (0-7)
            0: QColor(0, 0, 0),           # Black
            1: QColor(168, 0, 0),         # Red
            2: QColor(0, 168, 0),         # Green
            3: QColor(168, 84, 0),        # Brown
            4: QColor(0, 0, 168),         # Blue
            5: QColor(168, 0, 168),       # Magenta
            6: QColor(0, 168, 168),       # Cyan
            7: QColor(168, 168, 168),     # Light Gray

            # Bright colours (8-15)
            8: QColor(84, 84, 84),        # Dark Gray
            9: QColor(255, 84, 84),       # Light Red
            10: QColor(84, 255, 84),      # Light Green
            11: QColor(255, 255, 84),     # Yellow
            12: QColor(84, 84, 255),      # Light Blue
            13: QColor(255, 84, 255),     # Light Magenta
            14: QColor(84, 255, 255),     # Light Cyan
            15: QColor(255, 255, 255),    # White
        }
        return colors

    def render_screen(self, screen) -> None:
        """
        Render a pyte Screen object with bitmap fonts.

        Args:
            screen: pyte.Screen object with character buffer and attributes
        """
        # Clear back buffer
        self.back_buffer.fill(QColor(0, 0, 0))

        painter = QPainter(self.back_buffer)
        # Disable anti-aliasing for crisp text rendering
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)

        # Render each character
        for line_num in range(min(screen.lines, self.lines)):
            for col_num in range(min(screen.columns, self.columns)):
                char_obj = screen.buffer[line_num][col_num]

                # Get character (already decoded from CP437)
                char = char_obj.data
                if not char or char == '\x00':
                    char = ' '
                char_code = ord(char)

                # Get colours
                fg_color = self._get_char_color(char_obj, is_bg=False)
                bg_color = self._get_char_color(char_obj, is_bg=True)

                # Calculate position
                x = col_num * self.char_width
                y = line_num * self.char_height

                # Draw background
                painter.fillRect(x, y, self.char_width, self.char_height, bg_color)

                # Draw character glyph (colorized)
                self._draw_char(painter, char_code, x, y, fg_color)

        painter.end()

        # Trigger repaint
        self.update()

    def _get_char_color(self, char_obj, is_bg: bool) -> QColor:
        """
        Get the colour for a character.

        Args:
            char_obj: pyte character object
            is_bg: True for background colour, False for foreground

        Returns:
            QColor for the character
        """
        if is_bg:
            # Background colour
            if char_obj.bg == 'default':
                return self._ansi_colors[0]  # Black

            # Get background colour number
            if isinstance(char_obj.bg, str):
                color_map = {
                    'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
                    'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7
                }
                bg_num = color_map.get(char_obj.bg, 0)
            else:
                bg_num = char_obj.bg if char_obj.bg is not None else 0

            # iCE colours: blink adds 8 for bright backgrounds
            if hasattr(char_obj, 'blink') and char_obj.blink:
                bg_num += 8

            return self._ansi_colors.get(bg_num % 16, self._ansi_colors[0])
        else:
            # Foreground colour
            if isinstance(char_obj.fg, str):
                color_map = {
                    'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
                    'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7,
                    'default': 7
                }
                fg_num = color_map.get(char_obj.fg, 7)
            else:
                fg_num = char_obj.fg if char_obj.fg is not None else 7

            # Bold makes colours bright (adds 8)
            if char_obj.bold and fg_num < 8:
                fg_num += 8

            return self._ansi_colors.get(fg_num % 16, self._ansi_colors[7])

    def _draw_char(self, painter: QPainter, char_code: int, x: int, y: int, color: QColor) -> None:
        """
        Draw a character glyph.

        Args:
            painter: QPainter to draw with
            char_code: CP437 character code
            x: X position in pixels
            y: Y position in pixels (top of character cell)
            color: Foreground colour
        """
        # Convert character code to CP437 character
        try:
            char = chr(char_code)
        except:
            char = ' '

        # Set up painter
        painter.setFont(self.font)
        painter.setPen(color)

        # Draw character at exact position
        # Y coordinate for drawText is the baseline, so add height offset
        rect = QRect(x, y, self.char_width, self.char_height)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)

    def paintEvent(self, event):
        """Paint the back buffer to the widget."""
        painter = QPainter(self)
        # Disable smoothing for pixel-perfect rendering
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.drawImage(0, 0, self.back_buffer)

    def sizeHint(self) -> QSize:
        """Provide size hint for layout."""
        return QSize(
            self.columns * self.char_width,
            self.lines * self.char_height
        )

    def keyPressEvent(self, event):
        """Handle key press events and emit data."""
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
        elif event.key() == Qt.Key.Key_Up:
            self.data_entered.emit("\x1b[A")
            return
        elif event.key() == Qt.Key.Key_Down:
            self.data_entered.emit("\x1b[B")
            return
        elif event.key() == Qt.Key.Key_Right:
            self.data_entered.emit("\x1b[C")
            return
        elif event.key() == Qt.Key.Key_Left:
            self.data_entered.emit("\x1b[D")
            return

        # Regular character input
        text = event.text()
        if text:
            self.data_entered.emit(text)

    def clear(self) -> None:
        """Clear the terminal display."""
        self.back_buffer.fill(QColor(0, 0, 0))
        self.update()
