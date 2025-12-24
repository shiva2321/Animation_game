"""
Control widgets for physics, visuals, and audio settings.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QGroupBox,
    QTabWidget, QPushButton, QScrollArea, QLineEdit, QFileDialog,
    QToolButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
import logging

from src.core.settings import AppSettings

logger = logging.getLogger(__name__)


class InfoButton(QToolButton):
    """Information button with tooltip."""

    def __init__(self, tooltip_text: str, parent=None):
        super().__init__(parent)
        self.setText("ℹ")
        self.setStyleSheet("""
            QToolButton {
                background-color: #0f3460;
                color: #00d4ff;
                border: 1px solid #00d4ff;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
                padding: 2px;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }
            QToolButton:hover {
                background-color: #00d4ff;
                color: #1a1a2e;
            }
        """)
        self.setToolTip(tooltip_text)
        self.clicked.connect(lambda: self.show_info(tooltip_text))

    def show_info(self, text):
        """Show information dialog."""
        QMessageBox.information(self, "Information", text)


class ControlsWidget(QWidget):
    """Main controls widget with tabs."""

    settings_changed = pyqtSignal(AppSettings)

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.widgets = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the control tabs."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #0f3460;
                background-color: #16213e;
            }
            QTabBar::tab {
                background-color: #0f3460;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #e94560;
            }
            QTabBar::tab:hover {
                background-color: #1a5490;
            }
        """)

        # Create tabs
        self.create_basic_tab()
        self.create_objects_tab()
        self.create_appearance_tab()
        self.create_audio_tab()
        self.create_export_tab()
        self.create_advanced_tab()

        layout.addWidget(self.tabs)

        # Apply/Reset buttons
        button_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_settings)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5577;
            }
        """)

        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1a5490;
            }
        """)

        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)

    def create_basic_tab(self):
        """Create basic settings tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Main Shape Group
        shape_group = QGroupBox("Main Container Shape")
        shape_layout = QVBoxLayout()

        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Shape:"))
        self.widgets['container_shape'] = QComboBox()
        self.widgets['container_shape'].addItems(['circle', 'square', 'triangle', 'polygon'])
        self.widgets['container_shape'].setCurrentText(self.settings.container_shape)
        shape_row.addWidget(self.widgets['container_shape'])
        shape_row.addWidget(InfoButton(
            "Container Shape:\n"
            "• Circle: Classic round boundary, smooth bouncing\n"
            "• Square: Rectangular container, corner interactions\n"
            "• Triangle: Three-sided, unique dynamics\n"
            "• Polygon: Multi-sided (hexagon, octagon, etc.)"
        ))
        shape_layout.addLayout(shape_row)

        # Polygon sides (only for polygon)
        poly_row = QHBoxLayout()
        poly_row.addWidget(QLabel("Polygon Sides:"))
        self.widgets['polygon_sides'] = QSpinBox()
        self.widgets['polygon_sides'].setRange(5, 12)
        self.widgets['polygon_sides'].setValue(self.settings.polygon_sides)
        poly_row.addWidget(self.widgets['polygon_sides'])
        poly_row.addWidget(InfoButton("Number of sides for polygon shape (5-12)"))
        shape_layout.addLayout(poly_row)

        shape_group.setLayout(shape_layout)
        layout.addWidget(shape_group)

        # Animation Duration Group
        duration_group = QGroupBox("Animation Duration")
        duration_layout = QVBoxLayout()

        dur_row = QHBoxLayout()
        dur_row.addWidget(QLabel("Target Duration:"))
        self.widgets['duration_sec'] = QSpinBox()
        self.widgets['duration_sec'].setRange(30, 300)
        self.widgets['duration_sec'].setSuffix(" seconds")
        self.widgets['duration_sec'].setValue(self.settings.duration_sec)
        dur_row.addWidget(self.widgets['duration_sec'])
        dur_row.addWidget(InfoButton(
            "Animation Duration:\n"
            "Sets target video length (30s - 5min)\n"
            "The animation will:\n"
            "• Spawn objects dynamically\n"
            "• Gradually calm down\n"
            "• End naturally within this time\n\n"
            "Longer = more objects and action"
        ))
        duration_layout.addLayout(dur_row)

        # Quick presets
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Quick:"))
        for seconds, label in [(30, "30s"), (60, "1min"), (90, "1.5min"), (120, "2min")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=seconds: self.widgets['duration_sec'].setValue(s))
            preset_row.addWidget(btn)
        duration_layout.addLayout(preset_row)

        duration_group.setLayout(duration_layout)
        layout.addWidget(duration_group)

        layout.addStretch()
        self.tabs.addTab(scroll, "Basic")

    def create_objects_tab(self):
        """Create objects configuration tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Object Count Group
        count_group = QGroupBox("Object Count")
        count_layout = QVBoxLayout()

        # Initial count
        init_row = QHBoxLayout()
        init_row.addWidget(QLabel("Initial Objects:"))
        self.widgets['initial_count'] = QSpinBox()
        self.widgets['initial_count'].setRange(1, 10)
        self.widgets['initial_count'].setValue(self.settings.initial_count)
        init_row.addWidget(self.widgets['initial_count'])
        init_row.addWidget(InfoButton(
            "Initial Objects:\n"
            "Number of objects that drop at start\n"
            "Recommended: 2\n"
            "• 1: Single object (slow start)\n"
            "• 2: Ideal for collision spawning\n"
            "• 3-5: Multiple objects (faster action)\n"
            "• 6+: Crowded start"
        ))
        count_layout.addLayout(init_row)

        # Max count with slider
        max_row = QHBoxLayout()
        max_row.addWidget(QLabel("Max Objects:"))
        self.widgets['max_particles'] = QSpinBox()
        self.widgets['max_particles'].setRange(10, 500)
        self.widgets['max_particles'].setValue(self.settings.max_particles)
        max_row.addWidget(self.widgets['max_particles'])
        max_row.addWidget(InfoButton(
            "Maximum Objects:\n"
            "Total objects that can spawn\n"
            "• 10-30: Quick, simple videos\n"
            "• 30-80: Balanced (recommended)\n"
            "• 80-150: Lots of action\n"
            "• 150-300: Dense, chaotic\n"
            "• 300+: Performance heavy\n\n"
            "More objects = longer video"
        ))
        count_layout.addLayout(max_row)

        # Slider for max particles
        self.widgets['max_particles_slider'] = QSlider(Qt.Orientation.Horizontal)
        self.widgets['max_particles_slider'].setRange(10, 500)
        self.widgets['max_particles_slider'].setValue(self.settings.max_particles)
        self.widgets['max_particles_slider'].valueChanged.connect(
            lambda v: self.widgets['max_particles'].setValue(v)
        )
        self.widgets['max_particles'].valueChanged.connect(
            lambda v: self.widgets['max_particles_slider'].setValue(v)
        )
        count_layout.addWidget(self.widgets['max_particles_slider'])

        count_group.setLayout(count_layout)
        layout.addWidget(count_group)

        # Object Types Group
        types_group = QGroupBox("Object Types")
        types_layout = QVBoxLayout()

        types_layout.addWidget(QLabel("Select which objects can appear:"))

        self.object_checkboxes = {}
        object_types = [
            ('sphere', 'Sphere - Classic 3D ball'),
            ('rounded_star', 'Rounded Star - Smooth star shape'),
            ('hexagon', 'Hexagon - Six-sided polygon'),
            ('triangle', 'Triangle - Three-sided'),
            ('square', 'Square - Four-sided'),
            ('bubble', 'Bubble - Transparent with highlights')
        ]

        for obj_type, description in object_types:
            cb = QCheckBox(description)
            cb.setChecked(obj_type in self.settings.shapes)
            self.object_checkboxes[obj_type] = cb
            types_layout.addWidget(cb)

        types_group.setLayout(types_layout)
        layout.addWidget(types_group)

        # Size Group
        size_group = QGroupBox("Object Size")
        size_layout = QVBoxLayout()

        min_row = QHBoxLayout()
        min_row.addWidget(QLabel("Minimum Size:"))
        self.widgets['size_min'] = QDoubleSpinBox()
        self.widgets['size_min'].setRange(5.0, 50.0)
        self.widgets['size_min'].setValue(self.settings.size_min)
        self.widgets['size_min'].setSuffix(" px")
        min_row.addWidget(self.widgets['size_min'])
        min_row.addWidget(InfoButton("Smallest object size in pixels"))
        size_layout.addLayout(min_row)

        max_row = QHBoxLayout()
        max_row.addWidget(QLabel("Maximum Size:"))
        self.widgets['size_max'] = QDoubleSpinBox()
        self.widgets['size_max'].setRange(10.0, 100.0)
        self.widgets['size_max'].setValue(self.settings.size_max)
        self.widgets['size_max'].setSuffix(" px")
        max_row.addWidget(self.widgets['size_max'])
        max_row.addWidget(InfoButton("Largest object size in pixels"))
        size_layout.addLayout(max_row)

        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        layout.addStretch()
        self.tabs.addTab(scroll, "Objects")

    def create_appearance_tab(self):
        """Create appearance/visuals tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Color Scheme Group
        color_group = QGroupBox("Color Palette")
        color_layout = QVBoxLayout()

        scheme_row = QHBoxLayout()
        scheme_row.addWidget(QLabel("Palette:"))
        self.widgets['visual_scheme'] = QComboBox()
        self.widgets['visual_scheme'].addItems(['cosmic', 'ocean', 'neon', 'fire', 'forest', 'sunset', 'ice'])
        self.widgets['visual_scheme'].setCurrentText(self.settings.visual_scheme)
        scheme_row.addWidget(self.widgets['visual_scheme'])
        scheme_row.addWidget(InfoButton(
            "Color Palettes:\n"
            "• Cosmic: Deep blues, purples, space theme\n"
            "• Ocean: Blues, teals, aquatic\n"
            "• Neon: Bright pinks, greens, vibrant\n"
            "• Fire: Reds, oranges, yellows\n"
            "• Forest: Greens, browns, nature\n"
            "• Sunset: Warm oranges, pinks, purples\n"
            "• Ice: Cool blues, whites, crystalline"
        ))
        color_layout.addLayout(scheme_row)

        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        # 3D Effects Group
        effects_group = QGroupBox("3D Effects")
        effects_layout = QVBoxLayout()

        self.widgets['enable_3d_effect'] = QCheckBox("Enable 3D Shading")
        self.widgets['enable_3d_effect'].setChecked(self.settings.enable_3d_effect)
        effects_layout.addWidget(self.widgets['enable_3d_effect'])

        light_row = QHBoxLayout()
        light_row.addWidget(QLabel("Light Direction:"))
        self.widgets['light_direction'] = QDoubleSpinBox()
        self.widgets['light_direction'].setRange(0.0, 360.0)
        self.widgets['light_direction'].setValue(self.settings.light_direction)
        self.widgets['light_direction'].setSuffix("°")
        light_row.addWidget(self.widgets['light_direction'])
        light_row.addWidget(InfoButton(
            "Light Direction:\n"
            "Angle of light source in degrees\n"
            "• 0°: From right\n"
            "• 45°: From top-right (recommended)\n"
            "• 90°: From top\n"
            "• 270°: From bottom"
        ))
        effects_layout.addLayout(light_row)

        ambient_row = QHBoxLayout()
        ambient_row.addWidget(QLabel("Ambient Light:"))
        self.widgets['ambient_light'] = QDoubleSpinBox()
        self.widgets['ambient_light'].setRange(0.0, 1.0)
        self.widgets['ambient_light'].setSingleStep(0.05)
        self.widgets['ambient_light'].setValue(self.settings.ambient_light)
        ambient_row.addWidget(self.widgets['ambient_light'])
        ambient_row.addWidget(InfoButton(
            "Ambient Light:\n"
            "Base lighting level (0.0 - 1.0)\n"
            "• 0.0-0.2: Very dramatic shadows\n"
            "• 0.2-0.3: Good contrast (recommended)\n"
            "• 0.3-0.5: Moderate shadows\n"
            "• 0.5+: Flat appearance"
        ))
        effects_layout.addLayout(ambient_row)

        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)

        # Visual Effects Group
        fx_group = QGroupBox("Visual Effects")
        fx_layout = QVBoxLayout()

        self.widgets['glow_enabled'] = QCheckBox("Enable Glow")
        self.widgets['glow_enabled'].setChecked(self.settings.glow_enabled)
        fx_layout.addWidget(self.widgets['glow_enabled'])

        self.widgets['trails_enabled'] = QCheckBox("Enable Motion Trails")
        self.widgets['trails_enabled'].setChecked(self.settings.trails_enabled)
        fx_layout.addWidget(self.widgets['trails_enabled'])

        fx_group.setLayout(fx_layout)
        layout.addWidget(fx_group)

        layout.addStretch()
        self.tabs.addTab(scroll, "Appearance")

    def create_audio_tab(self):
        """Create audio settings tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Audio Enable
        self.widgets['audio_enabled'] = QCheckBox("Enable Audio")
        self.widgets['audio_enabled'].setChecked(self.settings.audio_enabled)
        layout.addWidget(self.widgets['audio_enabled'])

        # Instrument Group
        instrument_group = QGroupBox("Sound Instrument")
        instrument_layout = QVBoxLayout()

        inst_row = QHBoxLayout()
        inst_row.addWidget(QLabel("Instrument:"))
        self.widgets['audio_instrument'] = QComboBox()
        self.widgets['audio_instrument'].addItems(['piano', 'violin', 'bell', 'soft_pad', 'mixed'])
        self.widgets['audio_instrument'].setCurrentText(self.settings.audio_instrument)
        inst_row.addWidget(self.widgets['audio_instrument'])
        inst_row.addWidget(InfoButton(
            "Sound Instruments:\n"
            "• Piano: Classic, versatile tones\n"
            "• Violin: Smooth, flowing sounds\n"
            "• Bell: Bright, chime-like (recommended)\n"
            "• Soft Pad: Ambient, atmospheric\n"
            "• Mixed: Combination of all"
        ))
        instrument_layout.addLayout(inst_row)

        instrument_group.setLayout(instrument_layout)
        layout.addWidget(instrument_group)

        # Scale Group
        scale_group = QGroupBox("Musical Scale")
        scale_layout = QVBoxLayout()

        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("Scale:"))
        self.widgets['audio_scale'] = QComboBox()
        self.widgets['audio_scale'].addItems(['pentatonic_c', 'pentatonic_g', 'japanese', 'minor_a'])
        self.widgets['audio_scale'].setCurrentText(self.settings.audio_scale)
        scale_row.addWidget(self.widgets['audio_scale'])
        scale_row.addWidget(InfoButton(
            "Musical Scales:\n"
            "• Pentatonic C: Pleasant, versatile\n"
            "• Pentatonic G: Brighter, uplifting\n"
            "• Japanese: Exotic, zen-like\n"
            "• Minor A: Melancholic, emotional"
        ))
        scale_layout.addLayout(scale_row)

        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)

        # Volume Group
        volume_group = QGroupBox("Volume Levels")
        volume_layout = QVBoxLayout()

        master_row = QHBoxLayout()
        master_row.addWidget(QLabel("Master:"))
        self.widgets['audio_master_volume'] = QDoubleSpinBox()
        self.widgets['audio_master_volume'].setRange(0.0, 1.0)
        self.widgets['audio_master_volume'].setSingleStep(0.1)
        self.widgets['audio_master_volume'].setValue(self.settings.audio_master_volume)
        master_row.addWidget(self.widgets['audio_master_volume'])
        volume_layout.addLayout(master_row)

        collision_row = QHBoxLayout()
        collision_row.addWidget(QLabel("Collisions:"))
        self.widgets['audio_collision_volume'] = QDoubleSpinBox()
        self.widgets['audio_collision_volume'].setRange(0.0, 1.0)
        self.widgets['audio_collision_volume'].setSingleStep(0.1)
        self.widgets['audio_collision_volume'].setValue(self.settings.audio_collision_volume)
        collision_row.addWidget(self.widgets['audio_collision_volume'])
        volume_layout.addLayout(collision_row)

        spawn_row = QHBoxLayout()
        spawn_row.addWidget(QLabel("Spawns:"))
        self.widgets['audio_spawn_volume'] = QDoubleSpinBox()
        self.widgets['audio_spawn_volume'].setRange(0.0, 1.0)
        self.widgets['audio_spawn_volume'].setSingleStep(0.1)
        self.widgets['audio_spawn_volume'].setValue(self.settings.audio_spawn_volume)
        spawn_row.addWidget(self.widgets['audio_spawn_volume'])
        volume_layout.addLayout(spawn_row)

        volume_group.setLayout(volume_layout)
        layout.addWidget(volume_group)

        # Background Music Group
        bgm_group = QGroupBox("Background Music")
        bgm_layout = QVBoxLayout()

        bgm_layout.addWidget(QLabel("Calm, soothing background music:"))
        self.widgets['bgm_enabled'] = QCheckBox("Enable Background Music")
        self.widgets['bgm_enabled'].setChecked(True)  # New feature
        bgm_layout.addWidget(self.widgets['bgm_enabled'])

        bgm_style_row = QHBoxLayout()
        bgm_style_row.addWidget(QLabel("Style:"))
        self.widgets['bgm_style'] = QComboBox()
        self.widgets['bgm_style'].addItems(['calm', 'meditative', 'uplifting'])
        self.widgets['bgm_style'].setCurrentText('calm')
        bgm_style_row.addWidget(self.widgets['bgm_style'])
        bgm_style_row.addWidget(InfoButton(
            "BGM Styles:\n"
            "• Calm: Gentle ambient, soothing (recommended)\n"
            "• Meditative: Zen-like, singing bowls\n"
            "• Uplifting: Positive, major key progressions"
        ))
        bgm_layout.addLayout(bgm_style_row)

        bgm_vol_row = QHBoxLayout()
        bgm_vol_row.addWidget(QLabel("BGM Volume:"))
        self.widgets['bgm_volume'] = QDoubleSpinBox()
        self.widgets['bgm_volume'].setRange(0.0, 0.5)  # Lower max for background
        self.widgets['bgm_volume'].setSingleStep(0.05)
        self.widgets['bgm_volume'].setValue(0.15)
        bgm_vol_row.addWidget(self.widgets['bgm_volume'])
        bgm_vol_row.addWidget(InfoButton(
            "Background Music:\n"
            "Gradient ambient music plays throughout\n"
            "Recommended: 0.1-0.2 for subtle background"
        ))
        bgm_layout.addLayout(bgm_vol_row)

        bgm_group.setLayout(bgm_layout)
        layout.addWidget(bgm_group)

        layout.addStretch()
        self.tabs.addTab(scroll, "Audio")

    def create_export_tab(self):
        """Create export settings tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Resolution Group
        res_group = QGroupBox("Video Resolution")
        res_layout = QVBoxLayout()

        res_row = QHBoxLayout()
        res_row.addWidget(QLabel("Resolution:"))
        self.widgets['resolution'] = QComboBox()
        self.widgets['resolution'].addItems([
            '1280x720 (HD)',
            '1920x1080 (Full HD)',
            '2560x1440 (2K)',
            '3840x2160 (4K)'
        ])
        # Set current resolution
        current_res = f"{self.settings.resolution[0]}x{self.settings.resolution[1]}"
        for i in range(self.widgets['resolution'].count()):
            if current_res in self.widgets['resolution'].itemText(i):
                self.widgets['resolution'].setCurrentIndex(i)
                break
        res_row.addWidget(self.widgets['resolution'])
        res_row.addWidget(InfoButton(
            "Video Resolution:\n"
            "• HD (720p): Fast, smaller file\n"
            "• Full HD (1080p): Standard, recommended\n"
            "• 2K (1440p): High quality\n"
            "• 4K (2160p): Maximum quality, slow export"
        ))
        res_layout.addLayout(res_row)

        res_group.setLayout(res_layout)
        layout.addWidget(res_group)

        # FPS Group
        fps_group = QGroupBox("Frame Rate")
        fps_layout = QVBoxLayout()

        fps_row = QHBoxLayout()
        fps_row.addWidget(QLabel("FPS:"))
        self.widgets['fps_export'] = QComboBox()
        self.widgets['fps_export'].addItems(['30', '60'])
        self.widgets['fps_export'].setCurrentText(str(self.settings.fps_export))
        fps_row.addWidget(self.widgets['fps_export'])
        fps_row.addWidget(InfoButton(
            "Frame Rate:\n"
            "• 30 FPS: Standard, faster export\n"
            "• 60 FPS: Smooth motion, slower export\n\n"
            "Higher FPS = smoother but larger file"
        ))
        fps_layout.addLayout(fps_row)

        fps_group.setLayout(fps_layout)
        layout.addWidget(fps_group)

        # Quality Group
        quality_group = QGroupBox("Export Quality")
        quality_layout = QVBoxLayout()

        qual_row = QHBoxLayout()
        qual_row.addWidget(QLabel("Quality:"))
        self.widgets['quality'] = QComboBox()
        self.widgets['quality'].addItems(['preview_low', 'export_balanced', 'export_high'])
        self.widgets['quality'].setCurrentText(self.settings.quality)
        qual_row.addWidget(self.widgets['quality'])
        qual_row.addWidget(InfoButton(
            "Export Quality:\n"
            "• Preview Low: Fast, for testing\n"
            "• Balanced: Good quality, reasonable speed\n"
            "• High: Best quality, slow export"
        ))
        quality_layout.addLayout(qual_row)

        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        # Output Location Group
        output_group = QGroupBox("Output Location")
        output_layout = QVBoxLayout()

        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("Save to:"))
        self.widgets['output_path'] = QLineEdit()
        self.widgets['output_path'].setText("output/")
        self.widgets['output_path'].setReadOnly(True)
        path_row.addWidget(self.widgets['output_path'])

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_folder)
        path_row.addWidget(browse_btn)
        output_layout.addLayout(path_row)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Format Group
        format_group = QGroupBox("Video Format")
        format_layout = QVBoxLayout()

        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("Format:"))
        self.widgets['video_format'] = QComboBox()
        self.widgets['video_format'].addItems(['mp4', 'avi', 'mov'])
        fmt_row.addWidget(self.widgets['video_format'])
        fmt_row.addWidget(InfoButton(
            "Video Formats:\n"
            "• MP4: Universal, recommended\n"
            "• AVI: Windows compatible\n"
            "• MOV: Mac/Apple compatible"
        ))
        format_layout.addLayout(fmt_row)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        layout.addStretch()
        self.tabs.addTab(scroll, "Export")

    def create_advanced_tab(self):
        """Create advanced physics tab."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Warning label
        warning = QLabel("⚠️ Advanced Physics Controls - Adjust carefully!")
        warning.setStyleSheet("color: #e94560; font-weight: bold; padding: 10px;")
        layout.addWidget(warning)

        # Gravity Group
        gravity_group = QGroupBox("Gravity")
        gravity_layout = QVBoxLayout()

        grav_row = QHBoxLayout()
        grav_row.addWidget(QLabel("Strength:"))
        self.widgets['gravity_strength'] = QDoubleSpinBox()
        self.widgets['gravity_strength'].setRange(0.0, 1000.0)
        self.widgets['gravity_strength'].setValue(self.settings.gravity_strength)
        grav_row.addWidget(self.widgets['gravity_strength'])
        grav_row.addWidget(InfoButton(
            "Gravity Strength:\n"
            "Controls how fast objects fall\n"
            "• 0: No gravity (floating)\n"
            "• 100-200: Gentle falling\n"
            "• 200-400: Normal gravity (recommended)\n"
            "• 400-600: Strong pull\n"
            "• 600+: Very heavy\n\n"
            "Higher = objects fall faster and settle quicker"
        ))
        gravity_layout.addLayout(grav_row)

        gravity_group.setLayout(gravity_layout)
        layout.addWidget(gravity_group)

        # Drag Group
        drag_group = QGroupBox("Air Resistance")
        drag_layout = QVBoxLayout()

        drag_row = QHBoxLayout()
        drag_row.addWidget(QLabel("Drag:"))
        self.widgets['drag_coeff'] = QDoubleSpinBox()
        self.widgets['drag_coeff'].setRange(0.0, 0.1)
        self.widgets['drag_coeff'].setSingleStep(0.001)
        self.widgets['drag_coeff'].setDecimals(3)
        self.widgets['drag_coeff'].setValue(self.settings.drag_coeff)
        drag_row.addWidget(self.widgets['drag_coeff'])
        drag_row.addWidget(InfoButton(
            "Air Drag Coefficient:\n"
            "Slows down objects over time\n"
            "• 0.000: No air resistance\n"
            "• 0.001: Very low (recommended)\n"
            "• 0.005: Low resistance\n"
            "• 0.01: Moderate resistance\n"
            "• 0.05+: High resistance (quick stop)\n\n"
            "Higher = objects slow down faster"
        ))
        drag_layout.addLayout(drag_row)

        drag_group.setLayout(drag_layout)
        layout.addWidget(drag_group)

        # Restitution Group
        rest_group = QGroupBox("Bounciness")
        rest_layout = QVBoxLayout()

        rest_row = QHBoxLayout()
        rest_row.addWidget(QLabel("Restitution:"))
        self.widgets['restitution'] = QDoubleSpinBox()
        self.widgets['restitution'].setRange(0.0, 1.0)
        self.widgets['restitution'].setSingleStep(0.05)
        self.widgets['restitution'].setValue(self.settings.restitution)
        rest_row.addWidget(self.widgets['restitution'])
        rest_row.addWidget(InfoButton(
            "Restitution (Bounciness):\n"
            "Controls energy retained after collisions\n"
            "• 0.0: No bounce (dead stop)\n"
            "• 0.5: Half energy retained\n"
            "• 0.7-0.8: Moderate bounce\n"
            "• 0.85-0.92: Very bouncy (recommended)\n"
            "• 0.95+: Super bouncy (chaotic)\n"
            "• 1.0: Perfect bounce (perpetual)\n\n"
            "Higher = more energetic, longer action"
        ))
        rest_layout.addLayout(rest_row)

        rest_group.setLayout(rest_layout)
        layout.addWidget(rest_group)

        # Friction Group
        friction_group = QGroupBox("Surface Friction")
        friction_layout = QVBoxLayout()

        friction_row = QHBoxLayout()
        friction_row.addWidget(QLabel("Friction:"))
        self.widgets['friction'] = QDoubleSpinBox()
        self.widgets['friction'].setRange(0.0, 0.5)
        self.widgets['friction'].setSingleStep(0.01)
        self.widgets['friction'].setValue(self.settings.friction)
        friction_row.addWidget(self.widgets['friction'])
        friction_row.addWidget(InfoButton(
            "Surface Friction:\n"
            "Affects sliding and rolling\n"
            "• 0.0: Frictionless (ice-like)\n"
            "• 0.01: Very low (recommended)\n"
            "• 0.05: Low friction\n"
            "• 0.1: Moderate friction\n"
            "• 0.2+: High friction (sticky)\n\n"
            "Higher = objects stop sliding faster"
        ))
        friction_layout.addLayout(friction_row)

        friction_group.setLayout(friction_layout)
        layout.addWidget(friction_group)

        # Max Speed Group
        speed_group = QGroupBox("Speed Limit")
        speed_layout = QVBoxLayout()

        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Max Speed:"))
        self.widgets['max_speed'] = QDoubleSpinBox()
        self.widgets['max_speed'].setRange(500.0, 3000.0)
        self.widgets['max_speed'].setValue(self.settings.max_speed)
        speed_row.addWidget(self.widgets['max_speed'])
        speed_row.addWidget(InfoButton(
            "Maximum Speed:\n"
            "Caps object velocity\n"
            "• 500-1000: Slow, controlled\n"
            "• 1000-1500: Moderate speed\n"
            "• 1500-2000: Fast (recommended)\n"
            "• 2000-3000: Very fast\n\n"
            "Higher = more energetic collisions"
        ))
        speed_layout.addLayout(speed_row)

        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)

        layout.addStretch()
        self.tabs.addTab(scroll, "Advanced")

    def browse_output_folder(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.widgets['output_path'].text()
        )
        if folder:
            self.widgets['output_path'].setText(folder)

    def apply_settings(self):
        """Apply all settings."""
        try:
            # Basic settings
            self.settings.container_shape = self.widgets['container_shape'].currentText()
            self.settings.polygon_sides = self.widgets['polygon_sides'].value()
            self.settings.duration_sec = self.widgets['duration_sec'].value()

            # Objects
            self.settings.initial_count = self.widgets['initial_count'].value()
            self.settings.max_particles = self.widgets['max_particles'].value()

            # Get selected object types
            selected_shapes = [name for name, cb in self.object_checkboxes.items() if cb.isChecked()]
            if selected_shapes:
                self.settings.shapes = selected_shapes
                # Equal weights for now
                self.settings.shape_weights = [1.0 / len(selected_shapes)] * len(selected_shapes)

            self.settings.size_min = self.widgets['size_min'].value()
            self.settings.size_max = self.widgets['size_max'].value()

            # Appearance
            self.settings.visual_scheme = self.widgets['visual_scheme'].currentText()
            self.settings.enable_3d_effect = self.widgets['enable_3d_effect'].isChecked()
            self.settings.light_direction = self.widgets['light_direction'].value()
            self.settings.ambient_light = self.widgets['ambient_light'].value()
            self.settings.glow_enabled = self.widgets['glow_enabled'].isChecked()
            self.settings.trails_enabled = self.widgets['trails_enabled'].isChecked()

            # Audio
            self.settings.audio_enabled = self.widgets['audio_enabled'].isChecked()
            self.settings.audio_instrument = self.widgets['audio_instrument'].currentText()
            self.settings.audio_scale = self.widgets['audio_scale'].currentText()
            self.settings.audio_master_volume = self.widgets['audio_master_volume'].value()
            self.settings.audio_collision_volume = self.widgets['audio_collision_volume'].value()
            self.settings.audio_spawn_volume = self.widgets['audio_spawn_volume'].value()

            # Background Music
            if 'bgm_enabled' in self.widgets:
                self.settings.bgm_enabled = self.widgets['bgm_enabled'].isChecked()
                self.settings.bgm_volume = self.widgets['bgm_volume'].value()
                self.settings.bgm_style = self.widgets['bgm_style'].currentText()

            # Export
            res_text = self.widgets['resolution'].currentText()
            if '1280x720' in res_text:
                self.settings.resolution = [1280, 720]
            elif '1920x1080' in res_text:
                self.settings.resolution = [1920, 1080]
            elif '2560x1440' in res_text:
                self.settings.resolution = [2560, 1440]
            elif '3840x2160' in res_text:
                self.settings.resolution = [3840, 2160]

            self.settings.fps_export = int(self.widgets['fps_export'].currentText())
            self.settings.quality = self.widgets['quality'].currentText()

            # Advanced
            if 'gravity_strength' in self.widgets:
                self.settings.gravity_strength = self.widgets['gravity_strength'].value()
                self.settings.drag_coeff = self.widgets['drag_coeff'].value()
                self.settings.restitution = self.widgets['restitution'].value()
                self.settings.friction = self.widgets['friction'].value()
                self.settings.max_speed = self.widgets['max_speed'].value()

            # Validate
            self.settings.validate_and_clamp()

            # Emit signal
            self.settings_changed.emit(self.settings)

            logger.info("Settings applied successfully")

        except Exception as e:
            logger.exception("Error applying settings")
            QMessageBox.critical(self, "Error", f"Failed to apply settings: {e}")

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings = AppSettings()
            self.update_from_settings(self.settings)
            self.settings_changed.emit(self.settings)
            logger.info("Settings reset to defaults")

    def update_from_settings(self, settings: AppSettings):
        """Update UI from settings object."""
        self.settings = settings

        # Update all widgets from settings
        try:
            # Basic tab
            if 'container_shape' in self.widgets:
                self.widgets['container_shape'].setCurrentText(settings.container_shape)
            if 'polygon_sides' in self.widgets:
                self.widgets['polygon_sides'].setValue(settings.polygon_sides)
            if 'duration_sec' in self.widgets:
                self.widgets['duration_sec'].setValue(settings.duration_sec)

            # Objects tab
            if 'initial_count' in self.widgets:
                self.widgets['initial_count'].setValue(settings.initial_count)
            if 'max_particles' in self.widgets:
                self.widgets['max_particles'].setValue(settings.max_particles)
                self.widgets['max_particles_slider'].setValue(settings.max_particles)

            # Update object type checkboxes
            if hasattr(self, 'object_checkboxes'):
                for obj_type, checkbox in self.object_checkboxes.items():
                    checkbox.setChecked(obj_type in settings.shapes)

            if 'size_min' in self.widgets:
                self.widgets['size_min'].setValue(settings.size_min)
            if 'size_max' in self.widgets:
                self.widgets['size_max'].setValue(settings.size_max)

            # Appearance tab
            if 'visual_scheme' in self.widgets:
                self.widgets['visual_scheme'].setCurrentText(settings.visual_scheme)
            if 'enable_3d_effect' in self.widgets:
                self.widgets['enable_3d_effect'].setChecked(settings.enable_3d_effect)
            if 'light_direction' in self.widgets:
                self.widgets['light_direction'].setValue(settings.light_direction)
            if 'ambient_light' in self.widgets:
                self.widgets['ambient_light'].setValue(settings.ambient_light)
            if 'glow_enabled' in self.widgets:
                self.widgets['glow_enabled'].setChecked(settings.glow_enabled)
            if 'trails_enabled' in self.widgets:
                self.widgets['trails_enabled'].setChecked(settings.trails_enabled)

            # Audio tab
            if 'audio_enabled' in self.widgets:
                self.widgets['audio_enabled'].setChecked(settings.audio_enabled)
            if 'audio_instrument' in self.widgets:
                self.widgets['audio_instrument'].setCurrentText(settings.audio_instrument)
            if 'audio_scale' in self.widgets:
                self.widgets['audio_scale'].setCurrentText(settings.audio_scale)
            if 'audio_master_volume' in self.widgets:
                self.widgets['audio_master_volume'].setValue(settings.audio_master_volume)
            if 'audio_collision_volume' in self.widgets:
                self.widgets['audio_collision_volume'].setValue(settings.audio_collision_volume)
            if 'audio_spawn_volume' in self.widgets:
                self.widgets['audio_spawn_volume'].setValue(settings.audio_spawn_volume)

            # Background music
            if 'bgm_enabled' in self.widgets:
                self.widgets['bgm_enabled'].setChecked(getattr(settings, 'bgm_enabled', True))
            if 'bgm_style' in self.widgets:
                self.widgets['bgm_style'].setCurrentText(getattr(settings, 'bgm_style', 'calm'))
            if 'bgm_volume' in self.widgets:
                self.widgets['bgm_volume'].setValue(getattr(settings, 'bgm_volume', 0.15))

            # Export tab
            if 'resolution' in self.widgets:
                res_str = f"{settings.resolution[0]}x{settings.resolution[1]}"
                for i in range(self.widgets['resolution'].count()):
                    if res_str in self.widgets['resolution'].itemText(i):
                        self.widgets['resolution'].setCurrentIndex(i)
                        break

            if 'fps_export' in self.widgets:
                self.widgets['fps_export'].setCurrentText(str(settings.fps_export))
            if 'quality' in self.widgets:
                self.widgets['quality'].setCurrentText(settings.quality)

            # Advanced tab
            if 'gravity_strength' in self.widgets:
                self.widgets['gravity_strength'].setValue(settings.gravity_strength)
            if 'drag_coeff' in self.widgets:
                self.widgets['drag_coeff'].setValue(settings.drag_coeff)
            if 'restitution' in self.widgets:
                self.widgets['restitution'].setValue(settings.restitution)
            if 'friction' in self.widgets:
                self.widgets['friction'].setValue(settings.friction)
            if 'max_speed' in self.widgets:
                self.widgets['max_speed'].setValue(settings.max_speed)

            logger.info("UI updated from settings")

        except Exception as e:
            logger.exception("Error updating UI from settings")
            QMessageBox.warning(self, "Update Error", f"Some settings could not be displayed: {e}")


from src.core.settings import AppSettings

