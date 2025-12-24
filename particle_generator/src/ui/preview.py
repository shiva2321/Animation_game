
import pygame
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, QSize, Qt
from PyQt5.QtGui import QImage, QPainter
import os

# Set up environment for headless Pygame rendering suitable for embedding
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from ..core.settings import Settings
from ..physics.system import ParticleSystem
from ..graphics.renderer import Renderer
from ..core.events import event_queue

class PygamePreviewWidget(QWidget):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        # Initialize Pygame display module
        pygame.display.init()

        self.particle_system = ParticleSystem(settings)
        self.renderer = Renderer(settings)

        self.setMinimumSize(QSize(640, 360))
        self.setFocusPolicy(Qt.StrongFocus)

        # Create a Pygame surface for rendering
        self.screen = pygame.Surface(self.settings.simulation.resolution, flags=pygame.SRCALPHA)

        # Timer for the simulation and render loop
        self.timer = QTimer(self)
        self.timer.setInterval(1000 // self.settings.simulation.fps_preview)
        self.timer.timeout.connect(self.update_simulation)

        self.is_running = False
        self._last_dt = 1.0 / self.settings.simulation.fps_preview

    def resizeEvent(self, event):
        """Handle widget resizing."""
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Handle painting the Pygame screen onto the widget efficiently."""
        w, h = self.screen.get_size()

        # Directly map the Pygame surface buffer to a QImage
        # Format_RGB32 should be used for 32-bit surfaces, which is standard
        qimage = QImage(self.screen.get_buffer().raw, w, h, QImage.Format_RGB32)

        painter = QPainter(self)
        # Draw the QImage, scaling it to fit the widget's current size
        painter.drawImage(self.rect(), qimage, self.screen.get_rect())
        painter.end()

    def update_simulation(self):
        """Main loop called by the QTimer."""
        if not self.is_running:
            return

        dt = self.settings.simulation.dt_sim
        self._last_dt = 1.0 / self.settings.simulation.fps_preview

        # Run multiple simulation steps to match the preview framerate
        steps = int(self._last_dt / dt)
        for _ in range(max(1, steps)):
            self.particle_system.update(dt)

        # Draw the system state
        events = event_queue.get_events()
        self.renderer.draw(self.screen, self.particle_system, events, self._last_dt)
        self.update() # Trigger a paintEvent

    def play(self):
        if not self.is_running:
            self.is_running = True
            self.timer.start()
            if not self.particle_system.particles:
                self.reset()

    def pause(self):
        self.is_running = False
        self.timer.stop()

    def reset(self):
        self.particle_system.reset()
        if not self.is_running:
            # Draw the initial state if paused
            self.renderer.draw(self.screen, self.particle_system, [], self._last_dt)
            self.update()

    def update_settings(self, new_settings: Settings):
        self.settings = new_settings
        self.particle_system.settings = new_settings
        self.renderer.settings = new_settings
        self.renderer.palette.set_scheme(new_settings.visuals.scheme_name)

        # Check if resolution changed
        if self.screen.get_size() != self.settings.simulation.resolution:
            self.screen = pygame.Surface(self.settings.simulation.resolution, flags=pygame.SRCALPHA)

        self.timer.setInterval(1000 // self.settings.simulation.fps_preview)
        if self.is_running:
            self.timer.start()
