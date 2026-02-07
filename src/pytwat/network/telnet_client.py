"""
Async Telnet Client - Manages telnet connection to Trade Wars servers.

Uses direct socket connection with minimal telnet negotiation to preserve
all ANSI escape sequences and UTF-8 characters.
"""

import asyncio
from typing import Optional, Callable

from ..core.event_bus import get_event_bus, Event, EventType


# Telnet protocol constants
IAC = bytes([255])  # Interpret As Command
DONT = bytes([254])
DO = bytes([253])
WONT = bytes([252])
WILL = bytes([251])
SB = bytes([250])   # Subnegotiation Begin
SE = bytes([240])   # Subnegotiation End

# Telnet options
ECHO = bytes([1])
SUPPRESS_GO_AHEAD = bytes([3])
TERMINAL_TYPE = bytes([24])
NAWS = bytes([31])  # Negotiate About Window Size


class TelnetClient:
    """
    Async telnet client for Trade Wars servers.

    Manages connection lifecycle and data streaming with proper
    UTF-8 and ANSI escape sequence handling.
    """

    def __init__(self):
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
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
            # Open raw socket connection
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
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
            try:
                await self.writer.wait_closed()
            except Exception:
                pass

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

        # Encode as UTF-8 bytes
        self.writer.write(data.encode('utf-8'))
        await self.writer.drain()
        self.event_bus.publish(Event(EventType.DATA_SENT, {"data": data}))

    async def _read_loop(self) -> None:
        """Background task to read data from server and handle telnet negotiation."""
        try:
            while self.connected and self.reader:
                # Read raw bytes
                raw_bytes = await self.reader.read(4096)
                if not raw_bytes:
                    await self.disconnect()
                    break

                # Process telnet commands and extract display data
                processed_data = await self._process_telnet_data(raw_bytes)

                if processed_data:
                    # Check for terminal detection probes and respond
                    await self._handle_terminal_probes(processed_data)

                    # Decode as CP437 (DOS/IBM codepage) for BBS compatibility
                    # CP437 includes proper box-drawing characters and ANSI art
                    try:
                        data = processed_data.decode('cp437', errors='replace')
                        self.event_bus.publish(Event(EventType.DATA_RECEIVED, {"data": data}))
                    except Exception:
                        pass  # Skip invalid decoding

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.event_bus.publish(Event(EventType.DISCONNECTED, {"error": str(e)}))
            self.connected = False

    async def _process_telnet_data(self, data: bytes) -> bytes:
        """
        Process telnet IAC commands and return display data.

        Args:
            data: Raw bytes from server

        Returns:
            Bytes with telnet commands removed
        """
        result = bytearray()
        i = 0

        while i < len(data):
            if data[i:i+1] == IAC:
                # Handle telnet command
                if i + 1 >= len(data):
                    break

                command = data[i+1:i+2]

                if command in (DO, DONT, WILL, WONT):
                    # Three-byte command
                    if i + 2 >= len(data):
                        break
                    option = data[i+2:i+3]
                    await self._handle_telnet_command(command, option)
                    i += 3
                elif command == SB:
                    # Subnegotiation - find SE
                    end = data.find(IAC + SE, i + 2)
                    if end == -1:
                        break
                    # Handle subnegotiation
                    sb_data = data[i+2:end]
                    await self._handle_subnegotiation(sb_data)
                    i = end + 2
                elif command == IAC:
                    # Escaped IAC (255 sent as data)
                    result.append(255)
                    i += 2
                else:
                    # Two-byte command
                    i += 2
            else:
                # Regular data byte
                result.append(data[i])
                i += 1

        return bytes(result)

    async def _handle_telnet_command(self, command: bytes, option: bytes) -> None:
        """
        Handle telnet negotiation commands.

        Args:
            command: DO, DONT, WILL, or WONT
            option: The option being negotiated
        """
        if not self.writer:
            return

        # Respond to server requests
        if command == DO:
            if option == TERMINAL_TYPE:
                # We will provide terminal type (but wait for server to ask)
                self.writer.write(IAC + WILL + TERMINAL_TYPE)
            elif option == NAWS:
                # We will provide window size
                self.writer.write(IAC + WILL + NAWS)
                # Send window size immediately (80x24)
                self.writer.write(IAC + SB + NAWS + bytes([0, 80, 0, 24]) + IAC + SE)
            else:
                # We won't do other options
                self.writer.write(IAC + WONT + option)
        elif command == DONT:
            # Server doesn't want us to do something - acknowledge
            self.writer.write(IAC + WONT + option)
        elif command == WILL:
            # Server will do something - acknowledge common options
            if option in (ECHO, SUPPRESS_GO_AHEAD):
                self.writer.write(IAC + DO + option)
            else:
                self.writer.write(IAC + DONT + option)
        elif command == WONT:
            # Server won't do something - acknowledge
            self.writer.write(IAC + DONT + option)

        await self.writer.drain()

    async def _handle_subnegotiation(self, data: bytes) -> None:
        """
        Handle telnet subnegotiation.

        Args:
            data: Subnegotiation data (without IAC SB and IAC SE)
        """
        if not self.writer or len(data) < 1:
            return

        option = data[0:1]

        if option == TERMINAL_TYPE:
            # Server is asking for terminal type
            if len(data) >= 2 and data[1] == 1:  # SEND command
                # Respond with our terminal type
                term_type = b'ANSI'  # Use standard ANSI instead of ansi-bbs
                self.writer.write(IAC + SB + TERMINAL_TYPE + bytes([0]) + term_type + IAC + SE)
                await self.writer.drain()

    async def _handle_terminal_probes(self, data: bytes) -> None:
        """
        Handle terminal detection probes from Synchronet BBS.

        Args:
            data: Data that may contain terminal detection sequences
        """
        if not self.writer:
            return

        # Check for cursor position request: ESC[6n
        if b'\x1b[6n' in data:
            # Respond with cursor position report: ESC[24;80R (row 24, col 80)
            # This tells the BBS we're ANSI-capable
            self.writer.write(b'\x1b[24;80R')
            await self.writer.drain()

        # Check for device attributes request: ESC[c or ESC[0c
        if b'\x1b[c' in data or b'\x1b[0c' in data:
            # Respond as VT100: ESC[?1;0c
            self.writer.write(b'\x1b[?1;0c')
            await self.writer.drain()
