"""Advanced 3D rendering engine with realistic 3D effects"""

import pygame
import math
import numpy as np
from src.utils.colors import get_color_scheme, adjust_brightness


class Renderer3D:
    """3D-inspired renderer using 2D graphics"""

    def __init__(self, width=800, height=600):
        """Initialize 3D renderer"""
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2

        # Defer surface creation until needed
        self._surface = None

        # Visual settings
        self.color_scheme = "Pastel Dreams"
        self.boundary_style = "glowing"
        self.enable_shadows = True
        self.enable_reflections = True
        self.enable_gloss = True

        # Lighting
        self.light_x = width * 0.3
        self.light_y = height * 0.3
        self.light_brightness = 0.8

        # Performance
        self.fps = 60
        self.frame_count = 0

    @property
    def surface(self):
        """Lazy-load pygame surface"""
        if self._surface is None:
            self._surface = pygame.Surface((self.width, self.height))
        return self._surface

    def set_color_scheme(self, scheme_name):
        """Set color scheme"""
        self.color_scheme = scheme_name

    def _get_object_color(self, index, total):
        """Get color for object from scheme"""
        scheme = get_color_scheme(self.color_scheme)
        colors = scheme.get("particles", [(200, 200, 200)])
        return colors[index % len(colors)]

    def _draw_3d_sphere(self, surface, pos, radius, color, shine=0.8):
        """Draw a 3D sphere with lighting and shine"""
        x, y = int(pos[0]), int(pos[1])
        r = int(radius)

        # Create temporary surface with alpha
        temp = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)

        # Draw shadow (3D effect)
        shadow_x = x - int(radius * 0.3)
        shadow_y = y + int(radius * 0.6)
        shadow_color = (0, 0, 0, 40)
        pygame.draw.ellipse(temp, shadow_color, (shadow_x - x + r + 5, shadow_y - y + r + 5, r * 1.5, r * 0.4))

        # Draw main sphere with gradient (3D effect)
        # Darker base
        for i in range(r, 0, -1):
            alpha = int(255 * (1 - (i / r) ** 0.5))
            layer_color = (*color, alpha)
            pygame.draw.circle(temp, layer_color, (r + 5, r + 5), i)

        # Add highlight for shine
        if shine > 0:
            highlight_color = (255, 255, 255, int(150 * shine))
            highlight_x = r + 5 - int(r * 0.3)
            highlight_y = r + 5 - int(r * 0.3)
            pygame.draw.circle(temp, highlight_color, (highlight_x, highlight_y), int(r * 0.3))

        # Blit to surface
        surface.blit(temp, (x - r - 5, y - r - 5))

    def _draw_3d_cube(self, surface, pos, radius, color, rotation=0, shine=0.8):
        """Draw a 3D cube with rotation"""
        x, y = int(pos[0]), int(pos[1])
        r = int(radius)

        # Cube vertices (simplified 3D projection)
        vertices = []
        for vx in [-1, 1]:
            for vy in [-1, 1]:
                for vz in [-1, 1]:
                    # Apply rotation
                    rx = vx * math.cos(rotation) - vz * math.sin(rotation)
                    rz = vx * math.sin(rotation) + vz * math.cos(rotation)

                    # Project to 2D
                    px = x + rx * r
                    py = y + vy * r + rz * r * 0.3  # Perspective

                    vertices.append((px, py))

        # Draw cube faces
        temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Front face
        face_color = (*color, int(200 * shine))
        front_face = [vertices[0], vertices[1], vertices[3], vertices[2]]
        pygame.draw.polygon(temp, face_color, front_face)

        # Side faces with different brightness
        side_color = (*adjust_brightness(color, 0.7), int(180 * shine))
        pygame.draw.polygon(temp, side_color, [vertices[1], vertices[5], vertices[7], vertices[3]])

        surface.blit(temp, (0, 0))

    def _draw_3d_star(self, surface, pos, radius, color, rotation=0, shine=0.8):
        """Draw a 3D star"""
        x, y = int(pos[0]), int(pos[1])
        r = radius

        points = []
        for i in range(10):
            angle = rotation + (2 * math.pi * i / 10)
            dist = r if i % 2 == 0 else r / 2
            px = x + dist * math.cos(angle)
            py = y + dist * math.sin(angle)
            points.append((px, py))

        # Draw star with gradient
        temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        star_color = (*color, int(230 * shine))
        pygame.draw.polygon(temp, star_color, points)

        # Add inner glow
        glow_color = (*adjust_brightness(color, 1.3), int(100 * shine))
        for i in range(int(r * 0.3), 0, -1):
            alpha = int(glow_color[3] * (i / (r * 0.3)))
            pygame.draw.circle(temp, (*glow_color[:3], alpha), (x, y), i)

        surface.blit(temp, (0, 0))

    def _draw_3d_triangle(self, surface, pos, radius, color, rotation=0, shine=0.8):
        """Draw a 3D triangle"""
        x, y = int(pos[0]), int(pos[1])
        r = radius

        points = []
        for i in range(3):
            angle = rotation + (2 * math.pi * i / 3)
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            points.append((px, py))

        # Draw triangle
        temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        tri_color = (*color, int(220 * shine))
        pygame.draw.polygon(temp, tri_color, points)

        # Add shadow under triangle
        shadow_color = (0, 0, 0, 50)
        shadow_points = [
            (points[0][0], points[0][1] + r * 0.2),
            (points[1][0], points[1][1] + r * 0.2),
            (points[2][0], points[2][1] + r * 0.2)
        ]
        pygame.draw.polygon(temp, shadow_color, shadow_points)

        surface.blit(temp, (0, 0))

    def _draw_glowing_boundary(self, boundary_radius, boundary_type="circle"):
        """Draw glowing boundary"""
        x, y = int(self.center_x), int(self.center_y)

        # Create glow effect
        glow_color = (100, 150, 200)

        if boundary_type == "circle":
            # Draw multiple circles for glow
            for i in range(int(boundary_radius * 1.1), int(boundary_radius), -2):
                alpha = int(100 * (1 - (i - boundary_radius) / (boundary_radius * 0.1)))
                temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.circle(temp, (*glow_color, alpha), (x, y), i, 1)
                self.surface.blit(temp, (0, 0))

            # Draw main boundary
            pygame.draw.circle(self.surface, glow_color, (x, y), int(boundary_radius), 3)

        elif boundary_type == "square":
            half_size = boundary_radius
            rect = pygame.Rect(
                x - half_size, y - half_size,
                half_size * 2, half_size * 2
            )

            # Glow effect
            for i in range(10, 0, -1):
                alpha = int(100 * (i / 10))
                temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                expanded_rect = rect.inflate(i * 2, i * 2)
                pygame.draw.rect(temp, (*glow_color, alpha), expanded_rect, 1)
                self.surface.blit(temp, (0, 0))

            pygame.draw.rect(self.surface, glow_color, rect, 3)

        elif boundary_type == "triangle":
            # Draw triangle boundary
            points = []
            for i in range(3):
                angle = i * (2 * math.pi / 3) - math.pi / 2
                px = x + boundary_radius * math.cos(angle)
                py = y + boundary_radius * math.sin(angle)
                points.append((px, py))

            pygame.draw.polygon(self.surface, glow_color, points, 3)

    def render(self, objects, boundary_radius, boundary_type="circle"):
        """Render the scene"""
        # Get background color from scheme
        scheme = get_color_scheme(self.color_scheme)
        bg_color = scheme.get("background", (20, 20, 20))

        # Clear with background
        self.surface.fill(bg_color)

        # Draw glowing boundary
        self._draw_glowing_boundary(boundary_radius, boundary_type)

        # Draw objects
        for i, obj in enumerate(objects):
            color = self._get_object_color(i, len(objects) if objects else 1)

            # Get visual properties
            shine = obj.shine_intensity + obj.get_collision_intensity() * 0.3

            # Draw based on shape
            if obj.shape == "sphere":
                self._draw_3d_sphere(self.surface, (obj.x, obj.y), obj.radius, color, shine)
            elif obj.shape == "cube":
                self._draw_3d_cube(self.surface, (obj.x, obj.y), obj.radius, color, obj.rotation, shine)
            elif obj.shape == "star":
                self._draw_3d_star(self.surface, (obj.x, obj.y), obj.radius, color, obj.rotation, shine)
            elif obj.shape == "triangle":
                self._draw_3d_triangle(self.surface, (obj.x, obj.y), obj.radius, color, obj.rotation, shine)
            else:
                # Default to sphere
                self._draw_3d_sphere(self.surface, (obj.x, obj.y), obj.radius, color, shine)

            # Draw velocity trail for 3D effect
            if len(obj.trail) > 1:
                for j in range(len(obj.trail) - 1):
                    p1 = obj.trail[j]
                    p2 = obj.trail[j + 1]
                    alpha = int(50 * p2[2])  # Use shine intensity from trail

                    temp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    trail_color = (*color, alpha)
                    pygame.draw.line(temp, trail_color, (p1[0], p1[1]), (p2[0], p2[1]), 1)
                    self.surface.blit(temp, (0, 0))

        return self.surface

    def draw_hud(self, surface, object_count, fps, time_elapsed, max_objects):
        """Draw heads-up display"""
        import pygame.font

        if not hasattr(self, 'font_small'):
            self.font_small = pygame.font.Font(None, 24)
            self.font_large = pygame.font.Font(None, 36)

        # Stats
        stats = [
            f"Objects: {object_count}/{max_objects}",
            f"FPS: {fps:.1f}",
            f"Time: {time_elapsed:.1f}s",
        ]

        y_offset = 10
        for stat in stats:
            text_surface = self.font_small.render(stat, True, (200, 200, 200))
            surface.blit(text_surface, (10, y_offset))
            y_offset += 30

