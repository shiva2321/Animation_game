"""Control panel widgets for PyQt5"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox,
    QComboBox, QCheckBox, QGroupBox, QPushButton, QDoubleSpinBox,
    QColorDialog, QStyleFactory
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from src.utils.shapes import get_available_shapes
from src.utils.colors import get_available_schemes


class ParticleControlPanel(QGroupBox):
    """Control panel for particle settings"""

    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__("Particle Settings", parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Spawn Rate
        spawn_layout = QHBoxLayout()
        spawn_layout.addWidget(QLabel("Spawn Rate (particles/sec):"))
        self.spawn_rate_slider = QSlider(Qt.Horizontal)
        self.spawn_rate_slider.setRange(1, 20)
        self.spawn_rate_slider.setValue(5)
        self.spawn_rate_slider.valueChanged.connect(self.on_setting_changed)
        spawn_layout.addWidget(self.spawn_rate_slider)
        self.spawn_rate_label = QLabel("5")
        spawn_layout.addWidget(self.spawn_rate_label)
        layout.addLayout(spawn_layout)

        # Max Particles
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Max Particles:"))
        self.max_particles_slider = QSlider(Qt.Horizontal)
        self.max_particles_slider.setRange(10, 200)
        self.max_particles_slider.setValue(100)
        self.max_particles_slider.valueChanged.connect(self.on_setting_changed)
        max_layout.addWidget(self.max_particles_slider)
        self.max_particles_label = QLabel("100")
        max_layout.addWidget(self.max_particles_label)
        layout.addLayout(max_layout)

        # Initial Particles
        initial_layout = QHBoxLayout()
        initial_layout.addWidget(QLabel("Initial Particles:"))
        self.initial_particles_slider = QSlider(Qt.Horizontal)
        self.initial_particles_slider.setRange(1, 50)
        self.initial_particles_slider.setValue(10)
        self.initial_particles_slider.valueChanged.connect(self.on_setting_changed)
        initial_layout.addWidget(self.initial_particles_slider)
        self.initial_particles_label = QLabel("10")
        initial_layout.addWidget(self.initial_particles_label)
        layout.addLayout(initial_layout)

        # Particle Size Range
        size_layout = QVBoxLayout()
        size_layout.addWidget(QLabel("Particle Size Range:"))

        min_size_layout = QHBoxLayout()
        min_size_layout.addWidget(QLabel("Min:"))
        self.min_size_slider = QSlider(Qt.Horizontal)
        self.min_size_slider.setRange(1, 20)
        self.min_size_slider.setValue(3)
        self.min_size_slider.valueChanged.connect(self.on_setting_changed)
        min_size_layout.addWidget(self.min_size_slider)
        self.min_size_label = QLabel("3")
        min_size_layout.addWidget(self.min_size_label)
        size_layout.addLayout(min_size_layout)

        max_size_layout = QHBoxLayout()
        max_size_layout.addWidget(QLabel("Max:"))
        self.max_size_slider = QSlider(Qt.Horizontal)
        self.max_size_slider.setRange(1, 30)
        self.max_size_slider.setValue(15)
        self.max_size_slider.valueChanged.connect(self.on_setting_changed)
        max_size_layout.addWidget(self.max_size_slider)
        self.max_size_label = QLabel("15")
        max_size_layout.addWidget(self.max_size_label)
        size_layout.addLayout(max_size_layout)

        layout.addLayout(size_layout)

        # Particle Speed Range
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel("Particle Speed Range:"))

        min_speed_layout = QHBoxLayout()
        min_speed_layout.addWidget(QLabel("Min:"))
        self.min_speed_slider = QSlider(Qt.Horizontal)
        self.min_speed_slider.setRange(0, 50)
        self.min_speed_slider.setValue(1)
        self.min_speed_slider.valueChanged.connect(self.on_setting_changed)
        min_speed_layout.addWidget(self.min_speed_slider)
        self.min_speed_label = QLabel("1")
        min_speed_layout.addWidget(self.min_speed_label)
        speed_layout.addLayout(min_speed_layout)

        max_speed_layout = QHBoxLayout()
        max_speed_layout.addWidget(QLabel("Max:"))
        self.max_speed_slider = QSlider(Qt.Horizontal)
        self.max_speed_slider.setRange(0, 50)
        self.max_speed_slider.setValue(5)
        self.max_speed_slider.valueChanged.connect(self.on_setting_changed)
        max_speed_layout.addWidget(self.max_speed_slider)
        self.max_speed_label = QLabel("5")
        max_speed_layout.addWidget(self.max_speed_label)
        speed_layout.addLayout(max_speed_layout)

        layout.addLayout(speed_layout)

        # Shape
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("Particle Shape:"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(get_available_shapes())
        self.shape_combo.currentTextChanged.connect(self.on_setting_changed)
        shape_layout.addWidget(self.shape_combo)
        layout.addLayout(shape_layout)

        self.setLayout(layout)

    def on_setting_changed(self):
        """Emit settings changed signal"""
        self.spawn_rate_label.setText(str(self.spawn_rate_slider.value()))
        self.max_particles_label.setText(str(self.max_particles_slider.value()))
        self.initial_particles_label.setText(str(self.initial_particles_slider.value()))
        self.min_size_label.setText(str(self.min_size_slider.value()))
        self.max_size_label.setText(str(self.max_size_slider.value()))
        self.min_speed_label.setText(str(self.min_speed_slider.value() / 10.0))
        self.max_speed_label.setText(str(self.max_speed_slider.value() / 10.0))

        self.settings_changed.emit({
            "spawn_rate": self.spawn_rate_slider.value(),
            "max_particles": self.max_particles_slider.value(),
            "initial_particles": self.initial_particles_slider.value(),
            "min_size": self.min_size_slider.value(),
            "max_size": self.max_size_slider.value(),
            "min_speed": self.min_speed_slider.value() / 10.0,
            "max_speed": self.max_speed_slider.value() / 10.0,
            "shape": self.shape_combo.currentText(),
        })

    def load_settings(self, settings):
        """Load settings into UI"""
        self.spawn_rate_slider.setValue(settings.get("spawn_rate", 5))
        self.max_particles_slider.setValue(settings.get("max_particles", 100))
        self.initial_particles_slider.setValue(settings.get("initial_particles", 10))
        self.min_size_slider.setValue(settings.get("min_size", 3))
        self.max_size_slider.setValue(settings.get("max_size", 15))
        self.min_speed_slider.setValue(int(settings.get("min_speed", 1) * 10))
        self.max_speed_slider.setValue(int(settings.get("max_speed", 5) * 10))

        shape = settings.get("shape", "Circle")
        index = self.shape_combo.findText(shape)
        if index >= 0:
            self.shape_combo.setCurrentIndex(index)


class VisualControlPanel(QGroupBox):
    """Control panel for visual settings"""

    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__("Visual Settings", parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Color Scheme
        scheme_layout = QHBoxLayout()
        scheme_layout.addWidget(QLabel("Color Scheme:"))
        self.scheme_combo = QComboBox()
        self.scheme_combo.addItems(get_available_schemes())
        self.scheme_combo.currentTextChanged.connect(self.on_setting_changed)
        scheme_layout.addWidget(self.scheme_combo)
        layout.addLayout(scheme_layout)

        # Boundary Style
        boundary_layout = QHBoxLayout()
        boundary_layout.addWidget(QLabel("Boundary Style:"))
        self.boundary_combo = QComboBox()
        self.boundary_combo.addItems(["Solid", "Dashed", "Glow", "None"])
        self.boundary_combo.currentTextChanged.connect(self.on_setting_changed)
        boundary_layout.addWidget(self.boundary_combo)
        layout.addLayout(boundary_layout)

        # Effects
        self.glow_check = QCheckBox("Enable Glow")
        self.glow_check.setChecked(True)
        self.glow_check.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.glow_check)

        self.trails_check = QCheckBox("Enable Trails")
        self.trails_check.setChecked(True)
        self.trails_check.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.trails_check)

        # Trail Length
        trail_layout = QHBoxLayout()
        trail_layout.addWidget(QLabel("Trail Length:"))
        self.trail_slider = QSlider(Qt.Horizontal)
        self.trail_slider.setRange(5, 50)
        self.trail_slider.setValue(20)
        self.trail_slider.valueChanged.connect(self.on_setting_changed)
        trail_layout.addWidget(self.trail_slider)
        self.trail_label = QLabel("20")
        trail_layout.addWidget(self.trail_label)
        layout.addLayout(trail_layout)

        # Collision Effect
        effect_layout = QHBoxLayout()
        effect_layout.addWidget(QLabel("Collision Effect:"))
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["Ripple", "Sparkle", "Burst", "Wave"])
        self.effect_combo.currentTextChanged.connect(self.on_setting_changed)
        effect_layout.addWidget(self.effect_combo)
        layout.addLayout(effect_layout)

        self.blur_check = QCheckBox("Motion Blur")
        self.blur_check.setChecked(False)
        self.blur_check.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.blur_check)

        self.setLayout(layout)

    def on_setting_changed(self):
        """Emit settings changed signal"""
        self.trail_label.setText(str(self.trail_slider.value()))

        self.settings_changed.emit({
            "color_scheme": self.scheme_combo.currentText(),
            "boundary_style": self.boundary_combo.currentText(),
            "enable_glow": self.glow_check.isChecked(),
            "enable_trails": self.trails_check.isChecked(),
            "trail_length": self.trail_slider.value(),
            "collision_effect": self.effect_combo.currentText(),
            "motion_blur": self.blur_check.isChecked(),
        })

    def load_settings(self, settings):
        """Load settings into UI"""
        scheme = settings.get("color_scheme", "Pastel Dreams")
        index = self.scheme_combo.findText(scheme)
        if index >= 0:
            self.scheme_combo.setCurrentIndex(index)

        boundary = settings.get("boundary_style", "Solid")
        index = self.boundary_combo.findText(boundary)
        if index >= 0:
            self.boundary_combo.setCurrentIndex(index)

        self.glow_check.setChecked(settings.get("enable_glow", True))
        self.trails_check.setChecked(settings.get("enable_trails", True))
        self.trail_slider.setValue(settings.get("trail_length", 20))

        effect = settings.get("collision_effect", "Sparkle")
        index = self.effect_combo.findText(effect)
        if index >= 0:
            self.effect_combo.setCurrentIndex(index)

        self.blur_check.setChecked(settings.get("motion_blur", False))


class AudioControlPanel(QGroupBox):
    """Control panel for audio settings"""

    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__("Audio Settings", parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Instrument
        instr_layout = QHBoxLayout()
        instr_layout.addWidget(QLabel("Instrument:"))
        self.instrument_combo = QComboBox()
        self.instrument_combo.addItems(["Piano", "Violin", "Synth", "Mixed"])
        self.instrument_combo.currentTextChanged.connect(self.on_setting_changed)
        instr_layout.addWidget(self.instrument_combo)
        layout.addLayout(instr_layout)

        # Master Volume
        master_layout = QHBoxLayout()
        master_layout.addWidget(QLabel("Master Volume:"))
        self.master_volume_slider = QSlider(Qt.Horizontal)
        self.master_volume_slider.setRange(0, 100)
        self.master_volume_slider.setValue(50)
        self.master_volume_slider.valueChanged.connect(self.on_setting_changed)
        master_layout.addWidget(self.master_volume_slider)
        self.master_volume_label = QLabel("50%")
        master_layout.addWidget(self.master_volume_label)
        layout.addLayout(master_layout)

        # Collision Volume
        collision_layout = QHBoxLayout()
        collision_layout.addWidget(QLabel("Collision Volume:"))
        self.collision_volume_slider = QSlider(Qt.Horizontal)
        self.collision_volume_slider.setRange(0, 100)
        self.collision_volume_slider.setValue(70)
        self.collision_volume_slider.valueChanged.connect(self.on_setting_changed)
        collision_layout.addWidget(self.collision_volume_slider)
        self.collision_volume_label = QLabel("70%")
        collision_layout.addWidget(self.collision_volume_label)
        layout.addLayout(collision_layout)

        # Spawn Volume
        spawn_layout = QHBoxLayout()
        spawn_layout.addWidget(QLabel("Spawn Volume:"))
        self.spawn_volume_slider = QSlider(Qt.Horizontal)
        self.spawn_volume_slider.setRange(0, 100)
        self.spawn_volume_slider.setValue(30)
        self.spawn_volume_slider.valueChanged.connect(self.on_setting_changed)
        spawn_layout.addWidget(self.spawn_volume_slider)
        self.spawn_volume_label = QLabel("30%")
        spawn_layout.addWidget(self.spawn_volume_label)
        layout.addLayout(spawn_layout)

        # Ambient Volume
        ambient_layout = QHBoxLayout()
        ambient_layout.addWidget(QLabel("Ambient Volume:"))
        self.ambient_volume_slider = QSlider(Qt.Horizontal)
        self.ambient_volume_slider.setRange(0, 100)
        self.ambient_volume_slider.setValue(20)
        self.ambient_volume_slider.valueChanged.connect(self.on_setting_changed)
        ambient_layout.addWidget(self.ambient_volume_slider)
        self.ambient_volume_label = QLabel("20%")
        ambient_layout.addWidget(self.ambient_volume_label)
        layout.addLayout(ambient_layout)

        # Reverb
        self.reverb_check = QCheckBox("Enable Reverb")
        self.reverb_check.setChecked(True)
        self.reverb_check.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.reverb_check)

        # Mute All
        self.mute_check = QCheckBox("Mute All")
        self.mute_check.setChecked(False)
        self.mute_check.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.mute_check)

        self.setLayout(layout)

    def on_setting_changed(self):
        """Emit settings changed signal"""
        self.master_volume_label.setText(f"{self.master_volume_slider.value()}%")
        self.collision_volume_label.setText(f"{self.collision_volume_slider.value()}%")
        self.spawn_volume_label.setText(f"{self.spawn_volume_slider.value()}%")
        self.ambient_volume_label.setText(f"{self.ambient_volume_slider.value()}%")

        self.settings_changed.emit({
            "instrument": self.instrument_combo.currentText(),
            "master_volume": self.master_volume_slider.value() / 100.0,
            "collision_volume": self.collision_volume_slider.value() / 100.0,
            "spawn_volume": self.spawn_volume_slider.value() / 100.0,
            "ambient_volume": self.ambient_volume_slider.value() / 100.0,
            "enable_reverb": self.reverb_check.isChecked(),
            "mute_all": self.mute_check.isChecked(),
        })

    def load_settings(self, settings):
        """Load settings into UI"""
        instr = settings.get("instrument", "Piano")
        index = self.instrument_combo.findText(instr)
        if index >= 0:
            self.instrument_combo.setCurrentIndex(index)

        self.master_volume_slider.setValue(int(settings.get("master_volume", 0.5) * 100))
        self.collision_volume_slider.setValue(int(settings.get("collision_volume", 0.7) * 100))
        self.spawn_volume_slider.setValue(int(settings.get("spawn_volume", 0.3) * 100))
        self.ambient_volume_slider.setValue(int(settings.get("ambient_volume", 0.2) * 100))
        self.reverb_check.setChecked(settings.get("enable_reverb", True))
        self.mute_check.setChecked(settings.get("mute_all", False))

