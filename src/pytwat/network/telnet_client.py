"""
Async Telnet Client - Manages telnet connection to Trade Wars servers.

Uses telnetlib3 for async telnet with proper VT320 support.
"""

import asyncio
from typing import Optional, Callable
import telnetlib3
import codecs

from ..core.event_bus import get_event_bus, Event, EventType


class TelnetClient:
    """
    Async telnet client for Trade Wars servers.

    Manages connection lifecycle and data streaming.
    """

    def __init__(self):
        self.reader: Optional[telnetlib3.TelnetReader] = None
        self.writer: Optional[telnetlib3.TelnetWriter] = None
        self.connected = False
        self.event_bus = get_event_bus()
        self._read_task: Optional[asyncio.Task] = None

    async def connect(self, host: str, port: int, timeout: int = 30) -> bool:
        """
        Connect to a telnet server.

        Args:
            host: Server hostname or IP
            port: Server port
            timeout: Connection timeout in seconds

        Returns:
            True if connected successfully
        """
        try:
            # Connect with terminal type negotiation
            # Use 'latin-1' encoding to preserve raw bytes, we'll decode as CP437 ourselves
            self.reader, self.writer = await asyncio.wait_for(
                telnetlib3.open_connection(
                    host,
                    port,
                    term='ansi-bbs',  # BBS-specific ANSI terminal type
                    cols=80,
                    rows=24,
                    encoding='latin-1',  # Use latin-1 to preserve byte values (we decode CP437 later)
                    connect_minwait=0.1  # Reduce connection negotiation wait
                ),
                timeout=timeout
            )
            self.connected = True
            self.event_bus.publish(Event(EventType.CONNECTED, {"host": host, "port": port}))

            # Start reading data in background
            self._read_task = asyncio.create_task(self._read_loop())

            return True
        except Exception as e:
            self.event_bus.publish(Event(EventType.DISCONNECTED, {"error": str(e)}))
            return False

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

        self.connected = False
        self.reader = None
        self.writer = None
        self.event_bus.publish(Event(EventType.DISCONNECTED, {}))

    async def send(self, data: str) -> None:
        """
        Send data to the server.

        Args:
            data: String to send
        """
        if not self.connected or not self.writer:
            raise RuntimeError("Not connected to server")

        self.writer.write(data)
        await self.writer.drain()
        self.event_bus.publish(Event(EventType.DATA_SENT, {"data": data}))

    async def _read_loop(self) -> None:
        """Background task to read data from server."""
        try:
            while self.connected and self.reader:
                # Read data from server
                # Since we set encoding='latin-1', this preserves all byte values 0-255
                data = await self.reader.read(1024)
                if not data:
                    # Connection closed by server
                    await self.disconnect()
                    break

                # Selective CP437 decoding: only convert high bytes (128-255)
                # Keep ASCII range (0-127) intact for ANSI escape sequences
                try:
                    data_bytes = data.encode('latin-1')
                    result = []

                    for byte_val in data_bytes:
                        if byte_val < 128:
                            # ASCII range - keep as-is (includes ANSI escapes)
                            result.append(chr(byte_val))
                        else:
                            # High bytes - decode through CP437
                            # Convert single byte to its CP437 Unicode equivalent
                            cp437_char = bytes([byte_val]).decode('cp437', errors='replace')
                            result.append(cp437_char)

                    data = ''.join(result)
                except (UnicodeDecodeError, UnicodeEncodeError) as e:
                    # If conversion fails, use data as-is
                    pass

                self.event_bus.publish(Event(EventType.DATA_RECEIVED, {"data": data}))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.event_bus.publish(Event(EventType.DISCONNECTED, {"error": str(e)}))
            self.connected = False
