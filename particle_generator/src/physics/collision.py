
import numpy as np
from collections import defaultdict
from itertools import combinations
from typing import TYPE_CHECKING, List, Tuple

from ..core.settings import Settings
from ..core.events import event_queue, CollisionEvent
from .particle import Particle

if TYPE_CHECKING:
    from .system import ParticleSystem

class CollisionGrid:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.cell_size = settings.particles.size_max * 2.5
        self.grid = defaultdict(list)
        self.width, self.height = settings.simulation.resolution

    def _get_cell_coords(self, position: np.ndarray) -> Tuple[int, int]:
        return int(position[0] // self.cell_size), int(position[1] // self.cell_size)

    def _get_adjacent_cells(self, x: int, y: int) -> List[Tuple[int, int]]:
        return [
            (x, y),
            (x + 1, y),
            (x, y + 1),
            (x + 1, y + 1),
            (x - 1, y + 1),
        ]

    def update(self, particles: List[Particle]):
        self.grid.clear()
        for p in particles:
            cell_coords = self._get_cell_coords(p.position)
            self.grid[cell_coords].append(p)

    def find_and_resolve_collisions(self, system: 'ParticleSystem'):
        checked_pairs = set()

        for (x, y), particles_in_cell in list(self.grid.items()):
            for cell_coords in self._get_adjacent_cells(x, y):
                neighboring_particles = self.grid.get(cell_coords, [])

                # Check for collisions within the cell and with neighbors
                all_particles = particles_in_cell + neighboring_particles
                if len(all_particles) < 2:
                    continue

                for p1, p2 in combinations(all_particles, 2):
                    if p1.id == p2.id: continue

                    pair = tuple(sorted((p1.id, p2.id)))
                    if pair in checked_pairs:
                        continue
                    checked_pairs.add(pair)

                    self._check_and_resolve_pair(p1, p2, system)

    def _check_and_resolve_pair(self, p1: Particle, p2: Particle, system: 'ParticleSystem'):
        delta_pos = p2.position - p1.position
        dist_sq = np.sum(delta_pos**2)
        min_dist = p1.radius + p2.radius

        if dist_sq < min_dist**2 and dist_sq > 1e-6:
            dist = np.sqrt(dist_sq)
            normal = delta_pos / dist
            overlap = min_dist - dist

            # 1. Resolve Overlap
            # Move particles apart along the normal, weighted by inverse mass
            total_inv_mass = p1.inv_mass + p2.inv_mass
            correction = (overlap / total_inv_mass) * normal
            p1.position -= correction * p1.inv_mass
            p2.position += correction * p2.inv_mass

            # 2. Resolve Velocity (Impulse)
            delta_vel = p2.velocity - p1.velocity
            impulse_magnitude = np.dot(delta_vel, normal)

            if impulse_magnitude < 0:
                restitution = self.settings.physics.restitution
                j = -(1 + restitution) * impulse_magnitude / total_inv_mass
                impulse = j * normal

                p1.velocity -= impulse * p1.inv_mass
                p2.velocity += impulse * p2.inv_mass

                # 3. Emit Collision Event
                collision_energy = 0.5 * (p1.mass + p2.mass) * impulse_magnitude**2
                event_queue.add_event(CollisionEvent(
                    timestamp=system.time,
                    particle_a_id=p1.id,
                    particle_b_id=p2.id,
                    position=tuple((p1.position + p2.position) / 2),
                    energy=collision_energy,
                    relative_speed=abs(impulse_magnitude),
                    mixed_color=(255, 255, 255), # Placeholder
                    normal=tuple(normal.tolist())
                ))

                # 4. Trigger visual deformation
                self._trigger_deformation(p1, normal, impulse_magnitude)
                self._trigger_deformation(p2, -normal, impulse_magnitude)

    def _trigger_deformation(self, p: Particle, normal: np.ndarray, impulse: float):
        v_settings = self.settings.visuals
        energy_factor = min(1.0, impulse / 200.0) if v_settings.deformation_by_energy else 1.0
        amount = v_settings.impact_deformation_amount * energy_factor * 5.0 # Scale impulse

        # Apply an impulse to the deformation velocity along the collision normal
        # This will cause the spring model in the particle to react
        p.deformation_velocity -= normal * amount
