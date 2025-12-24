"""Main application class"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from src.ui.dashboard_3d import Dashboard3D


def main():
    """Entry point for the application"""
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("assets", exist_ok=True)

    # Create QApplication FIRST (very important!)
    app = QApplication(sys.argv)

    # Then create dashboard
    dashboard = Dashboard3D()
    dashboard.show()

    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

