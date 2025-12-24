"""
Color palette management and HSL/HSV utilities.
"""
from typing import Tuple, List, Dict
import numpy as np


class ColorPalette:
    """Color palette schemes for visual theming."""

    SCHEMES = {
        "cosmic": {
            "background_inner": (10, 10, 30),
            "background_outer": (5, 5, 15),
            "boundary": (100, 150, 255),
            "accent": (255, 100, 200)
        },
        "ocean": {
            "background_inner": (10, 30, 50),
            "background_outer": (5, 15, 30),
            "boundary": (50, 200, 255),
            "accent": (100, 255, 200)
        },
        "neon": {
            "background_inner": (20, 0, 20),
            "background_outer": (10, 0, 10),
            "boundary": (255, 0, 255),
            "accent": (0, 255, 255)
        },
        "fire": {
            "background_inner": (40, 10, 0),
            "background_outer": (20, 5, 0),
            "boundary": (255, 100, 0),
            "accent": (255, 200, 0)
        },
        "forest": {
            "background_inner": (10, 30, 10),
            "background_outer": (5, 15, 5),
            "boundary": (100, 255, 100),
            "accent": (200, 255, 100)
        }
    }

    def __init__(self, scheme_name: str = "cosmic"):
        self.scheme_name = scheme_name
        self.colors = self.SCHEMES.get(scheme_name, self.SCHEMES["cosmic"])

    def get_background_gradient(self, width: int, height: int) -> np.ndarray:
        """
        Generate radial gradient background.

        Returns:
            NumPy array of shape (height, width, 3) with RGB values
        """
        # Create coordinate grids
        center_x, center_y = width / 2, height / 2
        y, x = np.ogrid[:height, :width]

        # Distance from center (normalized)
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        dist_norm = np.clip(dist / max_dist, 0, 1)

        # Interpolate colors
        inner = np.array(self.colors["background_inner"])
        outer = np.array(self.colors["background_outer"])

        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(3):
            gradient[:, :, i] = (inner[i] * (1 - dist_norm) + outer[i] * dist_norm).astype(np.uint8)

        return gradient

    def get_boundary_color(self) -> Tuple[int, int, int]:
        """Get boundary color."""
        return self.colors["boundary"]

    def get_accent_color(self) -> Tuple[int, int, int]:
        """Get accent color."""
        return self.colors["accent"]


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """
    Convert HSV to RGB.

    Args:
        h: Hue [0, 1]
        s: Saturation [0, 1]
        v: Value [0, 1]

    Returns:
        RGB tuple (r, g, b) with values [0, 255]
    """
    if s == 0.0:
        r = g = b = v
    else:
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """
    Convert RGB to HSV.

    Args:
        r, g, b: RGB values [0, 255]

    Returns:
        HSV tuple (h, s, v) with values [0, 1]
    """
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c

    if diff == 0:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360

    s = 0 if max_c == 0 else diff / max_c
    v = max_c

    return (h / 360.0, s, v)


def interpolate_color(
    color1: Tuple[int, int, int],
    color2: Tuple[int, int, int],
    t: float
) -> Tuple[int, int, int]:
    """
    Linearly interpolate between two colors.

    Args:
        color1, color2: RGB tuples
        t: Interpolation factor [0, 1]

    Returns:
        Interpolated RGB color
    """
    t = max(0, min(1, t))
    r = int(color1[0] * (1 - t) + color2[0] * t)
    g = int(color1[1] * (1 - t) + color2[1] * t)
    b = int(color1[2] * (1 - t) + color2[2] * t)
    return (r, g, b)

