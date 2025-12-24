
import json
from dataclasses import dataclass, field, asdict
from typing import Tuple, List

def _clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

@dataclass
class SimulationSettings:
    fps_preview: int = 60
    fps_export: int = 60
    dt_sim: float = 1 / 120.0
    duration_sec: int = 60
    resolution: Tuple[int, int] = (1920, 1080)
    quality: str = 'export_medium'

    def __post_init__(self):
        self.fps_preview = _clamp(self.fps_preview, 15, 120)
        self.fps_export = _clamp(self.fps_export, 24, 60)
        self.duration_sec = _clamp(self.duration_sec, 5, 300)
        if self.quality not in ['preview_low', 'export_medium', 'export_high']:
            self.quality = 'export_medium'

@dataclass
class PhysicsSettings:
    gravity_enabled: bool = True
    gravity_strength: float = 9.8
    gravity_direction_deg: float = 90.0
    attractor_mode: bool = False
    drag_coeff: float = 0.02
    friction: float = 0.1
    restitution: float = 0.85
    max_speed: float = 500.0
    brownian_enabled: bool = True
    brownian_strength: float = 0.5
    vortex_enabled: bool = False
    vortex_strength: float = 1.0
    attraction_repulsion_enabled: bool = False
    attraction_strength: float = 0.5
    attraction_radius: float = 150.0
    boundary_radius_ratio: float = 0.95
    boundary_elasticity: float = 0.9
    soft_boundary_enabled: bool = True
    soft_boundary_softness: float = 0.1

    def __post_init__(self):
        self.gravity_strength = _clamp(self.gravity_strength, 0, 100)
        self.drag_coeff = _clamp(self.drag_coeff, 0, 1)
        self.restitution = _clamp(self.restitution, 0, 1)
        self.max_speed = _clamp(self.max_speed, 10, 5000)

@dataclass
class ParticleSettings:
    initial_count: int = 50
    max_particles: int = 200
    spawn_rate: float = 5.0
    size_min: float = 5.0
    size_max: float = 15.0
    shapes: List[str] = field(default_factory=lambda: ["circle", "square"])
    mass_from_area: bool = True

    def __post_init__(self):
        self.initial_count = _clamp(self.initial_count, 0, 1000)
        self.max_particles = _clamp(self.max_particles, 10, 2000)
        self.spawn_rate = _clamp(self.spawn_rate, 0, 100)

@dataclass
class VisualSettings:
    scheme_name: str = "cosmic"
    glow_toggle: bool = True
    glow_intensity: float = 0.8
    trails_toggle: bool = True
    trails_length: int = 15
    collision_effect_style: str = "ripple"
    boundary_style: str = "glow"
    impact_deformation_amount: float = 0.5
    spring_stiffness: float = 0.1
    damping: float = 0.05
    deformation_by_energy: bool = True
    palette_lock: bool = True

    def __post_init__(self):
        self.glow_intensity = _clamp(self.glow_intensity, 0, 1)
        self.trails_length = _clamp(self.trails_length, 2, 100)

@dataclass
class AudioSettings:
    enabled: bool = True
    instrument: str = "piano"
    scale: str = "pentatonic_c"
    master_volume: float = 0.8
    collision_volume: float = 0.7
    spawn_volume: float = 0.5
    ambient_volume: float = 0.2
    reverb_enabled: bool = True
    reverb_amount: float = 0.4
    limiter_enabled: bool = True
    limiter_threshold: float = -3.0
    music_mood: str = "Balanced"

    def __post_init__(self):
        self.master_volume = _clamp(self.master_volume, 0, 1)
        self.reverb_amount = _clamp(self.reverb_amount, 0, 1)

@dataclass
class Settings:
    seed: int = 42
    simulation: SimulationSettings = field(default_factory=SimulationSettings)
    physics: PhysicsSettings = field(default_factory=PhysicsSettings)
    particles: ParticleSettings = field(default_factory=ParticleSettings)
    visuals: VisualSettings = field(default_factory=VisualSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)

    @classmethod
    def from_dict(cls, data):
        data['simulation'] = SimulationSettings(**data.get('simulation', {}))
        data['physics'] = PhysicsSettings(**data.get('physics', {}))
        data['particles'] = ParticleSettings(**data.get('particles', {}))
        data['visuals'] = VisualSettings(**data.get('visuals', {}))
        data['audio'] = AudioSettings(**data.get('audio', {}))
        return cls(**data)

    def to_dict(self):
        return asdict(self)

    def save_to_json(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_json(cls, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

if __name__ == '__main__':
    # Example usage
    settings = Settings()
    print("Default settings:")
    print(settings)

    settings.save_to_json('default_settings.json')

    loaded_settings = Settings.load_from_json('default_settings.json')
    print("\nLoaded settings:")
    print(loaded_settings)

    assert settings == loaded_settings
    print("\nSettings match after save/load cycle.")
