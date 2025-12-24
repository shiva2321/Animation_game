"""
Particle class with physics state and rendering properties.
"""
import numpy as np
from typing import Tuple, Deque
from collections import deque


class Particle:
    """Single particle with complete physics and rendering state."""

    _next_id = 0

    def __init__(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        radius: float,
        mass: float,
        color: Tuple[int, int, int],
        shape: str = "circle",
        restitution: float = 0.95,
        friction: float = 0.05
    ):
        self.id = Particle._next_id
        Particle._next_id += 1

        # Physics state
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.zeros(2, dtype=float)
        self.radius = radius
        self.mass = mass
        self.restitution = restitution
        self.friction = friction

        # Rotation
        self.angle = 0.0
        self.angular_velocity = 0.0
        self.angular_damping = 0.98

        # Deformation (for squash/stretch effects)
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_vx = 0.0
        self.scale_vy = 0.0
        self.deform_spring = 20.0
        self.deform_damping = 0.8

        # Visual properties
        self.color = color
        self.shape = shape
        self.glow_intensity = 0.0  # Dynamic, based on kinetic energy

        # Trail (ring buffer)
        self.trail: Deque[np.ndarray] = deque(maxlen=100)

        # Lifetime
        self.age = 0.0
        self.alive = True

    def apply_force(self, force: np.ndarray):
        """Apply force to particle (F = ma -> a = F/m)."""
        self.acceleration += force / self.mass

    def update(self, dt: float):
        """
        Update particle state using semi-implicit Euler integration.

        Args:
            dt: Time step
        """
        # Update velocity (semi-implicit)
        self.velocity += self.acceleration * dt

        # Update position
        self.position += self.velocity * dt

        # Update rotation
        self.angle += self.angular_velocity * dt
        self.angular_velocity *= self.angular_damping

        # Update deformation (spring back to 1.0)
        self.scale_vx += (1.0 - self.scale_x) * self.deform_spring * dt
        self.scale_vy += (1.0 - self.scale_y) * self.deform_spring * dt
        self.scale_vx *= self.deform_damping
        self.scale_vy *= self.deform_damping
        self.scale_x += self.scale_vx * dt
        self.scale_y += self.scale_vy * dt

        # Update glow based on kinetic energy
        ke = 0.5 * self.mass * np.dot(self.velocity, self.velocity)
        self.glow_intensity = min(1.0, ke / 10000.0)

        # Reset acceleration for next frame
        self.acceleration[:] = 0

        # Update trail
        self.trail.append(self.position.copy())

        # Update age
        self.age += dt

    def get_kinetic_energy(self) -> float:
        """Calculate kinetic energy."""
        return 0.5 * self.mass * np.dot(self.velocity, self.velocity)

    def get_speed(self) -> float:
        """Get current speed (magnitude of velocity)."""
        return np.linalg.norm(self.velocity)

    def apply_deformation(self, direction: np.ndarray, intensity: float):
        """Apply deformation in a direction."""
        # Normalize direction
        norm = np.linalg.norm(direction)
        if norm > 0:
            direction = direction / norm

            # Apply scale change
            self.scale_x += direction[0] * intensity * 0.1
            self.scale_y += direction[1] * intensity * 0.1

            # Clamp scales
            self.scale_x = max(0.5, min(1.5, self.scale_x))
            self.scale_y = max(0.5, min(1.5, self.scale_y))

    @classmethod
    def reset_id_counter(cls):
        """Reset the ID counter (useful for deterministic exports)."""
        cls._next_id = 0

