"""
3D shading utilities for making 2D particles look 3D.
"""
import numpy as np
from typing import Tuple
import pygame


def apply_3d_shading(
    surface: pygame.Surface,
    color: Tuple[int, int, int],
    center: Tuple[int, int],
    radius: float,
    light_angle: float = 45.0,
    ambient: float = 0.3
) -> pygame.Surface:
    """
    Apply realistic 3D sphere shading with proper gradients and highlights.

    Creates a truly 3D-looking sphere with:
    - Smooth gradient from highlight to shadow
    - Specular highlight for glossy appearance
    - Ambient occlusion at edges
    - Proper light falloff
    """
    if radius < 2:
        pygame.draw.circle(surface, color, center, int(radius))
        return surface

    # Convert light angle to radians
    light_rad = np.radians(light_angle)
    light_x = np.cos(light_rad)
    light_y = np.sin(light_rad)

    # Draw pixel by pixel for perfect sphere shading
    int_radius = int(radius)
    radius_sq = radius * radius

    # Create temporary surface for anti-aliasing
    temp_size = int_radius * 2 + 4
    temp_surf = pygame.Surface((temp_size, temp_size), pygame.SRCALPHA)
    local_center = (temp_size // 2, temp_size // 2)

    # Draw sphere with proper 3D shading
    for y in range(-int_radius - 1, int_radius + 2):
        for x in range(-int_radius - 1, int_radius + 2):
            # Distance from center
            dist_sq = x*x + y*y

            if dist_sq <= radius_sq:
                # Point is inside sphere
                dist = np.sqrt(dist_sq)

                # Calculate surface normal (pointing outward)
                if dist < 0.01:
                    normal_z = 1.0
                else:
                    # Height on sphere surface
                    height_sq = radius_sq - dist_sq
                    if height_sq > 0:
                        normal_z = np.sqrt(height_sq) / radius
                    else:
                        normal_z = 0.0

                normal_x = x / radius if radius > 0 else 0
                normal_y = y / radius if radius > 0 else 0

                # Normalize normal vector
                normal_len = np.sqrt(normal_x*normal_x + normal_y*normal_y + normal_z*normal_z)
                if normal_len > 0:
                    normal_x /= normal_len
                    normal_y /= normal_len
                    normal_z /= normal_len

                # Light direction (pointing toward light)
                light_z = 0.7  # Light coming from above

                # Diffuse lighting (Lambertian)
                diffuse = max(0, normal_x * light_x + normal_y * light_y + normal_z * light_z)

                # Specular highlight (Blinn-Phong)
                view_z = 1.0  # Viewer looking straight at sphere
                half_x = light_x
                half_y = light_y
                half_z = light_z + view_z
                half_len = np.sqrt(half_x*half_x + half_y*half_y + half_z*half_z)
                if half_len > 0:
                    half_x /= half_len
                    half_y /= half_len
                    half_z /= half_len

                specular = max(0, normal_x * half_x + normal_y * half_y + normal_z * half_z)
                specular = specular ** 32  # Shininess

                # Ambient occlusion (darker at edges)
                edge_factor = 1.0 - (dist / radius) ** 2
                edge_factor = max(0, edge_factor)

                # Combine lighting
                lighting = ambient + (1 - ambient) * diffuse * edge_factor + specular * 0.5
                lighting = max(0, min(1.5, lighting))  # Allow overbrightness for highlights

                # Apply to color
                r = int(min(255, color[0] * lighting))
                g = int(min(255, color[1] * lighting))
                b = int(min(255, color[2] * lighting))

                # Anti-aliasing at edges
                if dist > radius - 1:
                    alpha = int(255 * (radius - dist))
                    alpha = max(0, min(255, alpha))
                    temp_surf.set_at((local_center[0] + x, local_center[1] + y), (r, g, b, alpha))
                else:
                    temp_surf.set_at((local_center[0] + x, local_center[1] + y), (r, g, b, 255))

    # Blit to main surface
    surface.blit(temp_surf, (center[0] - temp_size//2, center[1] - temp_size//2))

    return surface


def get_shaded_color(
    base_color: Tuple[int, int, int],
    normal: np.ndarray,
    light_dir: np.ndarray,
    ambient: float = 0.3
) -> tuple[int, ...]:
    """
    Calculate shaded color based on surface normal and light direction.

    Args:
        base_color: Base RGB color
        normal: Surface normal vector
        light_dir: Light direction vector
        ambient: Ambient light contribution

    Returns:
        Shaded RGB color
    """
    # Normalize vectors
    normal = normal / (np.linalg.norm(normal) + 1e-6)
    light_dir = light_dir / (np.linalg.norm(light_dir) + 1e-6)

    # Lambertian shading
    diffuse = max(0, np.dot(normal, light_dir))

    # Combine ambient and diffuse
    brightness = ambient + (1 - ambient) * diffuse
    brightness = max(0, min(1, brightness))

    # Apply to color
    return tuple(int(c * brightness) for c in base_color)


def create_sphere_surface(
    radius: int,
    color: Tuple[int, int, int],
    light_angle: float = 45.0,
    ambient: float = 0.3
) -> pygame.Surface:
    """
    Create a pre-rendered 3D sphere surface.

    Args:
        radius: Sphere radius in pixels
        color: Base color
        light_angle: Light direction
        ambient: Ambient lighting

    Returns:
        Surface with rendered sphere
    """
    size = radius * 2 + 4
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)

    # Apply 3D shading
    apply_3d_shading(surface, color, center, radius, light_angle, ambient)

    return surface


def create_bubble_surface(
    radius: int,
    color: Tuple[int, int, int],
    light_angle: float = 45.0
) -> pygame.Surface:
    """
    Create a realistic glass bubble/orb effect with refraction-like appearance.
    """
    size = radius * 2 + 4
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)

    # Light direction
    light_rad = np.radians(light_angle)
    light_offset_x = int(np.cos(light_rad) * radius * 0.4)
    light_offset_y = int(np.sin(light_rad) * radius * 0.4)

    # Draw outer glow (soft atmosphere)
    for i in range(3):
        glow_radius = radius + i * 2
        glow_alpha = int(30 * (1 - i/3))
        glow_color = (*color, glow_alpha)
        pygame.draw.circle(surface, glow_color, center, glow_radius)

    # Main body with gradient (transparent glass)
    for i in range(radius):
        t = i / radius
        # Glass transparency increases toward edge
        alpha = int(80 + 100 * t)
        # Slight color shift (refraction effect)
        tint = 1.0 - t * 0.3
        body_color = (
            int(color[0] * tint),
            int(color[1] * tint),
            int(color[2] * tint),
            alpha
        )
        pygame.draw.circle(surface, body_color, center, radius - i)

    # Dark rim (meniscus effect)
    rim_color = (
        max(0, color[0] - 60),
        max(0, color[1] - 60),
        max(0, color[2] - 60),
        200
    )
    pygame.draw.circle(surface, rim_color, center, radius, 2)

    # Primary highlight (bright specular)
    highlight_pos = (center[0] - light_offset_x, center[1] - light_offset_y)
    highlight_radius = int(radius * 0.35)

    # Draw gradient highlight
    for i in range(highlight_radius, 0, -1):
        t = i / highlight_radius
        alpha = int(200 * (1 - t) ** 2)
        pygame.draw.circle(surface, (255, 255, 255, alpha), highlight_pos, i)

    # Secondary highlight (reflection)
    sec_offset_x = light_offset_x // 2
    sec_offset_y = light_offset_y // 2
    sec_pos = (center[0] - sec_offset_x, center[1] - sec_offset_y)
    sec_radius = int(radius * 0.2)

    for i in range(sec_radius, 0, -1):
        t = i / sec_radius
        alpha = int(120 * (1 - t) ** 2)
        pygame.draw.circle(surface, (255, 255, 255, alpha), sec_pos, i)

    # Edge highlight (rim light on opposite side)
    edge_x = center[0] + int(light_offset_x * 0.8)
    edge_y = center[1] + int(light_offset_y * 0.8)
    edge_radius = int(radius * 0.15)

    for i in range(edge_radius, 0, -1):
        t = i / edge_radius
        alpha = int(80 * (1 - t))
        edge_color = (
            int(color[0] * 1.2),
            int(color[1] * 1.2),
            int(color[2] * 1.2),
            alpha
        )
        pygame.draw.circle(surface, edge_color, (edge_x, edge_y), i)

    return surface

