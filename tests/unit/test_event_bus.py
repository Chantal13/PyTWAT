"""Tests for the event bus."""

import pytest
from pytwat.core.event_bus import EventBus, Event, EventType


def test_event_bus_subscribe():
    """Test subscribing to events."""
    bus = EventBus()
    events_received = []

    def callback(event: Event):
        events_received.append(event)

    bus.subscribe(EventType.CONNECTED, callback)
    bus.publish(Event(EventType.CONNECTED, {"host": "test", "port": 23}))

    assert len(events_received) == 1
    assert events_received[0].event_type == EventType.CONNECTED
    assert events_received[0].data["host"] == "test"


def test_event_bus_unsubscribe():
    """Test unsubscribing from events."""
    bus = EventBus()
    events_received = []

    def callback(event: Event):
        events_received.append(event)

    bus.subscribe(EventType.CONNECTED, callback)
    bus.unsubscribe(EventType.CONNECTED, callback)
    bus.publish(Event(EventType.CONNECTED, {}))

    assert len(events_received) == 0


def test_event_bus_multiple_subscribers():
    """Test multiple subscribers to the same event."""
    bus = EventBus()
    events_a = []
    events_b = []

    def callback_a(event: Event):
        events_a.append(event)

    def callback_b(event: Event):
        events_b.append(event)

    bus.subscribe(EventType.DATA_RECEIVED, callback_a)
    bus.subscribe(EventType.DATA_RECEIVED, callback_b)
    bus.publish(Event(EventType.DATA_RECEIVED, {"data": "test"}))

    assert len(events_a) == 1
    assert len(events_b) == 1
