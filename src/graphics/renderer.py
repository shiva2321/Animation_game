"""
Advanced renderer with quality modes, GPU acceleration, and particle shape rendering.
"""
import pygame
import numpy as np
from typing import List, Tuple
import math
import logging

from src.physics.particle import Particle
from src.graphics.palette import ColorPalette
from src.graphics.effects import EffectsManager
from src.graphics.shading_3d import apply_3d_shading, create_sphere_surface, create_bubble_surface
from src.graphics.gpu_utils import GPURenderer, optimize_surface_for_gpu
from src.core.settings import AppSettings

logger = logging.getLogger(__name__)

class AdvancedRenderer:
    """High-quality renderer with GPU acceleration and multiple quality modes."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.width, self.height = settings.resolution

        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()

        # Initialize display module (but don't create a display window)
        if not pygame.display.get_init():
            pygame.display.init()

        # Try GPU acceleration
        self.gpu_renderer = None
        try:
            self.gpu_renderer = GPURenderer(self.width, self.height)
            if self.gpu_renderer.gpu_available:
                logger.info("GPU acceleration ENABLED")
                self.surface = self.gpu_renderer.surface
            else:
                raise Exception("GPU not available")
        except Exception as e:
            logger.info(f"Using software rendering: {e}")
            # Create surface (this is just a memory surface, not a window)
            try:
                self.surface = pygame.Surface((self.width, self.height))
            except Exception as e2:
                # Fallback to a smaller size if needed
                self.width, self.height = 1280, 720
                self.surface = pygame.Surface((self.width, self.height))
                logger.warning(f"Fallback to {self.width}x{self.height}")

        # Create subsurface for supersampling if needed
        self.use_supersampling = (settings.quality == "export_high")
        if self.use_supersampling:
            self.supersample_surface = pygame.Surface((self.width * 2, self.height * 2))
        else:
            self.supersample_surface = None

        # Palette
        self.palette = ColorPalette(settings.visual_scheme)

        # Effects
        self.effects = EffectsManager()

        # Cache for background
        self._background_cache = None
        self._render_background()

        # Boundary
        self.center = np.array([self.width / 2, self.height / 2])
        self.boundary_radius = min(self.width, self.height) * settings.boundary_radius_ratio

    def _render_background(self):
        """Pre-render background gradient."""
        try:
            gradient = self.palette.get_background_gradient(self.width, self.height)
            # Use pygame.surfarray with proper error handling
            self._background_cache = pygame.surfarray.make_surface(
                gradient.transpose(1, 0, 2)
            )
        except Exception as e:
            # Fallback to a simple solid color background
            self._background_cache = pygame.Surface((self.width, self.height))
            self._background_cache.fill((10, 10, 30))  # Dark blue

    def render_frame(self, particles: List[Particle]) -> pygame.Surface:
        """
        Render a complete frame.

        Args:
            particles: List of particles to render

        Returns:
            Rendered pygame Surface
        """
        # Choose target surface
        if self.use_supersampling:
            target = self.supersample_surface
            scale = 2
        else:
            target = self.surface
            scale = 1

        # Draw background
        if scale == 1:
            target.blit(self._background_cache, (0, 0))
        else:
            # Scale up background
            pygame.transform.scale(self._background_cache, (self.width * 2, self.height * 2), target)

        # Draw boundary
        self._draw_boundary(target, scale)

        # Draw particle trails (if enabled)
        if self.settings.trails_enabled:
            self._draw_trails(target, particles, scale)

        # Draw particles
        for particle in particles:
            if particle.alive:
                self._draw_particle(target, particle, scale)

        # Draw effects
        if scale == 1:
            self.effects.draw(target)
        else:
            # Effects don't scale well, draw on final surface
            pass

        # Downsample if supersampling
        if self.use_supersampling:
            pygame.transform.smoothscale(target, (self.width, self.height), self.surface)
            # Draw effects on final surface
            self.effects.draw(self.surface)
            return self.surface

        return target

    def _draw_boundary(self, surface: pygame.Surface, scale: int = 1):
        """Draw boundary circle."""
        center = (int(self.center[0] * scale), int(self.center[1] * scale))
        radius = int(self.boundary_radius * scale)
        color = self.palette.get_boundary_color()

        if self.settings.boundary_style == "solid":
            pygame.draw.circle(surface, color, center, radius, 2 * scale)

        elif self.settings.boundary_style == "glow" or self.settings.boundary_glow:
            # Multiple layers for glow effect
            layers = 5 if self.settings.quality == "export_high" else 3
            for i in range(layers):
                alpha = int(50 * (1 - i / layers))
                width = scale * (1 + i)
                glow_color = (*color, alpha)

                # Can't draw with alpha directly, so approximate with darker color
                approx_color = tuple(int(c * alpha / 255) for c in color)
                pygame.draw.circle(surface, approx_color, center, radius + i * scale, width)

        elif self.settings.boundary_style == "pulse":
            # Pulsing effect (would need time parameter, using simple version)
            pygame.draw.circle(surface, color, center, radius, 2 * scale)

    def _draw_trails(self, surface: pygame.Surface, particles: List[Particle], scale: int = 1):
        """Draw smooth, appealing particle trails with proper gradients."""
        if not self.settings.trails_enabled:
            return

        max_trail_length = self.settings.trail_length

        for particle in particles:
            if not particle.alive or len(particle.trail) < 2:
                continue

            trail_points = list(particle.trail)[-max_trail_length:]

            if len(trail_points) < 2:
                continue

            # Draw trail as smooth gradient with proper alpha
            num_points = len(trail_points)

            for i in range(num_points - 1):
                # Age factor (0 = oldest, 1 = newest)
                age_factor = i / num_points

                # Smooth alpha fade
                alpha = int(200 * (age_factor ** 0.7))  # Non-linear for better appearance

                if alpha < 10:
                    continue

                # Width tapers toward older end
                width = max(1, int(particle.radius * scale * age_factor * 0.6))

                # Color with alpha
                # Make trail slightly brighter than particle
                trail_color = tuple(min(255, int(c * 1.1)) for c in particle.color)

                # Get points
                p1 = (int(trail_points[i][0] * scale), int(trail_points[i][1] * scale))
                p2 = (int(trail_points[i+1][0] * scale), int(trail_points[i+1][1] * scale))

                # Draw smooth line segment
                try:
                    # Create temporary surface for alpha blending
                    temp_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)

                    # Draw line with width
                    if width > 1:
                        # Draw thick line with circles at endpoints for smooth caps
                        pygame.draw.line(temp_surface, (*trail_color, alpha), p1, p2, width)
                        pygame.draw.circle(temp_surface, (*trail_color, alpha), p1, width // 2)
                        pygame.draw.circle(temp_surface, (*trail_color, alpha), p2, width // 2)
                    else:
                        pygame.draw.line(temp_surface, (*trail_color, alpha), p1, p2, 1)

                    # Blit with alpha
                    surface.blit(temp_surface, (0, 0))

                except Exception as e:
                    # Fallback to simple line
                    try:
                        color_without_alpha = tuple(int(c * alpha / 255) for c in trail_color)
                        pygame.draw.line(surface, color_without_alpha, p1, p2, max(1, width))
                    except:
                        pass

    def _draw_particle(self, surface: pygame.Surface, particle: Particle, scale: int = 1):
        """Draw a single particle with 3D effects."""
        pos = (int(particle.position[0] * scale), int(particle.position[1] * scale))
        radius = particle.radius * scale

        # Use 3D rendering if enabled
        if self.settings.enable_3d_effect:
            if particle.shape in ["circle", "sphere"]:
                # Draw as 3D sphere
                apply_3d_shading(
                    surface,
                    particle.color,
                    pos,
                    radius,
                    self.settings.light_direction,
                    self.settings.ambient_light
                )
                return
            elif particle.shape == "bubble":
                # Draw as bubble
                bubble_surf = create_bubble_surface(
                    int(radius),
                    particle.color,
                    self.settings.light_direction
                )
                top_left = (pos[0] - int(radius), pos[1] - int(radius))
                surface.blit(bubble_surf, top_left)
                return

        # Draw glow layers (if enabled)
        if self.settings.glow_enabled:
            glow_layers = 3 if self.settings.quality == "export_high" else 2
            glow_intensity = particle.glow_intensity * self.settings.glow_intensity

            for i in range(glow_layers):
                glow_radius = radius * (1 + i * 0.5)
                alpha = int(80 * glow_intensity * (1 - i / glow_layers))

                # Approximate glow
                glow_color = tuple(int(c * alpha / 255) for c in particle.color)

                try:
                    pygame.draw.circle(surface, glow_color, pos, int(glow_radius))
                except:
                    pass

        # Draw particle shape
        self._draw_shape(
            surface,
            particle.shape,
            pos,
            radius,
            particle.color,
            particle.angle,
            particle.scale_x,
            particle.scale_y,
            scale
        )

    def _draw_shape(
        self,
        surface: pygame.Surface,
        shape: str,
        pos: Tuple[int, int],
        radius: float,
        color: Tuple[int, int, int],
        angle: float,
        scale_x: float,
        scale_y: float,
        render_scale: int = 1
    ):
        """Draw a particle shape with 3D appearance, rotation and deformation."""
        # Sphere is same as circle but with 3D shading (handled in _draw_particle)
        if shape in ["circle", "sphere"]:
            # Ellipse for deformed circle
            rect = pygame.Rect(
                pos[0] - radius * scale_x,
                pos[1] - radius * scale_y,
                radius * 2 * scale_x,
                radius * 2 * scale_y
            )
            try:
                pygame.draw.ellipse(surface, color, rect)
            except:
                pass

        elif shape == "rounded_star":
            # Star with rounded tips and 3D shading
            points = self._get_rounded_star_points(pos, radius, angle, scale_x, scale_y, 5)
            try:
                # Draw with gradient for 3D effect
                if self.settings.enable_3d_effect:
                    # Draw darker base
                    dark_color = tuple(int(c * 0.6) for c in color)
                    pygame.draw.polygon(surface, dark_color, points)
                    # Draw lighter top offset
                    offset_points = [(p[0] - 1, p[1] - 1) for p in points]
                    pygame.draw.polygon(surface, color, offset_points)
                else:
                    pygame.draw.polygon(surface, color, points)

                # Add smoothing circles at tips with gradient
                for idx, point in enumerate(points[::2]):  # Every other point (the tips)
                    tip_color = tuple(min(255, int(c * 1.2)) for c in color) if self.settings.enable_3d_effect else color
                    pygame.draw.circle(surface, tip_color, (int(point[0]), int(point[1])), int(radius * 0.15))
            except:
                pass

        elif shape == "square":
            points = self._get_square_points(pos, radius, angle, scale_x, scale_y)
            try:
                if self.settings.enable_3d_effect:
                    # 3D cube effect
                    # Shadow
                    shadow_color = tuple(int(c * 0.5) for c in color)
                    shadow_points = [(p[0] + 2, p[1] + 2) for p in points]
                    pygame.draw.polygon(surface, shadow_color, shadow_points)
                    # Main face
                    pygame.draw.polygon(surface, color, points)
                    # Highlight edge
                    highlight_color = tuple(min(255, int(c * 1.3)) for c in color)
                    pygame.draw.line(surface, highlight_color, points[0], points[1], 2)
                else:
                    pygame.draw.polygon(surface, color, points)
            except:
                pass

        elif shape == "triangle":
            points = self._get_triangle_points(pos, radius, angle, scale_x, scale_y)
            try:
                if self.settings.enable_3d_effect:
                    # Pyramid effect
                    dark_color = tuple(int(c * 0.6) for c in color)
                    pygame.draw.polygon(surface, dark_color, points)
                    # Lighter top face
                    offset_points = [(p[0] - 1, p[1] - 1) for p in points]
                    pygame.draw.polygon(surface, color, offset_points)
                    # Bright edge
                    highlight_color = tuple(min(255, int(c * 1.4)) for c in color)
                    pygame.draw.line(surface, highlight_color, points[0], points[1], 2)
                else:
                    pygame.draw.polygon(surface, color, points)
            except:
                pass

        elif shape == "star":
            points = self._get_star_points(pos, radius, angle, scale_x, scale_y, 5)
            try:
                if self.settings.enable_3d_effect:
                    # Draw with depth
                    for i in range(2, -1, -1):
                        shade = 0.5 + i * 0.25
                        shaded_color = tuple(int(c * shade) for c in color)
                        offset_points = [(p[0] - i, p[1] - i) for p in points]
                        pygame.draw.polygon(surface, shaded_color, offset_points)
                else:
                    pygame.draw.polygon(surface, color, points)
            except:
                pass

        elif shape == "hexagon":
            points = self._get_polygon_points(pos, radius, angle, scale_x, scale_y, 6)
            try:
                if self.settings.enable_3d_effect:
                    # Hex crystal effect
                    dark_color = tuple(int(c * 0.6) for c in color)
                    pygame.draw.polygon(surface, dark_color, points)
                    # Facets with different shading
                    center_points = [(p[0] * 0.7 + pos[0] * 0.3, p[1] * 0.7 + pos[1] * 0.3) for p in points]
                    pygame.draw.polygon(surface, color, center_points)
                    # Highlight edges
                    highlight_color = tuple(min(255, int(c * 1.3)) for c in color)
                    for i in range(len(points)):
                        pygame.draw.line(surface, highlight_color, points[i], points[(i+1)%len(points)], 1)
                else:
                    pygame.draw.polygon(surface, color, points)
            except:
                pass

        elif shape == "heart":
            points = self._get_heart_points(pos, radius, angle, scale_x, scale_y)
            try:
                if self.settings.enable_3d_effect:
                    # Glossy heart effect
                    dark_color = tuple(int(c * 0.7) for c in color)
                    pygame.draw.polygon(surface, dark_color, points)
                    # Highlight
                    highlight_offset = int(radius * 0.3)
                    highlight_pos = (pos[0] - highlight_offset, pos[1] - highlight_offset)
                    highlight_color = tuple(min(255, int(c * 1.5)) for c in color)
                    pygame.draw.circle(surface, highlight_color, highlight_pos, int(radius * 0.2))
                else:
                    pygame.draw.polygon(surface, color, points)
            except:
                pass

        else:  # Default to circle
            try:
                pygame.draw.circle(surface, color, pos, int(radius))
            except:
                pass

    def _get_square_points(
        self,
        center: Tuple[int, int],
        radius: float,
        angle: float,
        scale_x: float,
        scale_y: float
    ) -> List[Tuple[int, int]]:
        """Get square corner points."""
        points = [
            (-radius * scale_x, -radius * scale_y),
            (radius * scale_x, -radius * scale_y),
            (radius * scale_x, radius * scale_y),
            (-radius * scale_x, radius * scale_y)
        ]
        return self._rotate_points(points, center, angle)

    def _get_triangle_points(
        self,
        center: Tuple[int, int],
        radius: float,
        angle: float,
        scale_x: float,
        scale_y: float
    ) -> List[Tuple[int, int]]:
        """Get triangle corner points."""
        h = radius * 1.5
        points = [
            (0, -h * scale_y),
            (radius * scale_x, h * 0.5 * scale_y),
            (-radius * scale_x, h * 0.5 * scale_y)
        ]
        return self._rotate_points(points, center, angle)

    def _get_polygon_points(
        self,
        center: Tuple[int, int],
        radius: float,
        angle: float,
        scale_x: float,
        scale_y: float,
        sides: int
    ) -> List[Tuple[int, int]]:
        """Get regular polygon points."""
        points = []
        for i in range(sides):
            a = 2 * math.pi * i / sides
            x = radius * math.cos(a) * scale_x
            y = radius * math.sin(a) * scale_y
            points.append((x, y))
        return self._rotate_points(points, center, angle)

    def _get_star_points(
        self,
        center: Tuple[int, int],
        radius: float,
        angle: float,
        scale_x: float,
        scale_y: float,
        points_count: int
    ) -> List[Tuple[int, int]]:
        """Get star points."""
        points = []
        inner_radius = radius * 0.5
        for i in range(points_count * 2):
            a = math.pi * i / points_count
            r = radius if i % 2 == 0 else inner_radius
            x = r * math.cos(a) * scale_x
            y = r * math.sin(a) * scale_y
            points.append((x, y))
        return self._rotate_points(points, center, angle)

    def _get_rounded_star_points(
        self,
        center: Tuple[int, int],
        radius: float,
        angle: float,
        scale_x: float,
        scale_y: float,
        points_count: int
    ) -> List[Tuple[int, int]]:
        """Get rounded star points (like a star with curved edges)."""
        points = []
        inner_radius = radius * 0.6  # Less pronounced for rounded look
        for i in range(points_count * 2):
            a = math.pi * i / points_count
            r = radius if i % 2 == 0 else inner_radius
            x = r * math.cos(a) * scale_x
            y = r * math.sin(a) * scale_y
            points.append((x, y))
        return self._rotate_points(points, center, angle)

    def _get_heart_points(
        self,
        center: Tuple[int, int],
        radius: float,
        angle: float,
        scale_x: float,
        scale_y: float
    ) -> List[Tuple[int, int]]:
        """Get heart shape points."""
        points = []
        for t in np.linspace(0, 2 * math.pi, 20):
            x = radius * 16 * math.sin(t)**3 / 16
            y = -radius * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) / 16
            points.append((x * scale_x, y * scale_y))
        return self._rotate_points(points, center, angle)

    def _rotate_points(
        self,
        points: List[Tuple[float, float]],
        center: Tuple[int, int],
        angle: float
    ) -> List[Tuple[int, int]]:
        """Rotate points around center."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        rotated = []
        for x, y in points:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            rotated.append((int(center[0] + rx), int(center[1] + ry)))

        return rotated

    def update_effects(self, dt: float):
        """Update visual effects."""
        self.effects.update(dt)

    def add_collision_effect(
        self,
        position: np.ndarray,
        normal: np.ndarray,
        color: Tuple[int, int, int],
        energy: float
    ):
        """Add collision visual effect."""
        intensity = self.settings.collision_fx_intensity

        if self.settings.collision_fx_style in ["ripple", "both"]:
            self.effects.add_ripple(position, color, energy, intensity)

        if self.settings.collision_fx_style in ["sparkle", "both"]:
            self.effects.add_sparkles(position, normal, color, energy, intensity)

    def add_boundary_effect(
        self,
        position: np.ndarray,
        color: Tuple[int, int, int],
        energy: float
    ):
        """Add boundary hit effect."""
        intensity = self.settings.collision_fx_intensity * 0.7

        if self.settings.collision_fx_style != "none":
            self.effects.add_ripple(position, color, energy * 0.5, intensity)

    def clear_effects(self):
        """Clear all effects."""
        self.effects.clear()

    def get_frame_array(self) -> np.ndarray:
        """Get current frame as NumPy array (for video export)."""
        # Get pixel array
        array = pygame.surfarray.array3d(self.surface)
        # Transpose from (width, height, 3) to (height, width, 3)
        return array.transpose(1, 0, 2)

