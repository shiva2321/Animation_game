"""
Particle spawning system with various patterns.
"""
import numpy as np
from typing import Tuple, List
from src.physics.particle import Particle
from src.core.rng import DeterministicRNG
from src.core.events import SpawnEvent


class ParticleSpawner:
    """Spawns particles with various patterns."""

    def __init__(self, rng: DeterministicRNG):
        self.rng = rng
        self.spawn_accumulator = 0.0
        self.hue_offset = 0.0  # For golden ratio color generation
        self.golden_ratio = 0.618033988749895

    def spawn_particles(
        self,
        count: int,
        pattern: str,
        center: np.ndarray,
        boundary_radius: float,
        size_min: float,
        size_max: float,
        shapes: List[str],
        shape_weights: List[float],
        mass_from_area: bool,
        restitution: float,
        friction: float,
        initial_velocity_scale: float = 100.0
    ) -> Tuple[List[Particle], List[SpawnEvent]]:
        """
        Spawn particles with given pattern.

        Args:
            count: Number of particles to spawn
            pattern: Spawn pattern type
            center: Center position
            boundary_radius: Boundary radius
            size_min, size_max: Particle size range
            shapes: Available shapes
            shape_weights: Shape selection weights
            mass_from_area: Whether to calculate mass from area
            restitution: Bounciness
            friction: Friction coefficient
            initial_velocity_scale: Scale for initial velocities

        Returns:
            Tuple of (particles list, spawn events list)
        """
        particles = []
        events = []

        for _ in range(count):
            particle, event = self._spawn_single(
                pattern, center, boundary_radius,
                size_min, size_max, shapes, shape_weights,
                mass_from_area, restitution, friction,
                initial_velocity_scale
            )
            particles.append(particle)
            events.append(event)

        return particles, events

    def _spawn_single(
        self,
        pattern: str,
        center: np.ndarray,
        boundary_radius: float,
        size_min: float,
        size_max: float,
        shapes: List[str],
        shape_weights: List[float],
        mass_from_area: bool,
        restitution: float,
        friction: float,
        initial_velocity_scale: float
    ) -> Tuple[Particle, SpawnEvent]:
        """Spawn a single particle."""
        # Random size
        radius = self.rng.uniform(size_min, size_max)

        # Calculate mass
        if mass_from_area:
            mass = np.pi * radius * radius
        else:
            mass = radius

        # Position based on pattern
        position = self._get_spawn_position(pattern, center, boundary_radius, radius)

        # Initial velocity
        velocity = self._get_spawn_velocity(pattern, position, center, initial_velocity_scale)

        # Color using golden ratio hue stepping
        color = self._generate_color()

        # Shape
        shape = self.rng.choice(shapes, weights=shape_weights)

        # Create particle
        particle = Particle(
            position=position,
            velocity=velocity,
            radius=radius,
            mass=mass,
            color=color,
            shape=shape,
            restitution=restitution,
            friction=friction
        )

        # Create spawn event
        event = SpawnEvent(
            timestamp=0.0,  # Will be set by system
            particle_id=particle.id,
            position=position.copy(),
            velocity=velocity.copy(),
            radius=radius,
            color=color
        )

        return particle, event

    def _get_spawn_position(
        self,
        pattern: str,
        center: np.ndarray,
        boundary_radius: float,
        radius: float
    ) -> np.ndarray:
        """Get spawn position based on pattern."""
        if pattern == "drop":
            # Drop from top with good horizontal spacing
            # Use counter to space out initial objects
            if not hasattr(self, 'drop_counter'):
                self.drop_counter = 0

            # Calculate horizontal position based on drop counter
            if self.drop_counter == 0:
                x_offset = -boundary_radius * 0.3  # Left side
            elif self.drop_counter == 1:
                x_offset = boundary_radius * 0.3  # Right side
            else:
                # Random position for subsequent drops
                x_offset = self.rng.uniform(-boundary_radius * 0.5, boundary_radius * 0.5)

            self.drop_counter += 1

            # Position HIGHER above container so they have room to fall
            y_pos = -boundary_radius * 0.85  # Much higher up, almost at edge
            return center + np.array([x_offset, y_pos])

        elif pattern == "center":
            # Small random offset from center
            offset = self.rng.uniform(-radius * 2, radius * 2)
            return center + np.array([offset, offset])

        elif pattern == "ring":
            # Random position on a ring
            angle = self.rng.uniform(0, 2 * np.pi)
            ring_radius = boundary_radius * 0.7
            return center + ring_radius * np.array([np.cos(angle), np.sin(angle)])

        elif pattern == "spiral":
            # Spiral pattern
            t = self.rng.uniform(0, 4 * np.pi)
            r = boundary_radius * 0.5 * (t / (4 * np.pi))
            return center + r * np.array([np.cos(t), np.sin(t)])

        elif pattern == "burst":
            # Random angle, near center
            angle = self.rng.uniform(0, 2 * np.pi)
            r = self.rng.uniform(0, boundary_radius * 0.2)
            return center + r * np.array([np.cos(angle), np.sin(angle)])

        else:  # "random" or default
            # Random position inside boundary
            angle = self.rng.uniform(0, 2 * np.pi)
            r = self.rng.uniform(0, boundary_radius - radius * 2) * np.sqrt(self.rng.random())
            return center + r * np.array([np.cos(angle), np.sin(angle)])

    def _get_spawn_velocity(
        self,
        pattern: str,
        position: np.ndarray,
        center: np.ndarray,
        scale: float
    ) -> np.ndarray:
        """Get initial velocity based on pattern."""
        if pattern == "drop":
            # VERY strong initial downward velocity with high horizontal variation
            horizontal = self.rng.uniform(-250, 250)  # Much stronger horizontal
            vertical = self.rng.uniform(300, 500)  # MUCH stronger downward velocity
            return np.array([horizontal, vertical])

        elif pattern == "burst":
            # Velocity away from center
            direction = position - center
            norm = np.linalg.norm(direction)
            if norm > 0:
                direction = direction / norm
            else:
                direction = np.array([1.0, 0.0])
            speed = self.rng.uniform(scale * 0.5, scale * 1.5)
            return direction * speed

        elif pattern == "ring":
            # Tangential velocity
            to_center = center - position
            tangent = np.array([-to_center[1], to_center[0]])
            norm = np.linalg.norm(tangent)
            if norm > 0:
                tangent = tangent / norm
            speed = self.rng.uniform(scale * 0.5, scale)
            return tangent * speed

        elif pattern == "spiral":
            # Mixed radial and tangential
            to_center = center - position
            tangent = np.array([-to_center[1], to_center[0]])
            norm_t = np.linalg.norm(tangent)
            norm_r = np.linalg.norm(to_center)

            if norm_t > 0 and norm_r > 0:
                tangent = tangent / norm_t
                radial = to_center / norm_r
                velocity = tangent * scale * 0.7 + radial * scale * 0.3
            else:
                velocity = np.zeros(2)
            return velocity

        else:  # random, center, or default
            # Random velocity
            angle = self.rng.uniform(0, 2 * np.pi)
            speed = self.rng.uniform(0, scale)
            return speed * np.array([np.cos(angle), np.sin(angle)])

    def _generate_color(self) -> Tuple[int, int, int]:
        """Generate appealing, vibrant color using golden ratio hue stepping."""
        # Advance hue by golden ratio for pleasant distribution
        self.hue_offset += self.golden_ratio
        self.hue_offset %= 1.0

        # Generate appealing colors with varied saturation and value
        hue = self.hue_offset

        # Vary saturation for visual interest (avoid dull colors)
        # Higher saturation = more vivid colors
        saturation = self.rng.uniform(0.70, 0.95)

        # Vary value/brightness (avoid too dark or too bright)
        # Sweet spot for appealing colors
        value = self.rng.uniform(0.85, 1.0)

        # Occasionally create more saturated "pop" colors
        if self.rng.random() < 0.3:
            saturation = self.rng.uniform(0.90, 1.0)  # Super saturated
            value = self.rng.uniform(0.90, 1.0)  # Bright

        return self._hsv_to_rgb(hue, saturation, value)

    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB."""
        if s == 0.0:
            r = g = b = v
        else:
            i = int(h * 6.0)
            f = (h * 6.0) - i
            p = v * (1.0 - s)
            q = v * (1.0 - s * f)
            t = v * (1.0 - s * (1.0 - f))
            i = i % 6

            if i == 0:
                r, g, b = v, t, p
            elif i == 1:
                r, g, b = q, v, p
            elif i == 2:
                r, g, b = p, v, t
            elif i == 3:
                r, g, b = p, q, v
            elif i == 4:
                r, g, b = t, p, v
            else:
                r, g, b = v, p, q

        return (int(r * 255), int(g * 255), int(b * 255))

    def create_collision_spawn(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        color: Tuple[int, int, int],
        energy: float,
        size_min: float,
        size_max: float,
        shapes: List[str],
        shape_weights: List[float],
        mass_from_area: bool,
        restitution: float,
        friction: float
    ) -> Tuple[Particle, SpawnEvent]:
        """
        Spawn a particle from a collision event.

        Args:
            position: Spawn position
            velocity: Initial velocity (scaled by energy)
            color: Inherited color
            energy: Collision energy
            Other args: Same as spawn_particles

        Returns:
            Tuple of (particle, spawn event)
        """
        # Size based on energy
        size_scale = min(1.0, energy / 1000.0)
        radius = size_min + (size_max - size_min) * size_scale * 0.5

        # Add LARGE random offset to prevent clustering at collision point
        offset_distance = radius * self.rng.uniform(4, 8)  # 4-8 radii away (was 2-4)
        offset_angle = self.rng.uniform(0, 2 * np.pi)
        position_offset = np.array([
            np.cos(offset_angle) * offset_distance,
            np.sin(offset_angle) * offset_distance
        ])
        spawn_position = position + position_offset

        # Mass
        if mass_from_area:
            mass = np.pi * radius * radius
        else:
            mass = radius

        # Velocity scaled by energy with MUCH MORE randomization
        velocity_scale = min(1.5, energy / 300.0)  # Increased scale
        # Add VERY STRONG random velocity component to spread objects aggressively
        random_angle = self.rng.uniform(0, 2 * np.pi)
        random_velocity = np.array([
            np.cos(random_angle) * self.rng.uniform(200, 400),  # MUCH stronger (was 100-200)
            np.sin(random_angle) * self.rng.uniform(200, 400)
        ])
        velocity = velocity * velocity_scale + random_velocity

        # Shape
        shape = self.rng.choice(shapes, weights=shape_weights)

        # Create particle
        particle = Particle(
            position=spawn_position,
            velocity=velocity,
            radius=radius,
            mass=mass,
            color=color,
            shape=shape,
            restitution=restitution,
            friction=friction
        )

        # Create event
        event = SpawnEvent(
            timestamp=0.0,
            particle_id=particle.id,
            position=spawn_position.copy(),
            velocity=velocity.copy(),
            radius=radius,
            color=color
        )

        return particle, event

