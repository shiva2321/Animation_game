"""Graphics rendering engine using Pygame"""

import pygame
import math
import time
from src.utils.shapes import draw_shape, draw_glow
from src.utils.colors import get_color_scheme, adjust_brightness


class Renderer:
    """Handles all graphics rendering"""

    def __init__(self, width=800, height=600):
        """
        Initialize renderer

        Args:
            width, height: Canvas dimensions
        """
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2

        self.surface = pygame.Surface((width, height))
        self.clock = pygame.time.Clock()

        # Visual settings
        self.color_scheme = "Pastel Dreams"
        self.boundary_style = "Solid"
        self.enable_glow = True
        self.enable_trails = True
        self.trail_length = 20
        self.collision_effect = "Sparkle"
        self.motion_blur = False
        self.background_color = (240, 240, 255)
        self.boundary_color = (200, 180, 220)
        self.boundary_radius = 250

        # Performance tracking
        self.fps = 0
        self.frame_time = 0

    def set_color_scheme(self, scheme_name):
        """Set the color scheme"""
        self.color_scheme = scheme_name
        scheme = get_color_scheme(scheme_name)
        self.background_color = scheme.get("background", (240, 240, 255))
        self.boundary_color = scheme.get("boundary", (200, 180, 220))

    def _get_particle_color(self, index, total):
        """Get a color for particle from the scheme"""
        scheme = get_color_scheme(self.color_scheme)
        colors = scheme.get("particles", [(200, 200, 200)])
        return colors[index % len(colors)]

    def _draw_boundary(self):
        """Draw the circular boundary"""
        x = int(self.center_x)
        y = int(self.center_y)
        r = int(self.boundary_radius)

        if self.boundary_style == "Solid":
            pygame.draw.circle(self.surface, self.boundary_color, (x, y), r, 3)

        elif self.boundary_style == "Dashed":
            # Draw dashed circle
            segments = 60
            for i in range(segments):
                if i % 2 == 0:  # Only draw every other segment
                    start_angle = (2 * math.pi / segments) * i
                    end_angle = (2 * math.pi / segments) * (i + 1)

                    x1 = x + r * math.cos(start_angle)
                    y1 = y + r * math.sin(start_angle)
                    x2 = x + r * math.cos(end_angle)
                    y2 = y + r * math.sin(end_angle)

                    pygame.draw.line(self.surface, self.boundary_color, (x1, y1), (x2, y2), 2)

        elif self.boundary_style == "Glow":
            # Draw glowing boundary
            for thickness in range(10, 0, -1):
                color = adjust_brightness(self.boundary_color, 1 - thickness / 10)
                pygame.draw.circle(self.surface, color, (x, y), r, 1)
                r -= 1

        elif self.boundary_style == "None":
            pass  # Don't draw boundary

    def _draw_trails(self, particles):
        """Draw motion trails for particles"""
        for i, particle in enumerate(particles):
            if len(particle.trail) > 2:
                color = self._get_particle_color(i, len(particles))

                # Draw trail with fade effect
                for j, (px, py) in enumerate(particle.trail[:-1]):
                    alpha = int(255 * (j / len(particle.trail)))

                    next_px, next_py = particle.trail[j + 1]

                    # Create temporary surface for alpha blending
                    temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    pygame.draw.line(
                        temp, (*color, alpha), (px, py), (next_px, next_py), 1
                    )
                    self.surface.blit(temp, (0, 0))

    def _draw_collision_effect(self, particle):
        """Draw collision effect around particle"""
        pulse = particle.get_collision_pulse()

        if pulse > 0:
            if self.collision_effect == "Ripple":
                # Draw expanding rings
                color = self._get_particle_color(
                    hash(id(particle)) % 100, 100
                )
                radius = int(particle.radius * (1 + pulse * 3))

                temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.circle(
                    temp, (*color, int(255 * (1 - pulse))),
                    (int(particle.x), int(particle.y)), radius, 2
                )
                self.surface.blit(temp, (0, 0))

            elif self.collision_effect == "Sparkle":
                # Draw sparkles around collision point
                import random
                random.seed(int(particle.birth_time * 1000))

                for _ in range(int(pulse * 5)):
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(particle.radius, particle.radius * 3)

                    spark_x = particle.x + dist * math.cos(angle)
                    spark_y = particle.y + dist * math.sin(angle)

                    color = self._get_particle_color(
                        hash(id(particle)) % 100, 100
                    )

                    temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    pygame.draw.circle(
                        temp, (*color, int(255 * pulse)),
                        (int(spark_x), int(spark_y)), 2
                    )
                    self.surface.blit(temp, (0, 0))

            elif self.collision_effect == "Burst":
                # Expanding burst
                color = self._get_particle_color(
                    hash(id(particle)) % 100, 100
                )

                for i in range(int(pulse * 10)):
                    angle = (2 * math.pi / 10) * i
                    length = particle.radius * (1 + pulse * 5)

                    end_x = particle.x + length * math.cos(angle)
                    end_y = particle.y + length * math.sin(angle)

                    temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    pygame.draw.line(
                        temp, (*color, int(255 * (1 - pulse))),
                        (int(particle.x), int(particle.y)),
                        (int(end_x), int(end_y)), 1
                    )
                    self.surface.blit(temp, (0, 0))

    def render(self, particles, boundary_radius):
        """
        Render the current frame

        Args:
            particles: List of Particle objects
            boundary_radius: Radius of the circular boundary

        Returns:
            pygame.Surface: Rendered frame
        """
        self.boundary_radius = boundary_radius

        # Clear with background color
        self.surface.fill(self.background_color)

        # Draw trails first (behind particles)
        if self.enable_trails:
            self._draw_trails(particles)

        # Draw particles
        for i, particle in enumerate(particles):
            color = self._get_particle_color(i, max(100, len(particles)))

            # Update particle color for rendering
            particle.color = color

            # Draw glow effect
            if self.enable_glow:
                glow_radius = particle.radius * 1.5
                draw_glow(self.surface, (particle.x, particle.y), glow_radius, color, 100)

            # Draw particle
            draw_shape(
                self.surface, particle.shape,
                (particle.x, particle.y),
                particle.radius,
                color,
                particle.alpha
            )

            # Draw collision effect
            self._draw_collision_effect(particle)

        # Draw boundary
        self._draw_boundary()

        return self.surface

    def update_fps(self, dt):
        """Update FPS counter"""
        if dt > 0:
            self.fps = 1.0 / dt
        self.frame_time = dt

    def get_fps(self):
        """Get current FPS"""
        return self.fps

    def draw_hud(self, surface, particle_count, fps):
        """
        Draw heads-up display with stats

        Args:
            surface: Surface to draw on
            particle_count: Number of active particles
            fps: Current frames per second
        """
        import pygame.font

        if not hasattr(self, 'font'):
            self.font = pygame.font.Font(None, 24)

        stats = [
            f"Particles: {particle_count}",
            f"FPS: {fps:.1f}",
        ]

        y_offset = 10
        for stat in stats:
            text_surface = self.font.render(stat, True, (50, 50, 50))
            surface.blit(text_surface, (10, y_offset))
            y_offset += 30

