
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QGroupBox, QFormLayout,
    QSlider, QCheckBox, QComboBox, QPushButton, QSpinBox, QLabel
)
from PyQt5.QtCore import Qt

from ..core.settings import Settings
from ..audio.synthesis import SCALES

class ControlsWidget(QWidget):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.is_advanced_mode = False

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()

        # Create tabs
        self.physics_tab = QWidget()
        self.visuals_tab = QWidget()
        self.audio_tab = QWidget()

        self.tab_widget.addTab(self.physics_tab, "Physics")
        self.tab_widget.addTab(self.visuals_tab, "Visuals")
        self.tab_widget.addTab(self.audio_tab, "Audio")

        # Populate tabs with controls
        self._populate_physics_tab()
        self._populate_visuals_tab()
        self._populate_audio_tab()

        # Mode toggle button
        self.mode_button = QPushButton("Show Advanced")
        self.mode_button.clicked.connect(self._toggle_mode)

        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.mode_button)

        self._update_visibility()

    def _populate_physics_tab(self):
        layout = QFormLayout(self.physics_tab)
        p = self.settings.physics

        # --- Basic Controls ---
        self.restitution_slider = self._create_slider(0, 100, p.restitution * 100)
        self.drag_slider = self._create_slider(0, 100, p.drag_coeff * 100)
        self.gravity_strength_slider = self._create_slider(0, 100, p.gravity_strength)

        layout.addRow("Elasticity:", self.restitution_slider)
        layout.addRow("Air Drag:", self.drag_slider)
        layout.addRow("Gravity:", self.gravity_strength_slider)

        # --- Advanced Controls ---
        self.max_speed_slider = self._create_slider(100, 5000, p.max_speed)
        self.brownian_checkbox = QCheckBox()
        self.brownian_checkbox.setChecked(p.brownian_enabled)
        self.vortex_checkbox = QCheckBox()
        self.vortex_checkbox.setChecked(p.vortex_enabled)

        self.adv_physics_widgets = [
            QLabel("Max Speed:"), self.max_speed_slider,
            QLabel("Brownian Motion:"), self.brownian_checkbox,
            QLabel("Vortex Force:"), self.vortex_checkbox
        ]
        layout.addRow("Max Speed:", self.max_speed_slider)
        layout.addRow("Brownian Motion:", self.brownian_checkbox)
        layout.addRow("Vortex Force:", self.vortex_checkbox)

    def _populate_visuals_tab(self):
        layout = QFormLayout(self.visuals_tab)
        v = self.settings.visuals
        p = self.settings.particles

        # --- Basic Controls ---
        self.scheme_combo = QComboBox()
        self.scheme_combo.addItems(["cosmic", "ocean", "neon"])
        self.scheme_combo.setCurrentText(v.scheme_name)

        self.particle_count_slider = self._create_slider(10, 500, p.max_particles)
        self.trails_toggle = QCheckBox()
        self.trails_toggle.setChecked(v.trails_toggle)

        layout.addRow("Color Scheme:", self.scheme_combo)
        layout.addRow("Particle Count:", self.particle_count_slider)
        layout.addRow("Enable Trails:", self.trails_toggle)

        # --- Advanced Controls ---
        self.glow_toggle = QCheckBox()
        self.glow_toggle.setChecked(v.glow_toggle)
        self.glow_intensity_slider = self._create_slider(0, 100, v.glow_intensity * 100)

        self.adv_visual_widgets = [
            QLabel("Enable Glow:"), self.glow_toggle,
            QLabel("Glow Intensity:"), self.glow_intensity_slider,
        ]
        layout.addRow("Enable Glow:", self.glow_toggle)
        layout.addRow("Glow Intensity:", self.glow_intensity_slider)

    def _populate_audio_tab(self):
        layout = QFormLayout(self.audio_tab)
        a = self.settings.audio

        self.audio_enabled_check = QCheckBox()
        self.audio_enabled_check.setChecked(a.enabled)

        self.instrument_combo = QComboBox()
        self.instrument_combo.addItems(["piano", "violin", "bell", "soft_pad"])
        self.instrument_combo.setCurrentText(a.instrument)

        self.scale_combo = QComboBox()
        self.scale_combo.addItems(list(SCALES.keys()))
        self.scale_combo.setCurrentText(a.scale)

        self.reverb_toggle = QCheckBox()
        self.reverb_toggle.setChecked(a.reverb_enabled)

        layout.addRow("Enable Audio:", self.audio_enabled_check)
        layout.addRow("Instrument:", self.instrument_combo)
        layout.addRow("Musical Scale:", self.scale_combo)
        layout.addRow("Enable Reverb:", self.reverb_toggle)

        # Advanced audio controls are minimal here
        self.adv_audio_widgets = []

    def update_controls_from_settings(self):
        """Updates all control widgets to reflect the current self.settings object."""
        # Physics
        self.restitution_slider.setValue(int(self.settings.physics.restitution * 100))
        self.drag_slider.setValue(int(self.settings.physics.drag_coeff * 100))
        self.gravity_strength_slider.setValue(int(self.settings.physics.gravity_strength))
        self.max_speed_slider.setValue(int(self.settings.physics.max_speed))
        self.brownian_checkbox.setChecked(self.settings.physics.brownian_enabled)
        self.vortex_checkbox.setChecked(self.settings.physics.vortex_enabled)

        # Visuals
        self.scheme_combo.setCurrentText(self.settings.visuals.scheme_name)
        self.particle_count_slider.setValue(self.settings.particles.max_particles)
        self.trails_toggle.setChecked(self.settings.visuals.trails_toggle)
        self.glow_toggle.setChecked(self.settings.visuals.glow_toggle)
        self.glow_intensity_slider.setValue(int(self.settings.visuals.glow_intensity * 100))

        # Audio
        self.audio_enabled_check.setChecked(self.settings.audio.enabled)
        self.instrument_combo.setCurrentText(self.settings.audio.instrument)
        self.scale_combo.setCurrentText(self.settings.audio.scale)
        self.reverb_toggle.setChecked(self.settings.audio.reverb_enabled)

    def _create_slider(self, min_val, max_val, current_val):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(int(current_val))
        return slider

    def _toggle_mode(self):
        self.is_advanced_mode = not self.is_advanced_mode
        self._update_visibility()
        self.mode_button.setText("Show Basic" if self.is_advanced_mode else "Show Advanced")

    def _update_visibility(self):
        for widget in self.adv_physics_widgets + self.adv_visual_widgets + self.adv_audio_widgets:
            widget.setVisible(self.is_advanced_mode)

    def connect_signals(self, update_callback):
        # Physics
        self.restitution_slider.valueChanged.connect(lambda v: setattr(self.settings.physics, 'restitution', v / 100.0) or update_callback())
        self.drag_slider.valueChanged.connect(lambda v: setattr(self.settings.physics, 'drag_coeff', v / 100.0) or update_callback())
        self.gravity_strength_slider.valueChanged.connect(lambda v: setattr(self.settings.physics, 'gravity_strength', v) or update_callback())
        self.max_speed_slider.valueChanged.connect(lambda v: setattr(self.settings.physics, 'max_speed', v) or update_callback())
        self.brownian_checkbox.stateChanged.connect(lambda s: setattr(self.settings.physics, 'brownian_enabled', s == Qt.Checked) or update_callback())
        self.vortex_checkbox.stateChanged.connect(lambda s: setattr(self.settings.physics, 'vortex_enabled', s == Qt.Checked) or update_callback())

        # Visuals
        self.scheme_combo.currentTextChanged.connect(lambda t: setattr(self.settings.visuals, 'scheme_name', t) or update_callback())
        self.particle_count_slider.valueChanged.connect(lambda v: setattr(self.settings.particles, 'max_particles', v) or update_callback())
        self.trails_toggle.stateChanged.connect(lambda s: setattr(self.settings.visuals, 'trails_toggle', s == Qt.Checked) or update_callback())
        self.glow_toggle.stateChanged.connect(lambda s: setattr(self.settings.visuals, 'glow_toggle', s == Qt.Checked) or update_callback())
        self.glow_intensity_slider.valueChanged.connect(lambda v: setattr(self.settings.visuals, 'glow_intensity', v / 100.0) or update_callback())

        # Audio
        self.audio_enabled_check.stateChanged.connect(lambda s: setattr(self.settings.audio, 'enabled', s == Qt.Checked) or update_callback())
        self.instrument_combo.currentTextChanged.connect(lambda t: setattr(self.settings.audio, 'instrument', t) or update_callback())
        self.scale_combo.currentTextChanged.connect(lambda t: setattr(self.settings.audio, 'scale', t) or update_callback())
        self.reverb_toggle.stateChanged.connect(lambda s: setattr(self.settings.audio, 'reverb_enabled', s == Qt.Checked) or update_callback())
