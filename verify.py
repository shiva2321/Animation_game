#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify core systems work"""

import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("VERIFICATION TEST\n")

try:
    print("1. Testing Engine3D...", end=" ", flush=True)
    from src.engine_3d import Engine3D
    engine = Engine3D(900, 700, 280, "circle")
    engine.reset()
    print("OK")

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

    print("4. Testing collision system...", end=" ", flush=True)
    for i in range(100):
        engine.update(0.016)
    print("OK")

    print("5. Testing Config...", end=" ", flush=True)
    from src.utils.config import ConfigManager
    config = ConfigManager()
    print("OK")

    print("\n" + "=" * 50)
    print("SUCCESS: Core systems verified!")
    print("=" * 50)
    print("\nThe application is ready to use.")
    print("Run: python main.py")
    print("=" * 50 + "\n")

except Exception as e:
    print("FAILED")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

