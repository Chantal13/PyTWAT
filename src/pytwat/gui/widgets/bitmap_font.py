"""
Bitmap Font - Load and render CP437 bitmap fonts for pixel-perfect display.

Provides bitmap font loading and character glyph access for terminal rendering.
"""

from typing import Optional
from PyQt6.QtGui import QImage, QColor
from PyQt6.QtCore import QRect


class BitmapFont:
    """
    CP437 bitmap font loader and renderer.

    Loads a bitmap font image with 256 character glyphs arranged in a 16x16 grid.
    Each character is rendered as a fixed-size bitmap tile.
    """

    def __init__(self, font_path: Optional[str] = None, char_width: int = 8, char_height: int = 16):
        """
        Initialize bitmap font.

        Args:
            font_path: Path to bitmap font image (16x16 grid of 256 chars)
            char_width: Width of each character in pixels
            char_height: Height of each character in pixels
        """
        self.char_width = char_width
        self.char_height = char_height
        self.font_image: Optional[QImage] = None

        if font_path:
            self.load_font(font_path)
        else:
            # Generate default font if no path provided
            self._generate_default_font()

    def load_font(self, font_path: str) -> bool:
        """
        Load bitmap font from image file.

        Args:
            font_path: Path to bitmap font image

        Returns:
            True if loaded successfully
        """
        self.font_image = QImage(font_path)
        if self.font_image.isNull():
            self._generate_default_font()
            return False

        # Convert to 32-bit ARGB for easy manipulation
        if self.font_image.format() != QImage.Format.Format_ARGB32:
            self.font_image = self.font_image.convertToFormat(QImage.Format.Format_ARGB32)

        return True

    def _generate_default_font(self) -> None:
        """
        Generate a simple default font using Qt's built-in rendering.

        This creates a bitmap atlas of all 256 CP437 characters rendered
        with a monospace font as a fallback when no bitmap font is available.
        """
        from PyQt6.QtGui import QPainter, QFont, QPen
        from PyQt6.QtCore import Qt

        # Create 16x16 grid of characters (256 total)
        atlas_width = 16 * self.char_width
        atlas_height = 16 * self.char_height

        self.font_image = QImage(atlas_width, atlas_height, QImage.Format.Format_ARGB32)
        self.font_image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(self.font_image)

        # Use a monospace font for rendering
        font = QFont("Monaco", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        painter.setFont(font)

        # White text for the font atlas
        painter.setPen(QPen(QColor(255, 255, 255)))

        # Render each CP437 character
        for char_code in range(256):
            row = char_code // 16
            col = char_code % 16

            x = col * self.char_width
            y = row * self.char_height

            # Get the CP437 character
            try:
                char = bytes([char_code]).decode('cp437')

                # Draw character centered in its cell
                rect = QRect(x, y, self.char_width, self.char_height)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)
            except:
                pass  # Skip unprintable characters

        painter.end()

    def get_char_rect(self, char_code: int) -> QRect:
        """
        Get the rectangle in the font atlas for a character.

        Args:
            char_code: CP437 character code (0-255)

        Returns:
            QRect defining the character's position in the atlas
        """
        row = char_code // 16
        col = char_code % 16

        x = col * self.char_width
        y = row * self.char_height

        return QRect(x, y, self.char_width, self.char_height)

    def get_char_image(self, char_code: int) -> QImage:
        """
        Extract a character's bitmap from the font atlas.

        Args:
            char_code: CP437 character code (0-255)

        Returns:
            QImage containing the character glyph
        """
        if not self.font_image:
            return QImage()

        rect = self.get_char_rect(char_code)
        return self.font_image.copy(rect)
