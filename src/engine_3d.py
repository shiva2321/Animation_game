"""3D-inspired particle engine with collision-based spawning"""

import math
import random
import time
import numpy as np


class Object3D:
    """A 3D-inspired bouncing object"""

    def __init__(self, x, y, vx, vy, radius, color, shape="sphere", boundary_type="circle"):
        """
        Initialize a 3D object

        Args:
            x, y: Position
            vx, vy: Velocity
            radius: Object size
            color: RGB tuple
            shape: "sphere", "cube", "star", "triangle"
            boundary_type: "circle", "square", "triangle"
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.shape = shape
        self.boundary_type = boundary_type

        # 3D visual properties
        self.rotation = 0
        self.spin_speed = random.uniform(-0.1, 0.1)
        self.shine_intensity = 0.8
        self.shadow_offset = 3

        # Physics
        self.birth_time = time.time()
        self.last_bounce_time = 0
        self.collision_time = 0

        # Trail for 3D effect
        self.trail = []
        self.max_trail_length = 15

    def update(self, dt, speed_multiplier=1.0, gravity=0.25, calm_down_factor=1.0):
        """
        Update object position and properties with smooth momentum and calm-down

        Args:
            dt: Delta time
            speed_multiplier: Factor to increase speed over time
            gravity: Gravitational acceleration
            calm_down_factor: Factor to reduce movement (1.0 = normal, <1.0 = slowing)
        """
        # During spawning phase: increase speed chaotically
        # During calm-down phase: gradually reduce movements
        speed_factor = 1.0 + (speed_multiplier * dt * 0.1)
        self.vx *= (speed_factor * calm_down_factor)
        self.vy *= (speed_factor * calm_down_factor)

        # Gravity - pulls objects downward
        self.vy += gravity * dt

        # Update position smoothly
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Velocity limit to prevent instability
        max_velocity = 300
        velocity_mag = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if velocity_mag > max_velocity:
            scale = max_velocity / velocity_mag
            self.vx *= scale
            self.vy *= scale

        # Update rotation smoothly
        self.rotation += self.spin_speed
        self.rotation = self.rotation % (2 * math.pi)

        # Update shine intensity
        age = time.time() - self.birth_time
        self.shine_intensity = 0.7 + 0.2 * math.sin(age * 3)

        # Trail management
        self.trail.append((self.x, self.y, self.shine_intensity))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def check_boundary_collision(self, center_x, center_y, boundary_radius, boundary_type="circle"):
        """
        Check and handle collision with boundary

        Returns:
            bool: True if collision occurred
        """
        collision = False

        if boundary_type == "circle":
            dist_to_center = math.sqrt((self.x - center_x) ** 2 + (self.y - center_y) ** 2)
            max_dist = boundary_radius - self.radius - 15  # Larger margin for safety

            if dist_to_center > max_dist:
                if dist_to_center > 0.1:
                    nx = (self.x - center_x) / dist_to_center
                    ny = (self.y - center_y) / dist_to_center
                    # Push well inside
                    self.x = center_x + nx * max_dist
                    self.y = center_y + ny * max_dist
                    # Reflect and preserve more momentum for faster movement
                    dot_product = self.vx * nx + self.vy * ny
                    self.vx = (self.vx - 2 * dot_product * nx) * 0.78
                    self.vy = (self.vy - 2 * dot_product * ny) * 0.78
                    collision = True

        elif boundary_type == "square":
            margin = self.radius + 15
            half = boundary_radius - margin

            # Smooth boundaries with better momentum preservation
            if self.x < center_x - half:
                self.x = center_x - half
                self.vx = abs(self.vx) * 0.78
                collision = True
            elif self.x > center_x + half:
                self.x = center_x + half
                self.vx = -abs(self.vx) * 0.78
                collision = True

            if self.y < center_y - half:
                self.y = center_y - half
                self.vy = abs(self.vy) * 0.78
                collision = True
            elif self.y > center_y + half:
                self.y = center_y + half
                self.vy = -abs(self.vy) * 0.78
                collision = True

        elif boundary_type == "triangle":
            # Use inscribed circle of triangle for simple containment
            # This ensures objects stay within triangle bounds
            dist_to_center = math.sqrt((self.x - center_x) ** 2 + (self.y - center_y) ** 2)
            max_dist = boundary_radius * 0.58 - self.radius - 15

            if dist_to_center > max_dist:
                if dist_to_center > 0.1:
                    nx = (self.x - center_x) / dist_to_center
                    ny = (self.y - center_y) / dist_to_center
                    self.x = center_x + nx * max_dist
                    self.y = center_y + ny * max_dist
                    dot_product = self.vx * nx + self.vy * ny
                    self.vx = (self.vx - 2 * dot_product * nx) * 0.78
                    self.vy = (self.vy - 2 * dot_product * ny) * 0.78
                    collision = True

        if collision:
            self.last_bounce_time = time.time()

        return collision

    def check_collision(self, other):
        """Check if colliding with another object"""
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < (self.radius + other.radius)

    def resolve_collision(self, other):
        """Resolve collision with another object - smooth momentum transfer"""
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0 or dist < 0.1:
            dist = 0.1

        # Normal vector (direction of collision)
        nx = dx / dist
        ny = dy / dist

        # Relative velocity
        dvx = other.vx - self.vx
        dvy = other.vy - self.vy

        # Relative velocity along normal
        dvn = dvx * nx + dvy * ny

        # Don't process if moving apart
        if dvn >= 0:
            return False

        # Momentum transfer - equal mass elastic collision
        # Smooth and realistic momentum exchange
        impulse = dvn * 0.55  # Elastic collision factor

        self.vx += impulse * nx
        self.vy += impulse * ny
        other.vx -= impulse * nx
        other.vy -= impulse * ny

        # Smooth separation to prevent sticking
        overlap = (self.radius + other.radius) - dist
        if overlap > 0:
            # Gentle separation with small margin
            separation = (overlap / 2) + 0.5
            self.x -= separation * nx
            self.y -= separation * ny
            other.x += separation * nx
            other.y += separation * ny

        self.collision_time = time.time()
        other.collision_time = time.time()

        return True

    def get_bounce_intensity(self):
        """Get visual intensity of recent bounce (for sound)"""
        time_since_bounce = time.time() - self.last_bounce_time
        if time_since_bounce < 0.2:
            return max(0, 1 - (time_since_bounce / 0.2))
        return 0

    def get_collision_intensity(self):
        """Get visual intensity of recent collision"""
        time_since_collision = time.time() - self.collision_time
        if time_since_collision < 0.3:
            return max(0, 1 - (time_since_collision / 0.3))
        return 0


class Engine3D:
    """3D physics engine with collision-based spawning and calm-down phase"""

    # Simulation states
    STATE_SPAWNING = "spawning"      # Objects being created via collisions
    STATE_CALM_DOWN = "calm_down"    # Objects slowing down
    STATE_SETTLED = "settled"        # All objects at bottom

    def __init__(self, width=800, height=600, boundary_radius=250, boundary_type="circle"):
        """
        Initialize 3D engine

        Args:
            width, height: Canvas dimensions
            boundary_radius: Size of boundary
            boundary_type: "circle", "square", "triangle"
        """
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.boundary_radius = boundary_radius
        self.boundary_type = boundary_type

        self.objects = []
        self.max_objects = 50
        self.initial_objects = 2
        self.start_time = time.time()

        # Calm-down settings
        self.calm_down_duration = 10.0  # Seconds to calm down after max objects reached
        self.calm_down_time = 0  # Time when calm-down started
        self.state = self.STATE_SPAWNING

        # Settings - increased default speeds
        self.object_shape = "sphere"
        self.min_object_size = 5
        self.max_object_size = 15
        self.min_object_speed = 8
        self.max_object_speed = 16

        # Collision log for audio
        self.collision_log = []
        self.bounce_log = []

    def reset(self):
        """Reset engine"""
        self.objects = []
        self.collision_log = []
        self.bounce_log = []
        self.start_time = time.time()
        self.state = self.STATE_SPAWNING
        self.calm_down_time = 0

        # Create initial objects
        self._spawn_initial_objects()

    def _spawn_initial_objects(self):
        """Spawn initial objects"""
        for _ in range(self.initial_objects):
            self._create_random_object()

    def _create_random_object(self):
        """Create a new object at random position with random velocity"""
        # Don't spawn if in settled state
        if self.state == self.STATE_SETTLED:
            return None

        # Don't spawn if max reached (unless in calm-down, allow settling)
        if len(self.objects) >= self.max_objects:
            return None

        # Random position inside boundary
        angle = random.uniform(0, 2 * math.pi)
        # Spawn objects from top and sides for natural falling
        if random.random() < 0.7:
            # 70% spawn from top
            y = self.center_y - self.boundary_radius + 30
            x = self.center_x + random.uniform(-self.boundary_radius * 0.6, self.boundary_radius * 0.6)
        else:
            # 30% spawn from sides
            x = self.center_x + random.choice([-1, 1]) * (self.boundary_radius - 30)
            y = self.center_y + random.uniform(-self.boundary_radius * 0.6, self.boundary_radius * 0.6)

        # Random velocity - more chaotic when spawning
        vel_angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(self.min_object_speed, self.max_object_speed)
        vx = speed * math.cos(vel_angle)
        vy = speed * math.sin(vel_angle)

        # Random size
        obj_radius = random.uniform(self.min_object_size, self.max_object_size)

        # Color (will be set by renderer based on scheme)
        color = (200, 200, 200)

        obj = Object3D(
            x, y, vx, vy, obj_radius, color,
            shape=self.object_shape,
            boundary_type=self.boundary_type
        )

        self.objects.append(obj)
        return obj

    def update(self, dt):
        """Update all objects with proper state management"""
        elapsed = time.time() - self.start_time

        # Determine calm-down factor based on state
        calm_down_factor = 1.0

        if self.state == self.STATE_SPAWNING:
            # Check if we've reached max objects
            if len(self.objects) >= self.max_objects:
                self.state = self.STATE_CALM_DOWN
                self.calm_down_time = elapsed
            else:
                # Try to spawn new objects on collisions
                # Speed increases over time
                calm_down_factor = 1.0

        elif self.state == self.STATE_CALM_DOWN:
            # Calculate calm-down progress (0.0 to 1.0)
            calm_elapsed = elapsed - self.calm_down_time
            calm_progress = min(1.0, calm_elapsed / self.calm_down_duration)

            # Smooth easing function for calm-down
            # Uses cubic ease-out for natural deceleration
            calm_down_factor = (1.0 - calm_progress) ** 2

            # Transition to settled state
            if calm_progress >= 1.0:
                self.state = self.STATE_SETTLED
                calm_down_factor = 0.01  # Almost stationary

        elif self.state == self.STATE_SETTLED:
            # Objects barely moving
            calm_down_factor = 0.01

        # Calculate speed multiplier (increases during spawning phase)
        speed_multiplier = 0.8 if self.state == self.STATE_SPAWNING else 0.0

        # Update each object
        for obj in self.objects:
            obj.update(dt, speed_multiplier, gravity=0.3, calm_down_factor=calm_down_factor)

            # Check boundary collision
            if obj.check_boundary_collision(
                self.center_x, self.center_y,
                self.boundary_radius, self.boundary_type
            ):
                self.bounce_log.append({
                    'time': elapsed,
                    'x': obj.x,
                    'y': obj.y,
                    'intensity': 0.7
                })

        # Check object-object collisions
        for i in range(len(self.objects)):
            for j in range(i + 1, len(self.objects)):
                if self.objects[i].check_collision(self.objects[j]):
                    if self.objects[i].resolve_collision(self.objects[j]):
                        # Collision occurred - try to spawn new object (only in spawning state)
                        if self.state == self.STATE_SPAWNING:
                            new_obj = self._create_random_object()

                        # Log collision
                        self.collision_log.append({
                            'time': elapsed,
                            'x': (self.objects[i].x + self.objects[j].x) / 2,
                            'y': (self.objects[i].y + self.objects[j].y) / 2,
                            'intensity': 0.9
                        })

    def get_object_count(self):
        """Get number of active objects"""
        return len(self.objects)

    def get_state(self):
        """Get current simulation state"""
        return self.state

    def set_max_objects(self, count):
        """Set maximum object count"""
        self.max_objects = max(2, min(200, count))

    def set_calm_down_duration(self, seconds):
        """Set calm-down duration in seconds"""
        self.calm_down_duration = max(1.0, min(60.0, seconds))

    def set_object_shape(self, shape):
        """Set object shape"""
        self.object_shape = shape

    def set_object_size_range(self, min_size, max_size):
        """Set size range"""
        self.min_object_size = max(1, min_size)
        self.max_object_size = max(self.min_object_size, max_size)

    def set_object_speed_range(self, min_speed, max_speed):
        """Set speed range"""
        self.min_object_speed = max(0.1, min_speed)
        self.max_object_speed = max(self.min_object_speed, max_speed)

