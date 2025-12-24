
import numpy as np
from collections import deque
from ..core.settings import ParticleSettings

class Particle:
    def __init__(self, particle_id: int, settings: ParticleSettings, rng, position, velocity, radius, shape, color):
        self.id = particle_id
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.zeros(2, dtype=float)

        self.radius = radius
        self.mass = np.pi * radius**2 if settings.mass_from_area else 1.0
        self.inv_mass = 1.0 / self.mass if self.mass > 0 else 0.0

        self.shape = shape
        self.color = color # HSL tuple (h, s, l)

        # Rotational state
        self.angle = rng.uniform(0, 360)
        self.angular_velocity = rng.uniform(-180, 180) # degrees per second
        self.angular_damping = 0.98

        # Visual-only effects state
        self.glow_intensity = 0.0
        self.scale = np.array([1.0, 1.0], dtype=float)
        self.deformation_velocity = np.zeros(2, dtype=float)

        # Trail buffer
        self._trail_length = 20 # Default, will be updated from settings
        self.trail = deque(maxlen=self._trail_length)

    def update_trail_length(self, length: int):
        if self._trail_length != length:
            self._trail_length = length
            self.trail = deque(list(self.trail), maxlen=length)

    def add_force(self, force: np.ndarray):
        self.acceleration += force * self.inv_mass

    def integrate(self, dt: float, max_speed: float):
        # Semi-implicit Euler integration
        self.velocity += self.acceleration * dt

        # Clamp speed
        speed = np.linalg.norm(self.velocity)
        if speed > max_speed:
            self.velocity = (self.velocity / speed) * max_speed

        self.position += self.velocity * dt

        # Integrate rotation
        self.angle += self.angular_velocity * dt
        self.angular_velocity *= self.angular_damping
        self.angle %= 360

        # Reset acceleration for next frame
        self.acceleration.fill(0)

        # Update trail
        self.trail.append(self.position.copy())

    def update_visuals(self, dt: float, stiffness: float, damping: float):
        # Update deformation (damped spring model)
        displacement = self.scale - 1.0
        spring_force = -stiffness * displacement
        damping_force = -damping * self.deformation_velocity

        deformation_accel = spring_force + damping_force
        self.deformation_velocity += deformation_accel * dt
        self.scale += self.deformation_velocity * dt

        # Update glow from kinetic energy (simple model for now)
        speed = np.linalg.norm(self.velocity)
        target_glow = min(1.0, (speed / 500.0)**2) # Arbitrary scaling
        self.glow_intensity = self.glow_intensity * 0.95 + target_glow * 0.05
