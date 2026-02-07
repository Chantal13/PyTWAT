"""
Main Window - Primary application window for PyTWAT.

Provides the main GUI interface with menu bar, terminal display,
and connection controls.
"""

import asyncio
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QSpinBox, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer

from .widgets.bitmap_terminal_widget import BitmapTerminalWidget
from ..network.telnet_client import TelnetClient
from ..network.terminal_emulator import TerminalEmulator
from ..core.event_bus import get_event_bus, Event, EventType


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.telnet_client = TelnetClient()
        self.terminal_emulator = TerminalEmulator()
        self.event_bus = get_event_bus()

        # Subscribe to events
        self.event_bus.subscribe(EventType.DATA_RECEIVED, self._on_data_received)
        self.event_bus.subscribe(EventType.CONNECTED, self._on_connected)
        self.event_bus.subscribe(EventType.DISCONNECTED, self._on_disconnected)

        self._init_ui()
        self._setup_asyncio()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PyTWAT - Trade Wars Client")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Connection controls
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Host:"))
        self.host_input = QLineEdit("142.44.247.204")
        conn_layout.addWidget(self.host_input)

        conn_layout.addWidget(QLabel("Port:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(23)
        conn_layout.addWidget(self.port_input)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._on_connect_clicked)
        conn_layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self._on_disconnect_clicked)
        self.disconnect_button.setEnabled(False)
        conn_layout.addWidget(self.disconnect_button)

        layout.addLayout(conn_layout)

        # Terminal widget (bitmap-based for pixel-perfect rendering)
        self.terminal_widget = BitmapTerminalWidget(columns=80, lines=24)
        self.terminal_widget.data_entered.connect(self._on_terminal_input)
        layout.addWidget(self.terminal_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _setup_asyncio(self):
        """Set up asyncio event loop integration with Qt."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Run asyncio tasks periodically (less frequently to reduce CPU usage)
        self.async_timer = QTimer()
        self.async_timer.timeout.connect(self._process_async_tasks)
        self.async_timer.start(50)  # Process every 50ms (was 10ms - too fast!)

    def _process_async_tasks(self):
        """Process asyncio tasks in the Qt event loop."""
        # Run pending asyncio tasks without blocking
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()

    def _on_connect_clicked(self):
        """Handle connect button click."""
        host = self.host_input.text()
        port = self.port_input.value()

        self.status_bar.showMessage(f"Connecting to {host}:{port}...")
        asyncio.run_coroutine_threadsafe(
            self.telnet_client.connect(host, port),
            self.loop
        )

    def _on_disconnect_clicked(self):
        """Handle disconnect button click."""
        asyncio.run_coroutine_threadsafe(
            self.telnet_client.disconnect(),
            self.loop
        )

    def _on_terminal_input(self, data: str):
        """Handle input from terminal widget."""
        if self.telnet_client.connected:
            asyncio.run_coroutine_threadsafe(
                self.telnet_client.send(data),
                self.loop
            )

    def _on_data_received(self, event: Event):
        """Handle data received from server."""
        data = event.data.get("data", "")
        # Feed to terminal emulator for proper ANSI/cursor handling
        self.terminal_emulator.feed(data)
        # Render the screen buffer with proper formatting
        self.terminal_widget.render_screen(self.terminal_emulator.screen)

    def _on_connected(self, event: Event):
        """Handle connection established."""
        host = event.data.get("host")
        port = event.data.get("port")
        self.status_bar.showMessage(f"Connected to {host}:{port}")
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        self.terminal_widget.setFocus()

    def _on_disconnected(self, event: Event):
        """Handle disconnection."""
        error = event.data.get("error")
        if error:
            self.status_bar.showMessage(f"Disconnected: {error}")
        else:
            self.status_bar.showMessage("Disconnected")
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)

    def closeEvent(self, event):
        """Handle window close event."""
        if self.telnet_client.connected:
            asyncio.run_coroutine_threadsafe(
                self.telnet_client.disconnect(),
                self.loop
            )
        self.loop.stop()
        super().closeEvent(event)
