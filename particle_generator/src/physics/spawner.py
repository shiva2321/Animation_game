
import numpy as np
from typing import TYPE_CHECKING

from ..core.settings import Settings
from ..core.rng import rng
from ..core.events import event_queue, SpawnEvent
from .particle import Particle

if TYPE_CHECKING:
    from .system import ParticleSystem


class Spawner:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.spawn_counter = 0.0
        self.next_particle_id = 0
        self._hue_iterator = 0.0

    def spawn_initial(self, system: 'ParticleSystem'):
        self._hue_iterator = rng.random() # Start at a random hue
        for _ in range(self.settings.particles.initial_count):
            self._spawn_particle(system, is_initial=True)

    def update(self, dt: float, system: 'ParticleSystem'):
        if len(system.particles) >= self.settings.particles.max_particles:
            return

        spawn_rate = self.settings.particles.spawn_rate
        if spawn_rate > 0:
            self.spawn_counter += spawn_rate * dt
            while self.spawn_counter >= 1:
                if len(system.particles) < self.settings.particles.max_particles:
                    self._spawn_particle(system)
                    self.spawn_counter -= 1
                else:
                    break

    def _get_next_color(self):
        # Generates harmonious colors using the golden ratio.
        # This will be influenced by the color scheme later in the palette module.
        self._hue_iterator = (self._hue_iterator + 0.61803398875) % 1.0
        return (self._hue_iterator, 0.85, 0.95) # (h, s, l)

    def _spawn_particle(self, system: 'ParticleSystem', is_initial: bool = False):
        p_settings = self.settings.particles

        radius = rng.uniform(p_settings.size_min, p_settings.size_max)

        boundary_radius = self.settings.physics.boundary_radius_ratio * (min(self.settings.simulation.resolution) / 2)
        spawn_radius = boundary_radius - radius

        r = spawn_radius * np.sqrt(rng.random())
        theta = rng.uniform(0, 2 * np.pi)
        center = np.array(self.settings.simulation.resolution) / 2
        position = center + np.array([r * np.cos(theta), r * np.sin(theta)])

        initial_speed = rng.uniform(50, 150)
        angle = rng.uniform(0, 2 * np.pi)
        velocity = np.array([initial_speed * np.cos(angle), initial_speed * np.sin(angle)])

        shape = rng.choice(p_settings.shapes) if p_settings.shapes else "circle"
        color = self._get_next_color()

        particle = Particle(
            particle_id=self.next_particle_id,
            settings=p_settings,
            rng=rng,
            position=position,
            velocity=velocity,
            radius=radius,
            shape=shape,
            color=color,
        )

        system.add_particle(particle)
        event_queue.add_event(SpawnEvent(
            timestamp=system.time,
            particle_id=particle.id,
            position=tuple(particle.position.tolist())
        ))
        self.next_particle_id += 1
