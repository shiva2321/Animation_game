"""Preview canvas widget for PyQt5"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QRect
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter
import pygame
import numpy as np
import time

from src.particle_engine import ParticleEngine
from src.renderer import Renderer


class CanvasWidget(QWidget):
    """Custom widget to display pygame surface"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pygame_surface = None
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: black; border: 1px solid gray;")

    def set_pygame_surface(self, surface):
        """Set pygame surface to display"""
        self.pygame_surface = surface
        self.update()

    def paintEvent(self, event):
        """Paint the canvas"""
        if self.pygame_surface is None:
            return

        # Convert pygame surface to numpy array
        frame_array = pygame.surfarray.array3d(self.pygame_surface)
        frame_array = np.transpose(frame_array, (1, 0, 2))
        frame_array = np.ascontiguousarray(frame_array[:, :, ::-1])  # RGB to BGR for QImage

        # Create QImage
        h, w, ch = frame_array.shape
        bytes_per_line = ch * w
        qt_image = QImage(
            frame_array.data, w, h, bytes_per_line, QImage.Format_RGB888
        )

        # Draw on widget
        painter = QPainter(self)
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        x = (self.width() - scaled_pixmap.width()) // 2
        y = (self.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()


class PreviewCanvas(QWidget):
    """Real-time particle simulation preview"""

    particle_count_changed = pyqtSignal(int)
    fps_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.width = 800
        self.height = 600
        self.running = False
        self.paused = False

        # Initialize pygame surface
        pygame.init()
        self.pygame_surface = pygame.Surface((self.width, self.height))

        # Initialize engine and renderer
        boundary_radius = min(self.width, self.height) / 3
        self.engine = ParticleEngine(self.width, self.height, boundary_radius)
        self.renderer = Renderer(self.width, self.height)

        # Performance tracking
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

        # Timer for updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_simulation)
        self.update_timer.setInterval(16)  # ~60 FPS

        # UI Layout
        layout = QVBoxLayout()

        # Canvas area
        self.canvas = CanvasWidget()
        layout.addWidget(self.canvas)

        # Control buttons
        button_layout = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play)
        button_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        button_layout.addWidget(self.reset_button)

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

    def pause(self):
        """Pause simulation"""
        self.paused = True
        self.update_timer.stop()
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(True)

    def reset(self):
        """Reset simulation"""
        self.engine.reset()
        initial_count = min(10, self.engine.max_particles // 10)
        self.engine.spawn_particle(initial_count)

        # Render current state
        self.render_frame()

    def update_simulation(self):
        """Update particle simulation"""
        if not self.paused:
            dt = 1.0 / 60.0  # 60 FPS
            self.engine.update(dt)

            # Update FPS counter
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
                self.fps_changed.emit(float(self.fps))

            # Emit particle count
            self.particle_count_changed.emit(self.engine.get_particle_count())

        self.render_frame()

    def render_frame(self):
        """Render current frame to canvas"""
        if not hasattr(self, 'engine'):
            return

        # Render particles
        pygame_surface = self.renderer.render(
            self.engine.particles, self.engine.boundary_radius
        )

        # Draw HUD
        self.renderer.draw_hud(
            pygame_surface, self.engine.get_particle_count(), self.fps
        )

        # Display on canvas
        self.canvas.set_pygame_surface(pygame_surface)

    def apply_settings(self, config):
        """Apply configuration settings"""
        particle_settings = config.get("particle_settings")
        visual_settings = config.get("visual_settings")

        # Apply particle settings
        self.engine.spawn_rate = particle_settings.get("spawn_rate", 5)
        self.engine.max_particles = particle_settings.get("max_particles", 100)
        self.engine.set_particle_size_range(
            particle_settings.get("min_size", 3),
            particle_settings.get("max_size", 15)
        )
        self.engine.set_particle_speed_range(
            particle_settings.get("min_speed", 1),
            particle_settings.get("max_speed", 5)
        )
        self.engine.set_particle_shape(particle_settings.get("shape", "Circle"))

        # Apply visual settings
        self.renderer.set_color_scheme(visual_settings.get("color_scheme", "Pastel Dreams"))
        self.renderer.boundary_style = visual_settings.get("boundary_style", "Solid")
        self.renderer.enable_glow = visual_settings.get("enable_glow", True)
        self.renderer.enable_trails = visual_settings.get("enable_trails", True)
        self.renderer.trail_length = visual_settings.get("trail_length", 20)
        self.renderer.collision_effect = visual_settings.get("collision_effect", "Sparkle")

        # Refresh display
        self.render_frame()

