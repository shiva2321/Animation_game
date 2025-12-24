"""Enhanced color system with gradient backgrounds and color-coordinated objects"""

import math
import time


class GradientBackground:
    """Generate smooth, flowing gradient backgrounds"""

    @staticmethod
    def get_gradient_color(x, y, width, height, time_offset=0, scheme="ocean"):
        """Get gradient color at position with smooth wave animation"""

        # Normalize coordinates
        nx = x / width
        ny = y / height

        if scheme == "ocean":
            # Ocean theme - teals and blues with wave animation
            wave1 = math.sin(nx * 3 + time_offset) * 0.5 + 0.5
            wave2 = math.sin(ny * 2 + time_offset * 0.8) * 0.5 + 0.5

            r = int(20 + (100 * wave1))
            g = int(150 + (100 * wave2))
            b = int(200 + (50 * (wave1 + wave2) * 0.5))

        elif scheme == "sunset":
            # Sunset theme - oranges, reds, purples
            wave1 = math.sin(nx * 2.5 + time_offset * 0.7) * 0.5 + 0.5
            wave2 = math.sin(ny * 3 + time_offset) * 0.5 + 0.5

            r = int(180 + (75 * wave1))
            g = int(80 + (90 * wave2))
            b = int(100 + (155 * (1 - wave2)))

        elif scheme == "forest":
            # Forest theme - greens, browns, golds
            wave1 = math.sin(nx * 2 + time_offset * 0.9) * 0.5 + 0.5
            wave2 = math.sin(ny * 2.5 + time_offset * 0.6) * 0.5 + 0.5

            r = int(60 + (70 * wave2))
            g = int(100 + (100 * wave1))
            b = int(40 + (60 * (1 - wave1)))

        elif scheme == "pastel":
            # Pastel theme - soft pinks, blues, lavenders
            wave1 = math.sin(nx * 3 + time_offset * 0.8) * 0.5 + 0.5
            wave2 = math.sin(ny * 2 + time_offset) * 0.5 + 0.5

            r = int(200 + (55 * wave1))
            g = int(180 + (75 * wave2))
            b = int(220 + (35 * (wave1 + wave2) * 0.5))

        elif scheme == "neon":
            # Neon theme - bright cyberpunk
            wave1 = math.sin(nx * 4 + time_offset * 1.2) * 0.5 + 0.5
            wave2 = math.sin(ny * 3 + time_offset * 0.9) * 0.5 + 0.5

            r = int(30 + (200 * wave1))
            g = int(20 + (220 * wave2))
            b = int(50 + (200 * (1 - (wave1 + wave2) * 0.5)))

        else:  # Default to ocean
            return GradientBackground.get_gradient_color(x, y, width, height, time_offset, "ocean")

        # Clamp values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        return (r, g, b)


class ColorScheme:
    """Color schemes with coordinated object and boundary colors"""

    SCHEMES = {
        "ocean": {
            "name": "Ocean Breeze",
            "particles": [
                (30, 180, 220),   # Cyan
                (20, 200, 240),   # Light cyan
                (50, 150, 200),   # Teal
                (10, 220, 220),   # Bright cyan
                (60, 140, 200),   # Blue-teal
            ],
            "boundary": (100, 200, 255),
            "background_type": "ocean",
            "glow_color": (100, 180, 220),
        },
        "sunset": {
            "name": "Sunset Glow",
            "particles": [
                (255, 100, 80),    # Coral
                (255, 150, 50),    # Orange
                (220, 80, 140),    # Rose
                (255, 120, 100),   # Light coral
                (200, 100, 180),   # Mauve
            ],
            "boundary": (255, 140, 100),
            "background_type": "sunset",
            "glow_color": (255, 150, 120),
        },
        "forest": {
            "name": "Forest Magic",
            "particles": [
                (100, 180, 80),    # Light green
                (80, 200, 100),    # Fresh green
                (150, 180, 60),    # Yellow-green
                (120, 160, 80),    # Sage
                (180, 160, 40),    # Gold
            ],
            "boundary": (120, 200, 100),
            "background_type": "forest",
            "glow_color": (150, 180, 100),
        },
        "pastel": {
            "name": "Pastel Dreams",
            "particles": [
                (220, 150, 200),   # Light pink
                (200, 180, 240),   # Lavender
                (180, 220, 200),   # Mint
                (240, 200, 180),   # Peach
                (220, 200, 240),   # Light purple
            ],
            "boundary": (200, 180, 220),
            "background_type": "pastel",
            "glow_color": (220, 180, 220),
        },
        "neon": {
            "name": "Neon Nights",
            "particles": [
                (255, 0, 255),     # Magenta
                (0, 255, 255),     # Cyan
                (255, 0, 100),     # Hot pink
                (0, 255, 100),     # Green
                (255, 200, 0),     # Yellow
            ],
            "boundary": (100, 255, 255),
            "background_type": "neon",
            "glow_color": (255, 100, 255),
        },
    }

    @staticmethod
    def get_scheme(name):
        """Get color scheme by name"""
        if name in ColorScheme.SCHEMES:
            return ColorScheme.SCHEMES[name]
        return ColorScheme.SCHEMES["ocean"]  # Default

    @staticmethod
    def get_particle_color(scheme_name, index):
        """Get particle color for index"""
        scheme = ColorScheme.get_scheme(scheme_name)
        colors = scheme["particles"]
        return colors[index % len(colors)]

    @staticmethod
    def get_available_schemes():
        """Get list of available scheme names"""
        return list(ColorScheme.SCHEMES.keys())

    @staticmethod
    def get_scheme_names():
        """Get list of human-readable scheme names"""
        return [ColorScheme.SCHEMES[key]["name"] for key in ColorScheme.SCHEMES.keys()]

