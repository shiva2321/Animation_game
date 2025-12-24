
import sys
import shutil
from PyQt5.QtWidgets import QApplication, QMessageBox

from src.ui.dashboard import Dashboard

def check_ffmpeg():
    """Checks if ffmpeg is in the system's PATH."""
    return shutil.which("ffmpeg") is not None

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)

    if not check_ffmpeg():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("FFmpeg Not Found")
        msg.setInformativeText(
            "FFmpeg is required for video export. Please install it and ensure it is in your system's PATH.\n\n"
            "On Windows, you can install it via winget:\n"
            "winget install -e --id Gyan.FFmpeg\n\n"
            "Or download from gyan.dev and add the 'bin' folder to your PATH."
        )
        msg.setWindowTitle("Dependency Error")
        msg.exec_()
        sys.exit(1)

    dashboard = Dashboard()
    dashboard.apply_stylesheet()
    dashboard.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
