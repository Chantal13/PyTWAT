"""
PyTWAT entry point.

Run with: poetry run python -m pytwat
"""

import sys
import asyncio
from PyQt6.QtWidgets import QApplication
import qasync
from .gui.main_window import MainWindow


def main():
    """Main entry point for PyTWAT."""
    app = QApplication(sys.argv)
    app.setApplicationName("PyTWAT")
    app.setOrganizationName("PyTWAT")

    # Set up qasync event loop for proper Qt/asyncio integration
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        sys.exit(loop.run_forever())


if __name__ == "__main__":
    main()
