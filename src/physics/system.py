"""
Main particle system orchestrating physics simulation.
"""
import numpy as np
import logging
from typing import List, Tuple
from src.physics.particle import Particle
from src.physics.collision import CollisionDetector
from src.physics.spawner import ParticleSpawner
from src.core.settings import AppSettings
from src.core.rng import DeterministicRNG
from src.core.events import EventQueue, BoundaryHitEvent

logger = logging.getLogger(__name__)


class ParticleSystem:
    """Main physics system with fixed-step integration."""

    def __init__(self, settings: AppSettings, rng: DeterministicRNG):
        self.settings = settings
        self.rng = rng

        # Components
        self.collision_detector = CollisionDetector()
        self.spawner = ParticleSpawner(rng)

        # State
        self.particles: List[Particle] = []
        self.time = 0.0
        self.event_queue = EventQueue()

        # Settling detection for automatic video end
        self.settling_start_time = None
        self.is_settled = False
        self.spawn_limit_reached = False

        # Duration-based auto-calm system
        self.target_duration = settings.duration_sec
        self.calm_start_ratio = 0.7  # Start calming at 70% of duration
        self.original_drag = settings.drag_coeff
        self.original_friction = settings.friction
        self.original_restitution = settings.restitution

        # Spawn cooldown to prevent clustering
        self.last_spawn_time = 0.0
        self.spawn_cooldown = 0.05  # Reduced cooldown for faster spawning (was 0.1)

        # Simulation bounds
        width, height = settings.resolution
        self.center = np.array([width / 2, height / 2])
        self.boundary_radius = min(width, height) * settings.boundary_radius_ratio

        # Spawn initial particles
        self._spawn_initial_particles()

    def _spawn_initial_particles(self):
        """Spawn initial particle set."""
        particles, events = self.spawner.spawn_particles(
            count=self.settings.initial_count,
            pattern=self.settings.spawn_pattern,
            center=self.center,
            boundary_radius=self.boundary_radius,
            size_min=self.settings.size_min,
            size_max=self.settings.size_max,
            shapes=self.settings.shapes,
            shape_weights=self.settings.shape_weights,
            mass_from_area=self.settings.mass_from_area,
            restitution=self.settings.restitution,
            friction=self.settings.friction,
            initial_velocity_scale=100.0
        )

        self.particles.extend(particles)

        # Add spawn events
        for event in events:
            event.timestamp = self.time
            self.event_queue.add_spawn(event)

    def step(self, dt: float = None):
        """
        Advance simulation by one timestep.

        Args:
            dt: Time step (uses settings.dt_sim if None)
        """
        if dt is None:
            dt = self.settings.dt_sim

        # Apply forces to all particles
        self._apply_forces(dt)

        # Apply duration-based calming system
        if self.target_duration > 0:
            self._apply_duration_based_calming()

        # Update particles with substeps if needed
        for particle in self.particles:
            if not particle.alive:
                continue

            # Check if substeps needed (to prevent tunneling)
            speed = particle.get_speed()
            if speed * dt > particle.radius * 0.5:
                # Use substeps
                substeps = min(4, int(speed * dt / (particle.radius * 0.25)) + 1)
                sub_dt = dt / substeps
                for _ in range(substeps):
                    particle.update(sub_dt)
            else:
                particle.update(dt)

        # Apply boundary constraints
        self._apply_boundary_constraints()

        # Detect and resolve collisions
        max_diameter = self.settings.size_max * 2
        collision_events = self.collision_detector.detect_and_resolve(
            self.particles, max_diameter, self.time
        )

        for event in collision_events:
            self.event_queue.add_collision(event)

        # Spawn new particles if needed
        self._handle_spawning(dt)

        # Handle collision-spawned particles
        if self.settings.spawn_on_collision and collision_events:
            self._handle_collision_spawns(collision_events)

        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]

        # Check for settling (if spawn limit reached)
        if self.settings.settling_enabled and self.spawn_limit_reached:
            self._check_settling()

        # Update time
        self.time += dt

    def _apply_forces(self, dt: float):
        """Apply all forces to particles."""
        for particle in self.particles:
            if not particle.alive:
                continue

            # Gravity
            if self.settings.gravity_enabled:
                if self.settings.gravity_attractor_mode:
                    # Gravity toward center
                    to_center = self.center - particle.position
                    dist = np.linalg.norm(to_center)
                    if dist > 0:
                        direction = to_center / dist
                        force = direction * self.settings.gravity_strength * particle.mass
                        particle.apply_force(force)
                else:
                    # Directional gravity
                    # In screen coordinates: Y increases downward, X increases right
                    # 270° should point DOWN (positive Y), 90° should point UP (negative Y)
                    angle_rad = np.radians(self.settings.gravity_direction_deg)
                    # Flip Y component for screen coordinates
                    direction = np.array([np.cos(angle_rad), -np.sin(angle_rad)])
                    force = direction * self.settings.gravity_strength * particle.mass
                    particle.apply_force(force)

            # Quadratic drag
            if self.settings.drag_coeff > 0:
                speed = particle.get_speed()
                if speed > 0:
                    drag_force = -self.settings.drag_coeff * speed * particle.velocity
                    particle.apply_force(drag_force)

            # Brownian motion
            if self.settings.brownian_enabled:
                brownian_force = self.rng.randn(2) * self.settings.brownian_strength
                particle.apply_force(brownian_force)

            # Vortex force
            if self.settings.vortex_enabled:
                to_center = particle.position - self.center
                dist = np.linalg.norm(to_center)
                if dist > 0:
                    # Tangential force
                    tangent = np.array([-to_center[1], to_center[0]])
                    tangent = tangent / np.linalg.norm(tangent)

                    # Falloff with distance
                    falloff = 1.0 / (1.0 + (dist / 100.0) ** self.settings.vortex_falloff)
                    force = tangent * self.settings.vortex_strength * falloff
                    particle.apply_force(force)

            # Attraction to center
            if self.settings.attraction_enabled:
                to_center = self.center - particle.position
                dist = np.linalg.norm(to_center)
                if dist > 0 and dist < self.settings.attraction_radius:
                    direction = to_center / dist
                    strength = self.settings.attraction_strength * (1.0 - dist / self.settings.attraction_radius)
                    force = direction * strength
                    particle.apply_force(force)

            # Repulsion from center
            if self.settings.repulsion_enabled:
                from_center = particle.position - self.center
                dist = np.linalg.norm(from_center)
                if dist > 0 and dist < self.settings.repulsion_radius:
                    direction = from_center / dist
                    strength = self.settings.repulsion_strength * (1.0 - dist / self.settings.repulsion_radius)
                    force = direction * strength
                    particle.apply_force(force)

            # Speed cap
            speed = particle.get_speed()
            if speed > self.settings.max_speed:
                particle.velocity = particle.velocity * (self.settings.max_speed / speed)

    def _apply_boundary_constraints(self):
        """Apply boundary constraints to particles."""
        for particle in self.particles:
            if not particle.alive:
                continue

            # Distance from center
            to_center = particle.position - self.center
            dist = np.linalg.norm(to_center)

            # Soft boundary force
            if self.settings.soft_boundary_enabled:
                soft_start = self.boundary_radius * (1.0 - self.settings.soft_boundary_softness)
                if dist > soft_start:
                    # Apply spring force toward center
                    direction = -to_center / dist if dist > 0 else np.zeros(2)
                    penetration = (dist - soft_start) / (self.boundary_radius - soft_start)
                    force_magnitude = penetration * 1000.0 * particle.mass
                    particle.apply_force(direction * force_magnitude)

                    # Apply damping
                    radial_velocity = np.dot(particle.velocity, to_center / dist) if dist > 0 else 0
                    if radial_velocity > 0:  # Moving outward
                        damping_force = -particle.velocity * self.settings.soft_boundary_damping * particle.mass
                        particle.apply_force(damping_force)

            # Hard boundary (safety clamp)
            max_dist = self.boundary_radius - particle.radius
            if dist > max_dist:
                # Clamp position
                if dist > 0:
                    particle.position = self.center + (to_center / dist) * max_dist
                else:
                    particle.position = self.center.copy()

                # Reflect velocity
                direction = to_center / dist if dist > 0 else np.array([1.0, 0.0])
                vel_along_normal = np.dot(particle.velocity, direction)

                if vel_along_normal > 0:  # Moving outward
                    # Reflect with elasticity
                    particle.velocity -= direction * vel_along_normal * (1 + self.settings.boundary_elasticity)

                    # Apply tangential friction
                    tangent = np.array([-direction[1], direction[0]])
                    vel_along_tangent = np.dot(particle.velocity, tangent)
                    particle.velocity -= tangent * vel_along_tangent * self.settings.friction

                    # Add spin
                    particle.angular_velocity += vel_along_tangent * 0.1 / particle.radius

                    # Emit boundary hit event
                    energy = 0.5 * particle.mass * vel_along_normal ** 2
                    event = BoundaryHitEvent(
                        timestamp=self.time,
                        particle_id=particle.id,
                        point=particle.position.copy(),
                        normal=direction,
                        energy=energy,
                        color=particle.color
                    )
                    self.event_queue.add_boundary_hit(event)

    def _handle_spawning(self, dt: float):
        """Handle continuous particle spawning."""
        if self.settings.spawn_rate_per_sec <= 0:
            return

        if len(self.particles) >= self.settings.max_particles:
            return

        self.spawner.spawn_accumulator += dt
        spawn_interval = 1.0 / self.settings.spawn_rate_per_sec

        while self.spawner.spawn_accumulator >= spawn_interval:
            if len(self.particles) >= self.settings.max_particles:
                break

            particles, events = self.spawner.spawn_particles(
                count=1,
                pattern=self.settings.spawn_pattern if self.settings.spawn_pattern != "collision" else "random",
                center=self.center,
                boundary_radius=self.boundary_radius,
                size_min=self.settings.size_min,
                size_max=self.settings.size_max,
                shapes=self.settings.shapes,
                shape_weights=self.settings.shape_weights,
                mass_from_area=self.settings.mass_from_area,
                restitution=self.settings.restitution,
                friction=self.settings.friction,
                initial_velocity_scale=50.0
            )

            self.particles.extend(particles)

            for event in events:
                event.timestamp = self.time
                self.event_queue.add_spawn(event)

            self.spawner.spawn_accumulator -= spawn_interval

    def _handle_collision_spawns(self, collision_events):
        """Spawn particles from collision events."""
        if not self.settings.spawn_on_collision:
            return

        # Check if spawn limit reached
        if len(self.particles) >= self.settings.max_particles:
            if not self.spawn_limit_reached:
                self.spawn_limit_reached = True
                logger.info(f"Spawn limit reached: {len(self.particles)}/{self.settings.max_particles} objects")
            return

        # Check spawn cooldown to prevent rapid clustering
        if self.time - self.last_spawn_time < self.spawn_cooldown:
            return

        for event in collision_events:
            if len(self.particles) >= self.settings.max_particles:
                break

            # Check cooldown again for each spawn
            if self.time - self.last_spawn_time < self.spawn_cooldown:
                continue

            # Always spawn on collision in this mode (100% chance)
            spawn_chance = 1.0
            if self.rng.random() > spawn_chance:
                continue

            # Spawn at collision point with velocity perpendicular to collision
            tangent = np.array([-event.normal[1], event.normal[0]])
            if self.rng.random() > 0.5:
                tangent = -tangent

            velocity = tangent * event.relative_speed * 0.5

            particle, spawn_event = self.spawner.create_collision_spawn(
                position=event.point.copy(),
                velocity=velocity,
                color=event.mixed_color,
                energy=event.energy,
                size_min=self.settings.size_min,
                size_max=self.settings.size_max,
                shapes=self.settings.shapes,
                shape_weights=self.settings.shape_weights,
                mass_from_area=self.settings.mass_from_area,
                restitution=self.settings.restitution,
                friction=self.settings.friction
            )

            spawn_event.timestamp = self.time
            self.particles.append(particle)
            self.event_queue.add_spawn(spawn_event)

            # Update last spawn time
            self.last_spawn_time = self.time

            # Only spawn one object per collision event to prevent clustering
            break

    def _check_settling(self):
        """Check if all objects have settled (stopped moving)."""
        # Count how many particles are below velocity threshold
        settled_count = 0
        for particle in self.particles:
            if not particle.alive:
                continue
            speed = particle.get_speed()
            if speed < self.settings.settling_velocity_threshold:
                settled_count += 1

        # Check if all particles are settled
        all_settled = (settled_count == len(self.particles)) if self.particles else False

        if all_settled:
            if self.settling_start_time is None:
                # Start the settling timer
                self.settling_start_time = self.time
            elif (self.time - self.settling_start_time) >= self.settings.settling_time_required:
                # All particles have been settled for required time
                if not self.is_settled:
                    self.is_settled = True
                    logger.info(f"All objects settled after {self.time:.1f}s - simulation can end")
        else:
            # Reset if particles start moving again
            self.settling_start_time = None

    def _apply_duration_based_calming(self):
        """
        Gradually calm the simulation as it approaches target duration.
        Increases drag and friction, reduces restitution over time.
        """
        if self.target_duration <= 0:
            return

        # Calculate progress through video (0.0 to 1.0)
        progress = min(1.0, self.time / self.target_duration)

        # Start calming at calm_start_ratio (default 70% through)
        if progress < self.calm_start_ratio:
            return

        # Calculate calm factor (0.0 at start, 1.0 at end)
        calm_progress = (progress - self.calm_start_ratio) / (1.0 - self.calm_start_ratio)
        calm_factor = calm_progress ** 2  # Quadratic for gentle start, strong end

        # Gradually increase damping
        self.settings.drag_coeff = self.original_drag * (1.0 + calm_factor * 10.0)
        self.settings.friction = self.original_friction * (1.0 + calm_factor * 5.0)

        # Gradually reduce bounciness
        self.settings.restitution = self.original_restitution * (1.0 - calm_factor * 0.3)

        # Log the calming (only occasionally)
        if int(self.time * 10) % 20 == 0:
            logger.debug(f"Auto-calm at {progress*100:.1f}%: drag={self.settings.drag_coeff:.4f}, friction={self.settings.friction:.3f}, rest={self.settings.restitution:.2f}")

    def reset(self, seed: int = None):
        """Reset the system."""
        if seed is not None:
            self.rng.reset(seed)
            self.settings.seed = seed
        else:
            self.rng.reset(self.settings.seed)

        Particle.reset_id_counter()
        self.particles.clear()
        self.event_queue.clear()
        self.time = 0.0
        self.spawner.spawn_accumulator = 0.0
        self.spawner.hue_offset = 0.0
        self.settling_start_time = None
        self.is_settled = False
        self.spawn_limit_reached = False
        self.last_spawn_time = 0.0

        # Reset drop counter for proper initial spacing
        if hasattr(self.spawner, 'drop_counter'):
            self.spawner.drop_counter = 0

        self._spawn_initial_particles()

    def get_stats(self) -> dict:
        """Get current system statistics."""
        return {
            'time': self.time,
            'particle_count': len(self.particles),
            'alive_count': sum(1 for p in self.particles if p.alive),
            'total_energy': sum(p.get_kinetic_energy() for p in self.particles if p.alive),
            'spawn_limit_reached': self.spawn_limit_reached,
            'is_settled': self.is_settled
        }

