
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLabel, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

from ..core.settings import Settings
from .preview import PygamePreviewWidget
from .controls import ControlsWidget
from .export import ExportWidget
from ..export.video import ExportWorker

DARK_STYLESHEET = """
QWidget {
    background-color: #1a1a2e;
    color: #f0f0f0;
    font-family: Arial, sans-serif;
}
QPushButton {
    background-color: #e94560;
    border: 1px solid #0f3460;
    padding: 8px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #ff5777;
}
QPushButton:pressed {
    background-color: #d93650;
}
QFrame {
    border: 1px solid #0f3460;
    border-radius: 5px;
}
QLabel {
    font-size: 14px;
}
QTabWidget::pane { border: 0; }
QTabBar::tab { padding: 8px; background-color: #16213e; border-radius: 4px; }
QTabBar::tab:selected { background-color: #e94560; }
QProgressBar { border: 1px solid #0f3460; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background-color: #e94560; }
QTextEdit { background-color: #16213e; border: 1px solid #0f3460; }
"""

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Particle Collision Video Generator")
        self.setGeometry(100, 100, 1600, 900)

        self.settings = Settings.load_from_json('presets/cosmic.json')
        self.export_worker = None

        # --- Main Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # --- Column 1: Controls ---
        controls_layout = QVBoxLayout()
        self.controls_widget = ControlsWidget(self.settings)
        self.preset_layout = QHBoxLayout()
        self.save_preset_button = QPushButton("Save Preset")
        self.load_preset_button = QPushButton("Load Preset")
        self.preset_layout.addWidget(self.save_preset_button)
        self.preset_layout.addWidget(self.load_preset_button)
        controls_layout.addWidget(self.controls_widget)
        controls_layout.addLayout(self.preset_layout)
        controls_frame = QFrame()
        controls_frame.setFixedWidth(380)
        controls_frame.setLayout(controls_layout)

        # --- Column 2: Preview ---
        self.preview_layout = QVBoxLayout()
        self.preview_frame = QFrame()
        self.preview_frame.setLayout(self.preview_layout)
        self.preview_widget = PygamePreviewWidget(self.settings)
        self.preview_layout.addWidget(self.preview_widget)
        preview_controls_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.reset_button = QPushButton("Reset")
        preview_controls_layout.addWidget(self.play_button)
        preview_controls_layout.addWidget(self.pause_button)
        preview_controls_layout.addWidget(self.reset_button)
        self.preview_layout.addLayout(preview_controls_layout)

        # --- Column 3: Export ---
        self.export_widget = ExportWidget(self.settings)
        export_frame = QFrame()
        export_frame.setFixedWidth(380)
        export_layout = QVBoxLayout(export_frame)
        export_layout.addWidget(self.export_widget)

        # --- Assemble Main Layout ---
        self.main_layout.addWidget(controls_frame)
        self.main_layout.addWidget(self.preview_frame, 1)
        self.main_layout.addWidget(export_frame)

        self._connect_signals()
        self.update_ui_from_settings()

    def _connect_signals(self):
        self.play_button.clicked.connect(self.preview_widget.play)
        self.pause_button.clicked.connect(self.preview_widget.pause)
        self.reset_button.clicked.connect(self.preview_widget.reset)
        self.controls_widget.connect_signals(self.on_settings_changed)
        self.save_preset_button.clicked.connect(self.save_preset)
        self.load_preset_button.clicked.connect(self.load_preset)
        self.export_widget.generate_button.clicked.connect(self.start_export)
        self.export_widget.cancel_button.clicked.connect(self.cancel_export)

    def start_export(self):
        self.export_worker = ExportWorker(self.settings)
        self.export_worker.progress.connect(self.export_widget.update_progress)
        self.export_worker.finished.connect(self.on_export_finished)
        self.export_worker.error.connect(self.on_export_error)

        self.export_widget.on_export_start()
        self.export_worker.start()

    def cancel_export(self):
        if self.export_worker:
            self.export_worker.cancel()

    def on_export_finished(self, filepath):
        self.export_widget.on_export_finish(True)
        QMessageBox.information(self, "Export Complete", f"Video saved to:\n{filepath}")

    def on_export_error(self, message):
        self.export_widget.on_export_finish(False)
        QMessageBox.critical(self, "Export Error", message)

    def on_settings_changed(self):
        self.preview_widget.update_settings(self.settings)
        self.export_widget._update_settings() # Ensure export UI reflects changes

    def update_ui_from_settings(self):
        self.on_settings_changed()

    def save_preset(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Preset", "presets", "JSON Files (*.json)")
        if filepath:
            try: self.settings.save_to_json(filepath)
            except Exception as e: QMessageBox.critical(self, "Error", f"Could not save preset: {e}")

    def load_preset(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Preset", "presets", "JSON Files (*.json)")
        if filepath:
            try:
                self.settings = Settings.load_from_json(filepath)
                self.controls_widget.settings = self.settings
                self.controls_widget.update_controls_from_settings()
                self.on_settings_changed()
                self.preview_widget.reset()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load preset: {e}")

    def apply_stylesheet(self):
        self.setStyleSheet(DARK_STYLESHEET)

    def closeEvent(self, event):
        self.cancel_export()
        if self.export_worker:
            self.export_worker.wait()
        event.accept()
