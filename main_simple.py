"""Working application that loads the full Dashboard3D"""

import sys
import os
import warnings

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
warnings.filterwarnings('ignore')

def main():
    """Main working version"""
    try:
        print("Creating directories...", flush=True)
        os.makedirs("output", exist_ok=True)
        os.makedirs("config", exist_ok=True)

        print("Initializing pygame...", flush=True)
        try:
            import pygame
            pygame.init()
        except Exception as e:
            print(f"Pygame warning: {e}")

        print("Creating Qt Application...", flush=True)
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)

        print("Loading Dashboard3D...", flush=True)
        from src.ui.dashboard_3d import Dashboard3D

        print("Creating Dashboard...", flush=True)
        dashboard = Dashboard3D()

        print("Showing Dashboard...", flush=True)
        dashboard.show()

        print("Application Ready!\n", flush=True)

        sys.exit(app.exec_())

    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()

        # Show error in GUI
        try:
            from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton

            if 'app' not in locals():
                app = QApplication(sys.argv)

            error_window = QMainWindow()
            error_window.setWindowTitle("Error")
            error_window.setGeometry(100, 100, 600, 400)

            widget = QWidget()
            layout = QVBoxLayout()

            error_label = QLabel(f"Error loading application:\n\n{str(e)}\n\nCheck console for details.")
            layout.addWidget(error_label)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(app.quit)
            layout.addWidget(close_btn)

            widget.setLayout(layout)
            error_window.setCentralWidget(widget)
            error_window.show()

            sys.exit(app.exec_())
        except:
            sys.exit(1)

if __name__ == '__main__':
    main()

