"""Main dashboard window for the application"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QDockWidget,
    QLabel, QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from src.utils.config import ConfigManager
from src.ui.preview import PreviewCanvas
from src.ui.controls import ParticleControlPanel, VisualControlPanel, AudioControlPanel
from src.ui.export_panel import ExportPanel


class Dashboard(QMainWindow):
    """Main application dashboard"""

    def __init__(self):
        super().__init__()

        # Configuration
        self.config = ConfigManager()

        # Initialize UI
        self.init_ui()

        # Load saved settings
        self.load_settings()

        # Set window properties
        self.setWindowTitle("Particle Collision Video Generator")
        self.setMinimumSize(QSize(1600, 900))
        self.resize(1600, 900)

    def init_ui(self):
        """Initialize user interface"""
        # Create central widget with preview
        central_widget = QWidget()
        central_layout = QHBoxLayout()

        # Left panel - Controls
        left_layout = QVBoxLayout()

        # Particle controls
        self.particle_panel = ParticleControlPanel()
        self.particle_panel.settings_changed.connect(self.on_particle_settings_changed)
        left_layout.addWidget(self.particle_panel)

        # Visual controls
        self.visual_panel = VisualControlPanel()
        self.visual_panel.settings_changed.connect(self.on_visual_settings_changed)
        left_layout.addWidget(self.visual_panel)

        # Audio controls
        self.audio_panel = AudioControlPanel()
        self.audio_panel.settings_changed.connect(self.on_audio_settings_changed)
        left_layout.addWidget(self.audio_panel)

        left_layout.addStretch()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(350)

        central_layout.addWidget(left_widget)

        # Center - Preview
        self.preview = PreviewCanvas()
        self.preview.particle_count_changed.connect(self.on_particle_count_changed)
        self.preview.fps_changed.connect(self.on_fps_changed)
        central_layout.addWidget(self.preview, 1)

        # Right panel - Export
        self.export_panel = ExportPanel()
        self.export_panel.set_config(self.config)
        self.export_panel.export_started.connect(self.on_export_started)
        self.export_panel.export_finished.connect(self.on_export_finished)
        self.export_panel.setMaximumWidth(400)
        central_layout.addWidget(self.export_panel)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Status bar
        self.statusBar = QStatusBar()
        self.particle_label = QLabel("Particles: 0")
        self.fps_label = QLabel("FPS: 0")
        self.statusBar.addWidget(self.particle_label)
        self.statusBar.addPermanentWidget(self.fps_label)
        self.setStatusBar(self.statusBar)

    def load_settings(self):
        """Load settings from configuration"""
        particle_settings = self.config.get("particle_settings")
        visual_settings = self.config.get("visual_settings")
        audio_settings = self.config.get("audio_settings")

        self.particle_panel.load_settings(particle_settings)
        self.visual_panel.load_settings(visual_settings)
        self.audio_panel.load_settings(audio_settings)

        # Apply to preview
        self.preview.apply_settings(self.config)

    def on_particle_settings_changed(self, settings):
        """Handle particle settings change"""
        for key, value in settings.items():
            self.config.set("particle_settings", key, value=value)
        self.config.save_config()
        self.preview.apply_settings(self.config)

    def on_visual_settings_changed(self, settings):
        """Handle visual settings change"""
        for key, value in settings.items():
            self.config.set("visual_settings", key, value=value)
        self.config.save_config()
        self.preview.apply_settings(self.config)

    def on_audio_settings_changed(self, settings):
        """Handle audio settings change"""
        for key, value in settings.items():
            self.config.set("audio_settings", key, value=value)
        self.config.save_config()

    def on_particle_count_changed(self, count):
        """Update particle count in status bar"""
        self.particle_label.setText(f"Particles: {count}")

    def on_fps_changed(self, fps):
        """Update FPS in status bar"""
        self.fps_label.setText(f"FPS: {fps:.1f}")

    def on_export_started(self):
        """Handle export started"""
        self.preview.pause()

    def on_export_finished(self, output_path):
        """Handle export finished"""
        pass

    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, 'Exit Application',
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

