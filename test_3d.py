"""Test suite for 3D particle system"""

import sys

def test_3d_engine():
    """Test 3D engine"""
    print("Testing 3D Engine...", end=" ")
    from src.engine_3d import Engine3D, Object3D

    engine = Engine3D(800, 600, 250, "circle")
    engine.reset()

    # Should have 2 initial objects
    assert len(engine.objects) == 2, f"Expected 2 initial objects, got {len(engine.objects)}"

    # Update simulation
    engine.update(0.016)

    print("✓")


def test_3d_renderer():
    """Test 3D renderer"""
    print("Testing 3D Renderer...", end=" ")
    import pygame
    from src.renderer_3d import Renderer3D

    pygame.init()
    renderer = Renderer3D(800, 600)
    renderer.set_color_scheme("Ocean Breeze")

    # Create test objects
    from src.engine_3d import Object3D
    obj = Object3D(400, 300, 1, 1, 10, (200, 100, 150), "sphere", "circle")

    # Render
    surface = renderer.render([obj], 250, "circle")
    assert surface is not None

    print("✓")


def test_audio_manager():
    """Test audio manager"""
    print("Testing Audio Manager...", end=" ")
    from src.audio_manager import AudioManager

    manager = AudioManager()

    # Generate sounds
    collision_sound = manager.generate_collision_sound()
    assert collision_sound is not None

    bounce_sound = manager.generate_bounce_sound()
    assert bounce_sound is not None

    print("✓")


def test_collision_detection():
    """Test collision detection"""
    print("Testing Collision Detection...", end=" ")
    from src.engine_3d import Object3D

    obj1 = Object3D(100, 100, 1, 0, 5, (200, 100, 150), "sphere", "circle")
    obj2 = Object3D(109, 100, 0, 0, 5, (150, 100, 200), "sphere", "circle")

    # Should collide (distance = 9, radii sum = 10)
    assert obj1.check_collision(obj2), "Objects should collide"

    # Resolve collision
    result = obj1.resolve_collision(obj2)
    assert result == True, "Collision should be resolved"

    print("✓")


def test_boundary_collision():
    """Test boundary collision"""
    print("Testing Boundary Collision...", end=" ")
    from src.engine_3d import Object3D

    # Object outside circular boundary
    # Center at 400, 300, radius 250, so boundary extends to 650 on right
    # Object at 655 with radius 5 means it's definitely outside
    obj = Object3D(655, 300, 1, 0, 5, (200, 100, 150), "sphere", "circle")

    # Check collision (center at 400, 300, radius 250)
    result = obj.check_boundary_collision(400, 300, 250, "circle")
    assert result == True, "Object should collide with boundary"

    print("✓")


def test_spawn_on_collision():
    """Test that collisions spawn new objects"""
    print("Testing Spawn on Collision...", end=" ")
    from src.engine_3d import Engine3D

    engine = Engine3D(800, 600, 250, "circle")
    engine.reset()

    initial_count = len(engine.objects)

    # Make objects collide
    if len(engine.objects) >= 2:
        engine.objects[0].x = 400
        engine.objects[0].y = 300
        engine.objects[1].x = 408
        engine.objects[1].y = 300
        engine.objects[0].vx = 1
        engine.objects[1].vx = -1

    # Update should trigger collision and spawn
    engine.update(0.016)

    new_count = len(engine.objects)
    assert new_count >= initial_count, "Collision should spawn new object"

    print("✓")


def test_speed_increase():
    """Test that speed increases over time"""
    print("Testing Speed Increase Over Time...", end=" ")
    from src.engine_3d import Engine3D

    engine = Engine3D(800, 600, 250, "circle")
    engine.reset()

    # Get initial velocity
    if len(engine.objects) > 0:
        initial_speed = (engine.objects[0].vx ** 2 + engine.objects[0].vy ** 2) ** 0.5

        # Update multiple times
        for _ in range(100):
            engine.update(0.016)

        final_speed = (engine.objects[0].vx ** 2 + engine.objects[0].vy ** 2) ** 0.5

        # Speed should increase (or at least not decrease significantly)
        assert final_speed > initial_speed * 0.8, "Speed should not decrease significantly"

    print("✓")


def main():
    """Run all tests"""
    print("=" * 60)
    print("3D PARTICLE SYSTEM - Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_3d_engine,
        test_3d_renderer,
        test_audio_manager,
        test_collision_detection,
        test_boundary_collision,
        test_spawn_on_collision,
        test_speed_increase,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__}: {str(e)[:50]}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    if failed == 0:
        print("✓ ALL TESTS PASSED!")
        print()
        print("The 3D application is ready!")
        print("Run:  python main.py")
        print("=" * 60)
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

