"""Simplified 3D Dashboard - Stable Version"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QLabel, QSlider, QSpinBox, QComboBox, QCheckBox, QPushButton,
    QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont

from src.utils.config import ConfigManager
from src.utils.colors import get_available_schemes


class Dashboard3D(QMainWindow):
    """Simplified 3D dashboard - stable version"""

    def __init__(self):
        super().__init__()

        print("Dashboard: Starting initialization...")

        # Create window first
        self.setWindowTitle("3D Particle Collision Generator")
        self.setMinimumSize(QSize(1400, 900))
        self.resize(1400, 900)

        # Configuration
        try:
            self.config = ConfigManager()
            print("Dashboard: Config loaded")
        except Exception as e:
            print(f"Dashboard: Config error: {e}")
            self.config = None

        # Initialize UI components
        try:
            self.init_ui()
            print("Dashboard: UI initialized")
        except Exception as e:
            print(f"Dashboard: UI error: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Load settings
        try:
            if self.config:
                self.load_settings()
            print("Dashboard: Settings loaded")
        except Exception as e:
            print(f"Dashboard: Settings error: {e}")

    def init_ui(self):
        """Initialize user interface"""
        # Main layout
        main_layout = QHBoxLayout()

        # Left panel - Settings
        try:
            left_panel = self.create_settings_panel()
            left_panel.setMaximumWidth(320)
            main_layout.addWidget(left_panel)
            print("Dashboard: Left panel created")
        except Exception as e:
            print(f"Dashboard: Left panel error: {e}")
            raise

        # Center - 3D Preview (deferred creation)
        try:
            from src.ui.preview_improved import PreviewImproved
            self.preview = PreviewImproved()
            self.preview.object_count_changed.connect(self.on_object_count_changed)
            self.preview.fps_changed.connect(self.on_fps_changed)
            main_layout.addWidget(self.preview, 1)
            print("Dashboard: Preview created")
        except Exception as e:
            print(f"Dashboard: Preview error: {e}")
            # Create placeholder
            placeholder = QLabel("Preview unavailable")
            main_layout.addWidget(placeholder, 1)
            self.preview = None

        # Right panel - Advanced Settings
        try:
            right_panel = self.create_advanced_panel()
            right_panel.setMaximumWidth(250)
            main_layout.addWidget(right_panel)
            print("Dashboard: Right panel created")
        except Exception as e:
            print(f"Dashboard: Right panel error: {e}")
            raise

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Status bar
        try:
            self.statusBar = QStatusBar()
            self.object_label = QLabel("Objects: 2/50")
            self.fps_label = QLabel("FPS: 60")
            self.statusBar.addWidget(self.object_label)
            self.statusBar.addPermanentWidget(self.fps_label)
            self.setStatusBar(self.statusBar)
            print("Dashboard: Status bar created")
        except Exception as e:
            print(f"Dashboard: Status bar error: {e}")

    def create_settings_panel(self):
        """Create left settings panel"""
        panel = QGroupBox("Settings")
        layout = QVBoxLayout()

        # Boundary Type
        layout.addWidget(QLabel("Boundary Type:"))
        self.boundary_combo = QComboBox()
        self.boundary_combo.addItems(["Circle", "Square", "Triangle"])
        self.boundary_combo.currentTextChanged.connect(self.on_settings_changed)
        layout.addWidget(self.boundary_combo)

        # Object Shape
        layout.addWidget(QLabel("Object Shape:"))
        self.shape_combo = QComboBox()
        shapes = ["sphere", "cube", "star", "triangle"]
        self.shape_combo.addItems(shapes)
        self.shape_combo.currentTextChanged.connect(self.on_settings_changed)
        layout.addWidget(self.shape_combo)

        # Color Scheme
        layout.addWidget(QLabel("Color Scheme:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(get_available_schemes())
        self.color_combo.currentTextChanged.connect(self.on_settings_changed)
        layout.addWidget(self.color_combo)

        # Max Objects
        layout.addWidget(QLabel("Max Objects:"))
        self.max_objects_spin = QSpinBox()
        self.max_objects_spin.setRange(5, 200)
        self.max_objects_spin.setValue(50)
        self.max_objects_spin.valueChanged.connect(self.on_settings_changed)
        layout.addWidget(self.max_objects_spin)

        # Object Size
        layout.addWidget(QLabel("Object Size (px):"))
        size_layout = QHBoxLayout()

        size_layout.addWidget(QLabel("Min:"))
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(2, 30)
        self.min_size_spin.setValue(5)
        self.min_size_spin.valueChanged.connect(self.on_settings_changed)
        size_layout.addWidget(self.min_size_spin)

        size_layout.addWidget(QLabel("Max:"))
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(5, 50)
        self.max_size_spin.setValue(15)
        self.max_size_spin.valueChanged.connect(self.on_settings_changed)
        size_layout.addWidget(self.max_size_spin)

        layout.addLayout(size_layout)

        # Initial Speed
        layout.addWidget(QLabel("Initial Speed (px/s):"))
        speed_layout = QHBoxLayout()

        speed_layout.addWidget(QLabel("Min:"))
        self.min_speed_spin = QSpinBox()
        self.min_speed_spin.setRange(1, 20)
        self.min_speed_spin.setValue(2)
        self.min_speed_spin.valueChanged.connect(self.on_settings_changed)
        speed_layout.addWidget(self.min_speed_spin)

        speed_layout.addWidget(QLabel("Max:"))
        self.max_speed_spin = QSpinBox()
        self.max_speed_spin.setRange(2, 30)
        self.max_speed_spin.setValue(4)
        self.max_speed_spin.valueChanged.connect(self.on_settings_changed)
        speed_layout.addWidget(self.max_speed_spin)

        layout.addLayout(speed_layout)

        # Audio Controls
        layout.addWidget(QLabel("\nAudio Controls:"))

        self.mute_check = QCheckBox("Mute All Sounds")
        self.mute_check.stateChanged.connect(self.on_audio_settings_changed)
        layout.addWidget(self.mute_check)

        # Volume
        layout.addWidget(QLabel("Master Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(60)
        self.volume_slider.valueChanged.connect(self.on_audio_settings_changed)
        layout.addWidget(self.volume_slider)

        # Collision Volume
        layout.addWidget(QLabel("Collision Tone:"))
        self.collision_slider = QSlider(Qt.Horizontal)
        self.collision_slider.setRange(0, 100)
        self.collision_slider.setValue(80)
        self.collision_slider.valueChanged.connect(self.on_audio_settings_changed)
        layout.addWidget(self.collision_slider)

        # Bounce Volume
        layout.addWidget(QLabel("Bounce Tone:"))
        self.bounce_slider = QSlider(Qt.Horizontal)
        self.bounce_slider.setRange(0, 100)
        self.bounce_slider.setValue(40)
        self.bounce_slider.valueChanged.connect(self.on_audio_settings_changed)
        layout.addWidget(self.bounce_slider)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_advanced_panel(self):
        """Create right advanced settings panel"""
        panel = QGroupBox("Advanced")
        layout = QVBoxLayout()

        # Enable Shadows
        self.shadows_check = QCheckBox("3D Shadows")
        self.shadows_check.setChecked(True)
        self.shadows_check.stateChanged.connect(self.on_visual_settings_changed)
        layout.addWidget(self.shadows_check)

        # Enable Reflections
        self.reflections_check = QCheckBox("Reflections")
        self.reflections_check.setChecked(True)
        self.reflections_check.stateChanged.connect(self.on_visual_settings_changed)
        layout.addWidget(self.reflections_check)

        # Enable Gloss
        self.gloss_check = QCheckBox("Gloss Effect")
        self.gloss_check.setChecked(True)
        self.gloss_check.stateChanged.connect(self.on_visual_settings_changed)
        layout.addWidget(self.gloss_check)

        # Help Text
        layout.addWidget(QLabel("\nInfo:"))
        info_text = QLabel(
            "- Start with 2 objects\n"
            "- Collisions create new objects\n"
            "- Speed increases over time\n"
            "- Each bounce plays a tone\n"
            "- Click Play to begin"
        )
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Arial", 9))
        layout.addWidget(info_text)

        # Save Preset
        layout.addWidget(QLabel("\nSave Settings:"))
        self.save_preset_btn = QPushButton("Save as Preset")
        self.save_preset_btn.clicked.connect(self.save_preset)
        layout.addWidget(self.save_preset_btn)

        # Reset to Default
        self.reset_btn = QPushButton("Reset to Default")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(self.reset_btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def load_settings(self):
        """Load settings from config"""
        visual_settings = self.config.get("visual_settings", default={})
        particle_settings = self.config.get("particle_settings", default={})

        # Load visual settings
        boundary = visual_settings.get("boundary_type", "circle").capitalize()
        idx = self.boundary_combo.findText(boundary)
        if idx >= 0:
            self.boundary_combo.setCurrentIndex(idx)

        shape = visual_settings.get("object_shape", "sphere")
        idx = self.shape_combo.findText(shape)
        if idx >= 0:
            self.shape_combo.setCurrentIndex(idx)

        color = visual_settings.get("color_scheme", "Pastel Dreams")
        idx = self.color_combo.findText(color)
        if idx >= 0:
            self.color_combo.setCurrentIndex(idx)

        # Load particle settings
        self.max_objects_spin.setValue(particle_settings.get("max_particles", 50))
        self.min_size_spin.setValue(particle_settings.get("min_size", 5))
        self.max_size_spin.setValue(particle_settings.get("max_size", 15))
        self.min_speed_spin.setValue(particle_settings.get("min_speed", 2))
        self.max_speed_spin.setValue(particle_settings.get("max_speed", 4))

    def on_settings_changed(self):
        """Handle settings change"""
        if not self.config:
            return

        self.config.set("visual_settings", "boundary_type",
                       value=self.boundary_combo.currentText().lower())
        self.config.set("visual_settings", "object_shape",
                       value=self.shape_combo.currentText().lower())
        self.config.set("visual_settings", "color_scheme",
                       value=self.color_combo.currentText())
        self.config.set("particle_settings", "max_particles",
                       value=self.max_objects_spin.value())
        self.config.set("particle_settings", "min_size",
                       value=self.min_size_spin.value())
        self.config.set("particle_settings", "max_size",
                       value=self.max_size_spin.value())
        self.config.set("particle_settings", "min_speed",
                       value=self.min_speed_spin.value())
        self.config.set("particle_settings", "max_speed",
                       value=self.max_speed_spin.value())
        self.config.save_config()

        # Apply to preview if available
        if self.preview:
            self.preview.apply_settings(self.config)

    def on_audio_settings_changed(self):
        """Handle audio settings change"""
        if not self.config:
            return

        audio_settings = self.config.get("audio_settings", default={})

        audio_settings["mute_all"] = self.mute_check.isChecked()
        audio_settings["master_volume"] = self.volume_slider.value() / 100.0
        audio_settings["collision_volume"] = self.collision_slider.value() / 100.0
        audio_settings["bounce_volume"] = self.bounce_slider.value() / 100.0

        self.config.set("audio_settings", value=audio_settings)
        self.config.save_config()

        # Update audio manager if preview available
        if self.preview and self.preview.audio_manager:
            self.preview.audio_manager.mute_all = self.mute_check.isChecked()
            self.preview.audio_manager.master_volume = self.volume_slider.value() / 100.0
            self.preview.audio_manager.collision_volume = self.collision_slider.value() / 100.0
            self.preview.audio_manager.bounce_volume = self.bounce_slider.value() / 100.0

    def on_visual_settings_changed(self):
        """Handle visual settings change"""
        if self.preview and self.preview.renderer:
            self.preview.renderer.enable_shadows = self.shadows_check.isChecked()
            self.preview.renderer.enable_reflections = self.reflections_check.isChecked()
            self.preview.renderer.enable_gloss = self.gloss_check.isChecked()

    def on_object_count_changed(self, count):
        """Update object count in status bar"""
        if self.preview:
            max_count = self.preview.engine.max_objects if self.preview.engine else 50
            self.object_label.setText(f"Objects: {count}/{max_count}")

    def on_fps_changed(self, fps):
        """Update FPS in status bar"""
        self.fps_label.setText(f"FPS: {fps:.1f}")

    def save_preset(self):
        """Save current settings as preset"""
        from PyQt5.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            if self.config:
                self.config.save_preset(name)
            QMessageBox.information(self, "Success", f"Preset '{name}' saved!")

    def reset_to_defaults(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.config:
                self.config.reset_to_defaults()
                self.load_settings()
                self.on_settings_changed()

    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, "Exit",
            "Close application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

