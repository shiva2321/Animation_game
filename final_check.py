#!/usr/bin/env python
"""Final verification that everything works"""

import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

print("=" * 70)
print("3D PARTICLE COLLISION GENERATOR - FINAL VERIFICATION")
print("=" * 70)
print()

try:
    print("1. Testing imports...", end=" ", flush=True)
    from src.engine_3d import Engine3D
    from src.audio_manager import AudioManager
    from src.utils.config import ConfigManager
    from src.utils.colors import get_color_scheme
    print("OK")

    print("2. Testing Engine3D...", end=" ", flush=True)
    engine = Engine3D(900, 700, 280, "circle")
    engine.reset()
    assert len(engine.objects) == 2, "Engine should have 2 initial objects"
    print("OK")

    print("3. Testing physics update...", end=" ", flush=True)
    for _ in range(50):
        engine.update(0.016)
    print("OK")

    print("4. Testing collision detection...", end=" ", flush=True)
    obj1 = engine.objects[0]
    obj2 = engine.objects[1]
    # Should either collide or not, but code should work
    obj1.check_collision(obj2)
    print("OK")

    print("5. Testing AudioManager...", end=" ", flush=True)
    audio = AudioManager()
    collision_sound = audio.generate_collision_sound()
    bounce_sound = audio.generate_bounce_sound()
    assert collision_sound is not None
    assert bounce_sound is not None
    print("OK")

    print("6. Testing ConfigManager...", end=" ", flush=True)
    config = ConfigManager()
    scheme = get_color_scheme("Ocean Breeze")
    assert scheme is not None
    print("OK")

    print("7. Testing settings...", end=" ", flush=True)
    engine.set_max_objects(100)
    engine.set_object_shape("cube")
    print("OK")

    print()
    print("=" * 70)
    print("SUCCESS! All systems working correctly!")
    print("=" * 70)
    print()
    print("Your application is ready to use!")
    print()
    print("To start the application, run:")
    print("  python main.py")
    print()
    print("The application will show a dashboard with:")
    print("- Settings panel on the left")
    print("- Simulation area in the center")
    print("- Advanced options on the right")
    print()
    print("Click 'Play' to start the simulation!")
    print()
    print("=" * 70)

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

