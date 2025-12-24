"""
Collision detection and resolution with spatial hashing.
"""
import numpy as np
from typing import List, Dict, Tuple, Set
from src.physics.particle import Particle
from src.core.events import CollisionEvent


class SpatialHash:
    """Spatial hashing grid for efficient collision detection."""

    def __init__(self, cell_size: float):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], List[Particle]] = {}

    def clear(self):
        """Clear the grid."""
        self.grid.clear()

    def _hash(self, position: np.ndarray) -> Tuple[int, int]:
        """Hash position to grid cell."""
        x = int(position[0] / self.cell_size)
        y = int(position[1] / self.cell_size)
        return (x, y)

    def insert(self, particle: Particle):
        """Insert particle into grid."""
        cell = self._hash(particle.position)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(particle)

    def get_nearby(self, particle: Particle) -> List[Particle]:
        """Get particles in neighboring cells."""
        cell = self._hash(particle.position)
        nearby = []

        # Check 3x3 neighborhood
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_cell = (cell[0] + dx, cell[1] + dy)
                if check_cell in self.grid:
                    nearby.extend(self.grid[check_cell])

        return nearby


class CollisionDetector:
    """Collision detection and resolution."""

    def __init__(self):
        self.spatial_hash: SpatialHash = None

    def detect_and_resolve(
        self,
        particles: List[Particle],
        max_diameter: float,
        timestamp: float
    ) -> List[CollisionEvent]:
        """
        Detect and resolve all collisions.

        Args:
            particles: List of particles
            max_diameter: Maximum particle diameter for spatial hash cell size
            timestamp: Current simulation time

        Returns:
            List of collision events
        """
        events = []

        # Build spatial hash
        cell_size = max(max_diameter * 2, 10.0)
        self.spatial_hash = SpatialHash(cell_size)

        for particle in particles:
            if particle.alive:
                self.spatial_hash.insert(particle)

        # Check collisions
        checked_pairs: Set[Tuple[int, int]] = set()

        for particle in particles:
            if not particle.alive:
                continue

            nearby = self.spatial_hash.get_nearby(particle)

            for other in nearby:
                if not other.alive or particle.id == other.id:
                    continue

                # Ensure we only check each pair once
                pair = tuple(sorted([particle.id, other.id]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                # Check collision
                event = self._check_and_resolve_collision(particle, other, timestamp)
                if event:
                    events.append(event)

        return events

    def _check_and_resolve_collision(
        self,
        p1: Particle,
        p2: Particle,
        timestamp: float
    ) -> CollisionEvent:
        """
        Check and resolve collision between two particles.

        Returns:
            CollisionEvent if collision occurred, None otherwise
        """
        # Vector from p1 to p2
        delta = p2.position - p1.position
        distance = np.linalg.norm(delta)

        # Check overlap
        min_dist = p1.radius + p2.radius
        if distance >= min_dist:
            return None

        # Prevent division by zero
        if distance < 0.001:
            # Push apart in random direction
            delta = np.array([1.0, 0.0])
            distance = 0.001

        # Normal vector (from p1 to p2)
        normal = delta / distance

        # Overlap amount
        overlap = min_dist - distance

        # Collision point (on the line between centers)
        collision_point = p1.position + normal * p1.radius

        # Relative velocity
        rel_velocity = p2.velocity - p1.velocity

        # Velocity along normal
        vel_along_normal = np.dot(rel_velocity, normal)

        # Don't resolve if velocities are separating
        if vel_along_normal > 0:
            return None

        # Calculate restitution
        restitution = min(p1.restitution, p2.restitution)

        # Calculate impulse scalar
        impulse_scalar = -(1 + restitution) * vel_along_normal
        impulse_scalar /= (1 / p1.mass + 1 / p2.mass)

        # Apply impulse
        impulse = impulse_scalar * normal
        p1.velocity -= impulse / p1.mass
        p2.velocity += impulse / p2.mass

        # Apply tangential friction
        tangent = np.array([-normal[1], normal[0]])
        vel_along_tangent = np.dot(rel_velocity, tangent)
        friction = min(p1.friction, p2.friction)
        friction_impulse = -vel_along_tangent * friction
        friction_vector = friction_impulse * tangent

        p1.velocity -= friction_vector / (2 * p1.mass)
        p2.velocity += friction_vector / (2 * p2.mass)

        # Positional correction (bias to prevent sinking)
        correction_percent = 0.4
        slop = 0.01
        correction = max(overlap - slop, 0) / (1/p1.mass + 1/p2.mass) * correction_percent
        correction_vector = correction * normal

        p1.position -= correction_vector / p1.mass
        p2.position += correction_vector / p2.mass

        # Apply angular velocity from collision
        torque_factor = 0.1
        p1.angular_velocity += vel_along_tangent * torque_factor / p1.radius
        p2.angular_velocity -= vel_along_tangent * torque_factor / p2.radius

        # Apply deformation
        deform_intensity = min(abs(vel_along_normal) / 100, 1.0)
        p1.apply_deformation(-normal, deform_intensity)
        p2.apply_deformation(normal, deform_intensity)

        # Calculate collision energy
        energy = 0.5 * (p1.mass * p2.mass) / (p1.mass + p2.mass) * vel_along_normal ** 2

        # Mix colors
        mixed_color = self._mix_colors(p1.color, p2.color, p1.mass, p2.mass)

        # Create event
        return CollisionEvent(
            timestamp=timestamp,
            particle1_id=p1.id,
            particle2_id=p2.id,
            point=collision_point,
            normal=normal,
            energy=abs(energy),
            relative_speed=abs(vel_along_normal),
            mixed_color=mixed_color
        )

    @staticmethod
    def _mix_colors(
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        mass1: float,
        mass2: float
    ) -> Tuple[int, int, int]:
        """Mix two colors based on mass ratio."""
        total_mass = mass1 + mass2
        w1 = mass1 / total_mass
        w2 = mass2 / total_mass

        r = int(color1[0] * w1 + color2[0] * w2)
        g = int(color1[1] * w1 + color2[1] * w2)
        b = int(color1[2] * w1 + color2[2] * w2)

        return (r, g, b)

