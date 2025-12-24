
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np
from collections import deque

@dataclass
class BaseEvent:
    timestamp: float

@dataclass
class SpawnEvent(BaseEvent):
    particle_id: int
    position: Tuple[float, float]

@dataclass
class CollisionEvent(BaseEvent):
    particle_a_id: int
    particle_b_id: int
    position: Tuple[float, float]
    energy: float
    relative_speed: float
    mixed_color: Tuple[int, int, int]
    normal: Tuple[float, float]

@dataclass
class BoundaryHitEvent(BaseEvent):
    particle_id: int
    position: Tuple[float, float]
    energy: float

class EventQueue:
    def __init__(self):
        self._events = deque()

    def add_event(self, event: BaseEvent):
        self._events.append(event)

    def get_events(self) -> list[BaseEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def clear(self):
        self._events.clear()

# Global event queue instance
event_queue = EventQueue()
