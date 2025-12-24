
import numpy as np
import colorsys

# Predefined color schemes
# Each scheme defines a background gradient and a function to map a particle's hue.
PALETTES = {
    "cosmic": {
        "bg_gradient": ("#1a1a2e", "#16213e"),
        "map_hue": lambda h: h # No change, full spectrum
    },
    "ocean": {
        "bg_gradient": ("#0c1445", "#003366"),
        "map_hue": lambda h: (h + 0.5) % 1.0 * 0.4 + 0.5 # Blues and greens
    },
    "neon": {
        "bg_gradient": ("#0f0f0f", "#2c003e"),
        "map_hue": lambda h: h # Full spectrum, but visuals will be brighter
    }
}

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Converts a hex color string to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """Converts an HSL color value to an (R, G, B) tuple."""
    r, g, b = colorsys.hls_to_rgb(h, l, s) # Note: colorsys uses HLS
    return int(r * 255), int(g * 255), int(b * 255)

class Palette:
    def __init__(self, scheme_name: str = "cosmic"):
        self.set_scheme(scheme_name)

    def set_scheme(self, scheme_name: str):
        if scheme_name not in PALETTES:
            scheme_name = "cosmic"
        self.scheme_name = scheme_name
        self.config = PALETTES[scheme_name]
        self.bg_color1_rgb = hex_to_rgb(self.config["bg_gradient"][0])
        self.bg_color2_rgb = hex_to_rgb(self.config["bg_gradient"][1])

    def get_particle_color(self, base_hue: float, saturation: float, lightness: float, palette_lock: bool) -> tuple[int, int, int]:
        """
        Gets the final RGB color for a particle based on its hue and the current scheme.
        If palette_lock is on, the hue is mapped to the scheme's range.
        """
        hue = self.config["map_hue"](base_hue) if palette_lock else base_hue
        return hsl_to_rgb(hue, saturation, lightness)

    def get_mixed_color(self, color1_hsl, color2_hsl, palette_lock: bool, factor=0.5):
        """Mixes two HSL colors."""
        h1, s1, l1 = color1_hsl
        h2, s2, l2 = color2_hsl

        # Hue mixing is tricky, handle circular distance
        d = h2 - h1
        if d > 0.5: d -= 1.0
        if d < -0.5: d += 1.0
        mixed_h = (h1 + d * factor) % 1.0

        mixed_s = s1 + (s2 - s1) * factor
        mixed_l = l1 + (l2 - l1) * factor

        return self.get_particle_color(mixed_h, mixed_s, mixed_l, palette_lock)
