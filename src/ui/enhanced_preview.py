"""Enhanced 3D preview with gradient backgrounds, proper colors, and improved audio"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSlider, QSpinBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
import time
import math
import pygame
import numpy as np

from src.engine_3d import Engine3D
from src.audio_enhanced import AudioManager
from src.colors_enhanced import ColorScheme, GradientBackground


class CanvasWidget(QWidget):
    """Canvas to draw particles with enhanced visuals"""

    def __init__(self, engine, audio_manager, color_scheme, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.audio_manager = audio_manager
        self.color_scheme = color_scheme
        self.setStyleSheet("background-color: #0a0a0a;")
        self.setMinimumSize(900, 700)
        self.rotation_angle = 0
        self.anim_time = 0

    def draw_shape(self, painter, x, y, radius, shape, color, rotation):
        """Draw particle in selected shape"""
        x = int(x)
        y = int(y)
        r = int(radius)

        # Draw shadow
        shadow_color = QColor(0, 0, 0, 100)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(QPen(shadow_color))
        painter.drawEllipse(x - r + 3, y + r - 2, r * 2 - 6, int(r * 0.5))

        # Draw main shape
        qcolor = QColor(color[0], color[1], color[2])

        if shape == "sphere":
            painter.setBrush(QBrush(qcolor))
            painter.setPen(QPen(qcolor.darker(), 2))
            painter.drawEllipse(x - r, y - r, r * 2, r * 2)

        elif shape == "cube":
            painter.setBrush(QBrush(qcolor))
            painter.setPen(QPen(qcolor.darker(), 2))
            painter.save()
            painter.translate(x, y)
            painter.rotate(int(math.degrees(rotation)) % 360)
            painter.drawRect(-r, -r, r * 2, r * 2)
            painter.restore()

        elif shape == "star":
            points = []
            for i in range(10):
                angle = rotation + (2 * math.pi * i / 10)
                dist = r if i % 2 == 0 else r / 2
                px = x + dist * math.cos(angle)
                py = y + dist * math.sin(angle)
                points.append(QPoint(int(px), int(py)))

            painter.setBrush(QBrush(qcolor))
            painter.setPen(QPen(qcolor.darker(), 2))
            painter.drawPolygon(QPolygon(points))

        elif shape == "triangle":
            points = []
            for i in range(3):
                angle = rotation + (2 * math.pi * i / 3) - math.pi / 2
                px = x + r * math.cos(angle)
                py = y + r * math.sin(angle)
                points.append(QPoint(int(px), int(py)))

            painter.setBrush(QBrush(qcolor))
            painter.setPen(QPen(qcolor.darker(), 2))
            painter.drawPolygon(QPolygon(points))

        # Draw highlight
        highlight_color = QColor(255, 255, 255, 180)
        painter.setBrush(QBrush(highlight_color))
        painter.setPen(QPen(highlight_color))
        highlight_size = max(2, int(r * 0.3))
        painter.drawEllipse(
            x - int(r * 0.4),
            y - int(r * 0.4),
            highlight_size,
            highlight_size
        )

        # Draw glow ring
        ring_alpha = int(100 * (0.5 + 0.5 * math.sin(self.rotation_angle)))
        ring_color = QColor(color[0], color[1], color[2], ring_alpha)
        ring_pen = QPen(ring_color)
        ring_pen.setWidth(1)
        painter.setPen(ring_pen)
        painter.setBrush(Qt.NoBrush)

        ring_radius = int(r * 1.2)
        painter.drawEllipse(
            x - ring_radius,
            y - ring_radius,
            ring_radius * 2,
            ring_radius * 2
        )

    def paintEvent(self, event):
        """Draw scene with gradient background"""
        if not self.engine:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Update animation time
        self.rotation_angle += 0.01
        self.anim_time += 0.016

        # Draw gradient background more efficiently
        scheme = ColorScheme.get_scheme(self.color_scheme)
        background_type = scheme["background_type"]

        # Draw background using filled rectangles instead of individual pixels
        # This is much faster and still produces smooth gradients
        rect_height = 20  # Draw in strips for efficiency
        for y in range(0, self.height(), rect_height):
            for x in range(0, self.width(), rect_height):
                color = GradientBackground.get_gradient_color(
                    x + rect_height // 2,
                    y + rect_height // 2,
                    self.width(),
                    self.height(),
                    self.anim_time * 0.3,
                    background_type
                )
                painter.setBrush(QBrush(QColor(color[0], color[1], color[2])))
                painter.setPen(Qt.NoPen)
                painter.drawRect(x, y, rect_height, rect_height)

        # Draw boundary with appropriate color
        center_x = self.engine.center_x
        center_y = self.engine.center_y
        radius = self.engine.boundary_radius
        boundary_color = scheme["boundary"]
        glow_color = scheme["glow_color"]

        # Use contrasting color for boundary (inverse of theme for visibility)
        contrast_color = (
            255 - boundary_color[0],
            255 - boundary_color[1],
            255 - boundary_color[2]
        )

        # Draw stronger glow effect
        for glow in range(20, 0, -2):
            glow_alpha = int(60 * (1 - glow / 20))
            qglow_color = QColor(contrast_color[0], contrast_color[1], contrast_color[2], glow_alpha)
            glow_pen = QPen(qglow_color)
            glow_pen.setWidth(2)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.NoBrush)

            if self.engine.boundary_type == "circle":
                painter.drawEllipse(
                    int(center_x - radius - glow),
                    int(center_y - radius - glow),
                    int(radius * 2 + glow * 2),
                    int(radius * 2 + glow * 2)
                )
            elif self.engine.boundary_type == "square":
                painter.drawRect(
                    int(center_x - radius - glow),
                    int(center_y - radius - glow),
                    int(radius * 2 + glow * 2),
                    int(radius * 2 + glow * 2)
                )
            elif self.engine.boundary_type == "triangle":
                points = []
                for i in range(3):
                    angle = i * (2 * math.pi / 3) - math.pi / 2
                    px = center_x + (radius + glow) * math.cos(angle)
                    py = center_y + (radius + glow) * math.sin(angle)
                    points.append(QPoint(int(px), int(py)))
                painter.drawPolygon(QPolygon(points))

        # Draw main boundary - THICK and CONTRASTING
        boundary_pen = QPen(QColor(contrast_color[0], contrast_color[1], contrast_color[2]))
        boundary_pen.setWidth(8)  # Much thicker for visibility
        painter.setPen(boundary_pen)
        painter.setBrush(Qt.NoBrush)

        if self.engine.boundary_type == "circle":
            painter.drawEllipse(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2)
            )
        elif self.engine.boundary_type == "square":
            painter.drawRect(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2)
            )
        elif self.engine.boundary_type == "triangle":
            points = []
            for i in range(3):
                angle = i * (2 * math.pi / 3) - math.pi / 2
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                points.append(QPoint(int(px), int(py)))
            painter.drawPolygon(QPolygon(points))

        # Draw particles with scheme colors
        sorted_objects = sorted(self.engine.objects, key=lambda obj: obj.y)

        for i, obj in enumerate(sorted_objects):
            color = ColorScheme.get_particle_color(self.color_scheme, i)
            self.draw_shape(
                painter,
                obj.x,
                obj.y,
                obj.radius,
                self.engine.object_shape,
                color,
                obj.rotation
            )

        painter.end()


class SimplePreview(QWidget):
    """Enhanced preview with all improvements"""

    object_count_changed = pyqtSignal(int)
    fps_changed = pyqtSignal(float)

    def __init__(self, parent=None, color_scheme="ocean"):
        super().__init__(parent)

        self.width = 900
        self.height = 700
        self.running = False
        self.paused = False
        self.max_reached = False
        self.max_reached_time = 0
        self.color_scheme = color_scheme
        self.background_music_playing = False

        try:
            self.engine = Engine3D(self.width, self.height, boundary_radius=280, boundary_type="circle")
            self.audio_manager = AudioManager()

            # Initialize pygame mixer for audio playback
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            except:
                try:
                    pygame.mixer.quit()
                    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
                except:
                    pass

            self.engine.reset()
            print("Preview: Engine and audio initialized")

        except Exception as e:
            print(f"Preview: Initialization error: {e}")
            self.engine = None
            self.audio_manager = None

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.elapsed_time = 0
        self.background_music_queue = []

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_simulation)
        self.update_timer.setInterval(8)  # Higher frequency updates for smoother movement (125 FPS physics, 60 FPS render)

        # Background music timer
        self.music_timer = QTimer()
        self.music_timer.timeout.connect(self._play_background_music_loop)

        # UI Layout
        layout = QVBoxLayout()

        # Canvas
        self.canvas = CanvasWidget(self.engine, self.audio_manager, color_scheme)
        layout.addWidget(self.canvas)

        # Info label
        self.info_label = QLabel("Press Play to start")
        self.info_label.setStyleSheet("color: #ccc; padding: 5px;")
        layout.addWidget(self.info_label)

        # Control buttons
        button_layout = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play)
        self.play_button.setStyleSheet("padding: 8px; font-weight: bold;")
        button_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause)
        self.pause_button.setEnabled(False)
        self.pause_button.setStyleSheet("padding: 8px; font-weight: bold;")
        button_layout.addWidget(self.pause_button)

        self.apply_button = QPushButton("Apply New Settings")
        self.apply_button.clicked.connect(self.apply_new_settings)
        self.apply_button.setStyleSheet("padding: 8px; font-weight: bold; background-color: #2d7f2d; color: white;")
        button_layout.addWidget(self.apply_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.setStyleSheet("padding: 8px; font-weight: bold;")
        button_layout.addWidget(self.reset_button)

        # Speed slider
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.setMaximumWidth(200)
        speed_layout.addWidget(self.speed_slider)
        button_layout.addLayout(speed_layout)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Slowdown timer controls
        slowdown_layout = QHBoxLayout()
        slowdown_layout.addWidget(QLabel("Calm down after (sec):"))

        self.slowdown_delay_spin = QSpinBox()
        self.slowdown_delay_spin.setRange(5, 120)
        self.slowdown_delay_spin.setValue(0)  # Immediate
        self.slowdown_delay_spin.setMaximumWidth(80)
        slowdown_layout.addWidget(self.slowdown_delay_spin)

        slowdown_layout.addWidget(QLabel("Duration (sec):"))

        self.slowdown_duration_spin = QSpinBox()
        self.slowdown_duration_spin.setRange(5, 120)
        self.slowdown_duration_spin.setValue(30)
        self.slowdown_duration_spin.setMaximumWidth(80)
        slowdown_layout.addWidget(self.slowdown_duration_spin)

        slowdown_layout.addStretch()
        layout.addLayout(slowdown_layout)

        self.setLayout(layout)

    def play(self):
        """Start simulation"""
        if not self.engine:
            self.info_label.setText("Error: Engine not initialized")
            return

        self.running = True
        self.paused = False
        self.max_reached = False
        self.update_timer.start()
        self.music_timer.start(3000)  # Start background music loop
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.reset_button.setEnabled(False)
        self.info_label.setText("Simulation running...")

    def pause(self):
        """Pause simulation"""
        self.paused = True
        self.update_timer.stop()
        self.music_timer.stop()
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(True)
        self.info_label.setText("Paused")

    def apply_new_settings(self):
        """Apply new settings"""
        if not self.engine:
            return

        self.engine.objects = []
        self.engine.allow_spawning = True
        self.engine.reset()
        self.max_reached = False
        self.elapsed_time = 0

        if not self.update_timer.isActive():
            self.play()

        self.info_label.setText("New settings applied!")
        self.canvas.update()

    def reset(self):
        """Reset simulation"""
        if self.engine:
            self.engine.allow_spawning = True
            self.engine.reset()
        self.elapsed_time = 0
        self.frame_count = 0
        self.fps = 0
        self.max_reached = False
        self.info_label.setText("Reset - Press Play")
        self.canvas.update()

    def update_simulation(self):
        """Update simulation - physics runs at higher frequency"""
        if not self.paused and self.engine:
            dt = 0.008  # 8ms per frame for 125 Hz physics updates

            self.engine.update(dt)

            # Process bounce and collision sounds
            for bounce in self.engine.bounce_log:
                try:
                    sound = self.audio_manager.generate_bounce_sound()
                    if sound:
                        self._play_sound(sound)
                except:
                    pass
            self.engine.bounce_log = []

            for collision in self.engine.collision_log:
                try:
                    sound = self.audio_manager.generate_collision_sound()
                    if sound:
                        self._play_sound(sound)
                except:
                    pass
            self.engine.collision_log = []

            self.elapsed_time += dt

            # Check if max reached
            if not self.max_reached and len(self.engine.objects) >= self.engine.max_objects:
                self.max_reached = True
                self.max_reached_time = self.elapsed_time
                self.engine.allow_spawning = False

            # Apply smooth momentum decay after max reached
            if self.max_reached:
                time_since_max = self.elapsed_time - self.max_reached_time
                slowdown_duration = self.slowdown_duration_spin.value()

                # Exponential decay - momentum gradually fades
                # Using exponential function for smooth, natural decay
                if time_since_max > 0:
                    # Exponential decay: remaining = e^(-t/tau)
                    # This preserves momentum but gradually reduces it
                    decay_constant = slowdown_duration / 3.0  # 3 time constants to near-zero
                    momentum_factor = math.exp(-time_since_max / decay_constant)

                    # Apply to all objects - preserves direction, reduces magnitude
                    for obj in self.engine.objects:
                        obj.vx *= momentum_factor
                        obj.vy *= momentum_factor

            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
                self.fps_changed.emit(float(self.fps))

            current_count = self.engine.get_object_count()
            self.object_count_changed.emit(current_count)

            status = f"Objects: {current_count}/{self.engine.max_objects} | FPS: {self.fps} | Time: {self.elapsed_time:.1f}s"
            if self.max_reached:
                slowdown_duration = self.slowdown_duration_spin.value()
                time_since_max = self.elapsed_time - self.max_reached_time

                if time_since_max < slowdown_duration:
                    slowdown_progress = (time_since_max / slowdown_duration)
                    progress_percent = int(slowdown_progress * 100)
                    time_remaining = slowdown_duration - time_since_max
                    status += f" | Calming down... {progress_percent}% ({time_remaining:.1f}s remaining)"
                else:
                    status += f" | All stopped (Calm for {time_since_max - slowdown_duration:.1f}s)"

            self.info_label.setText(status)
            self.canvas.update()

    def _play_sound(self, sound):
        """Play sound using pygame mixer"""
        try:
            if sound and hasattr(sound, 'audio_data'):
                sound_obj = pygame.mixer.Sound(sound.audio_data)
                sound_obj.set_volume(self.audio_manager.master_volume * 0.5)
                sound_obj.play()
        except:
            pass

    def _play_background_music_loop(self):
        """Play background music in a loop"""
        try:
            if self.running and not self.paused:
                sound = self.audio_manager.generate_background_music()
                if sound:
                    self._play_sound(sound)
        except:
            pass

    def set_color_scheme(self, scheme_name):
        """Set color scheme"""
        self.color_scheme = scheme_name
        self.canvas.color_scheme = scheme_name
        self.canvas.update()

    def apply_settings(self, config):
        """Apply configuration"""
        if not self.engine:
            return

        visual_settings = config.get("visual_settings", default={})
        particle_settings = config.get("particle_settings", default={})

        boundary_type = visual_settings.get("boundary_type", "circle")
        self.engine.boundary_type = boundary_type

        object_shape = visual_settings.get("object_shape", "sphere")
        self.engine.set_object_shape(object_shape)

        max_objects = particle_settings.get("max_particles", 50)
        self.engine.set_max_objects(max_objects)

        self.canvas.update()

