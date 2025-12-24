#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test 3D system without GUI"""

import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "=" * 70)
print("3D PARTICLE SYSTEM - Core Test")
print("=" * 70 + "\n")

try:
    print("1. Testing Engine3D...", end=" ", flush=True)
    from src.engine_3d import Engine3D
    engine = Engine3D(900, 700, 280, "circle")
    engine.reset()
    print("OK (Objects: " + str(len(engine.objects)) + ")")

    print("2. Testing Renderer3D...", end=" ", flush=True)
    import pygame
    pygame.init()
    from src.renderer_3d import Renderer3D
    renderer = Renderer3D(900, 700)
    print("OK")

    print("3. Testing AudioManager...", end=" ", flush=True)
    from src.audio_manager import AudioManager
    audio = AudioManager()
    print("OK")

    print("4. Testing collision...", end=" ", flush=True)
    # Simulate some updates
    for i in range(100):
        engine.update(0.016)
    print("OK (Objects: " + str(len(engine.objects)) + ")")

    print("5. Testing rendering...", end=" ", flush=True)
    surface = renderer.render(engine.objects, engine.boundary_radius, "circle")
    print("OK")

    print("\n" + "=" * 70)
    print("SUCCESS: All core systems working!")
    print("=" * 70)
    print("\nRun: python main.py")
    print("=" * 70 + "\n")

except Exception as e:
    print("ERROR: " + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

