#!/usr/bin/env python
"""Quick test of the improved preview system"""

import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

try:
    print("Testing imports...", flush=True)

    from src.engine_3d import Engine3D
    print("✓ Engine3D imported", flush=True)

    from src.audio_manager import AudioManager
    print("✓ AudioManager imported", flush=True)

    from src.ui.preview_improved import PreviewImproved, CanvasWidgetImproved
    print("✓ PreviewImproved imported", flush=True)

    print("\nCreating engine...", flush=True)
    engine = Engine3D(900, 700, boundary_radius=280, boundary_type="circle")
    print(f"  Initial state: {engine.get_state()}", flush=True)
    print(f"  Initial objects: {len(engine.objects)}", flush=True)

    print("\nCalling reset...", flush=True)
    engine.reset()
    print(f"  Objects after reset: {len(engine.objects)}", flush=True)
    print(f"  State after reset: {engine.get_state()}", flush=True)

    if len(engine.objects) == 0:
        print("  WARNING: No objects created!", flush=True)
        print("  Trying to manually create object...", flush=True)
        obj = engine._create_random_object()
        print(f"  Created: {obj}", flush=True)
        print(f"  Objects now: {len(engine.objects)}", flush=True)

    print(f"✓ Engine ready with {engine.get_object_count()} objects", flush=True)

    print("\nTesting engine update...", flush=True)
    for i in range(10):
        engine.update(0.016)
    print(f"✓ Engine updated, now has {engine.get_object_count()} objects", flush=True)

    print("\nTesting state transitions...", flush=True)
    print(f"  Current state: {engine.get_state()}", flush=True)
    print(f"  Max objects: {engine.max_objects}", flush=True)
    print(f"  Calm down duration: {engine.calm_down_duration}s", flush=True)

    print("\nAll imports and basic tests passed!", flush=True)

except Exception as e:
    print(f"\n✗ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

