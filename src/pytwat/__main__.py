"""
PyTWAT entry point.

Run with: poetry run python -m pytwat
"""

import sys
from PyQt6.QtWidgets import QApplication
from .gui.main_window import MainWindow


def main():
    """Main entry point for PyTWAT."""
    app = QApplication(sys.argv)
    app.setApplicationName("PyTWAT")
    app.setOrganizationName("PyTWAT")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
