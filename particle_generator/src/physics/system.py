
import numpy as np
from typing import List

from ..core.settings import Settings
from ..core.rng import rng
from ..core.events import event_queue, BoundaryHitEvent
from .particle import Particle
from .spawner import Spawner
from .collision import CollisionGrid

class ParticleSystem:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.spawner = Spawner(settings)
        self.particles: List[Particle] = []
        self.collision_grid = CollisionGrid(settings)
        self.time = 0.0

    def reset(self):
        """Resets the simulation to its initial state."""
        self.particles.clear()
        rng.set_seed(self.settings.seed)
        self.time = 0.0
        self.spawner.next_particle_id = 0
        self.spawner.spawn_initial(self)

    def add_particle(self, particle: Particle):
        self.particles.append(particle)

    def remove_particle(self, particle: Particle):
        try:
            self.particles.remove(particle)
        except ValueError:
            pass

    def _apply_global_forces(self):
        """Applies forces that affect all particles."""
        p_settings = self.settings.physics
        sim_settings = self.settings.simulation

        center = np.array(sim_settings.resolution) / 2.0

        for p in self.particles:
            # Gravity / Center Attractor
            if p_settings.gravity_enabled:
                if p_settings.attractor_mode:
                    direction = center - p.position
                    dist_sq = np.sum(direction**2)
                    if dist_sq > 1.0:
                        force = direction / np.sqrt(dist_sq) * p_settings.gravity_strength * p.mass
                        p.add_force(force)
                else:
                    angle = np.deg2rad(p_settings.gravity_direction_deg)
                    gravity_vec = np.array([np.cos(angle), np.sin(angle)]) * p_settings.gravity_strength
                    p.add_force(gravity_vec * p.mass)

            # Quadratic Drag
            if p_settings.drag_coeff > 0:
                speed_sq = np.sum(p.velocity**2)
                if speed_sq > 0:
                    drag_force = -p_settings.drag_coeff * np.linalg.norm(p.velocity) * p.velocity
                    p.add_force(drag_force)

            # Brownian Motion
            if p_settings.brownian_enabled and p_settings.brownian_strength > 0:
                brownian_force = rng.normal(scale=p_settings.brownian_strength, size=2)
                p.add_force(brownian_force)

            # Vortex Force
            if p_settings.vortex_enabled and p_settings.vortex_strength != 0:
                relative_pos = p.position - center
                dist = np.linalg.norm(relative_pos)
                if dist > 1.0:
                    # Tangential direction
                    tangent_vec = np.array([-relative_pos[1], relative_pos[0]]) / dist
                    # Force magnitude with smooth falloff
                    falloff = dist / (1 + (dist / (center[0] * 0.25))**2)
                    vortex_force = tangent_vec * p_settings.vortex_strength * falloff
                    p.add_force(vortex_force)

            # Attraction/Repulsion
            if p_settings.attraction_repulsion_enabled and p_settings.attraction_strength != 0:
                for other in self.particles:
                    if p.id == other.id: continue
                    delta = other.position - p.position
                    dist_sq = np.sum(delta**2)
                    if dist_sq < p_settings.attraction_radius**2 and dist_sq > 1e-4:
                        dist = np.sqrt(dist_sq)
                        direction = delta / dist
                        # Force ramps down to zero at the edge of the radius
                        strength = p_settings.attraction_strength * (1 - dist / p_settings.attraction_radius)
                        force = direction * strength * p.mass * other.mass
                        p.add_force(force)

    def _handle_collisions(self):
        """Updates the collision grid and resolves all collisions."""
        self.collision_grid.update(self.particles)
        self.collision_grid.find_and_resolve_collisions(self)

    def _handle_boundary(self):
        """Handles particle interactions with the circular boundary."""
        p_settings = self.settings.physics
        sim_settings = self.settings.simulation
        center = np.array(sim_settings.resolution) / 2.0
        boundary_radius = (min(sim_settings.resolution) / 2.0) * p_settings.boundary_radius_ratio

        for p in self.particles:
            relative_pos = p.position - center
            dist = np.linalg.norm(relative_pos)

            if dist > boundary_radius - p.radius:
                # Soft boundary spring force
                if p_settings.soft_boundary_enabled:
                    overlap = dist - (boundary_radius - p.radius)
                    force_mag = -overlap * p_settings.soft_boundary_softness * 1000 # softness needs to be scaled
                    normal = relative_pos / dist
                    p.add_force(normal * force_mag)

                # Hard boundary reflection (safety)
                if dist > boundary_radius:
                    overlap = dist - boundary_radius
                    p.position -= (relative_pos / dist) * overlap # Correct position

                    normal = relative_pos / dist
                    velocity_normal_comp = np.dot(p.velocity, normal) * normal
                    velocity_tangent_comp = p.velocity - velocity_normal_comp

                    # Reflect velocity with elasticity
                    p.velocity = velocity_tangent_comp - velocity_normal_comp * p_settings.boundary_elasticity

                    # Add spin from tangential component
                    spin_effect = np.dot(velocity_tangent_comp, np.array([-normal[1], normal[0]]))
                    p.angular_velocity += spin_effect * p_settings.friction * 0.1

                    # Emit event
                    energy = 0.5 * p.mass * np.sum(velocity_normal_comp**2)
                    event_queue.add_event(BoundaryHitEvent(
                        timestamp=self.time,
                        particle_id=p.id,
                        position=tuple(p.position.tolist()),
                        energy=energy
                    ))

    def update(self, dt: float):
        """Advances the simulation by a single time step."""
        if dt <= 0: return
        self.time += dt
        self.spawner.update(dt, self)
        self._apply_global_forces()
        self._handle_collisions()
        self._handle_boundary()

        max_speed = self.settings.physics.max_speed
        for p in self.particles:
            speed = np.linalg.norm(p.velocity)
            substeps = 1
            if speed * dt > p.radius * 0.5:
                substeps = min(4, int(np.ceil(speed * dt / (p.radius * 0.5))))

            sub_dt = dt / substeps
            for _ in range(substeps):
                p.integrate(sub_dt, max_speed)

        v_settings = self.settings.visuals
        for p in self.particles:
            p.update_visuals(dt, v_settings.spring_stiffness, v_settings.damping)
            p.update_trail_length(v_settings.trails_length)
