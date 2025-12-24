"""
Core settings with validation, clamping, and JSON serialization.
"""
from dataclasses import dataclass, field, asdict
from typing import Literal, List, Dict, Any, Optional, Tuple
import json
from pathlib import Path


@dataclass
class AppSettings:
    """Complete application settings with validation."""

    # General
    seed: int = 42
    mode_ui: Literal["basic", "advanced"] = "basic"

    # Simulation
    fps_preview: int = 60
    fps_export: int = 60
    dt_sim: float = 1.0 / 120.0  # Fixed timestep
    duration_sec: int = 60
    resolution: Tuple[int, int] = (1920, 1080)
    quality: Literal["preview_low", "export_balanced", "export_high"] = "export_balanced"

    # Physics - Gravity
    gravity_enabled: bool = True
    gravity_strength: float = 200.0  # Moderate gravity for dynamic movement (was 300)
    gravity_direction_deg: float = 270.0  # Down
    gravity_attractor_mode: bool = False  # If True, gravity pulls to center

    # Physics - Damping
    drag_coeff: float = 0.001  # Very low drag for free movement (was 0.005)
    friction: float = 0.01  # Very low friction (was 0.03)

    # Physics - Collision
    restitution: float = 0.92  # Very bouncy for sustained movement
    max_speed: float = 1500.0  # Allow faster movement

    # Physics - Forces
    brownian_enabled: bool = False
    brownian_strength: float = 50.0

    vortex_enabled: bool = False
    vortex_strength: float = 100.0
    vortex_falloff: float = 1.0

    attraction_enabled: bool = False
    attraction_strength: float = 500.0
    attraction_radius: float = 200.0

    repulsion_enabled: bool = False
    repulsion_strength: float = 500.0
    repulsion_radius: float = 100.0

    # Boundary
    boundary_radius_ratio: float = 0.42  # Relative to min(width, height)
    boundary_elasticity: float = 0.9
    soft_boundary_enabled: bool = True
    soft_boundary_softness: float = 0.1  # Fraction of radius where soft force applies
    soft_boundary_damping: float = 0.5

    # Particles - New spawn-on-collision mode
    initial_count: int = 2  # Always start with 2 objects
    max_particles: int = 100  # Total objects that can spawn (user configurable)
    spawn_on_collision: bool = True  # Enable collision-based spawning
    spawn_rate_per_sec: float = 0.0  # Disable time-based spawning
    size_min: float = 12.0
    size_max: float = 24.0
    mass_from_area: bool = True
    spawn_pattern: Literal["random", "ring", "center", "spiral", "burst", "collision", "drop"] = "drop"

    # Container shape
    container_shape: Literal["circle", "square", "polygon", "triangle"] = "circle"
    polygon_sides: int = 6  # For polygon container

    # Particle shapes (weighted list) - 3D objects
    shapes: List[str] = field(default_factory=lambda: ["sphere", "rounded_star", "hexagon", "triangle"])
    shape_weights: List[float] = field(default_factory=lambda: [0.4, 0.3, 0.2, 0.1])

    # Visuals
    visual_scheme: str = "cosmic"
    glow_enabled: bool = True
    glow_intensity: float = 0.8
    trails_enabled: bool = False  # Disable trails for this mode
    trail_length: int = 20
    collision_fx_style: Literal["ripple", "sparkle", "both", "none"] = "sparkle"
    collision_fx_intensity: float = 1.0
    boundary_style: Literal["solid", "glow", "pulse"] = "solid"
    boundary_glow: bool = True

    # 3D rendering
    enable_3d_effect: bool = True  # Make objects look 3D
    light_direction: float = 45.0  # Light angle in degrees
    ambient_light: float = 0.3  # Ambient lighting strength

    # Settling detection (for video end)
    settling_enabled: bool = True
    settling_velocity_threshold: float = 3.0  # Lower threshold (was 5.0)
    settling_time_required: float = 4.0  # Longer time to confirm (was 3.0)

    # Audio
    audio_enabled: bool = True
    audio_preview_enabled: bool = True
    audio_instrument: Literal["piano", "violin", "bell", "soft_pad", "mixed"] = "piano"
    audio_scale: Literal["pentatonic_c", "pentatonic_g", "japanese", "minor_a"] = "pentatonic_c"
    audio_master_volume: float = 0.7
    audio_collision_volume: float = 1.0
    audio_spawn_volume: float = 0.5
    audio_boundary_volume: float = 0.6
    audio_ambient_volume: float = 0.3
    audio_reverb_enabled: bool = True
    audio_reverb_amount: float = 0.3
    audio_limiter_enabled: bool = True
    audio_limiter_threshold: float = 0.95
    audio_preview_polyphony: int = 16
    audio_preview_rate_limit: float = 100.0  # Max events per second

    # Background Music
    bgm_enabled: bool = True
    bgm_volume: float = 0.15
    bgm_style: Literal["calm", "meditative", "uplifting"] = "calm"

    # FFmpeg
    ffmpeg_path: Optional[str] = None

    def validate_and_clamp(self) -> List[str]:
        """
        Validate and clamp all values to safe ranges.
        Returns list of warnings/corrections made.
        """
        warnings = []

        # Seed
        if self.seed < 0:
            self.seed = 0
            warnings.append("Seed clamped to 0")

        # FPS
        if self.fps_preview < 24:
            self.fps_preview = 24
            warnings.append("Preview FPS clamped to 24")
        elif self.fps_preview > 120:
            self.fps_preview = 120
            warnings.append("Preview FPS clamped to 120")

        if self.fps_export not in [30, 60]:
            self.fps_export = 60
            warnings.append("Export FPS set to 60")

        # Duration
        if self.duration_sec < 10:
            self.duration_sec = 10
            warnings.append("Duration clamped to 10s")
        elif self.duration_sec > 300:
            self.duration_sec = 300
            warnings.append("Duration clamped to 300s")

        # Physics values
        self.gravity_strength = max(0, min(1000, self.gravity_strength))
        self.drag_coeff = max(0, min(1, self.drag_coeff))
        self.friction = max(0, min(1, self.friction))
        self.restitution = max(0, min(1, self.restitution))
        self.max_speed = max(100, min(5000, self.max_speed))

        self.brownian_strength = max(0, min(1000, self.brownian_strength))
        self.vortex_strength = max(0, min(1000, self.vortex_strength))
        self.vortex_falloff = max(0.1, min(10, self.vortex_falloff))
        self.attraction_strength = max(0, min(5000, self.attraction_strength))
        self.attraction_radius = max(10, min(1000, self.attraction_radius))
        self.repulsion_strength = max(0, min(5000, self.repulsion_strength))
        self.repulsion_radius = max(10, min(1000, self.repulsion_radius))

        # Boundary
        self.boundary_radius_ratio = max(0.1, min(0.9, self.boundary_radius_ratio))
        self.boundary_elasticity = max(0, min(1, self.boundary_elasticity))
        self.soft_boundary_softness = max(0, min(0.5, self.soft_boundary_softness))
        self.soft_boundary_damping = max(0, min(1, self.soft_boundary_damping))

        # Particles
        self.initial_count = max(1, min(1000, self.initial_count))
        self.max_particles = max(self.initial_count, min(2000, self.max_particles))
        self.spawn_rate_per_sec = max(0, min(100, self.spawn_rate_per_sec))
        self.size_min = max(2, min(50, self.size_min))
        self.size_max = max(self.size_min, min(100, self.size_max))

        # Visuals
        self.glow_intensity = max(0, min(2, self.glow_intensity))
        self.trail_length = max(0, min(100, self.trail_length))
        self.collision_fx_intensity = max(0, min(2, self.collision_fx_intensity))

        # Audio
        self.audio_master_volume = max(0, min(1, self.audio_master_volume))
        self.audio_collision_volume = max(0, min(2, self.audio_collision_volume))
        self.audio_spawn_volume = max(0, min(2, self.audio_spawn_volume))
        self.audio_boundary_volume = max(0, min(2, self.audio_boundary_volume))
        self.audio_ambient_volume = max(0, min(1, self.audio_ambient_volume))
        self.audio_reverb_amount = max(0, min(1, self.audio_reverb_amount))
        self.audio_limiter_threshold = max(0.5, min(1, self.audio_limiter_threshold))
        self.audio_preview_polyphony = max(4, min(64, self.audio_preview_polyphony))
        self.audio_preview_rate_limit = max(10, min(500, self.audio_preview_rate_limit))

        # Shapes validation
        if not self.shapes:
            self.shapes = ["circle"]
            self.shape_weights = [1.0]
            warnings.append("Shapes reset to default")
        elif len(self.shape_weights) != len(self.shapes):
            self.shape_weights = [1.0] * len(self.shapes)
            warnings.append("Shape weights reset to equal")

        return warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert tuple to list for JSON
        data['resolution'] = list(self.resolution)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """Create from dictionary (JSON deserialization)."""
        # Convert resolution list back to tuple
        if 'resolution' in data and isinstance(data['resolution'], list):
            data['resolution'] = tuple(data['resolution'])

        # Filter out unknown keys
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        return cls(**filtered_data)

    def save_json(self, path: Path) -> None:
        """Save settings to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, path: Path) -> 'AppSettings':
        """Load settings from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

