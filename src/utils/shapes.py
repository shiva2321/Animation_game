"""Shape drawing functions for particles"""

import math
import pygame


def draw_circle(surface, pos, radius, color, alpha=255):
    """Draw a circle particle"""
    x, y = int(pos[0]), int(pos[1])
    r = int(radius)

    # Create temporary surface with per-pixel alpha
    temp = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(temp, (*color, alpha), (r, r), r)
    surface.blit(temp, (x - r, y - r))


def draw_square(surface, pos, radius, color, alpha=255):
    """Draw a square particle"""
    x, y = int(pos[0]), int(pos[1])
    size = int(radius * 2)

    temp = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(temp, (*color, alpha), (0, 0, size, size))
    surface.blit(temp, (x - radius, y - radius))


def draw_triangle(surface, pos, radius, color, alpha=255):
    """Draw a triangle particle"""
    x, y = int(pos[0]), int(pos[1])
    r = radius

    # Calculate triangle vertices (pointing up)
    points = [
        (x, y - r),
        (x - r, y + r),
        (x + r, y + r),
    ]

    # Draw on temporary surface
    size = int(radius * 2.5)
    temp = pygame.Surface((size, size), pygame.SRCALPHA)
    offset = int(size / 2)

    adjusted_points = [
        (p[0] - x + offset, p[1] - y + offset) for p in points
    ]

    pygame.draw.polygon(temp, (*color, alpha), adjusted_points)
    surface.blit(temp, (x - offset, y - offset))


def draw_star(surface, pos, radius, color, alpha=255):
    """Draw a 5-point star particle"""
    x, y = int(pos[0]), int(pos[1])
    points = []

    for i in range(10):
        angle = math.pi / 2 + (i * math.pi / 5)
        r = radius if i % 2 == 0 else radius / 2
        px = x + r * math.cos(angle)
        py = y - r * math.sin(angle)
        points.append((px, py))

    # Draw on temporary surface
    size = int(radius * 2.5)
    temp = pygame.Surface((size, size), pygame.SRCALPHA)
    offset = int(size / 2)

    adjusted_points = [
        (p[0] - x + offset, p[1] - y + offset) for p in points
    ]

    pygame.draw.polygon(temp, (*color, alpha), adjusted_points)
    surface.blit(temp, (x - offset, y - offset))


def draw_hexagon(surface, pos, radius, color, alpha=255):
    """Draw a hexagon particle"""
    x, y = int(pos[0]), int(pos[1])
    points = []

    for i in range(6):
        angle = math.pi / 3 * i
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.append((px, py))

    # Draw on temporary surface
    size = int(radius * 2.5)
    temp = pygame.Surface((size, size), pygame.SRCALPHA)
    offset = int(size / 2)

    adjusted_points = [
        (p[0] - x + offset, p[1] - y + offset) for p in points
    ]

    pygame.draw.polygon(temp, (*color, alpha), adjusted_points)
    surface.blit(temp, (x - offset, y - offset))


def draw_heart(surface, pos, radius, color, alpha=255):
    """Draw a heart particle"""
    x, y = int(pos[0]), int(pos[1])
    scale = radius / 10

    points = []
    for t in range(0, 628, 5):  # 0 to 2*pi
        angle = t / 100.0

        # Heart shape parametric equations
        hx = 16 * math.sin(angle) ** 3
        hy = 13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle)

        px = x + hx * scale
        py = y - hy * scale / 2
        points.append((px, py))

    if len(points) > 2:
        size = int(radius * 3)
        temp = pygame.Surface((size, size), pygame.SRCALPHA)
        offset = int(size / 2)

        adjusted_points = [
            (p[0] - x + offset, p[1] - y + offset) for p in points
        ]

        pygame.draw.polygon(temp, (*color, alpha), adjusted_points)
        surface.blit(temp, (x - offset, y - offset))


def draw_glow(surface, pos, radius, color, alpha=255):
    """Draw a glow effect around a position"""
    x, y = int(pos[0]), int(pos[1])

    # Draw multiple circles with decreasing opacity for glow effect
    for i in range(int(radius * 1.5), 0, -2):
        opacity = int(alpha * (1 - (i / (radius * 1.5))))
        temp = pygame.Surface((i * 2, i * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, (*color, opacity), (i, i), i)
        surface.blit(temp, (x - i, y - i))


def draw_shape(surface, shape_type, pos, radius, color, alpha=255):
    """Draw a particle based on shape type"""
    shape_functions = {
        "Circle": draw_circle,
        "Square": draw_square,
        "Triangle": draw_triangle,
        "Star": draw_star,
        "Hexagon": draw_hexagon,
        "Heart": draw_heart,
    }

    drawer = shape_functions.get(shape_type, draw_circle)
    drawer(surface, pos, radius, color, alpha)


def get_available_shapes():
    """Get list of available shape types"""
    return ["Circle", "Square", "Triangle", "Star", "Hexagon", "Heart"]

