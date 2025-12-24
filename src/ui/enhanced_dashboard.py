"""Enhanced dashboard with improved UI and color scheme selection"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QLabel, QSlider, QSpinBox, QComboBox, QCheckBox, QPushButton,
    QStatusBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from src.utils.config import ConfigManager
from src.colors_enhanced import ColorScheme
from src.ui.enhanced_preview import SimplePreview


class EnhancedDashboard(QMainWindow):
    """Enhanced dashboard with color scheme support"""

    def __init__(self):
        super().__init__()

        try:
            self.config = ConfigManager()
            self.init_ui()
            self.load_settings()

            self.setWindowTitle("3D Particle Collision Generator - Enhanced")
            self.setMinimumSize(QSize(1400, 900))
            self.resize(1400, 900)

        except Exception as e:
            print(f"Error initializing dashboard: {e}")
            import traceback
            traceback.print_exc()
            raise

    def init_ui(self):
        """Initialize user interface"""
        main_layout = QHBoxLayout()

        # Left panel
        left_panel = self.create_settings_panel()
        left_panel.setMaximumWidth(320)
        main_layout.addWidget(left_panel)

        # Center - Preview
        self.preview = SimplePreview(color_scheme="ocean")
        self.preview.object_count_changed.connect(self.on_object_count_changed)
        self.preview.fps_changed.connect(self.on_fps_changed)
        main_layout.addWidget(self.preview, 1)

        # Right panel
        right_panel = self.create_advanced_panel()
        right_panel.setMaximumWidth(250)
        main_layout.addWidget(right_panel)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Status bar
        self.statusBar = QStatusBar()
        self.object_label = QLabel("Objects: 2/50")
        self.fps_label = QLabel("FPS: 60")
        self.statusBar.addWidget(self.object_label)
        self.statusBar.addPermanentWidget(self.fps_label)
        self.setStatusBar(self.statusBar)

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
        self.color_combo.addItems(ColorScheme.get_available_schemes())
        self.color_combo.currentTextChanged.connect(self.on_color_scheme_changed)
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

        # Visual Effects
        self.shadows_check = QCheckBox("3D Shadows")
        self.shadows_check.setChecked(True)
        self.shadows_check.stateChanged.connect(self.on_visual_settings_changed)
        layout.addWidget(self.shadows_check)

        self.reflections_check = QCheckBox("Reflections")
        self.reflections_check.setChecked(True)
        self.reflections_check.stateChanged.connect(self.on_visual_settings_changed)
        layout.addWidget(self.reflections_check)

        self.gloss_check = QCheckBox("Gloss Effect")
        self.gloss_check.setChecked(True)
        self.gloss_check.stateChanged.connect(self.on_visual_settings_changed)
        layout.addWidget(self.gloss_check)

        # Info
        layout.addWidget(QLabel("\nInfo:"))
        info_text = QLabel(
            "- 2 starting objects\n"
            "- Collisions create objects\n"
            "- Speed increases over time\n"
            "- Smooth bounces & physics\n"
            "- Calming music included"
        )
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Arial", 9))
        layout.addWidget(info_text)

        # Save Preset
        layout.addWidget(QLabel("\nSave Settings:"))
        self.save_preset_btn = QPushButton("Save as Preset")
        self.save_preset_btn.clicked.connect(self.save_preset)
        layout.addWidget(self.save_preset_btn)

        self.reset_btn = QPushButton("Reset to Default")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(self.reset_btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def on_color_scheme_changed(self):
        """Handle color scheme change"""
        scheme_name = self.color_combo.currentText()
        self.preview.set_color_scheme(scheme_name)

    def on_settings_changed(self):
        """Handle settings change"""
        if not self.config or not self.preview.engine:
            return

        self.config.set("visual_settings", "boundary_type",
                       value=self.boundary_combo.currentText().lower())
        self.config.set("visual_settings", "object_shape",
                       value=self.shape_combo.currentText().lower())
        self.config.set("particle_settings", "max_particles",
                       value=self.max_objects_spin.value())
        self.config.save_config()

        self.preview.engine.boundary_type = self.boundary_combo.currentText().lower()
        self.preview.engine.object_shape = self.shape_combo.currentText()
        self.preview.engine.set_max_objects(self.max_objects_spin.value())

    def on_audio_settings_changed(self):
        """Handle audio settings change"""
        if not self.preview.audio_manager:
            return

        self.preview.audio_manager.mute_all = self.mute_check.isChecked()
        self.preview.audio_manager.master_volume = self.volume_slider.value() / 100.0
        self.preview.audio_manager.collision_volume = self.collision_slider.value() / 100.0
        self.preview.audio_manager.bounce_volume = self.bounce_slider.value() / 100.0

    def on_visual_settings_changed(self):
        """Handle visual settings change"""
        pass

    def on_object_count_changed(self, count):
        """Update object count in status bar"""
        if self.preview.engine:
            max_count = self.preview.engine.max_objects
            self.object_label.setText(f"Objects: {count}/{max_count}")

    def on_fps_changed(self, fps):
        """Update FPS in status bar"""
        self.fps_label.setText(f"FPS: {fps:.1f}")

    def load_settings(self):
        """Load saved settings"""
        visual_settings = self.config.get("visual_settings", default={})

        boundary = visual_settings.get("boundary_type", "circle").capitalize()
        idx = self.boundary_combo.findText(boundary)
        if idx >= 0:
            self.boundary_combo.setCurrentIndex(idx)

        shape = visual_settings.get("object_shape", "sphere")
        idx = self.shape_combo.findText(shape)
        if idx >= 0:
            self.shape_combo.setCurrentIndex(idx)

    def save_preset(self):
        """Save current settings as preset"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox

        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            if self.config:
                self.config.save_preset(name)
            QMessageBox.information(self, "Success", f"Preset '{name}' saved!")

    def reset_to_defaults(self):
        """Reset to default settings"""
        from PyQt5.QtWidgets import QMessageBox

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

