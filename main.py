"""
Main application entry point.
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.dashboard import MainDashboard


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Particle Video Generator")

    # Create and show main window
    window = MainDashboard()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

