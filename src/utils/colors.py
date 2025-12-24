"""Color schemes and color utility functions"""

# Color scheme presets
COLOR_SCHEMES = {
    "Pastel Dreams": {
        "particles": [(255, 179, 217), (217, 179, 255), (179, 217, 255), (179, 255, 217)],
        "background": (240, 240, 255),
        "boundary": (200, 180, 220),
    },
    "Ocean Breeze": {
        "particles": [(0, 150, 200), (50, 200, 230), (0, 100, 150), (100, 220, 255)],
        "background": (20, 40, 80),
        "boundary": (0, 150, 200),
    },
    "Sunset Glow": {
        "particles": [(255, 100, 50), (255, 150, 80), (200, 50, 100), (255, 200, 100)],
        "background": (30, 20, 40),
        "boundary": (255, 100, 50),
    },
    "Forest Magic": {
        "particles": [(100, 200, 100), (150, 100, 200), (200, 180, 50), (100, 150, 80)],
        "background": (20, 40, 30),
        "boundary": (100, 200, 100),
    },
    "Neon Nights": {
        "particles": [(255, 0, 255), (0, 255, 255), (255, 255, 0), (0, 255, 0)],
        "background": (10, 10, 20),
        "boundary": (255, 0, 255),
    },
}


def get_color_scheme(name):
    """Get a color scheme by name"""
    return COLOR_SCHEMES.get(name, COLOR_SCHEMES["Pastel Dreams"])


def get_available_schemes():
    """Get list of available color scheme names"""
    return list(COLOR_SCHEMES.keys())


def interpolate_color(color1, color2, t):
    """Interpolate between two colors (t: 0-1)"""
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return (r, g, b)


def adjust_brightness(color, factor):
    """Adjust brightness of a color (factor: 0-2)"""
    return (
        int(min(255, color[0] * factor)),
        int(min(255, color[1] * factor)),
        int(min(255, color[2] * factor)),
    )


def rgb_to_hsv(r, g, b):
    """Convert RGB to HSV"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2.0

    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)

        if max_c == r:
            h = (g - b) / d + (6.0 if g < b else 0.0)
        elif max_c == g:
            h = (b - r) / d + 2.0
        else:
            h = (r - g) / d + 4.0
        h /= 6.0

    return h, s, l


def hsv_to_rgb(h, s, l):
    """Convert HSV to RGB"""
    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return (int(r * 255), int(g * 255), int(b * 255))

