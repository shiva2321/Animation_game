#!/usr/bin/env python3
"""
🌀 3D Particle Collision Generator
Real-time 3D visualization with collision-based spawning and procedural audio
"""

import sys
import os

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🌀 3D PARTICLE COLLISION GENERATOR")
    print("=" * 70)
    print("\nStarting application...\n")

    try:
        from src.app import Application

        # Create and run application
        app = Application()
        app.run()

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

