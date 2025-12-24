"""
Simple launcher that avoids PyQt5 initialization issues
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("\n" + "=" * 70)
    print("🌀 3D PARTICLE COLLISION GENERATOR")
    print("=" * 70)
    print("\nInitializing application...\n")

    try:
        # Import after path is set
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        from src.ui.dashboard_3d import Dashboard3D

        # Create application FIRST
        app = QApplication(sys.argv)

        print("✓ Qt Application created")

        # Create dashboard AFTER QApplication
        dashboard = Dashboard3D()

        print("✓ Dashboard created")

        # Show window
        dashboard.show()

        print("✓ Window shown")
        print("\n" + "=" * 70)
        print("Application ready! Click Play to start simulation.")
        print("=" * 70 + "\n")

        # Run event loop
        sys.exit(app.exec_())

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

