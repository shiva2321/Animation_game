"""
Improved preview with smooth physics, proper boundary rendering, and gradient background
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSlider, QSpinBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygon, QFont, QLinearGradient
import time
import math
import pygame
import numpy as np

from src.engine_3d import Engine3D
from src.audio_manager import AudioManager


class CanvasWidgetImproved(QWidget):
    """Canvas with smooth gradient background and proper boundary rendering"""

    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setStyleSheet("background-color: #000000;")
        self.setMinimumSize(900, 700)
        self.rotation_angle = 0
        self.time_counter = 0

    def draw_gradient_background(self, painter):
        """Draw smooth animated gradient background"""
        width = self.width()
        height = self.height()

        # Animate gradient colors smoothly
        t = self.time_counter * 0.001  # Slow animation

        # Create smooth color variations
        r1 = int(20 + 10 * math.sin(t * 0.5))
        g1 = int(30 + 15 * math.sin(t * 0.3 + 2))
        b1 = int(40 + 20 * math.sin(t * 0.7 + 4))

        r2 = int(10 + 8 * math.sin(t * 0.4 + 1))
        g2 = int(20 + 12 * math.sin(t * 0.2 + 3))
        b2 = int(35 + 18 * math.sin(t * 0.6 + 5))

        # Create gradient
        grad = QLinearGradient(0, 0, width, height)
        grad.setColorAt(0, QColor(r1, g1, b1))
        grad.setColorAt(0.5, QColor(15 + int(5 * math.sin(t)), 25 + int(8 * math.sin(t + 1)), 30 + int(10 * math.sin(t + 2))))
        grad.setColorAt(1, QColor(r2, g2, b2))

        painter.fillRect(0, 0, width, height, grad)

    def draw_boundary(self, painter):
        """Draw the simulation boundary with proper styling"""
        if not self.engine:
            return

        center_x = self.engine.center_x
        center_y = self.engine.center_y
        radius = self.engine.boundary_radius
        boundary_type = self.engine.boundary_type

        # Draw glow effect (multiple layers)
        for glow in range(20, 0, -1):
            glow_alpha = int(40 * (1 - glow / 20))
            glow_color = QColor(100, 180, 255, glow_alpha)
            glow_pen = QPen(glow_color)
            glow_pen.setWidth(1)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.NoBrush)

            if boundary_type == "circle":
                painter.drawEllipse(
                    int(center_x - radius - glow),
                    int(center_y - radius - glow),
                    int(radius * 2 + glow * 2),
                    int(radius * 2 + glow * 2)
                )
            elif boundary_type == "square":
                painter.drawRect(
                    int(center_x - radius - glow),
                    int(center_y - radius - glow),
                    int(radius * 2 + glow * 2),
                    int(radius * 2 + glow * 2)
                )
            elif boundary_type == "triangle":
                points = []
                for i in range(3):
                    angle = i * (2 * math.pi / 3) - math.pi / 2
                    px = center_x + (radius + glow) * math.cos(angle)
                    py = center_y + (radius + glow) * math.sin(angle)
                    points.append(QPoint(int(px), int(py)))
                painter.drawPolygon(QPolygon(points))

        # Draw main boundary with thick line
        boundary_pen = QPen(QColor(150, 220, 255, 255))
        boundary_pen.setWidth(5)
        boundary_pen.setCapStyle(Qt.RoundCap)
        boundary_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(boundary_pen)
        painter.setBrush(Qt.NoBrush)

        if boundary_type == "circle":
            painter.drawEllipse(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2)
            )
        elif boundary_type == "square":
            painter.drawRect(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2)
            )
        elif boundary_type == "triangle":
            points = []
            for i in range(3):
                angle = i * (2 * math.pi / 3) - math.pi / 2
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                points.append(QPoint(int(px), int(py)))
            painter.drawPolygon(QPolygon(points))

    def draw_shape(self, painter, x, y, radius, shape, color, rotation):
        """Draw particle with proper 3D effects"""
        x = int(x)
        y = int(y)
        r = int(radius)

        if r < 2:
            return

        # Draw shadow first (3D effect)
        shadow_offset = int(r * 0.4)
        shadow_color = QColor(0, 0, 0, 100)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(x + shadow_offset, y + shadow_offset, int(r * 1.5), int(r * 0.6))

        # Draw main shape
        if shape == "sphere":
            # Draw sphere with gradient effect
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 1))
            painter.drawEllipse(x - r, y - r, r * 2, r * 2)

            # Add highlight
            highlight_color = QColor(255, 255, 255, 180)
            painter.setBrush(QBrush(highlight_color))
            painter.setPen(Qt.NoPen)
            highlight_size = max(1, int(r * 0.35))
            painter.drawEllipse(
                x - int(r * 0.3),
                y - int(r * 0.3),
                highlight_size,
                highlight_size
            )

        elif shape == "cube":
            # Rotated square (isometric cube effect)
            painter.save()
            painter.translate(x, y)
            painter.rotate(math.degrees(rotation))

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 2))
            painter.drawRect(-r, -r, r * 2, r * 2)

            # Add 3D edge effect
            edge_color = QColor(color.red() + 30, color.green() + 30, color.blue() + 30, 200)
            painter.setPen(QPen(edge_color, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(-r + 2, -r + 2, r * 2 - 4, r * 2 - 4)

            painter.restore()

        elif shape == "star":
            # 5-pointed star with rotation
            points = []
            for i in range(10):
                angle = rotation + (2 * math.pi * i / 10)
                dist = r if i % 2 == 0 else r / 2.5
                px = x + dist * math.cos(angle)
                py = y + dist * math.sin(angle)
                points.append(QPoint(int(px), int(py)))

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 2))
            painter.drawPolygon(QPolygon(points))

        elif shape == "triangle":
            # Equilateral triangle
            points = []
            for i in range(3):
                angle = rotation + (2 * math.pi * i / 3) - math.pi / 2
                px = x + r * math.cos(angle)
                py = y + r * math.sin(angle)
                points.append(QPoint(int(px), int(py)))

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 2))
            painter.drawPolygon(QPolygon(points))

    def paintEvent(self, event):
        """Draw the entire scene"""
        if not self.engine:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw gradient background
        self.draw_gradient_background(painter)

        # Draw boundary
        self.draw_boundary(painter)

        # Draw objects sorted by depth (y position)
        sorted_objects = sorted(self.engine.objects, key=lambda obj: obj.y)

        # Color palette
        colors = [
            QColor(255, 100, 120),   # Red
            QColor(100, 200, 255),   # Blue
            QColor(100, 255, 150),   # Green
            QColor(255, 255, 100),   # Yellow
            QColor(255, 150, 200),   # Pink
            QColor(180, 120, 255),   # Purple
            QColor(100, 255, 255),   # Cyan
            QColor(255, 180, 100),   # Orange
        ]

        for i, obj in enumerate(sorted_objects):
            color = colors[i % len(colors)]

            # Adjust color brightness based on position (for depth effect)
            depth_factor = max(0.5, 1.0 - (obj.y - self.engine.center_y + self.engine.boundary_radius) / (2 * self.engine.boundary_radius))
            color_adjusted = QColor(
                max(50, int(color.red() * depth_factor)),
                max(50, int(color.green() * depth_factor)),
                max(50, int(color.blue() * depth_factor))
            )

            self.draw_shape(
                painter,
                obj.x,
                obj.y,
                obj.radius,
                self.engine.object_shape,
                color_adjusted,
                obj.rotation
            )

        # Update time counter for background animation
        self.time_counter += 1

        painter.end()


class PreviewImproved(QWidget):
    """Improved preview with smooth physics and proper calm-down"""

    object_count_changed = pyqtSignal(int)
    fps_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.width = 900
        self.height = 700
        self.running = False
        self.paused = False

        try:
            self.engine = Engine3D(self.width, self.height, boundary_radius=280, boundary_type="circle")
            self.audio_manager = AudioManager()

            # Initialize pygame mixer for audio
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            except Exception as ae:
                pass

            self.engine.reset()

        except Exception as e:
            print(f"PreviewImproved: Initialization error: {e}")
            self.engine = None
            self.audio_manager = None

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.elapsed_time = 0

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_simulation)
        self.update_timer.setInterval(16)  # 60 FPS

        # Build UI
        layout = QVBoxLayout()

        # Canvas
        self.canvas = CanvasWidgetImproved(self.engine)
        layout.addWidget(self.canvas)

        # Status label
        self.info_label = QLabel("Press Play to start")
        self.info_label.setStyleSheet("color: #aaa; padding: 5px; font-weight: bold;")
        self.info_label.setFont(QFont("Arial", 10))
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

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Calm-down settings
        calmdown_layout = QHBoxLayout()
        calmdown_layout.addWidget(QLabel("Calm down duration (sec):"))

        self.calmdown_spin = QSpinBox()
        self.calmdown_spin.setRange(5, 120)
        self.calmdown_spin.setValue(10)
        self.calmdown_spin.setMaximumWidth(80)
        calmdown_layout.addWidget(self.calmdown_spin)

        calmdown_layout.addStretch()
        layout.addLayout(calmdown_layout)

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
        """Apply new settings and restart"""
        if not self.engine:
            return

        self.engine.reset()
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
        self.info_label.setText("Reset - Press Play")
        self.canvas.update()

    def update_simulation(self):
        """Update with proper calm-down physics"""
        if not self.paused and self.engine:
            dt = 0.016  # 60 FPS

            # Update calm-down duration
            self.engine.set_calm_down_duration(self.calmdown_spin.value())

            # Update engine
            self.engine.update(dt)

            # Play collision/bounce sounds
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

            # Update FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
                self.fps_changed.emit(float(self.fps))

            current_count = self.engine.get_object_count()
            self.object_count_changed.emit(current_count)

            # Build status text
            state = self.engine.get_state()
            status = f"Objects: {current_count}/{self.engine.max_objects} | FPS: {self.fps}"

            if state == Engine3D.STATE_SPAWNING:
                status += " | Status: SPAWNING (chaotic)"
            elif state == Engine3D.STATE_CALM_DOWN:
                calm_elapsed = self.elapsed_time - self.engine.calm_down_time
                progress = (calm_elapsed / self.engine.calm_down_duration) * 100
                time_remaining = max(0, self.engine.calm_down_duration - calm_elapsed)
                status += f" | Status: CALMING DOWN ({progress:.0f}% - {time_remaining:.1f}s remaining)"
            elif state == Engine3D.STATE_SETTLED:
                status += " | Status: SETTLED (all stopped)"

            self.info_label.setText(status)
            self.canvas.update()

    def _play_sound(self, sound):
        """Play sound using pygame mixer"""
        try:
            if sound and hasattr(sound, 'audio_data'):
                audio_array = np.frombuffer(sound.audio_data, dtype=np.int16)
                if len(audio_array) > 0:
                    sound_obj = pygame.mixer.Sound(sound.audio_data)
                    sound_obj.set_volume(min(0.7, self.audio_manager.master_volume))
                    sound_obj.play()
        except:
            pass

    def apply_settings(self, config):
        """Apply configuration"""
        if not self.engine:
            return

        try:
            visual_settings = config.get("visual_settings", default={})
            particle_settings = config.get("particle_settings", default={})

            boundary_type = visual_settings.get("boundary_type", "circle")
            self.engine.boundary_type = boundary_type

            object_shape = visual_settings.get("object_shape", "sphere")
            self.engine.set_object_shape(object_shape)

            max_objects = particle_settings.get("max_particles", 50)
            self.engine.set_max_objects(max_objects)

            self.canvas.update()
        except:
            pass

