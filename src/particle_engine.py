"""Particle physics engine"""

import math
import random
import time


class Particle:
    """Represents a single particle in the simulation"""

    def __init__(self, x, y, vx, vy, radius, color, shape="Circle", lifetime=None):
        """
        Initialize a particle

        Args:
            x, y: Position
            vx, vy: Velocity
            radius: Particle size
            color: RGB tuple
            shape: Shape type (Circle, Square, Triangle, Star, Hexagon, Heart)
            lifetime: Maximum lifetime in seconds (None for infinite)
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.shape = shape
        self.alpha = 255
        self.lifetime = lifetime
        self.birth_time = time.time()
        self.trail = []
        self.max_trail_length = 20
        self.collision_time = 0

    def update(self, dt, gravity=0.1):
        """Update particle position and velocity"""
        # Apply gravity
        self.vy += gravity

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Add to trail for motion effect
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Apply velocity damping (friction)
        self.vx *= 0.9995
        self.vy *= 0.9995

        # Update alpha based on lifetime
        if self.lifetime is not None:
            age = time.time() - self.birth_time
            if age > self.lifetime:
                return False  # Particle should be removed

            # Fade out at end of lifetime
            fade_time = 0.5
            if age > self.lifetime - fade_time:
                progress = (age - (self.lifetime - fade_time)) / fade_time
                self.alpha = int(255 * (1 - progress))

        return True

    def check_boundary_collision(self, center_x, center_y, boundary_radius):
        """
        Check and handle collision with circular boundary

        Returns:
            list: New particles created from collision (if any)
        """
        dist_to_center = math.sqrt((self.x - center_x) ** 2 + (self.y - center_y) ** 2)

        if dist_to_center + self.radius > boundary_radius:
            # Collision detected
            # Move particle back inside boundary
            if dist_to_center > 0:
                # Normal vector from center to particle
                nx = (self.x - center_x) / dist_to_center
                ny = (self.y - center_y) / dist_to_center

                # Position particle at boundary
                self.x = center_x + nx * (boundary_radius - self.radius)
                self.y = center_y + ny * (boundary_radius - self.radius)

                # Reflect velocity
                dot_product = self.vx * nx + self.vy * ny
                self.vx = (self.vx - 2 * dot_product * nx) * 0.95
                self.vy = (self.vy - 2 * dot_product * ny) * 0.95

                return [self]  # Return collision marker

        return []

    def check_particle_collision(self, other):
        """
        Check if this particle collides with another

        Args:
            other: Another Particle object

        Returns:
            bool: True if collision occurred
        """
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        return dist < (self.radius + other.radius)

    def resolve_collision(self, other):
        """
        Resolve elastic collision between two particles

        Args:
            other: Another Particle object

        Returns:
            list: New particles created from collision
        """
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0:
            dist = 0.1

        # Normal vector
        nx = dx / dist
        ny = dy / dist

        # Relative velocity
        dvx = other.vx - self.vx
        dvy = other.vy - self.vy

        # Relative velocity along collision normal
        dvn = dvx * nx + dvy * ny

        # Don't process if velocities are moving apart
        if dvn >= 0:
            return []

        # Equal mass collision (simplified)
        # Exchange velocity components along normal
        self.vx += dvn * nx * 0.5
        self.vy += dvn * ny * 0.5
        other.vx -= dvn * nx * 0.5
        other.vy -= dvn * ny * 0.5

        # Separate particles to prevent overlap
        overlap = (self.radius + other.radius) - dist
        if overlap > 0:
            separation = overlap / 2 + 0.5
            self.x -= separation * nx
            self.y -= separation * ny
            other.x += separation * nx
            other.y += separation * ny

        # Record collision time for visual effect
        self.collision_time = time.time()
        other.collision_time = time.time()

        # Create new particles at collision point
        new_particles = []
        collision_count = random.randint(1, 3)

        for _ in range(collision_count):
            # New particle at collision point
            new_x = (self.x + other.x) / 2
            new_y = (self.y + other.y) / 2

            # Random velocity
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            new_vx = speed * math.cos(angle)
            new_vy = speed * math.sin(angle)

            # Smaller particle
            new_radius = random.uniform(
                max(1, self.radius * 0.3),
                max(1, (self.radius + other.radius) / 4)
            )

            # Mix colors
            new_color = (
                (self.color[0] + other.color[0]) // 2,
                (self.color[1] + other.color[1]) // 2,
                (self.color[2] + other.color[2]) // 2,
            )

            new_particle = Particle(
                new_x, new_y, new_vx, new_vy, new_radius, new_color,
                shape=self.shape, lifetime=1.0
            )
            new_particles.append(new_particle)

        return new_particles

    def get_collision_pulse(self):
        """Get collision pulse effect for glow animation"""
        time_since_collision = time.time() - self.collision_time
        if time_since_collision < 0.3:
            return max(0, 1 - (time_since_collision / 0.3))
        return 0


class ParticleEngine:
    """Main particle simulation engine"""

    def __init__(self, width=800, height=600, boundary_radius=250):
        """
        Initialize particle engine

        Args:
            width, height: Canvas dimensions
            boundary_radius: Radius of circular boundary
        """
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.boundary_radius = boundary_radius

        self.particles = []
        self.max_particles = 100
        self.spawn_rate = 5  # particles per second
        self.spawn_counter = 0
        self.gravity = 0.1

        # Settings
        self.particle_shape = "Circle"
        self.min_particle_size = 3
        self.max_particle_size = 15
        self.min_particle_speed = 1
        self.max_particle_speed = 5

        self.collision_log = []  # For audio generation

    def reset(self):
        """Clear all particles"""
        self.particles = []
        self.collision_log = []

    def spawn_particle(self, count=1):
        """Spawn new particles at random positions inside boundary"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            # Random position inside circular boundary
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, self.boundary_radius - 50)
            x = self.center_x + radius * math.cos(angle)
            y = self.center_y + radius * math.sin(angle)

            # Random velocity
            vel_angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(self.min_particle_speed, self.max_particle_speed)
            vx = speed * math.cos(vel_angle)
            vy = speed * math.sin(vel_angle)

            # Random size
            radius = random.uniform(self.min_particle_size, self.max_particle_size)

            # Random color from scheme (will be set by renderer)
            color = (200, 200, 200)

            particle = Particle(x, y, vx, vy, radius, color, shape=self.particle_shape)
            self.particles.append(particle)

    def update(self, dt):
        """Update all particles"""
        # Handle spawning
        self.spawn_counter += self.spawn_rate * dt
        while self.spawn_counter >= 1 and len(self.particles) < self.max_particles:
            self.spawn_particle(1)
            self.spawn_counter -= 1

        # Update particles
        particles_to_remove = []
        for particle in self.particles:
            if not particle.update(dt, self.gravity):
                particles_to_remove.append(particle)

            # Check boundary collision
            collisions = particle.check_boundary_collision(
                self.center_x, self.center_y, self.boundary_radius
            )
            if collisions:
                self.collision_log.append({
                    'type': 'boundary',
                    'time': len(self.collision_log) * dt,
                    'x': particle.x,
                    'y': particle.y,
                })

        # Remove dead particles
        for particle in particles_to_remove:
            if particle in self.particles:
                self.particles.remove(particle)

        # Check particle-particle collisions
        for i in range(len(self.particles)):
            for j in range(i + 1, len(self.particles)):
                if self.particles[i].check_particle_collision(self.particles[j]):
                    new_particles = self.particles[i].resolve_collision(self.particles[j])
                    self.particles.extend(new_particles)

                    self.collision_log.append({
                        'type': 'particle',
                        'time': len(self.collision_log) * dt,
                        'x': (self.particles[i].x + self.particles[j].x) / 2,
                        'y': (self.particles[i].y + self.particles[j].y) / 2,
                    })

                    # Limit particle growth
                    while len(self.particles) > self.max_particles:
                        # Remove smallest particles
                        smallest = min(self.particles, key=lambda p: p.radius)
                        if smallest in self.particles:
                            self.particles.remove(smallest)

    def get_particle_count(self):
        """Get current number of particles"""
        return len(self.particles)

    def set_spawn_rate(self, rate):
        """Set spawn rate (particles per second)"""
        self.spawn_rate = max(0, min(20, rate))

    def set_max_particles(self, max_count):
        """Set maximum particle count"""
        self.max_particles = max(10, min(200, max_count))

    def set_particle_size_range(self, min_size, max_size):
        """Set particle size range"""
        self.min_particle_size = max(1, min_size)
        self.max_particle_size = max(self.min_particle_size, max_size)

    def set_particle_speed_range(self, min_speed, max_speed):
        """Set particle speed range"""
        self.min_particle_speed = max(0.1, min_speed)
        self.max_particle_speed = max(self.min_particle_speed, max_speed)

    def set_particle_shape(self, shape):
        """Set particle shape"""
        self.particle_shape = shape

