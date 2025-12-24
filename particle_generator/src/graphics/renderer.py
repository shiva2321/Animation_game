
import pygame
import numpy as np
from typing import List

from ..core.settings import Settings
from ..core.events import BaseEvent, CollisionEvent
from ..physics.system import ParticleSystem
from ..physics.particle import Particle
from .palette import Palette, hsl_to_rgb

# Helper for temporary visual effects
class VFX:
    def __init__(self, position, lifetime, style, **kwargs):
        self.position = np.array(position, dtype=float)
        self.lifetime = lifetime
        self.age = 0
        self.style = style
        self.initial_radius = kwargs.get('radius', 5)
        self.max_radius = kwargs.get('max_radius', 50)
        self.color = kwargs.get('color', (255, 255, 255))

    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime

class Renderer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.width, self.height = settings.simulation.resolution
        self.palette = Palette(settings.visuals.scheme_name)

        self.vfx_list: List[VFX] = []
        self._precompute_shapes()

        # Cache for gradient background to avoid re-rendering
        self._bg_surface = None
        self._cached_bg_scheme = None

    def _precompute_shapes(self):
        """Precomputes polygon points for complex shapes."""
        self.shapes = {
            "star": self._create_star_points(),
            "hexagon": self._create_polygon_points(6),
            "triangle": self._create_polygon_points(3),
            "heart": self._create_heart_points()
        }

    def _create_polygon_points(self, sides, radius=1.0):
        return [
            (np.cos(2 * np.pi * i / sides), np.sin(2 * np.pi * i / sides)) * radius
            for i in range(sides)
        ]

    def _create_star_points(self, outer_radius=1.0, inner_radius=0.5, points=5):
        star_points = []
        for i in range(points * 2):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = i * np.pi / points
            star_points.append((np.sin(angle) * radius, -np.cos(angle) * radius))
        return star_points

    def _create_heart_points(self, scale=1.0):
        points = []
        for t in np.linspace(0, 2 * np.pi, 20):
            x = 16 * np.sin(t)**3
            y = -(13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t))
            points.append((x * scale * 0.06, y * scale * 0.06))
        return points

    def _draw_background(self, surface):
        if self.settings.visuals.scheme_name != self._cached_bg_scheme:
            self._bg_surface = None # Invalidate cache if scheme changes

        if self._bg_surface is None:
            self._cached_bg_scheme = self.settings.visuals.scheme_name
            self.palette.set_scheme(self.settings.visuals.scheme_name)
            self._bg_surface = pygame.Surface((self.width, self.height))

            # Simple two-color vertical gradient for performance
            c1 = self.palette.bg_color1_rgb
            c2 = self.palette.bg_color2_rgb
            for y in range(self.height):
                interp = y / self.height
                color = (
                    c1[0] + (c2[0] - c1[0]) * interp,
                    c1[1] + (c2[1] - c1[1]) * interp,
                    c1[2] + (c2[2] - c1[2]) * interp,
                )
                pygame.draw.line(self._bg_surface, color, (0, y), (self.width, y))

        surface.blit(self._bg_surface, (0, 0))

    def _draw_boundary(self, surface):
        style = self.settings.visuals.boundary_style
        if style == "none":
            return

        center = (self.width // 2, self.height // 2)
        radius = int((min(self.width, self.height) / 2.0) * self.settings.physics.boundary_radius_ratio)

        if style == "glow":
            num_layers = 3 if self.settings.simulation.quality == 'preview_low' else 8
            for i in range(num_layers, 0, -1):
                alpha = 10 - (i / num_layers * 5)
                color = (*self.palette.bg_color1_rgb, alpha)
                pygame.draw.circle(surface, color, center, radius + i * 2, width=2)

    def _draw_particle_shape(self, surface, particle: Particle):
        color_rgb = self.palette.get_particle_color(*particle.color, self.settings.visuals.palette_lock)

        if particle.shape == "circle":
            pygame.draw.circle(surface, color_rgb, particle.position, particle.radius)
        elif particle.shape == "square":
            size = particle.radius * 1.6 # approx
            points = [(-size, -size), (size, -size), (size, size), (-size, size)]
            angle_rad = np.deg2rad(particle.angle)
            cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
            rotated = [(x*cos_a - y*sin_a, x*sin_a + y*cos_a) for x, y in points]
            scaled = [(x * particle.scale[0], y * particle.scale[1]) for x, y in rotated]
            final_points = [(x + particle.position[0], y + particle.position[1]) for x, y in scaled]
            pygame.draw.polygon(surface, color_rgb, final_points)
        else: # Generic polygon shapes
            base_points = self.shapes.get(particle.shape, [])
            angle_rad = np.deg2rad(particle.angle)
            cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

            final_points = []
            for x, y in base_points:
                x_rot = x * cos_a - y * sin_a
                y_rot = x * sin_a + y * cos_a
                x_scaled = x_rot * particle.radius * 1.5 * particle.scale[0]
                y_scaled = y_rot * particle.radius * 1.5 * particle.scale[1]
                final_points.append((x_scaled + particle.position[0], y_scaled + particle.position[1]))

            if final_points:
                pygame.draw.polygon(surface, color_rgb, final_points)

    def _draw_particle(self, surface, p: Particle):
        # Draw Trail
        if self.settings.visuals.trails_toggle and len(p.trail) > 1:
            color_rgb = self.palette.get_particle_color(*p.color, self.settings.visuals.palette_lock)
            for i in range(len(p.trail) - 1):
                alpha = 150 * (i / len(p.trail))
                trail_color = (*color_rgb, alpha)
                start_pos = tuple(p.trail[i])
                end_pos = tuple(p.trail[i+1])
                pygame.draw.line(surface, trail_color, start_pos, end_pos, width=int(p.radius * 0.5))

        # Draw Glow
        if self.settings.visuals.glow_toggle:
            num_layers = 2 if self.settings.simulation.quality == 'preview_low' else 5
            base_glow = p.glow_intensity * self.settings.visuals.glow_intensity
            if base_glow > 0.05:
                glow_color = self.palette.get_particle_color(*p.color, self.settings.visuals.palette_lock)
                for i in range(num_layers, 0, -1):
                    alpha = int(base_glow * 50 * (1 - i / num_layers))
                    glow_surf = pygame.Surface((p.radius*4, p.radius*4), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*glow_color, alpha), (p.radius*2, p.radius*2), p.radius * (1 + i * 0.3))
                    surface.blit(glow_surf, (p.position[0] - p.radius*2, p.position[1] - p.radius*2), special_flags=pygame.BLEND_RGBA_ADD)

        # Draw main shape
        self._draw_particle_shape(surface, p)

    def _process_events(self, events: List[BaseEvent]):
        for event in events:
            if isinstance(event, CollisionEvent):
                if self.settings.visuals.collision_effect_style == 'ripple':
                    vfx = VFX(event.position, lifetime=0.5, style='ripple',
                              color=(200, 200, 255), max_radius=event.relative_speed * 0.2)
                    self.vfx_list.append(vfx)

    def _draw_vfx(self, surface, dt):
        self.vfx_list = [vfx for vfx in self.vfx_list if vfx.update(dt)]
        for vfx in self.vfx_list:
            if vfx.style == 'ripple':
                progress = vfx.age / vfx.lifetime
                current_radius = int(vfx.initial_radius + progress * vfx.max_radius)
                alpha = int(200 * (1 - progress))
                if alpha > 0:
                    # Create a separate surface for alpha blending
                    ripple_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(ripple_surface, (*vfx.color, alpha),
                                       (current_radius, current_radius), current_radius, width=max(1, int(4 * (1-progress))))
                    surface.blit(ripple_surface, (vfx.position[0] - current_radius, vfx.position[1] - current_radius))

    def draw(self, surface: pygame.Surface, system: ParticleSystem, events: List[BaseEvent], dt: float):
        self._draw_background(surface)
        self._draw_boundary(surface)

        self._process_events(events)
        self._draw_vfx(surface, dt)

        for p in sorted(system.particles, key=lambda prt: prt.position[1]):
            self._draw_particle(surface, p)
