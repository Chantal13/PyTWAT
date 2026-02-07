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
            # Modern BBS systems send UTF-8 (Unicode box-drawing chars)
            self.reader, self.writer = await asyncio.wait_for(
                telnetlib3.open_connection(
                    host,
                    port,
                    term='ansi-bbs',  # BBS-specific ANSI terminal type
                    cols=80,
                    rows=24,
                    encoding='utf-8',  # Modern BBS use UTF-8 (Unicode box chars)
                    connect_minwait=0.1
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
                # Read data from server (already decoded as UTF-8)
                data = await self.reader.read(1024)
                if not data:
                    # Connection closed by server
                    await self.disconnect()
                    break

                # Data is already properly decoded as UTF-8 by telnetlib3
                # Modern BBS send Unicode box-drawing chars in UTF-8
                self.event_bus.publish(Event(EventType.DATA_RECEIVED, {"data": data}))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.event_bus.publish(Event(EventType.DISCONNECTED, {"error": str(e)}))
            self.connected = False
