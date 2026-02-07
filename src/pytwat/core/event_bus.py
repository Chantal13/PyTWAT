"""
Event Bus - Central event system for loose coupling between components.

Events are used to communicate between layers (network, parser, GUI, automation)
without creating tight dependencies.
"""

from typing import Callable, Dict, List
from dataclasses import dataclass
from enum import Enum, auto


class EventType(Enum):
    """All event types in the system."""

    # Network events
    CONNECTED = auto()
    DISCONNECTED = auto()
    DATA_RECEIVED = auto()
    DATA_SENT = auto()

    # Parser events
    SECTOR_PARSED = auto()
    PORT_PARSED = auto()
    SHIP_PARSED = auto()
    PROMPT_DETECTED = auto()

    # Automation events
    SCRIPT_STARTED = auto()
    SCRIPT_STOPPED = auto()
    SCRIPT_ERROR = auto()


@dataclass
class Event:
    """Base event class."""
    event_type: EventType
    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class EventBus:
    """
    Central event bus using publish-subscribe pattern.

    Components subscribe to events they care about and publish events
    when something happens. This allows loose coupling between layers.
    """

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to listen for
            callback: Function to call when event occurs (receives Event object)
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Remove a subscriber."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event to publish
        """
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                callback(event)

    def clear(self) -> None:
        """Clear all subscribers (mainly for testing)."""
        self._subscribers.clear()


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus
