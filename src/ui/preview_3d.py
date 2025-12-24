"""Updated preview canvas for 3D visualization"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter
import pygame
import numpy as np
import time

from src.engine_3d import Engine3D
from src.renderer_3d import Renderer3D
from src.audio_manager import AudioManager


class CanvasWidget(QWidget):
    """Custom widget to display 3D simulation"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pygame_surface = None
        self.cached_pixmap = None
        self.setMinimumSize(900, 700)
        self.setStyleSheet("background-color: black; border: 2px solid #444;")

    def set_pygame_surface(self, surface):
        """Set pygame surface to display"""
        self.pygame_surface = surface

        if surface is not None:
            try:
                # Convert pygame surface to numpy array safely
                frame_array = pygame.surfarray.array3d(surface)
                frame_array = np.transpose(frame_array, (1, 0, 2))
                frame_array = np.ascontiguousarray(frame_array[:, :, ::-1])

                # Convert to bytes properly
                h, w, ch = frame_array.shape
                bytes_per_line = ch * w

                # Create QImage from bytes
                image_bytes = frame_array.astype(np.uint8).tobytes()
                qt_image = QImage(image_bytes, w, h, bytes_per_line, QImage.Format_RGB888)

                # Cache pixmap
                self.cached_pixmap = QPixmap.fromImage(qt_image)
            except Exception as e:
                print(f"Warning: Failed to convert surface: {e}")
                self.cached_pixmap = None

        self.update()

    def paintEvent(self, event):
        """Paint the canvas"""
        if self.cached_pixmap is None:
            return

        # Draw on widget
        painter = QPainter(self)
        scaled_pixmap = self.cached_pixmap.scaled(
            self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        x = (self.width() - scaled_pixmap.width()) // 2
        y = (self.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()


class Preview3D(QWidget):
    """Real-time 3D particle simulation preview"""

    object_count_changed = pyqtSignal(int)
    fps_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.width = 900
        self.height = 700
        self.running = False
        self.paused = False

        try:
            # Initialize pygame with error handling
            if not pygame.get_init():
                pygame.init()

            self.pygame_surface = pygame.Surface((self.width, self.height))

            # Initialize 3D engine and renderer
            self.engine = Engine3D(self.width, self.height, boundary_radius=280, boundary_type="circle")
            self.renderer = Renderer3D(self.width, self.height)
            self.audio_manager = AudioManager()

            # Reset engine to create initial objects
            self.engine.reset()

        except Exception as e:
            print(f"Warning: Pygame initialization had issues: {e}")
            # Create minimal fallback
            self.pygame_surface = None
            self.engine = None
            self.renderer = None
            self.audio_manager = None

        # Performance tracking
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.elapsed_time = 0

        # Timer for updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_simulation)
        self.update_timer.setInterval(16)  # 60 FPS

        # UI Layout
        layout = QVBoxLayout()

        # Canvas area
        self.canvas = CanvasWidget()
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

        self.setLayout(layout)

    def play(self):
        """Start simulation"""
        self.running = True
        self.paused = False
        self.update_timer.start()
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.reset_button.setEnabled(False)
        self.info_label.setText("🎮 Simulation running...")

    def pause(self):
        """Pause simulation"""
        self.paused = True
        self.update_timer.stop()
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(True)
        self.info_label.setText("⏸ Paused")

    def reset(self):
        """Reset simulation"""
        if self.engine:
            self.engine.reset()
        self.render_frame()
        self.info_label.setText("↻ Reset - Press Play")

    def update_simulation(self):
        """Update simulation and audio"""
        if not self.paused and self.engine:
            dt = 0.016  # 60 FPS

            # Get speed multiplier from slider
            speed_factor = self.speed_slider.value() / 5.0

            # Store old object count
            old_count = len(self.engine.objects)

            # Update engine
            self.engine.update(dt)

            # Handle audio for bounces
            for bounce in self.engine.bounce_log:
                if bounce.get('time', 0) > self.elapsed_time - dt:
                    sound = self.audio_manager.generate_bounce_sound()

            self.engine.bounce_log = []

            # Handle audio for collisions
            for collision in self.engine.collision_log:
                if collision.get('time', 0) > self.elapsed_time - dt:
                    sound = self.audio_manager.generate_collision_sound()

            self.engine.collision_log = []

            # Update time
            self.elapsed_time += dt

            # Update FPS counter
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
                self.fps_changed.emit(float(self.fps))

            # Emit object count
            current_count = self.engine.get_object_count()
            self.object_count_changed.emit(current_count)

            # Update info
            self.info_label.setText(
                f"Objects: {current_count}/{self.engine.max_objects} | "
                f"FPS: {self.fps} | Time: {self.elapsed_time:.1f}s"
            )

        self.render_frame()

    def render_frame(self):
        """Render current frame"""
        if not self.engine or not self.renderer:
            return

        # Render particles
        pygame_surface = self.renderer.render(
            self.engine.objects,
            self.engine.boundary_radius,
            self.engine.boundary_type
        )

        # Draw HUD
        self.renderer.draw_hud(
            pygame_surface,
            self.engine.get_object_count(),
            self.fps,
            self.elapsed_time,
            self.engine.max_objects
        )

        # Display on canvas
        self.canvas.set_pygame_surface(pygame_surface)

    def apply_settings(self, config):
        """Apply configuration settings"""
        visual_settings = config.get("visual_settings", {})

        # Apply visual settings
        self.renderer.set_color_scheme(
            visual_settings.get("color_scheme", "Pastel Dreams")
        )

        # Get boundary type from settings
        boundary_type = visual_settings.get("boundary_type", "circle")
        self.engine.boundary_type = boundary_type

        # Get object shape
        object_shape = visual_settings.get("object_shape", "sphere")
        self.engine.set_object_shape(object_shape)

        # Get max objects
        max_objects = config.get("particle_settings", {}).get("max_particles", 50)
        self.engine.set_max_objects(max_objects)

        self.render_frame()

