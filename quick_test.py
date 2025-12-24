"""Quick test to verify the application works without GUI"""

import sys
from src.particle_engine import ParticleEngine
from src.renderer import Renderer
from src.audio_engine import AudioEngine, AudioGenerator
from src.utils.config import ConfigManager
import numpy as np


def test_particle_engine():
    """Test particle engine"""
    print("Testing Particle Engine...", end=" ")
    engine = ParticleEngine(800, 600, 250)
    engine.spawn_particle(5)
    engine.update(0.016)  # 60fps
    assert len(engine.particles) > 0
    print("✓")


def test_renderer():
    """Test renderer"""
    print("Testing Renderer...", end=" ")
    renderer = Renderer(800, 600)
    renderer.set_color_scheme("Ocean Breeze")
    print("✓")


def test_audio_engine():
    """Test audio engine"""
    print("Testing Audio Engine...", end=" ")
    engine = AudioEngine()
    sound = engine.generate_collision_sound()
    assert sound is not None
    print("✓")


def test_audio_generator():
    """Test audio synthesis"""
    print("Testing Audio Generator...", end=" ")
    wave = AudioGenerator.generate_sine_wave(440.0, 100)
    assert len(wave) > 0

    audio = AudioGenerator.wave_to_audio_segment(wave)
    assert audio is not None
    print("✓")


def test_config_manager():
    """Test configuration management"""
    print("Testing Configuration Manager...", end=" ")
    config = ConfigManager("test_config")
    spawn_rate = config.get("particle_settings", "spawn_rate")
    assert spawn_rate == 5
    print("✓")


def test_simulation_loop():
    """Test a few frames of simulation"""
    print("Testing Simulation Loop...", end=" ")
    engine = ParticleEngine(800, 600, 250)
    engine.spawn_particle(10)

    for _ in range(10):
        engine.update(0.016)

    assert len(engine.particles) > 0
    print("✓")


def main():
    """Run all tests"""
    print("=" * 60)
    print("PARTICLE COLLISION VIDEO GENERATOR - Core Tests")
    print("=" * 60)
    print()

    tests = [
        test_particle_engine,
        test_renderer,
        test_audio_generator,
        test_audio_engine,
        test_config_manager,
        test_simulation_loop,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ Error: {e}")
            failed += 1

    print()
    print("=" * 60)
    if failed == 0:
        print("✓ ALL TESTS PASSED!")
        print()
        print("The application is ready to use.")
        print("Run:  python main.py")
        print("=" * 60)
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

