"""
Event system for physics simulation events.
"""
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np


@dataclass
class CollisionEvent:
    """Event emitted when two particles collide."""
    timestamp: float
    particle1_id: int
    particle2_id: int
    point: np.ndarray  # Collision point
    normal: np.ndarray  # Normal vector
    energy: float  # Collision energy
    relative_speed: float
    mixed_color: Tuple[int, int, int]  # RGB color


@dataclass
class BoundaryHitEvent:
    """Event emitted when a particle hits the boundary."""
    timestamp: float
    particle_id: int
    point: np.ndarray  # Hit point
    normal: np.ndarray  # Normal vector
    energy: float  # Impact energy
    color: Tuple[int, int, int]  # RGB color


@dataclass
class SpawnEvent:
    """Event emitted when a particle spawns."""
    timestamp: float
    particle_id: int
    position: np.ndarray
    velocity: np.ndarray
    radius: float
    color: Tuple[int, int, int]  # RGB color


class EventQueue:
    """Thread-safe event queue for simulation events."""

    def __init__(self):
        self.collision_events = []
        self.boundary_events = []
        self.spawn_events = []

    def add_collision(self, event: CollisionEvent):
        """Add a collision event."""
        self.collision_events.append(event)

    def add_boundary_hit(self, event: BoundaryHitEvent):
        """Add a boundary hit event."""
        self.boundary_events.append(event)

    def add_spawn(self, event: SpawnEvent):
        """Add a spawn event."""
        self.spawn_events.append(event)

    def clear(self):
        """Clear all events."""
        self.collision_events.clear()
        self.boundary_events.clear()
        self.spawn_events.clear()

    def get_all_events(self):
        """Get all events and clear the queue."""
        events = {
            'collisions': self.collision_events.copy(),
            'boundary': self.boundary_events.copy(),
            'spawns': self.spawn_events.copy()
        }
        self.clear()
        return events

