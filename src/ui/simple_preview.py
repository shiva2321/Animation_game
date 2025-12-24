"""Improved preview with proper shape rendering and audio playback"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSlider, QSpinBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
import time
import math
import pygame
import numpy as np

from src.engine_3d import Engine3D
from src.audio_manager import AudioManager


class CanvasWidget(QWidget):
    """Canvas to draw particles with proper shape rendering"""

    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setStyleSheet("background-color: #0a0a0a;")
        self.setMinimumSize(900, 700)
        self.rotation_angle = 0

    def draw_shape(self, painter, x, y, radius, shape, color, rotation):
        """Draw particle in selected shape"""
        x = int(x)
        y = int(y)
        r = int(radius)

        # Draw shadow first
        shadow_color = QColor(0, 0, 0, 80)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(QPen(shadow_color))
        painter.drawEllipse(x - r + 3, y + r - 2, r * 2 - 6, int(r * 0.5))

        # Draw shape
        if shape == "sphere":
            # Circle
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(), 2))
            painter.drawEllipse(x - r, y - r, r * 2, r * 2)

        elif shape == "cube":
            # Cube with rotation
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(), 2))

            # Simple square rotated
            angle_deg = int(math.degrees(rotation)) % 360
            painter.save()
            painter.translate(x, y)
            painter.rotate(angle_deg)
            painter.drawRect(-r, -r, r * 2, r * 2)
            painter.restore()

        elif shape == "star":
            # 5-pointed star
            points = []
            for i in range(10):
                angle = rotation + (2 * math.pi * i / 10)
                dist = r if i % 2 == 0 else r / 2
                px = x + dist * math.cos(angle)
                py = y + dist * math.sin(angle)
                points.append(QPoint(int(px), int(py)))

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(), 2))
            painter.drawPolygon(QPolygon(points))

        elif shape == "triangle":
            # Triangle
            points = []
            for i in range(3):
                angle = rotation + (2 * math.pi * i / 3) - math.pi / 2
                px = x + r * math.cos(angle)
                py = y + r * math.sin(angle)
                points.append(QPoint(int(px), int(py)))

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(), 2))
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

        # Draw rotation rings
        ring_alpha = int(100 * (0.5 + 0.5 * math.sin(self.rotation_angle)))
        ring_color = QColor(200, 200, 255, ring_alpha)
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
        """Draw particles and boundary with 3D effects"""
        if not self.engine:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Update rotation for 3D effect
        self.rotation_angle += 0.01

        # Draw boundary with glow
        center_x = self.engine.center_x
        center_y = self.engine.center_y
        radius = self.engine.boundary_radius

        # Draw glow effect
        for glow in range(15, 0, -1):
            glow_alpha = int(30 * (1 - glow / 15))
            glow_color = QColor(100, 150, 200, glow_alpha)
            glow_pen = QPen(glow_color)
            glow_pen.setWidth(1)
            painter.setPen(glow_pen)

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

        # Draw main boundary
        boundary_pen = QPen(QColor(100, 200, 255))
        boundary_pen.setWidth(3)
        painter.setPen(boundary_pen)

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

        # Draw particles with proper shapes
        sorted_objects = sorted(self.engine.objects, key=lambda obj: obj.y)

        colors = [
            QColor(255, 100, 100),   # Red
            QColor(100, 200, 255),   # Blue
            QColor(100, 255, 100),   # Green
            QColor(255, 255, 100),   # Yellow
            QColor(255, 150, 200),   # Pink
            QColor(150, 100, 255),   # Purple
        ]

        for i, obj in enumerate(sorted_objects):
            color = colors[i % len(colors)]
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
    """Improved preview with smooth physics and proper shapes"""

    object_count_changed = pyqtSignal(int)
    fps_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.width = 900
        self.height = 700
        self.running = False
        self.paused = False
        self.max_reached = False
        self.max_reached_time = 0

        try:
            self.engine = Engine3D(self.width, self.height, boundary_radius=280, boundary_type="circle")
            self.audio_manager = AudioManager()

            # Initialize pygame mixer for audio playback
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
                print("SimplePreview: Audio mixer initialized")
            except Exception as ae:
                print(f"SimplePreview: Audio mixer error (non-critical): {ae}")

            self.engine.reset()
            print("SimplePreview: Engine initialized")

        except Exception as e:
            print(f"SimplePreview: Initialization error: {e}")
            self.engine = None
            self.audio_manager = None

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.elapsed_time = 0

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_simulation)
        self.update_timer.setInterval(16)  # 60 FPS

        # UI Layout
        layout = QVBoxLayout()

        # Canvas area
        self.canvas = CanvasWidget(self.engine)
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
        self.slowdown_delay_spin.setValue(20)  # Default 20 seconds
        self.slowdown_delay_spin.setMaximumWidth(80)
        slowdown_layout.addWidget(self.slowdown_delay_spin)

        slowdown_layout.addWidget(QLabel("Duration (sec):"))

        self.slowdown_duration_spin = QSpinBox()
        self.slowdown_duration_spin.setRange(5, 120)
        self.slowdown_duration_spin.setValue(30)  # Default 30 seconds
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
        self.update_timer.start()
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.reset_button.setEnabled(False)
        self.info_label.setText("Simulation running...")

    def pause(self):
        """Pause simulation"""
        self.paused = True
        self.update_timer.stop()
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(True)
        self.info_label.setText("Paused")

    def apply_new_settings(self):
        """Apply new settings while keeping animation running"""
        if not self.engine:
            return

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
            self.engine.reset()
        self.elapsed_time = 0
        self.frame_count = 0
        self.fps = 0
        self.max_reached = False
        self.info_label.setText("Reset - Press Play")
        self.canvas.update()

    def update_simulation(self):
        """Update simulation with smooth physics and proper calm-down"""
        if not self.paused and self.engine:
            dt = 0.016  # 60 FPS

            # Update the engine
            self.engine.update(dt)

            # Process bounce sounds
            for bounce in self.engine.bounce_log:
                try:
                    sound = self.audio_manager.generate_bounce_sound()
                    if sound:
                        self._play_sound(sound)
                except:
                    pass
            self.engine.bounce_log = []

            # Process collision sounds
            for collision in self.engine.collision_log:
                try:
                    sound = self.audio_manager.generate_collision_sound()
                    if sound:
                        self._play_sound(sound)
                except:
                    pass
            self.engine.collision_log = []

            self.elapsed_time += dt

            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
                self.fps_changed.emit(float(self.fps))

            current_count = self.engine.get_object_count()
            self.object_count_changed.emit(current_count)

            # Update status based on engine state
            state = self.engine.get_state()
            status = f"Objects: {current_count}/{self.engine.max_objects} | FPS: {self.fps} | Time: {self.elapsed_time:.1f}s"

            if state == Engine3D.STATE_SPAWNING:
                status += " | Spawning..."
            elif state == Engine3D.STATE_CALM_DOWN:
                calm_start_time = self.engine.calm_down_time
                time_since_calm = self.elapsed_time - calm_start_time
                progress_percent = int((time_since_calm / self.engine.calm_down_duration) * 100)
                time_remaining = max(0, self.engine.calm_down_duration - time_since_calm)
                status += f" | Calming down... {progress_percent}% ({time_remaining:.1f}s remaining)"
            elif state == Engine3D.STATE_SETTLED:
                status += " | All objects settled"

            self.info_label.setText(status)

            self.canvas.update()

    def _play_sound(self, sound):
        """Play a sound using pygame mixer"""
        try:
            # Convert sound data to pygame sound
            if sound and hasattr(sound, 'audio_data'):
                # Create a numpy array from the bytes
                audio_array = np.frombuffer(sound.audio_data, dtype=np.int16)

                # Reshape for stereo conversion (optional)
                if len(audio_array) > 0:
                    # Create pygame sound object
                    sound_obj = pygame.mixer.Sound(sound.audio_data)
                    sound_obj.set_volume(self.audio_manager.master_volume * 0.5)
                    sound_obj.play()
        except Exception as e:
            # Silently fail if audio can't play
            pass

    def apply_settings(self, config):
        """Apply configuration settings"""
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

