"""
Visual effects: ripples, sparkles, and other collision effects.
"""
import numpy as np
from typing import List, Tuple
import pygame


class Ripple:
    """Expanding ripple effect from collisions."""

    def __init__(
        self,
        position: np.ndarray,
        color: Tuple[int, int, int],
        max_radius: float = 50.0,
        duration: float = 0.5,
        intensity: float = 1.0
    ):
        self.position = position.copy()
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.intensity = intensity
        self.age = 0.0
        self.alive = True

    def update(self, dt: float):
        """Update ripple state."""
        self.age += dt
        if self.age >= self.duration:
            self.alive = False

    def get_radius(self) -> float:
        """Get current radius based on age."""
        progress = self.age / self.duration
        return self.max_radius * progress

    def get_alpha(self) -> float:
        """Get current alpha (fade out)."""
        progress = self.age / self.duration
        return (1.0 - progress) * self.intensity

    def draw(self, surface: pygame.Surface):
        """Draw ripple on surface."""
        if not self.alive:
            return

        radius = self.get_radius()
        alpha = self.get_alpha()

        if radius < 1 or alpha < 0.01:
            return

        # Draw concentric circles
        for i in range(3):
            r_offset = i * 2
            a_scale = 1.0 - i * 0.3

            color = (*self.color, int(alpha * a_scale * 255))
            thickness = max(1, int(3 - i))

            try:
                pygame.draw.circle(
                    surface,
                    color[:3],
                    (int(self.position[0]), int(self.position[1])),
                    int(radius + r_offset),
                    thickness
                )
            except:
                pass


class Sparkle:
    """Sparkle particle effect."""

    def __init__(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        color: Tuple[int, int, int],
        size: float = 3.0,
        duration: float = 0.3,
        intensity: float = 1.0
    ):
        self.position = position.copy()
        self.velocity = velocity.copy()
        self.color = color
        self.size = size
        self.duration = duration
        self.intensity = intensity
        self.age = 0.0
        self.alive = True

    def update(self, dt: float):
        """Update sparkle state."""
        self.age += dt
        if self.age >= self.duration:
            self.alive = False

        # Update position
        self.position += self.velocity * dt

        # Apply gravity
        self.velocity[1] += 100 * dt

        # Damping
        self.velocity *= 0.98

    def get_alpha(self) -> float:
        """Get current alpha."""
        progress = self.age / self.duration
        return (1.0 - progress) * self.intensity

    def draw(self, surface: pygame.Surface):
        """Draw sparkle on surface."""
        if not self.alive:
            return

        alpha = self.get_alpha()
        if alpha < 0.01:
            return

        # Draw as a small bright circle
        color = (*self.color, int(alpha * 255))

        try:
            pygame.draw.circle(
                surface,
                color[:3],
                (int(self.position[0]), int(self.position[1])),
                int(self.size)
            )
        except:
            pass


class EffectsManager:
    """Manager for all visual effects."""

    def __init__(self):
        self.ripples: List[Ripple] = []
        self.sparkles: List[Sparkle] = []

    def add_ripple(
        self,
        position: np.ndarray,
        color: Tuple[int, int, int],
        energy: float = 100.0,
        intensity: float = 1.0
    ):
        """Add a ripple effect."""
        # Scale based on energy
        max_radius = 30 + min(energy / 20.0, 70.0)
        duration = 0.3 + min(energy / 500.0, 0.7)

        ripple = Ripple(
            position=position,
            color=color,
            max_radius=max_radius,
            duration=duration,
            intensity=intensity
        )
        self.ripples.append(ripple)

    def add_sparkles(
        self,
        position: np.ndarray,
        normal: np.ndarray,
        color: Tuple[int, int, int],
        energy: float = 100.0,
        intensity: float = 1.0,
        rng=None
    ):
        """Add sparkle effects."""
        if rng is None:
            rng = np.random

        # Number of sparkles based on energy
        count = int(3 + min(energy / 100.0, 12))

        for _ in range(count):
            # Random angle around normal
            angle = rng.uniform(-np.pi/2, np.pi/2)
            cos_a, sin_a = np.cos(angle), np.sin(angle)

            # Rotate normal
            direction = np.array([
                normal[0] * cos_a - normal[1] * sin_a,
                normal[0] * sin_a + normal[1] * cos_a
            ])

            # Random speed
            speed = rng.uniform(50, 200)
            velocity = direction * speed

            # Slightly varied color
            color_var = tuple(
                max(0, min(255, c + rng.randint(-30, 30)))
                for c in color
            )

            sparkle = Sparkle(
                position=position,
                velocity=velocity,
                color=color_var,
                size=rng.uniform(2, 4),
                duration=rng.uniform(0.2, 0.4),
                intensity=intensity
            )
            self.sparkles.append(sparkle)

    def update(self, dt: float):
        """Update all effects."""
        # Update ripples
        for ripple in self.ripples:
            ripple.update(dt)

        # Update sparkles
        for sparkle in self.sparkles:
            sparkle.update(dt)

        # Remove dead effects
        self.ripples = [r for r in self.ripples if r.alive]
        self.sparkles = [s for s in self.sparkles if s.alive]

    def draw(self, surface: pygame.Surface):
        """Draw all effects."""
        # Draw ripples first (background)
        for ripple in self.ripples:
            ripple.draw(surface)

        # Draw sparkles on top
        for sparkle in self.sparkles:
            sparkle.draw(surface)

    def clear(self):
        """Clear all effects."""
        self.ripples.clear()
        self.sparkles.clear()

